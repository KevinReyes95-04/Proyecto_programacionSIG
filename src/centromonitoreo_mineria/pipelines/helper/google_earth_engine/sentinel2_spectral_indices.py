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
    if formula not in {"normalized_difference", "expression"}:
        raise ValueError(f"El indice {name} debe usar formula normalized_difference o expression.")
    if not isinstance(config.get("bands"), dict) or not config["bands"]:
        raise ValueError(f"El indice {name} debe definir bands.")

    missing_bands = set(config["bands"].values()) - source_bands
    if missing_bands:
        raise ValueError(f"El indice {name} usa bandas no configuradas: {sorted(missing_bands)}.")
    if formula == "normalized_difference" and not {"first", "second"} <= set(config["bands"]):
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


def _calculate_index(image: Any, name: str, config: dict[str, Any]) -> Any:
    formula = config["formula"]
    bands = config["bands"]
    if formula == "normalized_difference":
        return image.normalizedDifference([bands["first"], bands["second"]]).rename(name)
    return image.expression(
        config["expression"],
        {alias: image.select(band_name) for alias, band_name in bands.items()},
    ).rename(name)
