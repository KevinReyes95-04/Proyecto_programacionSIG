from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.drive_export import (
    export_image_to_drive,
)


def export_sentinel2_to_drive(
    sentinel2_composite_image: Any,
    sentinel2_roi_geometry: Any,
    google_earth_engine_config: dict,
) -> dict:
    """Inicia una exportacion Sentinel-2 a Google Drive."""
    return export_image_to_drive(
        image=sentinel2_composite_image,
        region=sentinel2_roi_geometry,
        params=google_earth_engine_config["sentinel2_download"],
    )
