from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import initialize_earth_engine_client
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.roi_geometry import build_roi_geometry
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_collection import build_filtered_sentinel2_collection
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_composite import build_composite_image


def build_sentinel2_download_assets(config: dict) -> dict[str, Any]:
    """Construye ROI, coleccion e imagen compuesta Sentinel-2."""
    # Funcion para preparar los objetos de Earth Engine que se van a exportar.
    params = config["sentinel2_download"]
    gee_context = initialize_earth_engine_client(config["gee"])
    roi_geometry = build_roi_geometry(
        gee_context=gee_context,
        params_roi=params.get("roi", {}),
    )
    image_collection = build_filtered_sentinel2_collection(
        gee_context=gee_context,
        sentinel2_roi_geometry=roi_geometry,
        params=params,
    )
    composite_image = build_composite_image(
        sentinel2_image_collection=image_collection,
        params=params,
    )
    return {
        "roi_geometry": roi_geometry,
        "image_collection": image_collection,
        "composite_image": composite_image,
    }
