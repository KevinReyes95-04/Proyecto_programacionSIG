from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import requests


def download_sentinel2_bands_to_local(
    assets: dict[str, Any],
    sentinel2_download_metadata: dict,
    config: dict,
) -> dict:
    """Descarga las bandas Sentinel-2 procesadas a una carpeta local."""
    params = config["sentinel2_download"]
    local_params = params.get("local_download", {})
    if not local_params.get("enabled", True):
        return {"enabled": False, "downloaded_files": []}

    output_dir = Path(local_params.get("output_dir", "data/04_feature/sentinel2_bands"))
    output_dir.mkdir(parents=True, exist_ok=True)

    image = assets["composite_image"].clip(assets["roi_geometry"])
    downloaded_files = [
        _download_band(
            image=image,
            region=assets["roi_geometry"],
            band=band,
            params=params,
            local_params=local_params,
            output_dir=output_dir,
        )
        for band in params["bands"]
    ]

    return {
        "enabled": True,
        "output_dir": output_dir.as_posix(),
        "source_downloaded_at_utc": sentinel2_download_metadata.get(
            "downloaded_at_utc"
        ),
        "downloaded_files": downloaded_files,
    }


def _download_band(
    image: Any,
    region: Any,
    band: str,
    params: dict,
    local_params: dict,
    output_dir: Path,
) -> dict:
    output_path = output_dir / _band_filename(
        params=params,
        local_params=local_params,
        band=band,
    )
    band_image = image.select(band)
    get_download_url = getattr(band_image, "getDownloadURL", None)
    if get_download_url is None:
        get_download_url = band_image.getDownloadUrl

    url = get_download_url(_download_url_params(params, local_params, region, output_path))
    response = requests.get(url, timeout=local_params.get("timeout_seconds", 300))
    response.raise_for_status()
    _write_download_response(response.content, output_path)

    return {
        "band": band,
        "output_path": output_path.as_posix(),
        "file_size_bytes": output_path.stat().st_size,
    }


def _download_url_params(
    params: dict,
    local_params: dict,
    region: Any,
    output_path: Path,
) -> dict:
    url_params = {
        "name": output_path.stem,
        "region": region,
        "scale": params.get("scale", 20),
        "format": local_params.get("format", "GEO_TIFF"),
    }
    if params.get("crs"):
        url_params["crs"] = params["crs"]
    return url_params


def _band_filename(params: dict, local_params: dict, band: str) -> str:
    drive_params = params.get("drive_export", {})
    file_name_prefix = drive_params.get("file_name_prefix", "Sentinel2")
    template = local_params.get(
        "file_name_template",
        drive_params.get("band_file_name_template", "{file_name_prefix}_{band}_Masked"),
    )
    filename = template.format(
        band=band,
        file_name_prefix=file_name_prefix,
        description=drive_params.get("description", file_name_prefix),
    )
    return filename if filename.lower().endswith(".tif") else f"{filename}.tif"


def _write_download_response(content: bytes, output_path: Path) -> None:
    if content.startswith(b"PK"):
        with ZipFile(BytesIO(content)) as archive:
            tif_names = [
                name
                for name in archive.namelist()
                if name.lower().endswith((".tif", ".tiff"))
            ]
            if not tif_names:
                raise ValueError("La descarga comprimida no contiene archivos GeoTIFF.")
            with archive.open(tif_names[0]) as source, output_path.open("wb") as target:
                target.write(source.read())
        return
    output_path.write_bytes(content)
