from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_composite import build_composite_image

def build_sentinel2_composite(
    sentinel2_image_collection: Any, sentinel2_spectral_indices_config: dict
) -> Any:
    """Construye la imagen Sentinel-2 compuesta para indices."""
    return build_composite_image(
        sentinel2_image_collection=sentinel2_image_collection,
        params=sentinel2_spectral_indices_config["sentinel2_spectral_indices"],
    )
