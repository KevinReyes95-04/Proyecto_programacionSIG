from typing import Any


# Funcion para validar parametros de la validacion del mapa postprocesado.
def validate_postprocessed_mining_map_validation_params(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("postprocessed_mining_map_validation debe ser un diccionario.")
    _require_text(params.get("label_column"), "postprocessed_mining_map_validation.label_column")
    _require_text(params.get("positive_label"), "postprocessed_mining_map_validation.positive_label")
    _require_text(params.get("negative_label"), "postprocessed_mining_map_validation.negative_label")
    coordinate_columns = params.get("coordinate_columns", {})
    _require_text(coordinate_columns.get("longitude"), "coordinate_columns.longitude")
    _require_text(coordinate_columns.get("latitude"), "coordinate_columns.latitude")
    _validate_outputs(params.get("outputs", {}))
    return dict(params)


# Funcion para validar rutas de salida configuradas.
def _validate_outputs(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("postprocessed_mining_map_validation.outputs debe ser un diccionario.")
    for key in ("point_validation", "class_summary"):
        _require_text(outputs.get(key), f"postprocessed_mining_map_validation.outputs.{key}")


# Funcion para validar campos de texto.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")
