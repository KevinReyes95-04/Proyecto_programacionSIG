from typing import Any

import geopandas as gpd
import numpy as np
from rasterio import features
from shapely.geometry import shape


def extract_mining_polygons(
    class_map: np.ndarray,
    transform: Any,
    crs: Any,
    params: dict[str, Any],
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Vectoriza los parches conectados de la clase mineria."""
    mask = class_map == int(params["class_value"])
    records = []
    geometries = []
    shapes = features.shapes(
        mask.astype("uint8"),
        mask=mask,
        transform=transform,
        connectivity=int(params["connectivity"]),
    )
    for patch_id, (geometry, value) in enumerate(shapes, start=1):
        if int(value) != 1:
            continue
        geom = shape(geometry)
        geometries.append(geom)
        records.append(
            {
                "polygon_id": patch_id,
                "class_label": params["class_label"],
                "area_m2": float(geom.area),
                "area_ha": float(geom.area / 10000),
                "perimeter_m": float(geom.length),
            }
        )
    polygons = gpd.GeoDataFrame(records, geometry=geometries, crs=crs)
    return polygons, polygons.copy()


def rasterize_polygons(
    polygons: gpd.GeoDataFrame,
    class_map: np.ndarray,
    transform: Any,
    params: dict[str, Any],
) -> np.ndarray:
    """Rasteriza los poligonos conservados sobre la grilla original."""
    nodata = int(params["class_nodata"])
    output = np.where(class_map == nodata, nodata, int(params["negative_value"])).astype("uint8")
    if polygons.empty:
        return output

    shapes = [(geometry, int(params["class_value"])) for geometry in polygons.geometry]
    burned = features.rasterize(
        shapes,
        out_shape=class_map.shape,
        fill=0,
        transform=transform,
        dtype="uint8",
        all_touched=bool(params.get("all_touched", False)),
    )
    output[burned == int(params["class_value"])] = int(params["class_value"])
    return output


def pixel_area_ha(transform: Any) -> float:
    """Calcula el area de pixel en hectareas a partir del transform."""
    return float(abs(transform.a * transform.e) / 10000)
