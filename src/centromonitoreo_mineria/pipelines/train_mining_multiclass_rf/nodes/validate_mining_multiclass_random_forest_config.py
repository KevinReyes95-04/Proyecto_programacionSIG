from copy import deepcopy
from typing import Any


# Funcion para validar la configuracion del modelo multiclase.
def validate_mining_multiclass_random_forest_config(
    params_mining_multiclass_random_forest: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(params_mining_multiclass_random_forest, dict):
        raise ValueError("mining_multiclass_random_forest debe ser un diccionario.")
    params = deepcopy(params_mining_multiclass_random_forest)
    _require_text(params.get("label_column"), "label_column")
    _require_text(params.get("target_column"), "target_column")
    _require_text(params.get("prediction_column"), "prediction_column")
    _require_text_list(params.get("class_labels"), "class_labels")
    _require_text_list(params.get("feature_columns"), "feature_columns")
    if not isinstance(params.get("random_forest", {}), dict):
        raise ValueError("random_forest debe ser un diccionario.")
    return params


# Funcion para validar texto obligatorio.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mining_multiclass_random_forest.{name} debe ser texto no vacio.")


# Funcion para validar listas de texto.
def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"mining_multiclass_random_forest.{name} debe ser una lista de textos.")

