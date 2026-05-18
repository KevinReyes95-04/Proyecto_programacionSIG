from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


def _qa60_cloud_mask(image: Any) -> Any:
    qa60 = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa60.bitwiseAnd(cloud_bit_mask).eq(0).And(
        qa60.bitwiseAnd(cirrus_bit_mask).eq(0)
    )
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
    if params.get("cloud_mask", False):
        collection = collection.map(_qa60_cloud_mask)
    if params.get("cloud_cover_max") is not None:
        collection = collection.filter(
            ee.Filter.lte(
                params.get("cloud_cover_property", "CLOUDY_PIXEL_PERCENTAGE"),
                params["cloud_cover_max"],
            )
        )
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
