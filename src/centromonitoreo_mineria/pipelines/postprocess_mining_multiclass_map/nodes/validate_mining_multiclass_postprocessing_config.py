from copy import deepcopy
from typing import Any


# Funcion para validar la configuracion de postprocesamiento multiclase.
def validate_mining_multiclass_postprocessing_config(
    params_mining_multiclass_map_postprocessing: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(params_mining_multiclass_map_postprocessing, dict):
        raise ValueError("mining_multiclass_map_postprocessing debe ser un diccionario.")
    params = deepcopy(params_mining_multiclass_map_postprocessing)
    _require_text(params.get("classification_map"), "classification_map")
    _require_integer(params.get("class_nodata", 255), "class_nodata")
    if not isinstance(params.get("class_values"), dict) or not params["class_values"]:
        raise ValueError("mining_multiclass_map_postprocessing.class_values debe ser un diccionario no vacio.")
    _validate_outputs(params.get("outputs", {}))
    _validate_majority_filter(params.get("majority_filter", {}))
    return params


# Funcion para validar las rutas de salida.
def _validate_outputs(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("mining_multiclass_map_postprocessing.outputs debe ser un diccionario.")
    _require_text(outputs.get("postprocessed_classification_map"), "outputs.postprocessed_classification_map")
    _require_text(outputs.get("class_summary_csv"), "outputs.class_summary_csv")


# Funcion para validar el filtro de mayoria.
def _validate_majority_filter(filter_params: dict[str, Any]) -> None:
    if not isinstance(filter_params, dict):
        raise ValueError("mining_multiclass_map_postprocessing.majority_filter debe ser un diccionario.")
    size = int(filter_params.get("size", 3))
    iterations = int(filter_params.get("iterations", 1))
    if size < 3 or size % 2 == 0:
        raise ValueError("mining_multiclass_map_postprocessing.majority_filter.size debe ser impar y mayor o igual a 3.")
    if iterations < 0:
        raise ValueError("mining_multiclass_map_postprocessing.majority_filter.iterations no puede ser negativo.")


# Funcion para validar texto obligatorio.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mining_multiclass_map_postprocessing.{name} debe ser texto no vacio.")


# Funcion para validar enteros obligatorios.
def _require_integer(value: Any, name: str) -> None:
    if not isinstance(value, int):
        raise ValueError(f"mining_multiclass_map_postprocessing.{name} debe ser entero.")

