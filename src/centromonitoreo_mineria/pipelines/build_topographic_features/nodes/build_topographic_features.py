from datetime import datetime, timezone
from io import BytesIO
import os
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np
import rasterio
import requests
from rasterio.warp import Resampling, reproject

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import (
    initialize_earth_engine_client,
)
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.topographic_features import build_topographic_image


# Funcion para descargar DEM/pendiente y alinearlos a la grilla Sentinel-2.
def build_topographic_features(config: dict[str, Any]) -> dict[str, Any]:
    params = config["topographic_features"]
    raw_path = Path(params["download"]["output_dir"]) / params["download"]["source_file"]
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if params.get("download", {}).get("enabled", True):
        _download_topography(config, raw_path)
    if not raw_path.exists():
        raise FileNotFoundError(f"No existe el raster topografico fuente: {raw_path.as_posix()}")
    outputs = _align_topography(raw_path, params)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_raster": raw_path.as_posix(),
        "dem_asset": params["dem_asset"],
        "output_bands": params["output_bands"],
        "aligned_rasters": outputs,
    }


# Funcion para descargar el raster topografico desde Earth Engine.
def _download_topography(config: dict[str, Any], output_path: Path) -> None:
    gee_context = initialize_earth_engine_client(config["gee"])
    params = config["topographic_features"]
    roi = build_roi_geometry(
        gee_context=gee_context,
        params_roi=config["sentinel2_download"].get("roi", {}),
    )
    image = build_topographic_image(params).clip(roi)
    url = image.getDownloadURL(
        {
            "name": output_path.stem,
            "region": roi,
            "scale": params["download"].get("scale", 30),
            "crs": params["download"].get("crs", "EPSG:4326"),
            "format": params["download"].get("format", "GEO_TIFF"),
            "filePerBand": False,
        }
    )
    response = requests.get(url, timeout=params["download"].get("timeout_seconds", 300))
    response.raise_for_status()
    _write_download(response.content, output_path)


# Funcion para guardar GeoTIFF directo o extraerlo si viene comprimido.
def _write_download(content: bytes, output_path: Path) -> None:
    if content.startswith(b"PK"):
        with ZipFile(BytesIO(content)) as zip_file:
            tif_name = next(name for name in zip_file.namelist() if name.lower().endswith((".tif", ".tiff")))
            output_path.write_bytes(zip_file.read(tif_name))
        return
    output_path.write_bytes(content)


# Funcion para remuestrear DEM y pendiente a la misma grilla de Sentinel-2.
def _align_topography(source_path: Path, params: dict[str, Any]) -> list[dict[str, Any]]:
    alignment = params["alignment"]
    reference_path = Path(alignment["reference_raster"])
    if not reference_path.exists():
        raise FileNotFoundError(f"No existe el raster de referencia: {reference_path.as_posix()}")

    outputs = []
    output_names = list(params["output_bands"].values())
    with rasterio.Env(**_configure_proj()), rasterio.open(reference_path) as reference, rasterio.open(source_path) as source:
        if source.count < len(output_names):
            raise ValueError("El raster topografico no tiene suficientes bandas.")
        profile = reference.profile.copy()
        nodata = float(alignment.get("nodata_value", -9999.0))
        profile.update(driver="GTiff", count=1, dtype="float32", nodata=nodata, compress="lzw", BIGTIFF="IF_SAFER")
        for index, band in enumerate(output_names, start=1):
            output_path = Path(alignment["output_file_template"].format(band=band))
            if not output_path.is_absolute():
                output_path = Path(params["download"]["output_dir"]) / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            data = np.full((reference.height, reference.width), nodata, dtype="float32")
            reproject(
                source=rasterio.band(source, index),
                destination=data,
                src_transform=source.transform,
                src_crs=source.crs,
                src_nodata=source.nodata,
                dst_transform=reference.transform,
                dst_crs=reference.crs,
                dst_nodata=nodata,
                resampling=_resampling(alignment.get("resampling", "bilinear")),
            )
            with rasterio.open(output_path, "w", **profile) as target:
                target.write(data, 1)
            outputs.append({"band": band, "output_path": output_path.as_posix(), "nodata": nodata})
    return outputs


# Funcion para convertir nombre de remuestreo a rasterio.
def _resampling(name: str) -> Resampling:
    return Resampling[name]


# Funcion para evitar que rasterio use una instalacion externa de PROJ en Windows.
def _configure_proj() -> dict[str, str]:
    proj_dir = (Path(rasterio.__file__).parent / "proj_data").as_posix()
    os.environ["PROJ_DATA"] = proj_dir
    os.environ["PROJ_LIB"] = proj_dir
    return {"PROJ_DATA": proj_dir, "PROJ_LIB": proj_dir}
