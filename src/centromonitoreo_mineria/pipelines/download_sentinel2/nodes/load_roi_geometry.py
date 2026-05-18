from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry

def load_roi_geometry(gee_context: dict, google_earth_engine_config: dict) -> Any:
    """Carga el ROI configurado como geometria de Earth Engine."""
    return build_roi_geometry(
        gee_context=gee_context,
        params_roi=google_earth_engine_config["sentinel2_download"].get("roi", {}),
    )
