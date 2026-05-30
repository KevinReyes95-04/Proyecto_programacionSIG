from datetime import datetime, timezone
from copy import deepcopy
from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import (
    output_bands,
)
from centromonitoreo_mineria.utils.earth_engine import load_ee


def sentinel2_params_for_training_features(
    spectral_indices_params: dict[str, Any],
    training_features_params: dict[str, Any],
) -> dict[str, Any]:
    """Aplica sobre la configuracion Sentinel-2 los ajustes usados para muestreo."""
    overrides = training_features_params.get("sentinel2_overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("sentinel2_training_features.sentinel2_overrides debe ser un diccionario.")
    params = deepcopy(spectral_indices_params)
    params.update(overrides)
    return params


def validate_sentinel2_training_features_params(
    params: dict[str, Any],
    spectral_indices_params: dict[str, Any],
) -> dict[str, Any]:
    """Valida los parametros que controlan la extraccion puntual de variables."""
    if not isinstance(params, dict):
        raise ValueError("sentinel2_training_features debe ser un diccionario.")

    feature_columns = params.get("feature_columns") or output_bands(spectral_indices_params)
    _require_text_list(feature_columns, "sentinel2_training_features.feature_columns")
    unknown_features = set(feature_columns) - set(output_bands(spectral_indices_params))
    if unknown_features:
        raise ValueError(
            "sentinel2_training_features.feature_columns incluye columnas no disponibles: "
            f"{sorted(unknown_features)}."
        )

    coordinate_columns = params.get("coordinate_columns", {})
    _require_text(coordinate_columns.get("longitude"), "sentinel2_training_features.coordinate_columns.longitude")
    _require_text(coordinate_columns.get("latitude"), "sentinel2_training_features.coordinate_columns.latitude")
    _require_text(coordinate_columns.get("crs", "EPSG:4326"), "sentinel2_training_features.coordinate_columns.crs")
    if coordinate_columns.get("crs", "EPSG:4326") != "EPSG:4326":
        raise ValueError("Earth Engine requiere coordinate_columns.crs='EPSG:4326' para ee.Geometry.Point.")

    _require_text(params.get("label_column"), "sentinel2_training_features.label_column")
    _require_positive_number(params.get("sample_scale", 10), "sentinel2_training_features.sample_scale")
    _require_positive_number(params.get("tile_scale", 4), "sentinel2_training_features.tile_scale")
    if not isinstance(params.get("drop_missing_features", True), bool):
        raise ValueError("sentinel2_training_features.drop_missing_features debe ser true o false.")
    if not isinstance(params.get("geometries", False), bool):
        raise ValueError("sentinel2_training_features.geometries debe ser true o false.")

    validated = dict(params)
    validated["feature_columns"] = list(feature_columns)
    return validated


def sample_points_from_image(
    points: pd.DataFrame,
    image: Any,
    params: dict[str, Any],
    dataset_name: str,
) -> pd.DataFrame:
    """Muestrea una imagen de Earth Engine sobre puntos etiquetados."""
    feature_columns = params["feature_columns"]
    if points.empty:
        return pd.DataFrame(columns=_ordered_columns(params, feature_columns))

    image_to_sample = image.select(feature_columns)
    if params.get("unmask_value") is not None:
        image_to_sample = image_to_sample.unmask(params["unmask_value"])

    features = _feature_collection_from_points(points, params, dataset_name)
    sampled = image_to_sample.sampleRegions(
        collection=features["collection"],
        properties=features["properties"],
        scale=params.get("sample_scale", 10),
        tileScale=params.get("tile_scale", 4),
        geometries=params.get("geometries", False),
    )
    table = _feature_collection_to_dataframe(sampled)
    if params.get("drop_missing_features", True) and not table.empty:
        table = table.dropna(subset=feature_columns)
    return _order_table_columns(table, params, feature_columns)


def build_sentinel2_training_features_metadata(
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    training_features: pd.DataFrame,
    testing_features: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Resume entradas, salidas y configuracion de la extraccion Sentinel-2."""
    params = config["sentinel2_training_features"]
    label_column = params["label_column"]
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_columns": params["feature_columns"],
        "label_column": label_column,
        "sample_scale": params.get("sample_scale", 10),
        "coordinate_columns": params.get("coordinate_columns", {}),
        "drop_missing_features": params.get("drop_missing_features", True),
        "training": _dataset_metadata(training_labeled_points, training_features, label_column),
        "testing": _dataset_metadata(testing_labeled_points, testing_features, label_column),
        "sentinel2_spectral_indices": {
            "start_date": config["sentinel2_spectral_indices"]["start_date"],
            "end_date": config["sentinel2_spectral_indices"]["end_date"],
            "cloud_cover_max": config["sentinel2_spectral_indices"].get("cloud_cover_max"),
            "cloud_mask": config["sentinel2_spectral_indices"].get("cloud_mask"),
            "cloud_mask_method": config["sentinel2_spectral_indices"].get("cloud_mask_method"),
        },
    }


def _feature_collection_from_points(
    points: pd.DataFrame,
    params: dict[str, Any],
    dataset_name: str,
) -> dict[str, Any]:
    ee = load_ee()
    lon_col = params["coordinate_columns"]["longitude"]
    lat_col = params["coordinate_columns"]["latitude"]
    properties = _properties_to_keep(points, params)
    features = []
    copied_properties = ["sample_id", *properties]
    for index, row in points.reset_index(drop=True).iterrows():
        props = {"sample_id": f"{dataset_name}_{index:06d}"}
        props.update(_row_properties(row, properties))
        geometry = ee.Geometry.Point([float(row[lon_col]), float(row[lat_col])])
        features.append(ee.Feature(geometry, props))
    return {"collection": ee.FeatureCollection(features), "properties": copied_properties}


def _feature_collection_to_dataframe(feature_collection: Any) -> pd.DataFrame:
    features = feature_collection.getInfo().get("features", [])
    return pd.DataFrame([feature.get("properties", {}) for feature in features])


def _row_properties(row: pd.Series, properties: list[str]) -> dict[str, Any]:
    values = {}
    for column in properties:
        value = row[column]
        if pd.notna(value):
            values[column] = value.item() if hasattr(value, "item") else value
    return values


def _properties_to_keep(points: pd.DataFrame, params: dict[str, Any]) -> list[str]:
    configured = params.get("properties_to_keep") or list(points.columns)
    return [column for column in configured if column in points.columns]


def _order_table_columns(table: pd.DataFrame, params: dict[str, Any], feature_columns: list[str]) -> pd.DataFrame:
    ordered = [column for column in _ordered_columns(params, feature_columns) if column in table.columns]
    remaining = [column for column in table.columns if column not in ordered]
    return table[ordered + remaining].reset_index(drop=True)


def _ordered_columns(params: dict[str, Any], feature_columns: list[str]) -> list[str]:
    coordinate_columns = params["coordinate_columns"]
    return [
        "sample_id",
        params["label_column"],
        coordinate_columns["longitude"],
        coordinate_columns["latitude"],
        *feature_columns,
    ]


def _dataset_metadata(source: pd.DataFrame, features: pd.DataFrame, label_column: str) -> dict[str, Any]:
    return {
        "input_rows": int(len(source)),
        "output_rows": int(len(features)),
        "dropped_rows": int(len(source) - len(features)),
        "input_class_counts": source[label_column].value_counts().to_dict(),
        "output_class_counts": features[label_column].value_counts().to_dict() if label_column in features else {},
    }


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")


def _require_positive_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} debe ser un numero mayor que cero.")
