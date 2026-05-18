from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.drive_export import export_image_to_drive
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import export_params_with_output_bands

def export_sentinel2_spectral_indices_to_drive(
    sentinel2_spectral_indices_image: Any,
    sentinel2_roi_geometry: Any,
    sentinel2_spectral_indices_config: dict,
) -> dict:
    """Exporta la imagen con indices Sentinel-2 a Google Drive."""
    params = sentinel2_spectral_indices_config["sentinel2_spectral_indices"]
    return export_image_to_drive(
        image=sentinel2_spectral_indices_image,
        region=sentinel2_roi_geometry,
        params=export_params_with_output_bands(params),
    )
