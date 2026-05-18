from datetime import datetime, timezone
from typing import Any
from centromonitoreo_mineria.utils.earth_engine import load_ee

def build_download_metadata(
    sentinel2_image_collection: Any,
    sentinel2_drive_export_metadata: dict,
    params: dict,
) -> dict:
    return {
        "collection": params.get("collection", "COPERNICUS/S2_SR_HARMONIZED"),
        "roi": params.get("roi", {}),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "scene_count": sentinel2_image_collection.size().getInfo(),
        "start_date": params["start_date"],
        "end_date": params["end_date"],
        "cloud_cover_max": params.get("cloud_cover_max"),
        "cloud_cover_property": params.get("cloud_cover_property", "CLOUDY_PIXEL_PERCENTAGE"),
        "composite_method": params.get("composite_method", "median"),
        "sort_by": params.get("sort_by"),
        "sort_ascending": params.get("sort_ascending", True),
        "drive_export": sentinel2_drive_export_metadata,
        "reflectance_scaled": params.get("apply_reflectance_scale", True),
        "reflectance_scale_factor": params.get("reflectance_scale_factor", 0.0001),
        "scene_metadata": _scene_metadata(
            sentinel2_image_collection,
            params.get("scene_metadata_properties", []),
            params.get("scene_metadata_limit", 50),
        ),
    }


def _scene_metadata(collection: Any, properties: list[str], limit: int | None) -> list[dict]:
    if not properties:
        return []
    ee = load_ee()
    images = collection.toList(limit if limit else collection.size())
    return images.map(lambda image: ee.Image(image).toDictionary(properties)).getInfo()
