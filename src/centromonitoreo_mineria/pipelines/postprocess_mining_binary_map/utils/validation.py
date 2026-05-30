from typing import Any


def validate_outputs(outputs: dict[str, Any]) -> None:
    """Valida las rutas de salida del postprocesamiento."""
    if not isinstance(outputs, dict):
        raise ValueError("mining_binary_map_postprocessing.outputs debe ser un diccionario.")
    for key in ("postprocessed_classification_map", "polygons", "polygon_summary_csv"):
        require_text(outputs.get(key), f"mining_binary_map_postprocessing.outputs.{key}")


def validate_map_params(params: dict[str, Any]) -> None:
    """Valida la configuracion opcional del mapa cartografico."""
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_postprocessing.map debe ser un diccionario.")
    if "output_path" in params:
        require_text(params["output_path"], "mining_binary_map_postprocessing.map.output_path")


def require_text(value: Any, name: str) -> None:
    """Exige un texto no vacio."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def require_integer(value: Any, name: str) -> None:
    """Exige un entero real, no booleano."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} debe ser entero.")


def require_non_negative_number(value: Any, name: str) -> None:
    """Exige un numero mayor o igual a cero."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} debe ser un numero mayor o igual a cero.")
