from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def validate_mining_binary_map_prediction_params(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_prediction debe ser un diccionario.")
    _require_text(params.get("raster_dir"), "mining_binary_map_prediction.raster_dir")
    _require_text(params.get("band_file_template"), "mining_binary_map_prediction.band_file_template")
    _require_text(params.get("positive_label"), "mining_binary_map_prediction.positive_label")
    _require_text(params.get("negative_label"), "mining_binary_map_prediction.negative_label")
    _require_text_list(params.get("bands"), "mining_binary_map_prediction.bands")
    _require_text_list(params.get("feature_columns"), "mining_binary_map_prediction.feature_columns")
    _validate_outputs(params.get("outputs", {}))
    if not isinstance(params.get("apply_reflectance_scale", True), bool):
        raise ValueError("mining_binary_map_prediction.apply_reflectance_scale debe ser true o false.")
    _require_positive_number(params.get("reflectance_scale_factor", 0.0001), "reflectance_scale_factor")
    _require_positive_integer(params.get("window_size", 512), "mining_binary_map_prediction.window_size")
    threshold = params.get("classification_threshold", 0.5)
    if not isinstance(threshold, int | float) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
        raise ValueError("mining_binary_map_prediction.classification_threshold debe estar entre 0 y 1.")
    return dict(params)


def predict_mining_map_rasters(model: Any, params: dict[str, Any]) -> dict[str, Any]:
    raster_paths = _band_paths(params)
    _ensure_rasters_exist(raster_paths)
    class_path = Path(params["outputs"]["classification_map"])
    probability_path = Path(params["outputs"]["probability_map"])
    class_path.parent.mkdir(parents=True, exist_ok=True)
    probability_path.parent.mkdir(parents=True, exist_ok=True)

    class_counts: dict[str, int] = {}
    probability_values = []
    with ExitStack() as stack:
        sources = {band: stack.enter_context(rasterio.open(path)) for band, path in raster_paths.items()}
        _validate_raster_grid(sources)
        reference = sources[params.get("reference_band", params["bands"][0])]
        class_writer = stack.enter_context(rasterio.open(class_path, "w", **_classification_profile(reference, params)))
        probability_writer = stack.enter_context(rasterio.open(probability_path, "w", **_probability_profile(reference, params)))

        for window in _windows(reference.width, reference.height, params.get("window_size", 512)):
            bands = _read_bands(sources, window, params)
            features = _feature_stack(bands, params["feature_columns"])
            predicted, probabilities, valid_mask = _predict_window(model, features, params)
            class_writer.write(predicted, 1, window=window)
            probability_writer.write(probabilities, 1, window=window)
            _update_class_counts(class_counts, predicted, params)
            probability_values.append(probabilities[valid_mask])

        bounds = reference.bounds
        crs = reference.crs.to_string() if reference.crs else None
        shape = [reference.height, reference.width]

    probabilities = np.concatenate([values for values in probability_values if values.size]) if probability_values else np.array([])
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification_map": class_path.as_posix(),
        "probability_map": probability_path.as_posix(),
        "feature_columns": params["feature_columns"],
        "classification_threshold": params.get("classification_threshold", 0.5),
        "class_counts": class_counts,
        "probability_mineria": _probability_summary(probabilities),
        "raster": {
            "shape": shape,
            "crs": crs,
            "bounds": {
                "left": bounds.left,
                "bottom": bounds.bottom,
                "right": bounds.right,
                "top": bounds.top,
            },
        },
    }


