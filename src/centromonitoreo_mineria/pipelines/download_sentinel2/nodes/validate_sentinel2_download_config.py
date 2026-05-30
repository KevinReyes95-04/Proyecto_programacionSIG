from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.validation import (
    validate_gee_params,
    validate_sentinel2_download_params,
)


def validate_sentinel2_download_config(params_gee: dict, params_sentinel2_download: dict) -> dict:
    """Valida y agrupa la configuracion para descargar Sentinel-2."""
    gee = deepcopy(params_gee)
    sentinel2_download = deepcopy(params_sentinel2_download)
    validate_gee_params(gee)
    validate_sentinel2_download_params(sentinel2_download)
    return {"gee": gee, "sentinel2_download": sentinel2_download}


validate_google_earth_engine_config = validate_sentinel2_download_config
