from pathlib import Path
from typing import Any

import matplotlib
import rasterio

from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.utils.cartography import (
    draw_class_map,
    style_cartographic_axis,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_mining_binary_postprocessed_map(
    mining_binary_map_postprocessing_output_metadata: dict[str, Any],
    mining_binary_map_postprocessing_config: dict[str, Any],
) -> dict[str, Any]:
    """Genera un mapa cartografico del raster binario postprocesado."""
    params = mining_binary_map_postprocessing_config
    map_params = params.get("map", {})
    output_path = Path(map_params.get("output_path", "data/08_reporting/mining_binary_postprocessed_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(mining_binary_map_postprocessing_output_metadata["postprocessed_classification_map"]) as source:
        class_map = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        crs = source.crs.to_string() if source.crs else "CRS no definido"

    figure, axis = plt.subplots(figsize=tuple(map_params.get("figure_size", [9, 9])))
    draw_class_map(axis, class_map, extent, params)
    style_cartographic_axis(
        axis,
        extent,
        map_params,
        crs,
        mining_binary_map_postprocessing_output_metadata,
    )
    layout = map_params.get("layout", {})
    figure.subplots_adjust(
        left=float(layout.get("left", 0.11)),
        right=float(layout.get("right", 0.97)),
        bottom=float(layout.get("bottom", 0.12)),
        top=float(layout.get("top", 0.92)),
    )
    figure.savefig(output_path, dpi=int(map_params.get("dpi", 180)), bbox_inches="tight")
    plt.close(figure)
    return {
        "output_path": output_path.as_posix(),
        "title": map_params.get("title", "Mapa postprocesado de mineria"),
        "grid": bool(map_params.get("grid", {}).get("enabled", True)),
        "north_arrow": bool(map_params.get("north_arrow", {}).get("enabled", True)),
        "scale_bar": bool(map_params.get("scale_bar", {}).get("enabled", True)),
    }
