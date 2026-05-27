from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_prediction import (
    validate_mining_binary_map_prediction_params,
)


def validate_mining_binary_map_prediction_config(
    params_mining_binary_map_prediction: dict,
) -> dict:
    """Valida la configuracion para predecir mapa binario de mineria."""
    return validate_mining_binary_map_prediction_params(deepcopy(params_mining_binary_map_prediction))