def plot_mining_map(prediction_metadata: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    plot_params = params.get("visualization", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_classification_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(prediction_metadata["classification_map"]) as source:
        class_map = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    _plot_background(axis, params, extent)
    _plot_class_overlay(axis, class_map, params, plot_params, extent)
    axis.set_title(plot_params.get("title", "Mapa binario de mineria"))
    axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    categorical_metadata = _plot_categorical_map(class_map, extent, params)
    return {
        "output_path": output_path.as_posix(),
        "categorical_output_path": categorical_metadata["output_path"],
        "classification_map": prediction_metadata["classification_map"],
    }


def build_mining_map_metadata(
    prediction_metadata: dict[str, Any],
    plot_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "positive_label": params["positive_label"],
        "negative_label": params["negative_label"],
        "class_values": params.get("class_values", {}),
        "raster_dir": params["raster_dir"],
        "prediction": prediction_metadata,
        "plot": plot_metadata,
    }


def _band_paths(params: dict[str, Any]) -> dict[str, Path]:
    raster_dir = Path(params["raster_dir"])
    template = params["band_file_template"]
    return {band: raster_dir / template.format(band=band) for band in params["bands"]}


def _ensure_rasters_exist(raster_paths: dict[str, Path]) -> None:
    missing = [path.as_posix() for path in raster_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "No se encontraron las bandas Sentinel-2 locales. Descarga desde Drive "
            "los GeoTIFF y ubicalos en la carpeta configurada. Faltan: "
            f"{missing}"
        )


def _validate_raster_grid(sources: dict[str, Any]) -> None:
    reference = next(iter(sources.values()))
    for band, source in sources.items():
        if source.shape != reference.shape or source.transform != reference.transform or source.crs != reference.crs:
            raise ValueError(f"La banda {band} no coincide en grilla, transformacion o CRS.")


def _read_bands(sources: dict[str, Any], window: Window, params: dict[str, Any]) -> dict[str, np.ndarray]:
    bands = {}
    scale = params.get("reflectance_scale_factor", 0.0001) if params.get("apply_reflectance_scale", True) else 1.0
    for band, source in sources.items():
        data = source.read(1, window=window, masked=True).astype("float32")
        bands[band] = data.filled(np.nan) * scale
    return bands


def _feature_stack(bands: dict[str, np.ndarray], feature_columns: list[str]) -> dict[str, np.ndarray]:
    features = {
        **bands,
        "NDVI": _normalized_difference(bands["B8"], bands["B4"]),
        "MSAVI": _msavi(bands["B8"], bands["B4"]),
        "NDWI": _normalized_difference(bands["B3"], bands["B8"]),
        "BSI": _safe_divide((bands["B11"] + bands["B4"]) - (bands["B8"] + bands["B2"]), (bands["B11"] + bands["B4"]) + (bands["B8"] + bands["B2"])),
        "MBSI": _normalized_difference(bands["B11"], bands["B4"]),
        "NDSI": _normalized_difference(bands["B11"], bands["B3"]),
        "MSWI": _normalized_difference(bands["B12"], bands["B4"]),
        "NDBI": _normalized_difference(bands["B11"], bands["B8"]),
    }
    return {feature: features[feature] for feature in feature_columns}


def _predict_window(model: Any, features: dict[str, np.ndarray], params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    feature_arrays = [features[column] for column in params["feature_columns"]]
    valid_mask = np.logical_and.reduce([np.isfinite(array) for array in feature_arrays])
    shape = feature_arrays[0].shape
    class_array = np.full(shape, params.get("class_nodata", 255), dtype="uint8")
    probability_array = np.full(shape, params.get("probability_nodata", -9999.0), dtype="float32")
    if not valid_mask.any():
        return class_array, probability_array, valid_mask

    matrix = pd.DataFrame(
        {
            column: features[column][valid_mask]
            for column in params["feature_columns"]
        },
        columns=params["feature_columns"],
    )
    if hasattr(model, "predict_proba"):
        positive_index = list(model.classes_).index(params["positive_label"])
        positive_probability = model.predict_proba(matrix)[:, positive_index].astype("float32")
        probability_array[valid_mask] = positive_probability
        labels = np.where(
            positive_probability >= params.get("classification_threshold", 0.5),
            params["positive_label"],
            params["negative_label"],
        )
    else:
        labels = model.predict(matrix)
    class_array[valid_mask] = np.array([_class_value(label, params) for label in labels], dtype="uint8")
    return class_array, probability_array, valid_mask


def _classification_profile(reference: Any, params: dict[str, Any]) -> dict[str, Any]:
    profile = reference.profile.copy()
    profile.update(driver="GTiff", count=1, dtype="uint8", nodata=params.get("class_nodata", 255), compress="lzw", BIGTIFF="IF_SAFER")
    return profile


def _probability_profile(reference: Any, params: dict[str, Any]) -> dict[str, Any]:
    profile = reference.profile.copy()
    profile.update(driver="GTiff", count=1, dtype="float32", nodata=params.get("probability_nodata", -9999.0), compress="lzw", BIGTIFF="IF_SAFER")
    return profile


def _windows(width: int, height: int, window_size: int) -> list[Window]:
    return [
        Window(col, row, min(window_size, width - col), min(window_size, height - row))
        for row in range(0, height, window_size)
        for col in range(0, width, window_size)
    ]


def _normalized_difference(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return _safe_divide(first - second, first + second)


def _msavi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    radicand = np.maximum(np.power(2 * nir + 1, 2) - 8 * (nir - red), 0)
    return (2 * nir + 1 - np.sqrt(radicand)) / 2


def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(numerator, denominator, out=np.full_like(numerator, np.nan, dtype="float32"), where=denominator != 0)


def _class_value(label: str, params: dict[str, Any]) -> int:
    return int(params.get("class_values", {}).get(label, params.get("class_nodata", 255)))


def _update_class_counts(class_counts: dict[str, int], class_array: np.ndarray, params: dict[str, Any]) -> None:
    for label, value in params.get("class_values", {}).items():
        class_counts[label] = class_counts.get(label, 0) + int(np.sum(class_array == value))


def _probability_summary(values: np.ndarray) -> dict[str, float | int | None]:
    if values.size == 0:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {"count": int(values.size), "min": float(values.min()), "max": float(values.max()), "mean": float(values.mean())}


def _plot_background(axis: Any, params: dict[str, Any], extent: list[float]) -> None:
    background = params.get("visualization", {}).get("background", {})
    if not background.get("enabled", True):
        return
    bands = _band_paths(params)
    required = ["B4", "B3", "B2"]
    if not all(bands[band].exists() for band in required):
        return
    rgb = []
    for band in required:
        with rasterio.open(bands[band]) as source:
            rgb.append(_stretch(source.read(1).astype("float32")))
    axis.imshow(np.dstack(rgb), extent=extent)


def _plot_class_overlay(axis: Any, class_map: np.ndarray, params: dict[str, Any], plot_params: dict[str, Any], extent: list[float]) -> None:
    positive_value = _class_value(params["positive_label"], params)
    overlay = np.where(class_map == positive_value, 1, np.nan)
    cmap = ListedColormap([plot_params.get("mining_color", "#E31A1C")])
    axis.imshow(overlay, cmap=cmap, extent=extent, alpha=plot_params.get("mining_alpha", 0.55), interpolation="nearest")


def _plot_categorical_map(class_map: np.ndarray, extent: list[float], params: dict[str, Any]) -> dict[str, Any]:
    plot_params = params.get("categorical_visualization", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_classification_categorical_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    negative_value = _class_value(params["negative_label"], params)
    positive_value = _class_value(params["positive_label"], params)
    categorical = np.where(class_map == positive_value, 1, np.where(class_map == negative_value, 0, np.nan))
    colors = [
        plot_params.get("negative_color", "#1A9850"),
        plot_params.get("positive_color", "#E31A1C"),
    ]
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    image = axis.imshow(categorical, cmap=ListedColormap(colors), extent=extent, vmin=0, vmax=1, interpolation="nearest")
    colorbar = figure.colorbar(image, ax=axis, fraction=0.036, pad=0.02, ticks=[0.25, 0.75])
    colorbar.ax.set_yticklabels([params["negative_label"], params["positive_label"]])
    axis.set_title(plot_params.get("title", "Mapa categorico Mineria vs No Mineria"))
    axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix()}


def _stretch(array: np.ndarray) -> np.ndarray:
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return np.zeros_like(array, dtype="float32")
    lower, upper = np.percentile(finite, [2, 98])
    if lower == upper:
        return np.zeros_like(array, dtype="float32")
    return np.clip((array - lower) / (upper - lower), 0, 1)


def _validate_outputs(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_prediction.outputs debe ser un diccionario.")
    _require_text(params.get("classification_map"), "outputs.classification_map")
    _require_text(params.get("probability_map"), "outputs.probability_map")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")


def _require_positive_number(value: Any, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} debe ser un numero mayor que cero.")


def _require_positive_integer(value: Any, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} debe ser un entero positivo.")
