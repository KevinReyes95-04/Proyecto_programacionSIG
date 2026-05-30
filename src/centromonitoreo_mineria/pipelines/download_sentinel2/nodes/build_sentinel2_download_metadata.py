from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.download_metadata import (
    build_download_metadata,
)


def build_sentinel2_download_metadata(assets: dict[str, Any], sentinel2_drive_export_metadata: dict, config: dict) -> dict:
    """Construye metadatos reproducibles de la descarga Sentinel-2."""
    return build_download_metadata(
        sentinel2_image_collection=assets["image_collection"],
        sentinel2_drive_export_metadata=sentinel2_drive_export_metadata,
        params=config["sentinel2_download"],
    )
