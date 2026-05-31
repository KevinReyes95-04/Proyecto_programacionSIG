from copy import deepcopy
from typing import Any


# Funcion para validar la configuracion de prediccion multiclase.
def validate_mining_multiclass_map_prediction_config(
    params_mining_multiclass_map_prediction: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(params_mining_multiclass_map_prediction, dict):
        raise ValueError("mining_multiclass_map_prediction debe ser un diccionario.")
    params = deepcopy(params_mining_multiclass_map_prediction)
    _require_text(params.get("raster_dir"), "raster_dir")
    _require_text(params.get("band_file_template"), "band_file_template")
    _require_text_list(params.get("bands"), "bands")
    _require_text_list(params.get("feature_columns"), "feature_columns")
    if not isinstance(params.get("class_values", {}), dict) or not params["class_values"]:
        raise ValueError("mining_multiclass_map_prediction.class_values debe ser un diccionario no vacio.")
    _validate_outputs(params.get("outputs", {}))
    return params


# Funcion para validar las salidas raster configuradas.
def _validate_outputs(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("mining_multiclass_map_prediction.outputs debe ser un diccionario.")
    _require_text(outputs.get("classification_map"), "outputs.classification_map")
    _require_text(outputs.get("probability_max_map"), "outputs.probability_max_map")


# Funcion para validar texto obligatorio.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mining_multiclass_map_prediction.{name} debe ser texto no vacio.")


# Funcion para validar listas de texto.
def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"mining_multiclass_map_prediction.{name} debe ser una lista de textos.")

