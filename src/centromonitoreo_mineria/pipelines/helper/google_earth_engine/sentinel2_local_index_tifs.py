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

import numpy as np
import rasterio


def write_sentinel2_index_tifs(params: dict[str, Any]) -> dict:
    # Funcion para calcular y guardar todos los indices como GeoTIFF locales.
    local = params.get("local_tif_export", {})
    if not local.get("enabled", True):
        return {"enabled": False, "files": []}

    input_dir = Path(local.get("input_dir", "data/04_feature/sentinel2_bands"))
    output_dir = Path(local.get("output_dir", input_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    scale = params.get("reflectance_scale_factor", 0.0001) if params.get("apply_reflectance_scale", True) else 1

    files = []
    for index_name, index_config in params["indices"].items():
        if not index_config.get("enabled", True):
            continue
        bands, profile = _read_bands(input_dir, local, index_config["bands"], scale)
        output_path = output_dir / _index_filename(local, index_name)
        with rasterio.open(output_path, "w", **(profile | {"count": 1, "dtype": "float32", "nodata": np.nan})) as target:
            target.write(_calculate_index(index_config, bands).astype("float32"), 1)
        files.append(
            {
                "index": index_name,
                "output_path": output_path.as_posix(),
                "crs": str(profile.get("crs")),
                "file_size_bytes": output_path.stat().st_size,
            }
        )
    return {"enabled": True, "output_dir": output_dir.as_posix(), "files": files}


def _read_bands(input_dir: Path, local: dict, bands: dict[str, str], scale: float) -> tuple[dict[str, Any], dict]:
    # Funcion para leer las bandas necesarias desde la carpeta local.
    arrays = {}
    profile = None
    template = local.get("source_band_template", "Sentinel2_{band}_Masked.tif")
    for alias, band_name in bands.items():
        path = input_dir / template.format(band=band_name)
        if not path.exists():
            raise FileNotFoundError(f"No se encontro la banda requerida: {path.as_posix()}")
        with rasterio.open(path) as source:
            profile = profile or source.profile.copy()
            arrays[alias] = source.read(1, masked=True).astype("float32").filled(np.nan) * scale
    return arrays, profile or {}


def _calculate_index(config: dict[str, Any], bands: dict[str, Any]) -> Any:
    # Funcion para calcular un indice espectral con numpy.
    with np.errstate(divide="ignore", invalid="ignore"):
        if config["formula"] == "normalized_difference":
            first = bands["first"]
            second = bands["second"]
            denominator = first + second
            return np.where(denominator == 0, np.nan, (first - second) / denominator)
        return eval(
            config["expression"],
            {"__builtins__": {}},
            {"sqrt": np.sqrt, "pow": np.power, "np": np, **bands},
        )


def _index_filename(local: dict, index_name: str) -> str:
    # Funcion para construir el nombre del GeoTIFF del indice.
    template = local.get("index_file_template", "Sentinel2_{index}_Masked.tif")
    filename = template.format(index=index_name, index_name=index_name)
    return filename if filename.lower().endswith(".tif") else f"{filename}.tif"
