import json
from pathlib import Path
from typing import Any
from centromonitoreo_mineria.utils.earth_engine import load_ee


def build_roi_geometry(gee_context: dict, params_roi: dict) -> Any:
    if not gee_context.get("initialized"):
        raise RuntimeError("Earth Engine no fue inicializado correctamente.")

    ee = load_ee()
    roi_source = params_roi.get("source")
    if roi_source == "bbox" or (not roi_source and params_roi.get("bbox")):
        bbox = params_roi["bbox"]
        values = (
            [bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"]]
            if isinstance(bbox, dict)
            else bbox
        )
        return ee.Geometry.BBox(*values)

    if roi_source == "inline_geojson" or (
        not roi_source and params_roi.get("inline_geojson")
    ):
        geojson = params_roi["inline_geojson"]
    else:
        roi_geojson_path = params_roi.get("geojson_path")
        if not roi_geojson_path:
            raise ValueError(
                "Configura sentinel2_download.roi.geojson_path, "
                "sentinel2_download.roi.bbox o sentinel2_download.roi.inline_geojson."
            )
        with Path(roi_geojson_path).open("r", encoding="utf-8") as file:
            geojson = json.load(file)

    geojson_type = geojson.get("type")
    if geojson_type == "FeatureCollection":
        return ee.FeatureCollection(geojson).geometry()
    if geojson_type == "Feature":
        return ee.Feature(geojson).geometry()
    return ee.Geometry(geojson)
