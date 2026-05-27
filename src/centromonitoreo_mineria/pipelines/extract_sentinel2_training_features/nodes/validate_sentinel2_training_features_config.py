from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_feature_extraction import (
    sentinel2_params_for_training_features,
    validate_sentinel2_training_features_params,
)
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import (
    validate_sentinel2_spectral_indices_params,
)
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.validation import (
    validate_gee_params,
)


def validate_sentinel2_training_features_config(
    params_gee: dict,
    params_sentinel2_spectral_indices: dict,
    params_sentinel2_training_features: dict,
) -> dict:
    """Valida y agrupa la configuracion para extraer variables Sentinel-2."""
    gee = deepcopy(params_gee)
    spectral_indices = deepcopy(params_sentinel2_spectral_indices)
    training_features = deepcopy(params_sentinel2_training_features)
    validate_gee_params(gee)
    spectral_indices = sentinel2_params_for_training_features(spectral_indices, training_features)
    validate_sentinel2_spectral_indices_params(spectral_indices)
    training_features = validate_sentinel2_training_features_params(training_features, spectral_indices)
    return {
        "gee": gee,
        "sentinel2_spectral_indices": spectral_indices,
        "sentinel2_training_features": training_features,
    }
