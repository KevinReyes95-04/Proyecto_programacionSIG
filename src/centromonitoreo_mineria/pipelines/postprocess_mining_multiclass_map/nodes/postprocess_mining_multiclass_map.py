from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import convolve


# Funcion para suavizar el mapa multiclase y guardar el raster postprocesado.
def postprocess_mining_multiclass_map(
    mining_multiclass_map_postprocessing_config: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    params = mining_multiclass_map_postprocessing_config
    source_path = Path(params["classification_map"])
    output_path = Path(params["outputs"]["postprocessed_classification_map"])
    if not source_path.exists():
        raise FileNotFoundError(f"No existe el mapa multiclase: {source_path.as_posix()}")

    with rasterio.open(source_path) as source:
        class_map = source.read(1)
        profile = source.profile.copy()
        postprocessed = _majority_filter(class_map, params)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        profile.update(dtype="uint8", nodata=int(params.get("class_nodata", 255)), compress="lzw", BIGTIFF="IF_SAFER")
        with rasterio.open(output_path, "w", **profile) as destination:
            destination.write(postprocessed.astype("uint8"), 1)
        bounds = source.bounds
        crs = source.crs.to_string() if source.crs else None
        pixel_area_ha = abs(source.transform.a * source.transform.e) / 10000

    summary = _class_summary(class_map, postprocessed, pixel_area_ha, params)
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification_map": source_path.as_posix(),
        "postprocessed_classification_map": output_path.as_posix(),
        "class_summary_csv": params["outputs"]["class_summary_csv"],
        "majority_filter": params.get("majority_filter", {}),
        "changed_pixels": int(np.sum(class_map != postprocessed)),
        "class_nodata": int(params.get("class_nodata", 255)),
        "raster": {
            "shape": [int(class_map.shape[0]), int(class_map.shape[1])],
            "crs": crs,
            "bounds": {"left": bounds.left, "bottom": bounds.bottom, "right": bounds.right, "top": bounds.top},
            "pixel_area_ha": float(pixel_area_ha),
        },
    }
    return metadata, summary


# Funcion para aplicar un filtro de mayoria preservando NoData.
def _majority_filter(class_map: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    filter_params = params.get("majority_filter", {})
    if not filter_params.get("enabled", True):
        return class_map.copy()

    result = class_map.copy()
    class_values = [int(value) for value in params["class_values"].values()]
    nodata = int(params.get("class_nodata", 255))
    kernel = np.ones((int(filter_params.get("size", 3)), int(filter_params.get("size", 3))), dtype="uint8")
    for _ in range(int(filter_params.get("iterations", 1))):
        counts = np.stack([convolve((result == value).astype("uint8"), kernel, mode="constant", cval=0) for value in class_values])
        winners = np.array(class_values, dtype="uint8")[counts.argmax(axis=0)]
        max_counts = counts.max(axis=0)
        smoothed = np.where(max_counts > 0, winners, nodata).astype("uint8")
        for index, value in enumerate(class_values):
            smoothed[(result == value) & (counts[index] == max_counts)] = value
        smoothed[result == nodata] = nodata
        result = smoothed
    return result


# Funcion para resumir pixeles y area por clase antes y despues del filtro.
def _class_summary(
    original: np.ndarray,
    postprocessed: np.ndarray,
    pixel_area_ha: float,
    params: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    for label, value in params["class_values"].items():
        original_pixels = int(np.sum(original == int(value)))
        postprocessed_pixels = int(np.sum(postprocessed == int(value)))
        rows.append(
            {
                "class_label": label,
                "class_value": int(value),
                "original_pixels": original_pixels,
                "postprocessed_pixels": postprocessed_pixels,
                "pixel_delta": postprocessed_pixels - original_pixels,
                "postprocessed_area_ha": float(postprocessed_pixels * pixel_area_ha),
            }
        )
    return pd.DataFrame(rows)

