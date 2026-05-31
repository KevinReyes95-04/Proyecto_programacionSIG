from pathlib import Path
from typing import Any

import matplotlib
from rasterio.enums import Resampling

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.figure_output import (
    finish_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.raster_layers import (
    classification_path,
    plot_mining_overlay,
    plot_rgb_background,
    probability_path,
    read_raster_for_plot,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Funcion para obtener y crear la ruta de salida de un mapa.
def map_output_path(plot_params: dict[str, Any], default_path: str) -> Path:
    output_path = Path(plot_params.get("output_path", default_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


# Funcion para crear una figura cartografica.
def map_figure(plot_params: dict[str, Any]) -> tuple[Any, Any]:
    return plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))


# Funcion para dibujar el raster clasificado y la capa minera.
def plot_classification_base(
    axis: Any,
    mining_binary_map_metadata: dict[str, Any],
    params: dict[str, Any],
    plot_params: dict[str, Any],
) -> tuple[Any, list[float], Any]:
    class_map, extent, crs = read_raster_for_plot(
        classification_path(mining_binary_map_metadata),
        params,
        Resampling.nearest,
    )
    plot_rgb_background(axis, mining_binary_map_metadata, params, class_map.shape, extent)
    plot_mining_overlay(axis, class_map, extent, params, plot_params)
    return class_map, extent, crs


# Funcion para dibujar el raster de probabilidad con barra de color.
def plot_probability_base(
    axis: Any,
    figure: Any,
    mining_binary_map_metadata: dict[str, Any],
    params: dict[str, Any],
    plot_params: dict[str, Any],
) -> tuple[Any, list[float], Any]:
    probability, extent, crs = read_raster_for_plot(
        probability_path(mining_binary_map_metadata),
        params,
        Resampling.bilinear,
    )
    image = axis.imshow(
        probability,
        extent=extent,
        cmap=plot_params.get("cmap", "viridis"),
        vmin=0,
        vmax=1,
    )
    figure.colorbar(
        image,
        ax=axis,
        fraction=0.036,
        pad=0.02,
        label=plot_params.get("colorbar_label", "Probabilidad Mineria"),
    )
    return probability, extent, crs


# Funcion para finalizar, guardar y cerrar un mapa.
def save_map(axis: Any, figure: Any, output_path: Path, plot_params: dict[str, Any], title: str) -> None:
    finish_map(axis, figure, output_path, plot_params, title)
    plt.close(figure)
