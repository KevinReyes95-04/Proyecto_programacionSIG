from typing import Any


def validate_mining_binary_map_validation_config(
    params_mining_binary_map_validation: dict[str, Any],
) -> dict[str, Any]:
    """Valida los parametros para superponer puntos sobre el mapa binario."""
    if not isinstance(params_mining_binary_map_validation, dict):
        raise ValueError("mining_binary_map_validation debe ser un diccionario.")

    params = params_mining_binary_map_validation
    _require_text(params.get("positive_label"), "mining_binary_map_validation.positive_label")
    _require_text(params.get("target_column"), "mining_binary_map_validation.target_column")
    _require_text(params.get("prediction_column"), "mining_binary_map_validation.prediction_column")
    _require_text(params.get("label_column"), "mining_binary_map_validation.label_column")

    coordinate_columns = params.get("coordinate_columns", {})
    _require_text(coordinate_columns.get("longitude"), "coordinate_columns.longitude")
    _require_text(coordinate_columns.get("latitude"), "coordinate_columns.latitude")
    _require_text(coordinate_columns.get("source_crs"), "coordinate_columns.source_crs")
    return dict(params)


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")
