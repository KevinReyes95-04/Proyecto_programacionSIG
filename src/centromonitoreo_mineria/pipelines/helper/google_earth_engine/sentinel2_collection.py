from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


def _apply_cloud_mask(image: Any, params: dict) -> Any:
    method = params.get("cloud_mask_method", "qa60")
    if method == "qa60":
        return _qa60_cloud_mask(image)
    if method == "scl":
        return _scl_cloud_mask(image, params)
    if method == "qa60_and_scl":
        return _scl_cloud_mask(_qa60_cloud_mask(image), params)
    raise ValueError("cloud_mask_method debe ser qa60, scl o qa60_and_scl.")


def _qa60_cloud_mask(image: Any) -> Any:
    qa60 = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa60.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa60.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
    return image.updateMask(mask).copyProperties(image, image.propertyNames())


def _scl_cloud_mask(image: Any, params: dict) -> Any:
    scl = image.select("SCL")
    masked_classes = params.get("cloud_mask_scl_classes", [3, 8, 9, 10])
    mask = scl.neq(masked_classes[0])
    for scl_class in masked_classes[1:]:
        mask = mask.And(scl.neq(scl_class))
    return image.updateMask(mask).copyProperties(image, image.propertyNames())


def build_filtered_sentinel2_collection(
    gee_context: dict, sentinel2_roi_geometry: Any, params: dict
) -> Any:
    if not gee_context.get("initialized"):
        raise RuntimeError("Earth Engine no fue inicializado correctamente.")

    ee = load_ee()
    collection = (
        ee.ImageCollection(params.get("collection", "COPERNICUS/S2_SR_HARMONIZED"))
        .filterBounds(sentinel2_roi_geometry)
        .filterDate(params["start_date"], params["end_date"])
    )
    if params.get("cloud_cover_max") is not None:
        collection = collection.filter(
            ee.Filter.lte(
                params.get("cloud_cover_property", "CLOUDY_PIXEL_PERCENTAGE"),
                params["cloud_cover_max"],
            )
        )
    if params.get("cloud_mask", False):
        collection = collection.map(lambda image: _apply_cloud_mask(image, params))
    collection = collection.select(params["bands"])
    if params.get("sort_by"):
        collection = collection.sort(
            params["sort_by"],
            params.get("sort_ascending", True),
        )
    if collection.size().getInfo() == 0:
        raise ValueError(
            "No se encontraron escenas Sentinel-2 para el ROI, fechas y filtro "
            "de nubosidad configurados."
        )
    return collection
