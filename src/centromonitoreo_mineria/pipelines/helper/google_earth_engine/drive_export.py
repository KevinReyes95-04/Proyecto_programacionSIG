import time
from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


def export_image_to_drive(image: Any, region: Any, params: dict) -> dict:
    ee = load_ee()
    export_params = build_drive_export_params(image=image, region=region, params=params)
    task = ee.batch.Export.image.toDrive(**export_params)
    task.start()

    drive_params = params.get("drive_export", {})
    status = task.status()
    if drive_params.get("wait_for_completion", False):
        status = _wait_for_task(
            task,
            drive_params.get("poll_interval_seconds", 30),
            drive_params.get("timeout_seconds", 7200),
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
        "waited_for_completion": drive_params.get("wait_for_completion", False),
    }


def build_drive_export_params(image: Any, region: Any, params: dict) -> dict:
    drive_params = params.get("drive_export", {})
    file_name_prefix = drive_params.get("file_name_prefix") or "sentinel2_composite"
    export_params = {
        "image": image,
        "description": drive_params.get("description") or file_name_prefix,
        "fileNamePrefix": file_name_prefix,
        "region": region,
        "scale": params.get("scale", 20),
        "maxPixels": drive_params.get("max_pixels", 100000000),
        "fileFormat": drive_params.get("file_format", "GeoTIFF"),
    }
    optional_params = {
        "folder": drive_params.get("folder"),
        "crs": params.get("crs"),
        "shardSize": drive_params.get("shard_size"),
        "fileDimensions": tuple(drive_params["file_dimensions"])
        if isinstance(drive_params.get("file_dimensions"), list)
        else drive_params.get("file_dimensions"),
        "skipEmptyTiles": drive_params.get("skip_empty_tiles"),
        "priority": drive_params.get("priority"),
    }
    export_params.update({key: value for key, value in optional_params.items() if value is not None})

    format_options = {
        "cloudOptimized": drive_params["cloud_optimized"]
        for key in ["cloud_optimized"]
        if drive_params.get(key) is not None
    }
    if drive_params.get("no_data") is not None:
        format_options["noData"] = drive_params["no_data"]
    if format_options:
        export_params["formatOptions"] = format_options

    return export_params


def _wait_for_task(task: Any, poll_interval: int, timeout: int) -> dict:
    start_time = time.monotonic()
    while True:
        status = task.status()
        state = _state(status)
        if state in {"COMPLETED", "FAILED", "CANCELLED"}:
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
    if hasattr(state, "value"):
        return state.value # type: ignore
    return None if state is None else str(state)


def _status_error_message(status: dict) -> str:
    message = status.get("error_message") or status.get("errorMessage")
    if message:
        return str(message)
    return f"Estado completo: {_json_safe(status)}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value.value if hasattr(value, "value") else value
