from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    validate_binary_random_forest_params,
)


def validate_mining_binary_random_forest_config(
    params_mining_binary_random_forest: dict,
) -> dict:
    """Valida la configuracion del Random Forest binario."""
    return validate_binary_random_forest_params(deepcopy(params_mining_binary_random_forest))
