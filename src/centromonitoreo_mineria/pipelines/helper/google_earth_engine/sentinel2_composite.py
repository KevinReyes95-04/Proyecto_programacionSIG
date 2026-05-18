from typing import Any


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
    if params.get("apply_reflectance_scale", True):
        return image.multiply(params.get("reflectance_scale_factor", 0.0001)).toFloat()
    return image
