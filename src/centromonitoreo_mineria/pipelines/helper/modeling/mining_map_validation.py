from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def validate_mining_binary_map_validation_params(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_validation debe ser un diccionario.")
    _require_text(params.get("positive_label"), "mining_binary_map_validation.positive_label")
    _require_text(params.get("target_column"), "mining_binary_map_validation.target_column")
    _require_text(params.get("prediction_column"), "mining_binary_map_validation.prediction_column")
    _require_text(params.get("label_column"), "mining_binary_map_validation.label_column")
    coordinate_columns = params.get("coordinate_columns", {})
    _require_text(coordinate_columns.get("longitude"), "coordinate_columns.longitude")
    _require_text(coordinate_columns.get("latitude"), "coordinate_columns.latitude")
    _require_text(coordinate_columns.get("source_crs"), "coordinate_columns.source_crs")
    return dict(params)


def plot_classification_points_overlay(
    training_points: pd.DataFrame,
    testing_predictions: pd.DataFrame,
    map_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    plot_params = params.get("classification_points_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_classification_points.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    class_map, extent, crs = _read_raster_for_plot(_classification_path(map_metadata), params, Resampling.nearest)
    training = _project_points(training_points, crs, params)
    testing = _project_points(testing_predictions, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    _plot_rgb_background(axis, map_metadata, params, class_map.shape, extent)
    _plot_mining_overlay(axis, class_map, extent, params, plot_params)
    _plot_points_by_label(axis, training, params["label_column"], params, marker="o", size=plot_params.get("training_point_size", 12), alpha=0.75)
    _plot_points_by_label(axis, testing, params["label_column"], params, marker="^", size=plot_params.get("testing_point_size", 18), alpha=0.95)
    _finish_map(axis, figure, output_path, plot_params, "Clasificacion binaria con puntos")
    return {"output_path": output_path.as_posix(), "training_points": int(len(training)), "testing_points": int(len(testing))}


def plot_probability_points_overlay(
    testing_predictions: pd.DataFrame,
    map_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    plot_params = params.get("probability_points_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_probability_points.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    probability, extent, crs = _read_raster_for_plot(_probability_path(map_metadata), params, Resampling.bilinear)
    testing = _project_points(testing_predictions, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    image = axis.imshow(probability, extent=extent, cmap=plot_params.get("cmap", "viridis"), vmin=0, vmax=1)
    figure.colorbar(image, ax=axis, fraction=0.036, pad=0.02, label=plot_params.get("colorbar_label", "Probabilidad Mineria"))
    _plot_points_by_label(axis, testing, params["label_column"], params, marker="o", size=plot_params.get("point_size", 20), alpha=0.9)
    _finish_map(axis, figure, output_path, plot_params, "Probabilidad de mineria con puntos de prueba")
    return {"output_path": output_path.as_posix(), "testing_points": int(len(testing))}


def plot_testing_errors_overlay(
    testing_predictions: pd.DataFrame,
    map_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    plot_params = params.get("errors_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_testing_errors.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    class_map, extent, crs = _read_raster_for_plot(_classification_path(map_metadata), params, Resampling.nearest)
    testing = _project_points(testing_predictions, crs, params)
    false_negatives, false_positives = _error_groups(testing, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    _plot_rgb_background(axis, map_metadata, params, class_map.shape, extent)
    _plot_mining_overlay(axis, class_map, extent, params, plot_params)
    axis.scatter(testing.geometry.x, testing.geometry.y, s=plot_params.get("context_point_size", 10), c="#ffffff", edgecolors="#333333", linewidths=0.3, alpha=0.65, label="Puntos test")
    _plot_error_group(axis, false_negatives, plot_params, "false_negative", "Mineria omitida")
    _plot_error_group(axis, false_positives, plot_params, "false_positive", "Falso positivo")
    _finish_map(axis, figure, output_path, plot_params, "Errores sobre mapa clasificado")
    return {
        "output_path": output_path.as_posix(),
        "false_negatives": int(len(false_negatives)),
        "false_positives": int(len(false_positives)),
    }


def build_mining_binary_map_validation_metadata(
    testing_predictions: pd.DataFrame,
    classification_points_metadata: dict[str, Any],
    probability_points_metadata: dict[str, Any],
    testing_errors_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    false_negatives, false_positives = _error_groups(testing_predictions, params)
    return {
        "positive_label": params["positive_label"],
        "testing_rows": int(len(testing_predictions)),
        "false_negatives": int(len(false_negatives)),
        "false_positives": int(len(false_positives)),
        "classification_points_plot": classification_points_metadata,
        "probability_points_plot": probability_points_metadata,
        "testing_errors_plot": testing_errors_metadata,
    }


def _classification_path(map_metadata: dict[str, Any]) -> str:
    return map_metadata["prediction"]["classification_map"]


def _probability_path(map_metadata: dict[str, Any]) -> str:
    return map_metadata["prediction"]["probability_map"]


def _read_raster_for_plot(path: str, params: dict[str, Any], resampling: Resampling) -> tuple[np.ndarray, list[float], Any]:
    with rasterio.open(path) as source:
        max_size = params.get("visualization", {}).get("max_size", 1600)
        scale = min(max_size / source.width, max_size / source.height, 1)
        shape = (max(1, int(source.height * scale)), max(1, int(source.width * scale)))
        data = source.read(1, out_shape=shape, resampling=resampling).astype("float32")
        if source.nodata is not None:
            data = np.where(data == source.nodata, np.nan, data)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        return data, extent, source.crs


def _project_points(points: pd.DataFrame, target_crs: Any, params: dict[str, Any]) -> gpd.GeoDataFrame:
    coordinate_columns = params["coordinate_columns"]
    gdf = gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(points[coordinate_columns["longitude"]], points[coordinate_columns["latitude"]]),
        crs=coordinate_columns["source_crs"],
    )
    return gdf.to_crs(target_crs) if target_crs else gdf


def _plot_rgb_background(axis: Any, map_metadata: dict[str, Any], params: dict[str, Any], shape: tuple[int, int], extent: list[float]) -> None:
    raster_dir = Path(map_metadata["raster_dir"])
    template = params.get("band_file_template", "Sentinel2_{band}_Masked.tif")
    rgb = []
    for band in ["B4", "B3", "B2"]:
        path = raster_dir / template.format(band=band)
        with rasterio.open(path) as source:
            rgb.append(_stretch(source.read(1, out_shape=shape, resampling=Resampling.bilinear).astype("float32")))
    axis.imshow(np.dstack(rgb), extent=extent)


def _plot_mining_overlay(axis: Any, class_map: np.ndarray, extent: list[float], params: dict[str, Any], plot_params: dict[str, Any]) -> None:
    mining_value = params.get("class_values", {}).get(params["positive_label"], 1)
    overlay = np.where(class_map == mining_value, 1, np.nan)
    axis.imshow(
        overlay,
        extent=extent,
        cmap=ListedColormap([plot_params.get("mining_color", "#E31A1C")]),
        alpha=plot_params.get("mining_alpha", 0.5),
        interpolation="nearest",
    )


def _plot_points_by_label(axis: Any, points: gpd.GeoDataFrame, label_column: str, params: dict[str, Any], marker: str, size: int, alpha: float) -> None:
    colors = params.get("class_colors", {})
    for label in sorted(points[label_column].dropna().unique()):
        subset = points[points[label_column] == label]
        axis.scatter(
            subset.geometry.x,
            subset.geometry.y,
            s=size,
            marker=marker,
            c=colors.get(label, "#ffffff"),
            edgecolors="#111111",
            linewidths=0.35,
            alpha=alpha,
            label=str(label),
        )


def _plot_error_group(axis: Any, points: gpd.GeoDataFrame, plot_params: dict[str, Any], key: str, label: str) -> None:
    if points.empty:
        return
    style = plot_params.get(key, {})
    axis.scatter(
        points.geometry.x,
        points.geometry.y,
        s=style.get("point_size", 80),
        marker=style.get("marker", "X"),
        c=style.get("color", "#00FFFF"),
        edgecolors=style.get("edgecolor", "#000000"),
        linewidths=style.get("linewidth", 0.8),
        label=label,
    )


def _error_groups(points: pd.DataFrame, params: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = params["target_column"]
    prediction = params["prediction_column"]
    positive = params["positive_label"]
    false_negatives = points[(points[target] == positive) & (points[prediction] != positive)]
    false_positives = points[(points[target] != positive) & (points[prediction] == positive)]
    return false_negatives, false_positives


def _finish_map(axis: Any, figure: Any, output_path: Path, plot_params: dict[str, Any], default_title: str) -> None:
    axis.set_title(plot_params.get("title", default_title))
    axis.set_axis_off()
    axis.legend(fontsize=plot_params.get("legend_font_size", 7), loc=plot_params.get("legend_location", "best"))
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)


def _stretch(array: np.ndarray) -> np.ndarray:
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return np.zeros_like(array, dtype="float32")
    lower, upper = np.percentile(finite, [2, 98])
    if lower == upper:
        return np.zeros_like(array, dtype="float32")
    return np.clip((array - lower) / (upper - lower), 0, 1)


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")
