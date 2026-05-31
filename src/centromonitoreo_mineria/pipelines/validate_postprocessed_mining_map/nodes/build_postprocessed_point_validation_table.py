from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point


# Funcion para cruzar puntos de entrenamiento/prueba con poligonos mineros.
def build_postprocessed_point_validation_table(
    training_points: pd.DataFrame,
    testing_points: pd.DataFrame,
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> pd.DataFrame:
    polygons = _read_mining_polygons(postprocessing_metadata)
    points = _prepare_points(training_points, testing_points, polygons.crs, params)
    mining_area = polygons.geometry.union_all() if hasattr(polygons.geometry, "union_all") else polygons.unary_union
    inside = points.geometry.apply(mining_area.covers) if not polygons.empty else pd.Series(False, index=points.index)
    result = points.drop(columns="geometry").copy()
    result["inside_mining_polygon"] = inside.astype(bool).values
    result["observed_binary_label"] = np.where(
        result[params["label_column"]] == params["positive_label"],
        params["positive_label"],
        params["negative_label"],
    )
    result["postprocessed_prediction"] = np.where(
        result["inside_mining_polygon"],
        params["positive_label"],
        params["negative_label"],
    )
    result["validation_status"] = result.apply(lambda row: _validation_status(row, params), axis=1)
    return result


# Funcion para leer los poligonos mineros postprocesados.
def _read_mining_polygons(postprocessing_metadata: dict[str, Any]) -> gpd.GeoDataFrame:
    data = postprocessing_metadata["postprocessing"]
    polygons = gpd.read_file(data["polygons"])
    raster_crs = data.get("raster", {}).get("crs")
    if raster_crs:
        polygons = polygons.set_crs(raster_crs, allow_override=True)
    return polygons


# Funcion para unir puntos de entrenamiento y prueba como GeoDataFrame.
def _prepare_points(
    training_points: pd.DataFrame,
    testing_points: pd.DataFrame,
    target_crs: Any,
    params: dict[str, Any],
) -> gpd.GeoDataFrame:
    training = training_points.copy()
    testing = testing_points.copy()
    training["dataset_split"] = "training"
    testing["dataset_split"] = "testing"
    points = pd.concat([training, testing], ignore_index=True)
    coordinate_columns = params["coordinate_columns"]
    geometries = [
        Point(xy)
        for xy in zip(points[coordinate_columns["longitude"]], points[coordinate_columns["latitude"]])
    ]
    source_crs = coordinate_columns.get("source_crs")
    gdf = gpd.GeoDataFrame(points, geometry=geometries, crs=source_crs)
    return gdf.to_crs(target_crs) if source_crs and target_crs else gdf


# Funcion para clasificar cada punto como TP, TN, FP o FN.
def _validation_status(row: pd.Series, params: dict[str, Any]) -> str:
    observed = row["observed_binary_label"] == params["positive_label"]
    predicted = row["postprocessed_prediction"] == params["positive_label"]
    if observed and predicted:
        return "TP"
    if observed and not predicted:
        return "FN"
    if not observed and predicted:
        return "FP"
    return "TN"
