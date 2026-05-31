from copy import deepcopy
from typing import Any


# Funcion para validar la configuracion de validacion multiclase.
def validate_mining_multiclass_map_validation_config(
    params_mining_multiclass_map_validation: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(params_mining_multiclass_map_validation, dict):
        raise ValueError("mining_multiclass_map_validation debe ser un diccionario.")
    params = deepcopy(params_mining_multiclass_map_validation)
    _require_text(params.get("label_column"), "label_column")
    _require_text(params.get("prediction_column"), "prediction_column")
    _require_text_list(params.get("class_labels"), "class_labels")
    if not isinstance(params.get("class_values", {}), dict) or not params["class_values"]:
        raise ValueError("mining_multiclass_map_validation.class_values debe ser un diccionario no vacio.")
    if not isinstance(params.get("coordinate_columns", {}), dict):
        raise ValueError("mining_multiclass_map_validation.coordinate_columns debe ser un diccionario.")
    return params


# Funcion para validar texto obligatorio.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mining_multiclass_map_validation.{name} debe ser texto no vacio.")


# Funcion para validar listas de texto.
def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"mining_multiclass_map_validation.{name} debe ser una lista de textos.")

