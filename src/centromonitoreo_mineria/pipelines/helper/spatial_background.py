from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import box


# Funcion para agregar una imagen Sentinel-2 como fondo de un mapa.
def add_sentinel2_background(
    axis: Any,
    plot_params: dict[str, Any],
    target_crs: Any,
    points_bounds: Any | None = None,
) -> dict[str, Any]:
    params = plot_params.get("sentinel2_background", {})
    if not params.get("enabled", False):
        return _metadata(False, False, None, None)

    image_path = Path(params["image_path"])
    try:
        image = plt.imread(image_path)
        extent = _project_extent(params["extent"], params.get("extent_crs", "EPSG:4326"), target_crs)
        axis.imshow(
            image,
            extent=[extent[0], extent[2], extent[1], extent[3]],
            origin=params.get("origin", "upper"),
            alpha=params.get("alpha", 1.0),
            aspect=params.get("aspect", "auto"),
        )
        plot_bounds = _bounds_with_margin(_combine_bounds(extent, points_bounds), params.get("margin", 0.02))
        axis.set_xlim(plot_bounds[0], plot_bounds[2])
        axis.set_ylim(plot_bounds[1], plot_bounds[3])
        return _metadata(True, True, image_path.as_posix(), None)
    except Exception as exc:
        if params.get("strict", False):
            raise RuntimeError("No se pudo agregar la imagen Sentinel-2 de fondo.") from exc
        return _metadata(True, False, image_path.as_posix(), str(exc))


# Funcion para proyectar la extension de la imagen al CRS del mapa.
def _project_extent(extent: list[float], extent_crs: str, target_crs: Any) -> list[float]:
    bounds = gpd.GeoSeries([box(*extent)], crs=extent_crs).to_crs(target_crs).total_bounds
    return [float(value) for value in bounds]


# Funcion para unir los limites de la imagen y de los puntos.
def _combine_bounds(background_bounds: list[float], points_bounds: Any | None) -> list[float]:
    if points_bounds is None:
        return background_bounds
    bounds = np.array([background_bounds, list(points_bounds)], dtype=float)
    return [
        float(bounds[:, 0].min()),
        float(bounds[:, 1].min()),
        float(bounds[:, 2].max()),
        float(bounds[:, 3].max()),
    ]


# Funcion para agregar margen alrededor del mapa.
def _bounds_with_margin(bounds: list[float], margin: float) -> list[float]:
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    return [
        bounds[0] - width * margin,
        bounds[1] - height * margin,
        bounds[2] + width * margin,
        bounds[3] + height * margin,
    ]


# Funcion para devolver metadatos del fondo Sentinel-2.
def _metadata(requested: bool, added: bool, image_path: str | None, error: str | None) -> dict[str, Any]:
    return {
        "sentinel2_background_requested": requested,
        "sentinel2_background_added": added,
        "sentinel2_background_image_path": image_path,
        "sentinel2_background_error": error,
    }
