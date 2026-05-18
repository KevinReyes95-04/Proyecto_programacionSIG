from datetime import datetime, timezone
from typing import Any
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import output_bands

def build_sentinel2_spectral_indices_metadata(
    sentinel2_image_collection: Any,
    sentinel2_spectral_indices_drive_export_metadata: dict,
    sentinel2_spectral_indices_maps_metadata: dict,
    sentinel2_spectral_indices_config: dict,
) -> dict:
    """Construye metadatos reproducibles del calculo de indices Sentinel-2."""
    params = sentinel2_spectral_indices_config["sentinel2_spectral_indices"]
    enabled_indices = {name: config for name, config in params["indices"].items() if config.get("enabled", True)}
    
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sensor": "Sentinel-2",
        "collection": params["collection"],
        "roi": params.get("roi", {}),
        "start_date": params["start_date"],
        "end_date": params["end_date"],
        "scene_count": sentinel2_image_collection.size().getInfo(),
        "source_bands": params["bands"],
        "output_bands": output_bands(params),
        "indices": enabled_indices,
        "maps": sentinel2_spectral_indices_maps_metadata,
        "drive_export": sentinel2_spectral_indices_drive_export_metadata,
        "reflectance_scaled": params.get("apply_reflectance_scale", True),
        "reflectance_scale_factor": params.get("reflectance_scale_factor", 0.0001),
    }
