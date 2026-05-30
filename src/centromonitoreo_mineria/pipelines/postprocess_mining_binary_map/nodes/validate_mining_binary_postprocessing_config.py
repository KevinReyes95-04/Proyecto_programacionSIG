from typing import Any

from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.utils.validation import (
    require_integer,
    require_non_negative_number,
    require_text,
    validate_map_params,
    validate_outputs,
)


def validate_mining_binary_postprocessing_config(
    params_mining_binary_map_postprocessing: dict[str, Any],
) -> dict[str, Any]:
    """Valida los parametros para filtrar parches mineros y generar salidas."""
    if not isinstance(params_mining_binary_map_postprocessing, dict):
        raise ValueError("mining_binary_map_postprocessing debe ser un diccionario.")

    params = params_mining_binary_map_postprocessing
    require_text(params.get("classification_map"), "mining_binary_map_postprocessing.classification_map")
    require_text(params.get("class_label"), "mining_binary_map_postprocessing.class_label")
    require_text(params.get("negative_label"), "mining_binary_map_postprocessing.negative_label")
    require_integer(params.get("class_value"), "mining_binary_map_postprocessing.class_value")
    require_integer(params.get("negative_value"), "mining_binary_map_postprocessing.negative_value")
    require_integer(params.get("class_nodata"), "mining_binary_map_postprocessing.class_nodata")
    require_non_negative_number(params.get("min_area_ha"), "mining_binary_map_postprocessing.min_area_ha")
    if params.get("connectivity") not in {4, 8}:
        raise ValueError("mining_binary_map_postprocessing.connectivity debe ser 4 u 8.")
    validate_outputs(params.get("outputs", {}))
    validate_map_params(params.get("map", {}))
    return dict(params)
