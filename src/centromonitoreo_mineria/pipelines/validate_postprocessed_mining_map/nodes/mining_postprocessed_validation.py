"""Nodos para validar el mapa de mineria postprocesado."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from shapely.geometry import Point

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def validate_postprocessed_mining_map_validation_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida los parametros para contrastar puntos contra el mapa postprocesado."""
    if not isinstance(params, dict):
        raise ValueError("postprocessed_mining_map_validation debe ser un diccionario.")
    _require_text(params.get("label_column"), "postprocessed_mining_map_validation.label_column")
    _require_text(params.get("positive_label"), "postprocessed_mining_map_validation.positive_label")
    _require_text(params.get("negative_label"), "postprocessed_mining_map_validation.negative_label")
    coordinate_columns = params.get("coordinate_columns", {})
    _require_text(coordinate_columns.get("longitude"), "coordinate_columns.longitude")
    _require_text(coordinate_columns.get("latitude"), "coordinate_columns.latitude")
    _validate_outputs(params.get("outputs", {}))
    return dict(params)


def build_postprocessed_point_validation_table(
    training_points: pd.DataFrame,
    testing_points: pd.DataFrame,
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> pd.DataFrame:
    """Cruza puntos de entrenamiento y prueba con poligonos mineros postprocesados."""
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


def build_postprocessed_class_summary(
    point_validation: pd.DataFrame,
    params: dict[str, Any],
) -> pd.DataFrame:
    """Resume por clase cuantos puntos caen dentro de poligonos mineros."""
    label_column = params["label_column"]
    summary = (
        point_validation.groupby(["dataset_split", label_column], dropna=False)
        .agg(
            total_points=("sample_id", "count"),
            points_inside_mining_polygon=("inside_mining_polygon", "sum"),
        )
        .reset_index()
    )
    summary["pct_inside_mining_polygon"] = (
        summary["points_inside_mining_polygon"] / summary["total_points"] * 100
    ).round(4)
    return summary.sort_values(["dataset_split", label_column]).reset_index(drop=True)


def plot_postprocessed_validation_map(
    point_validation: pd.DataFrame,
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Genera el mapa de validacion con estados TP, TN, FP y FN."""
    plot_params = params.get("map", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/postprocessed_mining_map_validation.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    class_map, extent, crs = _read_postprocessed_raster(postprocessing_metadata)
    points = _points_from_validation_table(point_validation, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [9, 9])))
    _draw_class_map(axis, class_map, extent, params)
    _draw_validation_points(axis, points, plot_params)
    _style_map(axis, extent, plot_params, postprocessing_metadata)
    figure.subplots_adjust(left=0.11, right=0.97, bottom=0.12, top=0.92)
    figure.savefig(output_path, dpi=int(plot_params.get("dpi", 180)), bbox_inches="tight")
    plt.close(figure)
    testing = point_validation[point_validation["dataset_split"] == "testing"]
    return {
        "output_path": output_path.as_posix(),
        "total_false_negatives": int((point_validation["validation_status"] == "FN").sum()),
        "total_false_positives": int((point_validation["validation_status"] == "FP").sum()),
        "testing_false_negatives": int((testing["validation_status"] == "FN").sum()),
        "testing_false_positives": int((testing["validation_status"] == "FP").sum()),
    }


def build_postprocessed_validation_metadata(
    point_validation: pd.DataFrame,
    class_summary: pd.DataFrame,
    plot_metadata: dict[str, Any],
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Resume conteos de validacion, area postprocesada y salidas graficas."""
    status_counts = point_validation["validation_status"].value_counts().to_dict()
    testing = point_validation[point_validation["dataset_split"] == "testing"]
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "positive_label": params["positive_label"],
        "negative_label": params["negative_label"],
        "total_points": int(len(point_validation)),
        "training_points": int((point_validation["dataset_split"] == "training").sum()),
        "testing_points": int(len(testing)),
        "status_counts": {key: int(value) for key, value in status_counts.items()},
        "testing_status_counts": {key: int(value) for key, value in testing["validation_status"].value_counts().to_dict().items()},
        "class_summary_rows": int(len(class_summary)),
        "postprocessed_area_ha": postprocessing_metadata["postprocessing"]["kept_area_ha"],
        "polygons": postprocessing_metadata["postprocessing"]["polygons"],
        "plot": plot_metadata,
    }


def _read_mining_polygons(postprocessing_metadata: dict[str, Any]) -> gpd.GeoDataFrame:
    data = postprocessing_metadata["postprocessing"]
    polygons = gpd.read_file(data["polygons"])
    raster_crs = data.get("raster", {}).get("crs")
    if raster_crs:
        polygons = polygons.set_crs(raster_crs, allow_override=True)
    return polygons


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


def _points_from_validation_table(point_validation: pd.DataFrame, target_crs: Any, params: dict[str, Any]) -> gpd.GeoDataFrame:
    coordinate_columns = params["coordinate_columns"]
    gdf = gpd.GeoDataFrame(
        point_validation.copy(),
        geometry=gpd.points_from_xy(point_validation[coordinate_columns["longitude"]], point_validation[coordinate_columns["latitude"]]),
        crs=coordinate_columns.get("source_crs"),
    )
    return gdf.to_crs(target_crs) if coordinate_columns.get("source_crs") and target_crs else gdf


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


def _read_postprocessed_raster(postprocessing_metadata: dict[str, Any]) -> tuple[np.ndarray, list[float], Any]:
    path = postprocessing_metadata["postprocessing"]["postprocessed_classification_map"]
    with rasterio.open(path) as source:
        data = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        return data, extent, source.crs


def _draw_class_map(axis: Any, class_map: np.ndarray, extent: list[float], params: dict[str, Any]) -> None:
    map_params = params.get("map", {})
    nodata = params.get("class_nodata", 255)
    plot_data = np.ma.masked_where(class_map == nodata, class_map)
    cmap = ListedColormap([map_params.get("no_mining_color", "#1A9850"), map_params.get("mining_color", "#E31A1C")])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    axis.imshow(plot_data, cmap=cmap, norm=norm, extent=extent, interpolation="nearest")


def _draw_validation_points(axis: Any, points: gpd.GeoDataFrame, plot_params: dict[str, Any]) -> None:
    styles = plot_params.get("status_styles", {})
    labels = {"TP": "Mineria validada", "TN": "No mineria validada", "FP": "Falso positivo", "FN": "Mineria omitida"}
    for status in ["TN", "TP", "FP", "FN"]:
        subset = points[points["validation_status"] == status]
        if subset.empty:
            continue
        style = styles.get(status, {})
        axis.scatter(
            subset.geometry.x,
            subset.geometry.y,
            s=style.get("size", 18),
            marker=style.get("marker", "o"),
            c=style.get("color", "#ffffff"),
            edgecolors=style.get("edgecolor", "#111111"),
            linewidths=style.get("linewidth", 0.4),
            alpha=style.get("alpha", 0.9),
            label=labels[status],
        )
    legend_items = [
        Patch(facecolor=plot_params.get("no_mining_color", "#1A9850"), edgecolor="black", label="No Mineria"),
        Patch(facecolor=plot_params.get("mining_color", "#E31A1C"), edgecolor="black", label="Mineria"),
    ]
    point_legend = axis.legend(loc=plot_params.get("points_legend_location", "lower left"), fontsize=plot_params.get("legend_font_size", 8))
    axis.add_artist(point_legend)
    axis.legend(handles=legend_items, loc=plot_params.get("class_legend_location", "upper left"), fontsize=plot_params.get("legend_font_size", 8))


def _style_map(axis: Any, extent: list[float], plot_params: dict[str, Any], metadata: dict[str, Any]) -> None:
    axis.set_xlim(extent[0], extent[1])
    axis.set_ylim(extent[2], extent[3])
    axis.set_aspect("equal")
    axis.set_title(plot_params.get("title", "Validacion del mapa postprocesado"), fontsize=plot_params.get("title_font_size", 15), weight="bold")
    axis.set_xlabel(plot_params.get("x_label", "Este (m)"))
    axis.set_ylabel(plot_params.get("y_label", "Norte (m)"))
    axis.ticklabel_format(style="plain", useOffset=False)
    axis.grid(True, color=plot_params.get("grid_color", "#303030"), alpha=plot_params.get("grid_alpha", 0.35), linewidth=plot_params.get("grid_linewidth", 0.6))
    _add_north_arrow(axis, plot_params.get("north_arrow", {}))
    _add_scale_bar(axis, extent, plot_params.get("scale_bar", {}))
    note = f"Area minera postprocesada: {metadata['postprocessing']['kept_area_ha']:.2f} ha"
    axis.text(0.01, -0.09, note, transform=axis.transAxes, ha="left", va="top", fontsize=plot_params.get("note_font_size", 8))


def _add_north_arrow(axis: Any, params: dict[str, Any]) -> None:
    x = float(params.get("x", 0.93))
    y = float(params.get("y", 0.88))
    axis.annotate(
        "N",
        xy=(x, y),
        xytext=(x, y - 0.12),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=int(params.get("font_size", 13)),
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "linewidth": 1.8, "color": "black"},
    )


