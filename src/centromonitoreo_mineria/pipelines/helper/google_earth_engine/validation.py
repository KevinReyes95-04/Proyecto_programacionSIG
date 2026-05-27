from datetime import date
from pathlib import Path
from typing import Any


SENTINEL2_SR_COLLECTIONS = {"COPERNICUS/S2_SR", "COPERNICUS/S2_SR_HARMONIZED"}


def validate_gee_params(params_gee: dict) -> None:
    if not isinstance(params_gee, dict):
        raise ValueError("gee debe ser un diccionario de parametros.")

    _require_text(params_gee.get("project"), "gee.project")
    auth_method = params_gee.get("auth_method", "oauth")
    if auth_method not in {"oauth", "service_account", "adc"}:
        raise ValueError("gee.auth_method debe ser oauth, service_account o adc.")
    if not isinstance(params_gee.get("authenticate", False), bool):
        raise ValueError("gee.authenticate debe ser true o false.")
    if params_gee.get("auth_mode") is not None:
        _require_text(params_gee.get("auth_mode"), "gee.auth_mode")
    _require_text_list(params_gee.get("adc_scopes", []), "gee.adc_scopes")

    if auth_method == "service_account":
        _require_text(params_gee.get("service_account_email"), "gee.service_account_email")
        key_path = Path(_require_text(params_gee.get("service_account_key_path"), "gee.service_account_key_path"))
        if not key_path.exists():
            raise ValueError(f"gee.service_account_key_path no existe: {key_path.as_posix()}")
        if key_path.suffix.lower() != ".json":
            raise ValueError("gee.service_account_key_path debe apuntar a un .json.")


def validate_sentinel2_download_params(params: dict) -> None:
    if not isinstance(params, dict):
        raise ValueError("sentinel2_download debe ser un diccionario de parametros.")

    _require_text(params.get("collection"), "sentinel2_download.collection")
    _validate_roi(params.get("roi", {}))
    start_date = _parse_date(params.get("start_date"), "sentinel2_download.start_date")
    end_date = _parse_date(params.get("end_date"), "sentinel2_download.end_date")
    if start_date >= end_date:
        raise ValueError("sentinel2_download.start_date debe ser menor que end_date.")

    cloud_cover = params.get("cloud_cover_max")
    if cloud_cover is not None and (not _is_number(cloud_cover) or not 0 <= cloud_cover <= 100):
        raise ValueError("sentinel2_download.cloud_cover_max debe estar entre 0 y 100.")

    if not isinstance(params.get("cloud_mask", False), bool):
        raise ValueError("sentinel2_download.cloud_mask debe ser true o false.")
    if params.get("cloud_mask_method", "qa60") not in {"qa60", "scl", "qa60_and_scl"}:
        raise ValueError("sentinel2_download.cloud_mask_method debe ser qa60, scl o qa60_and_scl.")
    _validate_scl_classes(params.get("cloud_mask_scl_classes", [3, 8, 9, 10]))

    _require_text_list(params.get("bands"), "sentinel2_download.bands")
    if not params.get("bands"):
        raise ValueError("sentinel2_download.bands no puede estar vacio.")
    if params["collection"] in SENTINEL2_SR_COLLECTIONS and "B10" in params["bands"]:
        raise ValueError(
            "sentinel2_download.bands incluye B10, pero las colecciones "
            "Sentinel-2 Level-2A/SR no tienen esa banda."
        )
    _require_positive_number(params.get("scale"), "sentinel2_download.scale")
    if params.get("composite_method", "median") not in {"median", "mean", "mosaic"}:
        raise ValueError("sentinel2_download.composite_method debe ser median, mean o mosaic.")
    if params.get("sort_by") is not None:
        _require_text(params.get("sort_by"), "sentinel2_download.sort_by")
    if not isinstance(params.get("sort_ascending", True), bool):
        raise ValueError("sentinel2_download.sort_ascending debe ser true o false.")
    if params.get("crs") is not None:
        _require_text(params.get("crs"), "sentinel2_download.crs")
    if not isinstance(params.get("apply_reflectance_scale", True), bool):
        raise ValueError("sentinel2_download.apply_reflectance_scale debe ser true o false.")
    _require_positive_number(
        params.get("reflectance_scale_factor", 0.0001),
        "sentinel2_download.reflectance_scale_factor",
    )

    _validate_drive_export_params(params.get("drive_export", {}))


