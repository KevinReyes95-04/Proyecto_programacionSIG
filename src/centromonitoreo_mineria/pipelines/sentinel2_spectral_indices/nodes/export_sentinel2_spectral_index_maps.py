from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_index_maps import build_sentinel2_spectral_index_maps


def export_sentinel2_spectral_index_maps(
    assets: dict[str, Any],
    sentinel2_spectral_indices_config: dict,
) -> dict:
    """Genera mapas PNG de los indices espectrales Sentinel-2."""
    # Funcion para exportar los indices espectrales como mapas PNG.
    return build_sentinel2_spectral_index_maps(
        image=assets["indices_image"],
        region=assets["roi_geometry"],
        params=sentinel2_spectral_indices_config["sentinel2_spectral_indices"],
    )