def _add_scale_bar(axis: Any, extent: list[float], params: dict[str, Any]) -> None:
    width = extent[1] - extent[0]
    height = extent[3] - extent[2]
    length = _nice_scale_length(width * float(params.get("fraction", 0.2)))
    x0 = extent[0] + width * float(params.get("x_fraction", 0.08))
    y0 = extent[2] + height * float(params.get("y_fraction", 0.07))
    axis.plot([x0, x0 + length], [y0, y0], color="black", linewidth=3)
    axis.plot([x0, x0], [y0 - height * 0.005, y0 + height * 0.005], color="black", linewidth=2)
    axis.plot([x0 + length, x0 + length], [y0 - height * 0.005, y0 + height * 0.005], color="black", linewidth=2)
    axis.text(x0 + length / 2, y0 + height * 0.012, _format_distance(length), ha="center", va="bottom", fontsize=int(params.get("font_size", 10)), weight="bold")


def _nice_scale_length(value: float) -> float:
    if value <= 0:
        return 1
    exponent = np.floor(np.log10(value))
    base = value / (10**exponent)
    nice_base = 1 if base < 2 else 2 if base < 5 else 5
    return float(nice_base * 10**exponent)


def _format_distance(meters: float) -> str:
    return f"{meters / 1000:g} km" if meters >= 1000 else f"{meters:g} m"


def _validate_outputs(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("postprocessed_mining_map_validation.outputs debe ser un diccionario.")
    for key in ("point_validation", "class_summary"):
        _require_text(outputs.get(key), f"postprocessed_mining_map_validation.outputs.{key}")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")
