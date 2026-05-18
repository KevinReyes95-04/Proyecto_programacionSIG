from copy import deepcopy
from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.validation import (
    validate_sentinel2_download_params,
)


def validate_sentinel2_spectral_indices_params(params: dict[str, Any]) -> None:
    validate_sentinel2_download_params(params)
    if not isinstance(params.get("include_original_bands", True), bool):
        raise ValueError("sentinel2_spectral_indices.include_original_bands debe ser true o false.")
    if not isinstance(params.get("indices"), dict) or not params["indices"]:
        raise ValueError("sentinel2_spectral_indices.indices debe tener al menos un indice.")

    source_bands = set(params.get("bands", []))
    enabled_indices = [name for name, config in params["indices"].items() if config.get("enabled", True)]
    if not enabled_indices:
        raise ValueError("Activa al menos un indice en sentinel2_spectral_indices.indices.")

    for name, config in params["indices"].items():
        _validate_index_config(name=name, config=config, source_bands=source_bands)
    _validate_output_band_order(params, enabled_indices)
    _validate_visualization_params(params.get("visualization", {}), enabled_indices)


def build_sentinel2_indices_image(sentinel2_composite_image: Any, params: dict[str, Any]) -> Any:
    index_images = [
        _calculate_index(sentinel2_composite_image, name, config)
        for name, config in params["indices"].items()
        if config.get("enabled", True)
    ]
    if not index_images:
        raise ValueError("No hay indices activos para calcular.")

    image = index_images[0]
    for index_image in index_images[1:]:
        image = image.addBands(index_image)
    if params.get("include_original_bands", True):
        image = sentinel2_composite_image.select(params["bands"]).addBands(image)
    if params.get("output_band_order"):
        image = image.select(params["output_band_order"])
    return image.toFloat()


def output_bands(params: dict[str, Any]) -> list[str]:
    if params.get("output_band_order"):
        return list(params["output_band_order"])
    index_names = [name for name, config in params["indices"].items() if config.get("enabled", True)]
    return list(params.get("bands", [])) + index_names if params.get("include_original_bands", True) else index_names


def export_params_with_output_bands(params: dict[str, Any]) -> dict[str, Any]:
    export_params = deepcopy(params)
    export_params["bands"] = output_bands(params)
    return export_params


def _validate_index_config(name: str, config: dict[str, Any], source_bands: set[str]) -> None:
    if not isinstance(config, dict):
        raise ValueError(f"El indice {name} debe configurarse como diccionario.")
    if not isinstance(config.get("enabled", True), bool):
        raise ValueError(f"sentinel2_spectral_indices.indices.{name}.enabled debe ser true o false.")

    formula = config.get("formula")
    if formula not in {"normalized_difference", "ratio", "expression"}:
        raise ValueError(f"El indice {name} debe usar formula normalized_difference, ratio o expression.")
    if not isinstance(config.get("bands"), dict) or not config["bands"]:
        raise ValueError(f"El indice {name} debe definir bands.")

    missing_bands = set(config["bands"].values()) - source_bands
    if missing_bands:
        raise ValueError(f"El indice {name} usa bandas no configuradas: {sorted(missing_bands)}.")
    if formula in {"normalized_difference", "ratio"} and not {"first", "second"} <= set(config["bands"]):
        raise ValueError(f"El indice {name} requiere bands.first y bands.second.")
    if formula == "expression" and not isinstance(config.get("expression"), str):
        raise ValueError(f"El indice {name} requiere expression como texto.")


def _validate_output_band_order(params: dict[str, Any], enabled_indices: list[str]) -> None:
    output_band_order = params.get("output_band_order")
    if output_band_order is None:
        return
    if not isinstance(output_band_order, list) or not all(isinstance(item, str) for item in output_band_order):
        raise ValueError("sentinel2_spectral_indices.output_band_order debe ser una lista de textos.")
    allowed_bands = set(params.get("bands", [])) | set(enabled_indices)
    unknown_bands = set(output_band_order) - allowed_bands
    if unknown_bands:
        raise ValueError(f"output_band_order incluye bandas desconocidas: {sorted(unknown_bands)}.")


def _validate_visualization_params(params: dict[str, Any], enabled_indices: list[str]) -> None:
    if not isinstance(params, dict):
        raise ValueError("sentinel2_spectral_indices.visualization debe ser un diccionario.")
    if not isinstance(params.get("enabled", True), bool):
        raise ValueError("sentinel2_spectral_indices.visualization.enabled debe ser true o false.")
    if not params.get("enabled", True):
        return
    default_style = params.get("default_style", {})
    _validate_map_style("default_style", default_style)
    for index_name, style in params.get("indices", {}).items():
        if index_name not in enabled_indices:
            raise ValueError(f"visualization.indices incluye indice no activo: {index_name}.")
        _validate_map_style(index_name, default_style | style)


def _validate_map_style(name: str, style: dict[str, Any]) -> None:
    if not isinstance(style, dict):
        raise ValueError(f"visualization.{name} debe ser un diccionario.")
    if not isinstance(style.get("palette"), list) or not style["palette"]:
        raise ValueError(f"visualization.{name}.palette debe ser una lista no vacia.")
    for key in ("min", "max"):
        if not isinstance(style.get(key), int | float) or isinstance(style.get(key), bool):
            raise ValueError(f"visualization.{name}.{key} debe ser numerico.")
    if style["min"] >= style["max"]:
        raise ValueError(f"visualization.{name}.min debe ser menor que max.")


def _calculate_index(image: Any, name: str, config: dict[str, Any]) -> Any:
    formula = config["formula"]
    bands = config["bands"]
    if formula == "normalized_difference":
        return image.normalizedDifference([bands["first"], bands["second"]]).rename(name)
    if formula == "ratio":
        return image.select(bands["first"]).divide(image.select(bands["second"])).rename(name)
    return image.expression(
        config["expression"],
        {alias: image.select(band_name) for alias, band_name in bands.items()},
    ).rename(name)
