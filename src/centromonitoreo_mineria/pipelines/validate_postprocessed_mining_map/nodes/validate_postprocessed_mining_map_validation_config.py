from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    validate_postprocessed_mining_map_validation_params,
)


def validate_postprocessed_mining_map_validation_config(
    params_postprocessed_mining_map_validation: dict,
) -> dict:
    """Valida la configuracion para validar el mapa postprocesado."""
    return validate_postprocessed_mining_map_validation_params(deepcopy(params_postprocessed_mining_map_validation))
