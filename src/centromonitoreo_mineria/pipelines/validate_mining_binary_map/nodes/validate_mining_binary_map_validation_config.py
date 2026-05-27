from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import (
    validate_mining_binary_map_validation_params,
)


def validate_mining_binary_map_validation_config(
    params_mining_binary_map_validation: dict,
) -> dict:
    """Valida la configuracion para revisar el mapa binario."""
    return validate_mining_binary_map_validation_params(deepcopy(params_mining_binary_map_validation))
