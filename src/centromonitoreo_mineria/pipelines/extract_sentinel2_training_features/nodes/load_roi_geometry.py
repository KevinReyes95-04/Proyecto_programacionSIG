from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import (
    build_roi_geometry,
)


def load_roi_geometry(gee_context: dict, sentinel2_training_features_config: dict) -> Any:
    """Carga el ROI configurado para extraer variables Sentinel-2."""
    return build_roi_geometry(
        gee_context=gee_context,
        params_roi=sentinel2_training_features_config["sentinel2_spectral_indices"].get("roi", {}),
    )
