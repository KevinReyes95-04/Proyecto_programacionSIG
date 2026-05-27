from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_postprocessing import (
    validate_mining_binary_map_postprocessing_params,
)


def validate_mining_binary_postprocessing_config(
    params_mining_binary_map_postprocessing: dict,
) -> dict:
    """Valida la configuracion para postprocesar el mapa binario."""
    return validate_mining_binary_map_postprocessing_params(deepcopy(params_mining_binary_map_postprocessing))
