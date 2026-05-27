import time
from copy import deepcopy
from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


def export_image_to_drive(image: Any, region: Any, params: dict) -> dict:
    """Exporta una imagen de Earth Engine a Google Drive."""
    image = image.clip(region)
    params, image = _align_image_if_configured(image=image, params=params)
    export_params = build_drive_export_params(image=image, region=region, params=params)
    task = load_ee().batch.Export.image.toDrive(**export_params)
    task.start()

    drive = params.get("drive_export", {})
    status = (
        _wait_for_task(
            task,
            drive.get("poll_interval_seconds", 30),
            drive.get("timeout_seconds", 7200),
        )
        if drive.get("wait_for_completion", False)
        else task.status()
    )

    return {
        "method": "drive_export",
        "task_id": task.id,
        "operation_name": task.operation_name,
        "state": _state(status),
        "status": _json_safe(status),
        "drive_folder": export_params.get("folder"),
        "file_name_prefix": export_params.get("fileNamePrefix"),
        "description": export_params["description"],
        "file_format": export_params.get("fileFormat"),
        "bands": params.get("bands", []),
        "scale": export_params.get("scale"),
        "crs": export_params.get("crs"),
        "max_pixels": export_params.get("maxPixels"),
        "waited_for_completion": drive.get("wait_for_completion", False),
    }


def build_drive_export_params(image: Any, region: Any, params: dict) -> dict:
    drive = params.get("drive_export", {})
    file_name_prefix = drive.get("file_name_prefix") or "sentinel2_composite"
    export_params = {
        "image": image,
        "description": drive.get("description") or file_name_prefix,
        "fileNamePrefix": file_name_prefix,
        "region": region,
        "scale": params.get("scale", 20),
        "maxPixels": drive.get("max_pixels", 100000000),
        "fileFormat": drive.get("file_format", "GeoTIFF"),
        **{
            key: value
            for key, value in {
                "folder": drive.get("folder"),
                "crs": params.get("crs"),
            }.items()
            if value is not None
        },
    }
    return export_params


def _align_image_if_configured(image: Any, params: dict) -> tuple[dict, Any]:
    projection = _reference_projection(image, params)
    if projection is None:
        return params, image

    aligned_params = deepcopy(params)
    aligned_params["crs"] = projection.crs().getInfo()
    aligned_params["scale"] = projection.nominalScale().getInfo()
    return aligned_params, image.reproject(projection)


def _reference_projection(image: Any, params: dict) -> Any | None:
    drive = params.get("drive_export", {})
    if not drive.get("align_to_reference_band", False):
        return None

    reference_band = drive.get("reference_band") or params.get("bands", [None])[0]
    if reference_band not in params.get("bands", []):
        raise ValueError(
            "drive_export.reference_band debe existir en la lista de bandas "
            f"configuradas. Valor recibido: {reference_band}."
        )
    return image.select(reference_band).projection()


def _wait_for_task(task: Any, poll_interval: int, timeout: int) -> dict:
    start_time = time.monotonic()
    while True:
        status = task.status()
        state = _state(status)
        if state in TERMINAL_STATES:
            if state != "COMPLETED":
                raise RuntimeError(
                    "La exportacion a Drive termino en estado "
                    f"{state}. {_status_error_message(status)}"
                )
            return status
        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                "La exportacion a Drive sigue activa despues de "
                f"{timeout} segundos."
            )
        time.sleep(poll_interval)


def _state(status: dict) -> str | None:
    state = status.get("state")
    return state.value if hasattr(state, "value") else None if state is None else str(state)


def _status_error_message(status: dict) -> str:
    return str(
        status.get("error_message")
        or status.get("errorMessage")
        or f"Estado completo: {_json_safe(status)}"
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value.value if hasattr(value, "value") else value
