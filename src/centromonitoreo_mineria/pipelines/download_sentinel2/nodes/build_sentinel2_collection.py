from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_collection import build_filtered_sentinel2_collection

def build_sentinel2_collection(
    gee_context: dict, sentinel2_roi_geometry: Any, google_earth_engine_config: dict
) -> Any:
    """Construye la coleccion Sentinel-2 filtrada."""
    return build_filtered_sentinel2_collection(
        gee_context=gee_context,
        sentinel2_roi_geometry=sentinel2_roi_geometry,
        params=google_earth_engine_config["sentinel2_download"],
    )
