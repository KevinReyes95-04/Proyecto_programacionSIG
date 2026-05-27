from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


def build_composite_image(sentinel2_image_collection: Any, params: dict) -> Any:
    method = params.get("composite_method", "median")
    composite_methods = {
        "median": sentinel2_image_collection.median,
        "mean": sentinel2_image_collection.mean,
        "mosaic": sentinel2_image_collection.mosaic,
    }
    if method not in composite_methods:
        raise ValueError(
            "sentinel2_download.composite_method debe ser median, mean o mosaic."
        )

    image = composite_methods[method]()
    image = _set_reference_projection(image, sentinel2_image_collection, params)
    if params.get("apply_reflectance_scale", True):
        return image.multiply(params.get("reflectance_scale_factor", 0.0001)).toFloat()
    return image


def _set_reference_projection(image: Any, collection: Any, params: dict) -> Any:
    drive_params = params.get("drive_export", {})
    if not drive_params.get("align_to_reference_band", False):
        return image

    reference_band = drive_params.get("reference_band") or params["bands"][0]
    ee = load_ee()
    projection = ee.Image(collection.first()).select(reference_band).projection()
    return image.setDefaultProjection(projection)
