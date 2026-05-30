from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import initialize_earth_engine_client
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_collection import build_filtered_sentinel2_collection
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_composite import build_composite_image
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import build_sentinel2_indices_image


def build_sentinel2_spectral_indices_assets(config: dict) -> dict[str, Any]:
    """Construye ROI, coleccion, composite e imagen de indices Sentinel-2."""
    # Funcion para preparar en Earth Engine la imagen final con indices espectrales.
    params = config["sentinel2_spectral_indices"]
    gee_context = initialize_earth_engine_client(config["gee"])
    roi_geometry = build_roi_geometry(gee_context=gee_context, params_roi=params.get("roi", {}))
    image_collection = build_filtered_sentinel2_collection(
        gee_context=gee_context,
        sentinel2_roi_geometry=roi_geometry,
        params=params,
    )
    composite_image = build_composite_image(
        sentinel2_image_collection=image_collection,
        params=params,
    )
    indices_image = build_sentinel2_indices_image(
        sentinel2_composite_image=composite_image,
        params=params,
    )
    return {
        "roi_geometry": roi_geometry,
        "image_collection": image_collection,
        "composite_image": composite_image,
        "indices_image": indices_image,
    }
