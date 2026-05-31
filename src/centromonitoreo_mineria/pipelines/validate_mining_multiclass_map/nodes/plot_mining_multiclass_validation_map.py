from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import ListedColormap
from rasterio.enums import Resampling

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Funcion para graficar aciertos y errores sobre el mapa multiclase.
def plot_mining_multiclass_validation_map(
    mining_multiclass_point_validation: pd.DataFrame,
    mining_multiclass_map_metadata: dict[str, Any],
    mining_multiclass_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_multiclass_map_validation_config
    plot_params = params.get("validation_map", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/validate_mining_multiclass_map/mining_multiclass_validation_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    class_map, extent, crs = _read_classification_for_plot(mining_multiclass_map_metadata, params)
    points = _project_points(mining_multiclass_point_validation, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [9, 9])))
    labels = list(params["class_values"].keys())
    cmap = ListedColormap([params.get("class_colors", {}).get(label, "#999999") for label in labels])
    axis.imshow(_display_array(class_map, labels, params), cmap=cmap, extent=extent, vmin=-0.5, vmax=len(labels) - 0.5, interpolation="nearest")
    _plot_status_points(axis, points, plot_params)
    axis.set_title(plot_params.get("title", "Validacion espacial multiclase"))
    axis.set_axis_off()
    axis.legend(loc=plot_params.get("legend_location", "lower left"), fontsize=plot_params.get("legend_font_size", 8))
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {
        "output_path": output_path.as_posix(),
        "total_points": int(len(points)),
        "errors": int((points["validation_status"] == "error").sum()),
        "correct": int((points["validation_status"] == "correcto").sum()),
    }


# Funcion para leer el raster clasificado remuestreado para mapa.
def _read_classification_for_plot(map_metadata: dict[str, Any], params: dict[str, Any]) -> tuple[np.ndarray, list[float], Any]:
    with rasterio.open(map_metadata["prediction"]["classification_map"]) as source:
        max_size = params.get("visualization", {}).get("max_size", 1600)
        scale = min(max_size / source.width, max_size / source.height, 1)
        shape = (max(1, int(source.height * scale)), max(1, int(source.width * scale)))
        data = source.read(1, out_shape=shape, resampling=Resampling.nearest).astype("float32")
        if source.nodata is not None:
            data = np.where(data == source.nodata, np.nan, data)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        return data, extent, source.crs


# Funcion para convertir valores raster en indices de colores.
def _display_array(class_map: np.ndarray, labels: list[str], params: dict[str, Any]) -> np.ndarray:
    display = np.full(class_map.shape, np.nan, dtype="float32")
    for index, label in enumerate(labels):
        display[class_map == int(params["class_values"][label])] = index
    return display


# Funcion para crear puntos y proyectarlos al CRS del raster.
def _project_points(points: pd.DataFrame, target_crs: Any, params: dict[str, Any]) -> gpd.GeoDataFrame:
    coordinate_columns = params["coordinate_columns"]
    gdf = gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(points[coordinate_columns["longitude"]], points[coordinate_columns["latitude"]]),
        crs=coordinate_columns.get("source_crs", "EPSG:4326"),
    )
    return gdf.to_crs(target_crs) if target_crs else gdf


# Funcion para dibujar puntos segun estado de validacion.
def _plot_status_points(axis: Any, points: gpd.GeoDataFrame, plot_params: dict[str, Any]) -> None:
    labels = {"correcto": "Correcto", "error": "Error", "sin_datos": "Sin datos"}
    for status, label in labels.items():
        subset = points[points["validation_status"] == status]
        if subset.empty:
            continue
        style = plot_params.get(status, {})
        axis.scatter(
            subset.geometry.x,
            subset.geometry.y,
            s=style.get("point_size", 45),
            marker=style.get("marker", "o"),
            c=style.get("color", "#ffffff"),
            edgecolors=style.get("edgecolor", "#111111"),
            linewidths=style.get("linewidth", 0.6),
            alpha=style.get("alpha", 0.9),
            label=label,
        )

