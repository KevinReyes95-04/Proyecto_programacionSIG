from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from matplotlib.colors import ListedColormap
from rasterio.enums import Resampling


def classification_path(map_metadata: dict[str, Any]) -> str:
    """Obtiene la ruta del raster clasificado desde los metadatos."""
    return map_metadata["prediction"]["classification_map"]


def probability_path(map_metadata: dict[str, Any]) -> str:
    """Obtiene la ruta del raster de probabilidad desde los metadatos."""
    return map_metadata["prediction"]["probability_map"]


def read_raster_for_plot(
    path: str,
    params: dict[str, Any],
    resampling: Resampling,
) -> tuple[np.ndarray, list[float], Any]:
    """Lee un raster remuestreado para graficarlo sin cargarlo completo."""
    with rasterio.open(path) as source:
        max_size = params.get("visualization", {}).get("max_size", 1600)
        scale = min(max_size / source.width, max_size / source.height, 1)
        shape = (max(1, int(source.height * scale)), max(1, int(source.width * scale)))
        data = source.read(1, out_shape=shape, resampling=resampling).astype("float32")
        if source.nodata is not None:
            data = np.where(data == source.nodata, np.nan, data)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        return data, extent, source.crs


def plot_rgb_background(
    axis: Any,
    map_metadata: dict[str, Any],
    params: dict[str, Any],
    shape: tuple[int, int],
    extent: list[float],
) -> None:
    """Dibuja una composicion RGB Sentinel-2 como fondo cartografico."""
    raster_dir = Path(map_metadata["raster_dir"])
    template = params.get("band_file_template", "Sentinel2_{band}_Masked.tif")
    rgb = []
    for band in ["B4", "B3", "B2"]:
        path = raster_dir / template.format(band=band)
        with rasterio.open(path) as source:
            band_data = source.read(1, out_shape=shape, resampling=Resampling.bilinear)
            rgb.append(stretch(band_data.astype("float32")))
    axis.imshow(np.dstack(rgb), extent=extent)


def plot_mining_overlay(
    axis: Any,
    class_map: np.ndarray,
    extent: list[float],
    params: dict[str, Any],
    plot_params: dict[str, Any],
) -> None:
    """Dibuja la clase mineria como una capa semitransparente."""
    mining_value = params.get("class_values", {}).get(params["positive_label"], 1)
    overlay = np.where(class_map == mining_value, 1, np.nan)
    axis.imshow(
        overlay,
        extent=extent,
        cmap=ListedColormap([plot_params.get("mining_color", "#E31A1C")]),
        alpha=plot_params.get("mining_alpha", 0.5),
        interpolation="nearest",
    )


def stretch(array: np.ndarray) -> np.ndarray:
    """Escala una banda al rango 0-1 usando percentiles robustos."""
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return np.zeros_like(array, dtype="float32")
    lower, upper = np.percentile(finite, [2, 98])
    if lower == upper:
        return np.zeros_like(array, dtype="float32")
    return np.clip((array - lower) / (upper - lower), 0, 1)
