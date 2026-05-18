from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import build_sentinel2_indices_image

def calculate_sentinel2_spectral_indices(
    sentinel2_composite_image: Any, sentinel2_spectral_indices_config: dict
) -> Any:
    """Calcula indices espectrales Sentinel-2 configurados por parametros."""
    return build_sentinel2_indices_image(
        sentinel2_composite_image=sentinel2_composite_image,
        params=sentinel2_spectral_indices_config["sentinel2_spectral_indices"],
    )
