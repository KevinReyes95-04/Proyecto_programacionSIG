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

import rasterio
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from rasterio.crs import CRS
from rasterio.warp import Resampling, calculate_default_transform, reproject

from centromonitoreo_mineria.utils.earth_engine import load_ee


def download_sentinel2_drive_export_to_local(
    drive_export_metadata: dict,
    config: dict,
) -> dict:
    """Descarga desde Drive el GeoTIFF exportado y lo separa por bandas."""
    # Funcion para descargar, reproyectar y separar las bandas Sentinel-2.
    params = config["sentinel2_download"]
    local = params.get("local_download", {})
    if not local.get("enabled", True):
        return {"enabled": False, "downloaded_files": []}
    if drive_export_metadata.get("state") != "COMPLETED":
        raise RuntimeError("La exportacion a Drive debe estar COMPLETED antes de descargarla.")

    output_dir = Path(local.get("output_dir", "data/04_feature/sentinel2_bands"))
    output_dir.mkdir(parents=True, exist_ok=True)
    source_path = output_dir / f"{drive_export_metadata['file_name_prefix']}.tif"

    _download_from_drive(drive_export_metadata, source_path)
    _reproject_file(source_path, local)
    downloaded_files = _split_bands(source_path, output_dir, params, local)

    return {
        "enabled": True,
        "source_path": source_path.as_posix(),
        "output_dir": output_dir.as_posix(),
        "downloaded_files": downloaded_files,
    }


def _download_from_drive(metadata: dict, output_path: Path) -> None:
    # Funcion para buscar y descargar el GeoTIFF exportado en Google Drive.
    drive = build(
        "drive",
        "v3",
        credentials=load_ee().data.get_persistent_credentials(),
        cache_discovery=False,
    )
    folder_filter = ""
    if folder_name := metadata.get("drive_folder"):
        folders = (
            drive.files()
            .list(
                q=(
                    "mimeType = 'application/vnd.google-apps.folder' "
                    f"and name = '{folder_name}' and trashed = false"
                ),
                fields="files(id, name)",
            )
            .execute()
            .get("files", [])
        )
        if not folders:
            raise FileNotFoundError(f"No se encontro la carpeta {folder_name} en Google Drive.")
        folder_filter = f" and '{folders[0]['id']}' in parents"

    files = (
        drive.files()
        .list(
            q=f"name = '{output_path.name}' and trashed = false{folder_filter}",
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
        .get("files", [])
    )
    if not files:
        raise FileNotFoundError(f"No se encontro {output_path.name} en Google Drive.")

    with output_path.open("wb") as file:
        downloader = MediaIoBaseDownload(file, drive.files().get_media(fileId=files[0]["id"]))
        done = False
        while not done:
            _, done = downloader.next_chunk()


def _reproject_file(path: Path, local: dict) -> None:
    # Funcion para reproyectar el GeoTIFF completo al CRS configurado.
    target_crs = local.get("target_crs")
    if not target_crs:
        return

    target_crs = CRS.from_user_input(target_crs)
    with rasterio.open(path) as source:
        if source.crs == target_crs:
            return
        profile = _reprojected_profile(source, target_crs, source.count)
        temp_path = path.with_name(f"{path.stem}_reprojected{path.suffix}")
        with rasterio.open(temp_path, "w", **profile) as target:
            for index in range(1, source.count + 1):
                reproject(
                    source=rasterio.band(source, index),
                    destination=rasterio.band(target, index),
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=target.transform,
                    dst_crs=target.crs,
                    resampling=_resampling(local.get("resampling", "bilinear")),
                )

    temp_path.replace(path)


def _split_bands(
    source_path: Path,
    output_dir: Path,
    params: dict,
    local: dict,
) -> list[dict]:
    # Funcion para separar el GeoTIFF multibanda en archivos por banda.
    downloaded_files = []
    with rasterio.open(source_path) as source:
        if source.count < len(params["bands"]):
            raise ValueError("El GeoTIFF descargado tiene menos bandas que las configuradas.")

        profile = source.profile | {"count": 1}
        for index, band in enumerate(params["bands"], start=1):
            output_path = output_dir / _band_filename(params, local, band)
            with rasterio.open(output_path, "w", **profile) as target:
                target.write(source.read(index), 1)
            downloaded_files.append(
                {
                    "band": band,
                    "output_path": output_path.as_posix(),
                    "crs": str(profile.get("crs")),
                    "file_size_bytes": output_path.stat().st_size,
                }
            )
    return downloaded_files


def _reprojected_profile(source: Any, target_crs: CRS, count: int) -> dict:
    # Funcion para calcular el perfil raster de salida reproyectado.
    transform, width, height = calculate_default_transform(
        source.crs,
        target_crs,
        source.width,
        source.height,
        *source.bounds,
    )
    return source.profile | {
        "count": count,
        "crs": target_crs,
        "transform": transform,
        "width": width,
        "height": height,
    }


def _resampling(name: str) -> Resampling:
    # Funcion para convertir el nombre del remuestreo a rasterio.
    if name not in {"nearest", "bilinear", "cubic"}:
        raise ValueError("sentinel2_download.local_download.resampling debe ser nearest, bilinear o cubic.")
    return Resampling[name]


def _band_filename(params: dict, local: dict, band: str) -> str:
    # Funcion para construir el nombre del archivo de cada banda.
    drive = params.get("drive_export", {})
    prefix = drive.get("file_name_prefix", "Sentinel2")
    template = local.get("file_name_template", "{file_name_prefix}_{band}_Masked.tif")
    filename = template.format(
        band=band,
        file_name_prefix=prefix,
        description=drive.get("description", prefix),
    )
    return filename if filename.lower().endswith(".tif") else f"{filename}.tif"
