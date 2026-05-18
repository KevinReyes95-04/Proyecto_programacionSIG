from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry

def load_roi_geometry(gee_context: dict, sentinel2_spectral_indices_config: dict) -> Any:
    """Carga el ROI como geometria de Earth Engine."""
    return build_roi_geometry(
        gee_context=gee_context,
        params_roi=sentinel2_spectral_indices_config["sentinel2_spectral_indices"].get("roi", {}),
    )
