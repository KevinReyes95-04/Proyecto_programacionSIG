from pathlib import Path
from typing import Any

import requests


def download_sentinel2_bands_to_local(
    assets: dict[str, Any],
    sentinel2_download_metadata: dict,
    config: dict,
) -> dict:
    """Descarga cada banda Sentinel-2 como GeoTIFF local."""
    params = config["sentinel2_download"]
    local = params.get("local_download", {})
    if not local.get("enabled", True):
        return {"enabled": False, "downloaded_files": []}

    output_dir = Path(local.get("output_dir", "data/04_feature/sentinel2_bands"))
    output_dir.mkdir(parents=True, exist_ok=True)

    image = assets["composite_image"].clip(assets["roi_geometry"])
    downloaded_files = []
    for band in params["bands"]:
        output_path = output_dir / _band_filename(params, local, band)
        url = image.select(band).getDownloadURL(
            {
                "name": output_path.stem,
                "region": assets["roi_geometry"],
                "scale": params.get("scale", 20),
                "format": "GEO_TIFF",
                **({"crs": params["crs"]} if params.get("crs") else {}),
            }
        )
        response = requests.get(url, timeout=local.get("timeout_seconds", 300))
        response.raise_for_status()
        output_path.write_bytes(response.content)
        downloaded_files.append(
            {
                "band": band,
                "output_path": output_path.as_posix(),
                "file_size_bytes": output_path.stat().st_size,
            }
        )

    return {
        "enabled": True,
        "output_dir": output_dir.as_posix(),
        "source_downloaded_at_utc": sentinel2_download_metadata.get(
            "downloaded_at_utc"
        ),
        "downloaded_files": downloaded_files,
    }


def _band_filename(params: dict, local: dict, band: str) -> str:
    drive = params.get("drive_export", {})
    prefix = drive.get("file_name_prefix", "Sentinel2")
    template = local.get("file_name_template", "{file_name_prefix}_{band}_Masked.tif")
    filename = template.format(
        band=band,
        file_name_prefix=prefix,
        description=drive.get("description", prefix),
    )
    return filename if filename.lower().endswith(".tif") else f"{filename}.tif"