def _validate_roi(params_roi: dict) -> None:
    if not isinstance(params_roi, dict):
        raise ValueError("sentinel2_download.roi debe ser un diccionario.")

    roi_source = params_roi.get("source")
    if roi_source is not None and roi_source not in {"bbox", "inline_geojson", "geojson_path"}:
        raise ValueError("sentinel2_download.roi.source debe ser bbox, inline_geojson o geojson_path.")

    configured_sources = {
        key for key in ("bbox", "inline_geojson", "geojson_path") if params_roi.get(key) is not None
    }
    if "geojson_path" in configured_sources and not params_roi.get("geojson_path"):
        configured_sources.remove("geojson_path")
    if roi_source and roi_source not in configured_sources:
        raise ValueError(f"sentinel2_download.roi.source es {roi_source}, pero esa fuente no esta configurada.")
    if not roi_source and not configured_sources:
        raise ValueError(
            "Configura sentinel2_download.roi.geojson_path, "
            "sentinel2_download.roi.bbox o sentinel2_download.roi.inline_geojson."
        )

    active_sources = [roi_source] if roi_source else configured_sources
    if "geojson_path" in active_sources:
        geojson_path = Path(params_roi["geojson_path"])
        if not geojson_path.exists():
            raise ValueError(f"sentinel2_download.roi.geojson_path no existe: {geojson_path.as_posix()}")
        if geojson_path.suffix.lower() not in {".geojson", ".json"}:
            raise ValueError("sentinel2_download.roi.geojson_path debe apuntar a un .geojson o .json.")
    if "inline_geojson" in active_sources:
        inline_geojson = params_roi["inline_geojson"]
        if not isinstance(inline_geojson, dict) or not inline_geojson.get("type"):
            raise ValueError("sentinel2_download.roi.inline_geojson debe ser un GeoJSON valido.")
    if "bbox" in active_sources:
        bbox = params_roi["bbox"]
        values = (
            [bbox.get("min_lon"), bbox.get("min_lat"), bbox.get("max_lon"), bbox.get("max_lat")]
            if isinstance(bbox, dict)
            else list(bbox) if isinstance(bbox, list | tuple) and len(bbox) == 4
            else None
        )
        if values is None or not all(_is_number(value) for value in values):
            raise ValueError("sentinel2_download.roi.bbox debe contener numeros.")
        min_lon, min_lat, max_lon, max_lat = values
        if min_lon >= max_lon or min_lat >= max_lat: # type: ignore
            raise ValueError("sentinel2_download.roi.bbox tiene limites invalidos.")
        if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90: # type: ignore
            raise ValueError("sentinel2_download.roi.bbox esta fuera de rango geografico.")


def _validate_drive_export_params(params: dict) -> None:
    if not isinstance(params, dict):
        raise ValueError("sentinel2_download.drive_export debe ser un diccionario.")

    for key in ("folder", "file_name_prefix", "description"):
        value = params.get(key)
        if value is not None:
            _require_text(value, f"sentinel2_download.drive_export.{key}")
    if params.get("file_format", "GeoTIFF") not in {"GeoTIFF", "TFRecord"}:
        raise ValueError("sentinel2_download.drive_export.file_format debe ser GeoTIFF o TFRecord.")
    _require_positive_integer(params.get("max_pixels", 100000000), "sentinel2_download.drive_export.max_pixels")

    shard_size = params.get("shard_size")
    if shard_size is not None:
        _require_positive_integer(shard_size, "sentinel2_download.drive_export.shard_size")
    file_dimensions = params.get("file_dimensions")
    if file_dimensions is not None and not (
        (isinstance(file_dimensions, int) and not isinstance(file_dimensions, bool) and file_dimensions > 0)
        or (
            isinstance(file_dimensions, list | tuple)
            and len(file_dimensions) == 2
            and all(isinstance(item, int) and not isinstance(item, bool) and item > 0 for item in file_dimensions)
        )
    ):
        raise ValueError(
            "sentinel2_download.drive_export.file_dimensions debe ser un entero, "
            "una lista de dos enteros positivos o null."
        )
    for key in (
        "skip_empty_tiles",
        "cloud_optimized",
        "wait_for_completion",
        "file_per_band",
        "align_to_reference_band",
    ):
        if not isinstance(params.get(key, False), bool):
            raise ValueError(f"sentinel2_download.drive_export.{key} debe ser true o false.")
    for key in ("band_file_name_template", "band_description_template", "reference_band"):
        value = params.get(key)
        if value is not None:
            _require_text(value, f"sentinel2_download.drive_export.{key}")
    no_data = params.get("no_data")
    if no_data is not None and not _is_number(no_data):
        raise ValueError("sentinel2_download.drive_export.no_data debe ser un numero o null.")
    priority = params.get("priority", 100)
    if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 9999:
        raise ValueError("sentinel2_download.drive_export.priority debe estar entre 0 y 9999.")
    _require_positive_integer(params.get("poll_interval_seconds", 30), "sentinel2_download.drive_export.poll_interval_seconds")
    _require_positive_integer(params.get("timeout_seconds", 7200), "sentinel2_download.drive_export.timeout_seconds")


def _validate_scl_classes(value: Any) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("sentinel2_download.cloud_mask_scl_classes debe ser una lista no vacia.")
    if not all(isinstance(item, int) and not isinstance(item, bool) and 0 <= item <= 11 for item in value):
        raise ValueError("sentinel2_download.cloud_mask_scl_classes debe contener enteros entre 0 y 11.")


def _parse_date(value: Any, name: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{name} debe ser una fecha en formato YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} debe ser una fecha en formato YYYY-MM-DD.") from exc


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")
    return value


def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")


def _require_positive_number(value: Any, name: str) -> None:
    if not _is_number(value) or value <= 0:
        raise ValueError(f"{name} debe ser un numero mayor que cero.")


def _require_positive_integer(value: Any, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} debe ser un entero mayor que cero.")


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)
