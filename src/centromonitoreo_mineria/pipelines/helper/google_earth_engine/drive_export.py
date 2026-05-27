import time
from copy import deepcopy
from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


def export_image_to_drive(image: Any, region: Any, params: dict) -> dict:
    ee = load_ee()
    if params.get("drive_export", {}).get("file_per_band", False):
        return _export_bands_to_drive(ee=ee, image=image, region=region, params=params)

    image = image.clip(region)
    reference_grid = _reference_grid(image, params)
    if reference_grid is not None:
        image = image.reproject(reference_grid["projection"])
        params = deepcopy(params)
        params["crs"] = reference_grid["crs"]
        params["scale"] = reference_grid["scale"]
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


def _export_bands_to_drive(ee: Any, image: Any, region: Any, params: dict) -> dict:
    bands = params.get("bands", [])
    if not bands:
        raise ValueError("Para exportar por banda, params.bands no puede estar vacio.")

    image = image.clip(region)
    reference_grid = _reference_grid(image, params)
    tasks = []
    for band in bands:
        band_params = params_for_band_export(params, band)
        band_image = image.select(band)
        if reference_grid is not None:
            band_image = band_image.reproject(reference_grid["projection"])
            band_params["crs"] = reference_grid["crs"]
            band_params["scale"] = reference_grid["scale"]
        export_params = build_drive_export_params(
            image=band_image,
            region=region,
            params=band_params,
        )
        task = ee.batch.Export.image.toDrive(**export_params)
        task.start()
        tasks.append({"band": band, "task": task, "export_params": export_params})

    drive_params = params.get("drive_export", {})
    task_metadata = _task_metadata(tasks)
    if drive_params.get("wait_for_completion", False):
        task_metadata = _wait_for_tasks(
            tasks,
            drive_params.get("poll_interval_seconds", 30),
            drive_params.get("timeout_seconds", 7200),
        )

    return {
        "method": "drive_export_per_band",
        "drive_folder": drive_params.get("folder"),
        "file_name_prefix": drive_params.get("file_name_prefix"),
        "band_file_name_template": drive_params.get(
            "band_file_name_template",
            "{file_name_prefix}_{band}_masked",
        ),
        "file_format": drive_params.get("file_format", "GeoTIFF"),
        "bands": bands,
        "scale": params.get("scale", 20),
        "crs": params.get("crs"),
        "max_pixels": drive_params.get("max_pixels", 100000000),
        "align_to_reference_band": drive_params.get("align_to_reference_band", False),
        "reference_band": drive_params.get("reference_band"),
        "waited_for_completion": drive_params.get("wait_for_completion", False),
        "tasks": task_metadata,
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


def params_for_band_export(params: dict, band: str) -> dict:
    band_params = deepcopy(params)
    drive_params = deepcopy(params.get("drive_export", {}))
    file_name_prefix = drive_params.get("file_name_prefix") or "sentinel2_composite"
    description = drive_params.get("description") or file_name_prefix
    template_context = {
        "band": band,
        "file_name_prefix": file_name_prefix,
        "description": description,
    }
    drive_params["file_name_prefix"] = drive_params.get(
        "band_file_name_template",
        "{file_name_prefix}_{band}_masked",
    ).format(**template_context)
    drive_params["description"] = drive_params.get(
        "band_description_template",
        "{description}_{band}_masked",
    ).format(**template_context)
    band_params["bands"] = [band]
    band_params["drive_export"] = drive_params
    return band_params


def _reference_grid(image: Any, params: dict) -> dict[str, Any] | None:
    drive_params = params.get("drive_export", {})
    if not drive_params.get("align_to_reference_band", False):
        return None
    reference_band = drive_params.get("reference_band") or params.get("bands", [None])[0]
    if reference_band not in params.get("bands", []):
        raise ValueError(
            "drive_export.reference_band debe existir en la lista de bandas "
            f"configuradas. Valor recibido: {reference_band}."
        )
    projection = image.select(reference_band).projection()
    return {
        "projection": projection,
        "crs": projection.crs().getInfo(),
        "scale": projection.nominalScale().getInfo(),
    }


def _task_metadata(tasks: list[dict]) -> list[dict]:
    return [
        _single_task_metadata(
            band=task_data["band"],
            task=task_data["task"],
            export_params=task_data["export_params"],
            status=task_data["task"].status(),
        )
        for task_data in tasks
    ]


def _wait_for_tasks(tasks: list[dict], poll_interval: int, timeout: int) -> list[dict]:
    start_time = time.monotonic()
    completed: dict[str, dict] = {}
    while len(completed) < len(tasks):
        for task_data in tasks:
            band = task_data["band"]
            if band in completed:
                continue
            status = task_data["task"].status()
            state = _state(status)
            if state in {"COMPLETED", "FAILED", "CANCELLED"}:
                if state != "COMPLETED":
                    raise RuntimeError(
                        "La exportacion a Drive de la banda "
                        f"{band} termino en estado {state}. {_status_error_message(status)}"
                    )
                completed[band] = _single_task_metadata(
                    band=band,
                    task=task_data["task"],
                    export_params=task_data["export_params"],
                    status=status,
                )
        if len(completed) == len(tasks):
            break
        if time.monotonic() - start_time > timeout:
            pending = [
                task_data["band"]
                for task_data in tasks
                if task_data["band"] not in completed
            ]
            raise TimeoutError(
                "La exportacion por banda sigue activa despues de "
                f"{timeout} segundos. Bandas pendientes: {pending}."
            )
        time.sleep(poll_interval)
    return [completed[task_data["band"]] for task_data in tasks]


def _single_task_metadata(
    band: str,
    task: Any,
    export_params: dict,
    status: dict,
) -> dict:
    return {
        "band": band,
        "task_id": task.id,
        "operation_name": task.operation_name,
        "state": _state(status),
        "status": _json_safe(status),
        "file_name_prefix": export_params.get("fileNamePrefix"),
        "description": export_params["description"],
    }


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
