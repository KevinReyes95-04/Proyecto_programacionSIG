from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.drive_export import export_image_to_drive


def export_sentinel2_download_to_drive(assets: dict[str, Any], config: dict) -> dict:
    """Exporta la imagen compuesta Sentinel-2 a Google Drive."""
    # Funcion para exportar la imagen compuesta a Google Drive.
    return export_image_to_drive(
        image=assets["composite_image"],
        region=assets["roi_geometry"],
        params=config["sentinel2_download"],
    )
