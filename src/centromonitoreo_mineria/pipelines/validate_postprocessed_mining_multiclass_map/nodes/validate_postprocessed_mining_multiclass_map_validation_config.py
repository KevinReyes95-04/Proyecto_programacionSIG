from typing import Any

from centromonitoreo_mineria.pipelines.validate_mining_multiclass_map.nodes import (
    validate_mining_multiclass_map_validation_config,
)


# Funcion para validar la configuracion de validacion del mapa multiclase postprocesado.
def validate_postprocessed_mining_multiclass_map_validation_config(
    params_postprocessed_mining_multiclass_map_validation: dict[str, Any],
) -> dict[str, Any]:
    return validate_mining_multiclass_map_validation_config(params_postprocessed_mining_multiclass_map_validation)

