from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.utils.output_writers import (
    write_postprocessing_outputs,
)
from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.utils.polygon_processing import (
    extract_mining_polygons,
    pixel_area_ha,
    rasterize_polygons,
)


def postprocess_mining_binary_map(
    mining_binary_map_postprocessing_config: dict[str, Any],
) -> dict[str, Any]:
    """Filtra parches pequenos, escribe raster postprocesado y exporta poligonos."""
    params = mining_binary_map_postprocessing_config
    classification_path = Path(params["classification_map"])
    if not classification_path.exists():
        raise FileNotFoundError(f"No existe el mapa clasificado: {classification_path.as_posix()}")

    with rasterio.open(classification_path) as source:
        class_map = source.read(1)
        profile = source.profile.copy()
        polygons, all_patches = extract_mining_polygons(
            class_map,
            source.transform,
            source.crs,
            params,
        )
        filtered = polygons[polygons["area_ha"] >= float(params["min_area_ha"])].copy()
        postprocessed = rasterize_polygons(filtered, class_map, source.transform, params)
        metadata = write_postprocessing_outputs(
            filtered,
            postprocessed,
            profile,
            source.bounds,
            source.crs,
            params,
        )

    original_pixels = int(np.sum(class_map == int(params["class_value"])))
    kept_pixels = int(np.sum(postprocessed == int(params["class_value"])))
    area_per_pixel_ha = pixel_area_ha(profile["transform"])
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification_map": classification_path.as_posix(),
        "postprocessed_classification_map": metadata["postprocessed_classification_map"],
        "polygons": metadata["polygons"],
        "polygon_summary_csv": metadata["polygon_summary_csv"],
        "vector_write_status": metadata["vector_write_status"],
        "class_label": params["class_label"],
        "negative_label": params["negative_label"],
        "min_area_ha": float(params["min_area_ha"]),
        "connectivity": int(params["connectivity"]),
        "original_patches": int(len(all_patches)),
        "kept_patches": int(len(filtered)),
        "removed_patches": int(len(all_patches) - len(filtered)),
        "original_mining_pixels": original_pixels,
        "kept_mining_pixels": kept_pixels,
        "removed_mining_pixels": original_pixels - kept_pixels,
        "pixel_area_ha": area_per_pixel_ha,
        "kept_area_ha": float(kept_pixels * area_per_pixel_ha),
        "raster": metadata["raster"],
    }
