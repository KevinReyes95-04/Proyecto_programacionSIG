from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_index_maps import (
    build_sentinel2_spectral_index_maps,
)


def plot_sentinel2_spectral_indices(
    sentinel2_spectral_indices_image: Any,
    sentinel2_roi_geometry: Any,
    sentinel2_spectral_indices_config: dict,
) -> dict:
    """Genera mapas PNG de los indices espectrales Sentinel-2."""
    return build_sentinel2_spectral_index_maps(
        image=sentinel2_spectral_indices_image,
        region=sentinel2_roi_geometry,
        params=sentinel2_spectral_indices_config["sentinel2_spectral_indices"],
    )
