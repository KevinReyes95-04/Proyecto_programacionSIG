from copy import deepcopy
from typing import Any

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.validation import validate_gee_params


# Funcion para validar la configuracion de variables topograficas.
def validate_topographic_features_config(
    params_gee: dict[str, Any],
    params_sentinel2_download: dict[str, Any],
    params_topographic_features: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(params_topographic_features, dict):
        raise ValueError("topographic_features debe ser un diccionario.")
    gee = deepcopy(params_gee)
    sentinel2_download = deepcopy(params_sentinel2_download)
    params = deepcopy(params_topographic_features)
    validate_gee_params(gee)
    _require_text(params.get("dem_asset"), "topographic_features.dem_asset")
    _require_text(params.get("elevation_band", "elevation"), "topographic_features.elevation_band")
    if not isinstance(params.get("output_bands", {}), dict):
        raise ValueError("topographic_features.output_bands debe ser un diccionario.")
    _require_text(params["output_bands"].get("elevation"), "topographic_features.output_bands.elevation")
    _require_text(params["output_bands"].get("slope"), "topographic_features.output_bands.slope")
    _validate_download(params.get("download", {}))
    _validate_alignment(params.get("alignment", {}))
    _validate_map_plots(params.get("map_plots", {}))
    return {"gee": gee, "sentinel2_download": sentinel2_download, "topographic_features": params}


# Funcion para validar parametros de descarga.
def _validate_download(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("topographic_features.download debe ser un diccionario.")
    if not isinstance(params.get("enabled", True), bool):
        raise ValueError("topographic_features.download.enabled debe ser true o false.")
    _require_text(params.get("output_dir"), "topographic_features.download.output_dir")
    _require_text(params.get("source_file"), "topographic_features.download.source_file")
    _require_positive_number(params.get("scale", 30), "topographic_features.download.scale")


# Funcion para validar parametros de alineacion raster.
def _validate_alignment(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("topographic_features.alignment debe ser un diccionario.")
    _require_text(params.get("reference_raster"), "topographic_features.alignment.reference_raster")
    _require_text(params.get("output_file_template"), "topographic_features.alignment.output_file_template")
    if params.get("resampling", "bilinear") not in {"nearest", "bilinear", "cubic"}:
        raise ValueError("topographic_features.alignment.resampling debe ser nearest, bilinear o cubic.")


# Funcion para validar parametros de mapas topograficos.
def _validate_map_plots(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("topographic_features.map_plots debe ser un diccionario.")
    if "output_dir" in params:
        _require_text(params["output_dir"], "topographic_features.map_plots.output_dir")
    if "dpi" in params:
        _require_positive_number(params["dpi"], "topographic_features.map_plots.dpi")
    if "percentile_clip" in params:
        clip = params["percentile_clip"]
        if (
            not isinstance(clip, list)
            or len(clip) != 2
            or not all(isinstance(value, int | float) and not isinstance(value, bool) for value in clip)
            or not 0 <= clip[0] < clip[1] <= 100
        ):
            raise ValueError("topographic_features.map_plots.percentile_clip debe tener dos percentiles entre 0 y 100.")
    if "layers" not in params:
        return
    if not isinstance(params["layers"], list) or not params["layers"]:
        raise ValueError("topographic_features.map_plots.layers debe ser una lista no vacia.")
    for index, layer in enumerate(params["layers"]):
        if not isinstance(layer, dict):
            raise ValueError(f"topographic_features.map_plots.layers[{index}] debe ser un diccionario.")
        _require_text(layer.get("band"), f"topographic_features.map_plots.layers[{index}].band")
        if "output_path" in layer:
            _require_text(layer["output_path"], f"topographic_features.map_plots.layers[{index}].output_path")


# Funcion para validar texto obligatorio.
def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


# Funcion para validar numeros positivos.
def _require_positive_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} debe ser un numero mayor que cero.")

