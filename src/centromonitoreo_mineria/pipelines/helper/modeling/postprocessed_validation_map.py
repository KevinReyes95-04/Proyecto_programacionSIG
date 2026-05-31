from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Funcion para dibujar y guardar el mapa de validacion postprocesado.
def save_postprocessed_validation_map(
    point_validation: pd.DataFrame,
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
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


# Funcion para reconstruir puntos desde la tabla de validacion.
def _points_from_validation_table(point_validation: pd.DataFrame, target_crs: Any, params: dict[str, Any]) -> gpd.GeoDataFrame:
    coordinate_columns = params["coordinate_columns"]
    gdf = gpd.GeoDataFrame(
        point_validation.copy(),
        geometry=gpd.points_from_xy(point_validation[coordinate_columns["longitude"]], point_validation[coordinate_columns["latitude"]]),
        crs=coordinate_columns.get("source_crs"),
    )
    return gdf.to_crs(target_crs) if coordinate_columns.get("source_crs") and target_crs else gdf


# Funcion para leer el raster postprocesado.
def _read_postprocessed_raster(postprocessing_metadata: dict[str, Any]) -> tuple[np.ndarray, list[float], Any]:
    path = postprocessing_metadata["postprocessing"]["postprocessed_classification_map"]
    with rasterio.open(path) as source:
        data = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        return data, extent, source.crs


# Funcion para dibujar el mapa binario postprocesado.
def _draw_class_map(axis: Any, class_map: np.ndarray, extent: list[float], params: dict[str, Any]) -> None:
    map_params = params.get("map", {})
    nodata = params.get("class_nodata", 255)
    plot_data = np.ma.masked_where(class_map == nodata, class_map)
    cmap = ListedColormap([map_params.get("no_mining_color", "#1A9850"), map_params.get("mining_color", "#E31A1C")])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    axis.imshow(plot_data, cmap=cmap, norm=norm, extent=extent, interpolation="nearest")


# Funcion para dibujar puntos de validacion sobre el mapa.
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


# Funcion para ajustar estilo, grilla y anotaciones del mapa.
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


# Funcion para agregar flecha norte.
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


# Funcion para agregar barra de escala.
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


# Funcion para elegir una longitud de escala legible.
def _nice_scale_length(value: float) -> float:
    if value <= 0:
        return 1
    exponent = np.floor(np.log10(value))
    base = value / (10**exponent)
    nice_base = 1 if base < 2 else 2 if base < 5 else 5
    return float(nice_base * 10**exponent)


# Funcion para formatear distancias de la escala.
def _format_distance(meters: float) -> str:
    return f"{meters / 1000:g} km" if meters >= 1000 else f"{meters:g} m"
