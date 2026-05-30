from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import rasterio
import numpy as np


def write_postprocessing_outputs(
    polygons: gpd.GeoDataFrame,
    postprocessed: np.ndarray,
    profile: dict[str, Any],
    bounds: Any,
    crs: Any,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Escribe raster, vector y tabla resumen del postprocesamiento."""
    outputs = params["outputs"]
    raster_path = Path(outputs["postprocessed_classification_map"])
    polygon_path = Path(outputs["polygons"])
    csv_path = Path(outputs["polygon_summary_csv"])
    for path in [raster_path, polygon_path, csv_path]:
        path.parent.mkdir(parents=True, exist_ok=True)

    _write_postprocessed_raster(raster_path, postprocessed, profile, params)
    vector_write_status = _write_polygons(polygons, polygon_path, outputs)
    polygon_summary(polygons).to_csv(csv_path, index=False)

    return {
        "postprocessed_classification_map": raster_path.as_posix(),
        "polygons": polygon_path.as_posix(),
        "polygon_summary_csv": csv_path.as_posix(),
        "vector_write_status": vector_write_status,
        "raster": {
            "shape": [int(postprocessed.shape[0]), int(postprocessed.shape[1])],
            "crs": crs.to_string() if crs else None,
            "bounds": {
                "left": bounds.left,
                "bottom": bounds.bottom,
                "right": bounds.right,
                "top": bounds.top,
            },
        },
    }


def polygon_summary(polygons: gpd.GeoDataFrame) -> pd.DataFrame:
    """Construye el resumen tabular de poligonos mineros."""
    if polygons.empty:
        return pd.DataFrame(
            columns=[
                "polygon_id",
                "class_label",
                "area_m2",
                "area_ha",
                "perimeter_m",
                "centroid_x",
                "centroid_y",
            ]
        )
    summary = polygons.drop(columns="geometry").copy()
    centroids = polygons.geometry.centroid
    summary["centroid_x"] = centroids.x
    summary["centroid_y"] = centroids.y
    return summary.sort_values("area_ha", ascending=False).reset_index(drop=True)


def _write_postprocessed_raster(
    raster_path: Path,
    postprocessed: np.ndarray,
    profile: dict[str, Any],
    params: dict[str, Any],
) -> None:
    raster_profile = profile.copy()
    raster_profile.update(
        dtype="uint8",
        count=1,
        nodata=int(params["class_nodata"]),
        compress="lzw",
        BIGTIFF="IF_SAFER",
    )
    raster_profile.pop("blockxsize", None)
    raster_profile.pop("blockysize", None)
    with rasterio.open(raster_path, "w", **raster_profile) as target:
        target.write(postprocessed, 1)


def _write_polygons(polygons: gpd.GeoDataFrame, polygon_path: Path, outputs: dict[str, Any]) -> str:
    layer = outputs.get("polygon_layer", "mining_binary_polygons")
    driver = _vector_driver(polygon_path)
    try:
        if driver == "GPKG":
            _remove_existing_vector(polygon_path)
            polygons.to_file(polygon_path, layer=layer, driver=driver)
        else:
            polygons.to_file(polygon_path, driver=driver)
        return "written"
    except PermissionError:
        if polygon_path.exists() and polygon_path.stat().st_size > 0:
            return "reused_existing_locked_file"
        raise


def _vector_driver(path: Path) -> str:
    return "GeoJSON" if path.suffix.lower() in {".geojson", ".json"} else "GPKG"


def _remove_existing_vector(path: Path) -> None:
    for candidate in [path, Path(f"{path}-wal"), Path(f"{path}-shm")]:
        if candidate.exists():
            candidate.unlink()
