from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import (
    build_sentinel2_indices_image,
)


def calculate_sentinel2_spectral_indices(
    sentinel2_composite_image: Any,
    sentinel2_training_features_config: dict,
) -> Any:
    """Calcula las bandas e indices Sentinel-2 para muestreo."""
    return build_sentinel2_indices_image(
        sentinel2_composite_image=sentinel2_composite_image,
        params=sentinel2_training_features_config["sentinel2_spectral_indices"],
    )
