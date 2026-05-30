import os
from importlib.util import find_spec
from pathlib import Path
from typing import Any

_rasterio_spec = find_spec("rasterio")
if _rasterio_spec and _rasterio_spec.origin:
    _proj_data = Path(_rasterio_spec.origin).parent / "proj_data"
    if (_proj_data / "proj.db").exists():
        os.environ["PROJ_LIB"] = str(_proj_data)
        os.environ["PROJ_DATA"] = str(_proj_data)

import matplotlib
import numpy as np
import rasterio

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def build_sentinel2_download_visualizations(local_download_metadata: dict, config: dict) -> dict:
    """Genera PNGs de visualizacion desde las bandas Sentinel-2 descargadas."""
    # Funcion para crear mapas RGB y grilla de bandas desde GeoTIFF locales.
    params = config["sentinel2_download"]
    visualization = params.get("visualization", {})
    if not visualization.get("enabled", True):
        return {"enabled": False, "outputs": {}}

    output_dir = Path(visualization.get("output_dir", "data/08_reporting/sentinel2_download_visualizations"))
    output_dir.mkdir(parents=True, exist_ok=True)
    local = params.get("local_download", {})
    input_dir = Path(local_download_metadata.get("output_dir") or local.get("output_dir", "data/04_feature/sentinel2_bands"))

    outputs = {}
    rgb_defaults = {
        "true_color": {"bands": ["B4", "B3", "B2"], "output_name": "sentinel2_true_color.png", "title": "Sentinel-2 color verdadero"},
        "true_color_background": {"bands": ["B4", "B3", "B2"], "output_name": "sentinel2_true_color_background.png", "title": None},
        "false_color": {"bands": ["B8", "B4", "B3"], "output_name": "sentinel2_false_color.png", "title": "Sentinel-2 falso color"},
    }
    for name, default in rgb_defaults.items():
        spec = default | visualization.get(name, {})
        if spec.get("enabled", True):
            outputs[name] = _save_rgb(input_dir, output_dir, params, visualization, spec)

    grid = visualization.get("band_grid", {})
    if grid.get("enabled", True):
        outputs["band_grid"] = _save_band_grid(input_dir, output_dir, params, visualization, grid)

    return {"enabled": True, "output_dir": output_dir.as_posix(), "outputs": outputs}


def _save_rgb(input_dir: Path, output_dir: Path, params: dict, visualization: dict, spec: dict) -> dict:
    # Funcion para guardar una composicion RGB Sentinel-2.
    output_path = output_dir / spec["output_name"]
    rgb = np.dstack([_read_stretched_band(input_dir, params, band, visualization) for band in spec["bands"]])
    _save_image(rgb, output_path, spec.get("title"), visualization, background=spec.get("title") is None)
    return {"output_path": output_path.as_posix(), "bands": spec["bands"]}


def _save_band_grid(input_dir: Path, output_dir: Path, params: dict, visualization: dict, grid: dict) -> dict:
    # Funcion para guardar una grilla con todas las bandas descargadas.
    bands = params.get("bands", [])
    columns = int(grid.get("columns", 4))
    rows = int(np.ceil(len(bands) / columns))
    output_path = output_dir / grid.get("output_name", "sentinel2_bands_grid.png")
    figure, axes = plt.subplots(rows, columns, figsize=tuple(grid.get("figure_size", [14, 10])))
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for axis, band in zip(axes, bands):
        axis.imshow(_read_stretched_band(input_dir, params, band, visualization), cmap="gray")
        axis.set_title(band)
        axis.set_axis_off()
    for axis in axes[len(bands):]:
        axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=visualization.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "bands": bands}


def _read_stretched_band(input_dir: Path, params: dict, band: str, visualization: dict) -> Any:
    # Funcion para leer una banda y normalizarla para visualizacion.
    path = input_dir / _band_filename(params, band)
    if not path.exists():
        raise FileNotFoundError(f"No se encontro la banda requerida para visualizar: {path.as_posix()}")
    with rasterio.open(path) as source:
        array = source.read(1, masked=True).astype("float32").filled(np.nan)
    lower, upper = np.nanpercentile(array, visualization.get("percentile_range", [2, 98]))
    if not np.isfinite(lower) or not np.isfinite(upper) or lower == upper:
        return np.zeros(array.shape, dtype="float32")
    return np.clip((array - lower) / (upper - lower), 0, 1)


def _save_image(image: Any, output_path: Path, title: str | None, visualization: dict, background: bool = False) -> None:
    # Funcion para guardar una imagen PNG con o sin titulo/ejes.
    figure, axis = plt.subplots(figsize=tuple(visualization.get("figure_size", [8, 8])))
    axis.imshow(image)
    axis.set_axis_off()
    if title:
        axis.set_title(title)
    figure.tight_layout(pad=0 if background else 0.4)
    figure.savefig(output_path, dpi=visualization.get("dpi", 160), bbox_inches="tight", pad_inches=0 if background else 0.1)
    plt.close(figure)


def _band_filename(params: dict, band: str) -> str:
    # Funcion para construir el nombre local de una banda descargada.
    drive = params.get("drive_export", {})
    local = params.get("local_download", {})
    filename = local.get("file_name_template", "{file_name_prefix}_{band}_Masked.tif").format(
        band=band,
        file_name_prefix=drive.get("file_name_prefix", "Sentinel2"),
    )
    return filename if filename.lower().endswith(".tif") else f"{filename}.tif"
