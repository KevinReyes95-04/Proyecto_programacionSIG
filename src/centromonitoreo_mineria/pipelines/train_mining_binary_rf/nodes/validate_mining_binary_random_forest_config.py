from typing import Any


# Funcion para validar la configuracion del Random Forest binario.
def validate_mining_binary_random_forest_config(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_random_forest debe ser un diccionario.")
    _require_text(params.get("label_column"), "mining_binary_random_forest.label_column")
    _require_text(params.get("positive_label"), "mining_binary_random_forest.positive_label")
    _require_text(params.get("negative_label"), "mining_binary_random_forest.negative_label")
    _require_text_list(params.get("negative_source_labels"), "mining_binary_random_forest.negative_source_labels")
    _require_text_list(params.get("feature_columns"), "mining_binary_random_forest.feature_columns")
    _validate_probability_threshold(params.get("classification_threshold", 0.5))
    _validate_random_forest_params(params.get("random_forest", {}))
    return dict(params)


# Funcion para validar parametros numericos del Random Forest.
def _validate_random_forest_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_random_forest.random_forest debe ser un diccionario.")
    for key in ("n_estimators", "min_samples_leaf", "min_samples_split"):
        value = params.get(key)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            raise ValueError(f"mining_binary_random_forest.random_forest.{key} debe ser entero positivo.")


# Funcion para validar el umbral de clasificacion.
def _validate_probability_threshold(value: Any) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError("mining_binary_random_forest.classification_threshold debe estar entre 0 y 1.")


# Funcion para validar campos de texto.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


# Funcion para validar listas de texto.
def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")
