from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import rasterio

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .build_topographic_features import _configure_proj


# Funcion para generar mapas PNG de DEM y pendiente a partir de los raster alineados.
def plot_topographic_feature_maps(
    topographic_features_metadata: dict[str, Any],
    topographic_features_config: dict[str, Any],
) -> dict[str, Any]:
    params = topographic_features_config["topographic_features"]
    plot_params = params.get("map_plots", {})
    aligned_rasters = {
        item["band"]: item["output_path"]
        for item in topographic_features_metadata.get("aligned_rasters", [])
    }
    plot_metadata = []
    for layer in _layers_to_plot(params):
        band = layer["band"]
        if band not in aligned_rasters:
            raise ValueError(f"No existe raster alineado para la banda topografica: {band}")
        output_path = _output_path(layer, plot_params)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plot_metadata.append(
            _plot_raster_map(
                raster_path=Path(aligned_rasters[band]),
                output_path=output_path,
                layer=layer,
                plot_params=plot_params,
            )
        )
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "plots": plot_metadata,
    }


def _layers_to_plot(params: dict[str, Any]) -> list[dict[str, Any]]:
    output_bands = params.get("output_bands", {})
    default_layers = [
        {
            "band": output_bands.get("elevation", "DEM"),
            "output_path": "data/08_reporting/topographic_features/topography_dem_map.png",
            "title": "Modelo digital de elevacion (DEM)",
            "colorbar_label": "Elevacion (m s. n. m.)",
            "cmap": "terrain",
        },
        {
            "band": output_bands.get("slope", "SLOPE"),
            "output_path": "data/08_reporting/topographic_features/topography_slope_map.png",
            "title": "Pendiente derivada del DEM",
            "colorbar_label": "Pendiente (grados)",
            "cmap": "magma",
        },
    ]
    return list(params.get("map_plots", {}).get("layers", default_layers))


def _output_path(layer: dict[str, Any], plot_params: dict[str, Any]) -> Path:
    path = Path(layer.get("output_path", ""))
    if str(path):
        return path
    output_dir = Path(plot_params.get("output_dir", "data/08_reporting/topographic_features"))
    return output_dir / f"topography_{layer['band'].lower()}_map.png"


def _plot_raster_map(
    raster_path: Path,
    output_path: Path,
    layer: dict[str, Any],
    plot_params: dict[str, Any],
) -> dict[str, Any]:
    with rasterio.Env(**_configure_proj()), rasterio.open(raster_path) as source:
        data = source.read(1, masked=True).astype("float32")
        bounds = source.bounds
        extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

    values = data.compressed()
    if values.size == 0:
        raise ValueError(f"No hay datos validos para graficar: {raster_path.as_posix()}")
    vmin, vmax = _display_limits(values, plot_params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [10, 8])), constrained_layout=True)
    figure.patch.set_facecolor("white")
    axis.set_facecolor(plot_params.get("background_color", "#f7fbff"))
    image = axis.imshow(data, cmap=layer.get("cmap", "viridis"), extent=extent, vmin=vmin, vmax=vmax)
    axis.set_title(layer.get("title", layer["band"]), fontsize=15, fontweight="bold", pad=12)
    axis.set_xlabel(plot_params.get("x_label", "Coordenada X (EPSG:9377)"), fontsize=10)
    axis.set_ylabel(plot_params.get("y_label", "Coordenada Y (EPSG:9377)"), fontsize=10)
    axis.ticklabel_format(style="plain", useOffset=False)
    axis.tick_params(labelsize=8)
    colorbar = figure.colorbar(image, ax=axis, fraction=0.036, pad=0.03)
    colorbar.set_label(layer.get("colorbar_label", layer["band"]), fontsize=10)
    colorbar.ax.tick_params(labelsize=8)
    figure.savefig(output_path, dpi=int(plot_params.get("dpi", 220)), bbox_inches="tight")
    plt.close(figure)
    return {
        "band": layer["band"],
        "source_raster": raster_path.as_posix(),
        "output_path": output_path.as_posix(),
        "cmap": layer.get("cmap", "viridis"),
        "min": float(values.min()),
        "max": float(values.max()),
        "display_min": float(vmin),
        "display_max": float(vmax),
    }


def _display_limits(values: np.ndarray, plot_params: dict[str, Any]) -> tuple[float, float]:
    percentiles = plot_params.get("percentile_clip", [2, 98])
    vmin, vmax = np.percentile(values, percentiles)
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
        return float(values.min()), float(values.max())
    return float(vmin), float(vmax)
