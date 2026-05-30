from copy import deepcopy
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import validate_sentinel2_spectral_indices_params
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.validation import validate_gee_params


def validate_sentinel2_spectral_indices_config(
    params_gee: dict, params_sentinel2_spectral_indices: dict
) -> dict:
    """Valida y agrupa la configuracion para indices Sentinel-2."""
    # Funcion para validar y unir la configuracion de GEE e indices Sentinel-2.
    gee = deepcopy(params_gee)
    sentinel2_spectral_indices = deepcopy(params_sentinel2_spectral_indices)
    validate_gee_params(gee)
    validate_sentinel2_spectral_indices_params(sentinel2_spectral_indices)
    return {"gee": gee, "sentinel2_spectral_indices": sentinel2_spectral_indices}
