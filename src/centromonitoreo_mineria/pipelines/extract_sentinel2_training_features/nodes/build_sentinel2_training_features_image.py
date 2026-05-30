from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import initialize_earth_engine_client
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_collection import build_filtered_sentinel2_collection
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_composite import build_composite_image
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import build_sentinel2_indices_image


def build_sentinel2_training_features_image(config: dict) -> Any:
    """Construye la imagen Sentinel-2 con bandas e indices para muestrear puntos."""
    gee_context = initialize_earth_engine_client(config["gee"])
    sentinel2_params = config["sentinel2_spectral_indices"]
    roi_geometry = build_roi_geometry(
        gee_context=gee_context,
        params_roi=sentinel2_params.get("roi", {}),
    )
    collection = build_filtered_sentinel2_collection(
        gee_context=gee_context,
        sentinel2_roi_geometry=roi_geometry,
        params=sentinel2_params,
    )
    composite = build_composite_image(
        sentinel2_image_collection=collection,
        params=sentinel2_params,
    )
    return build_sentinel2_indices_image(
        sentinel2_composite_image=composite,
        params=sentinel2_params,
    )
