from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from sklearn.ensemble import RandomForestClassifier


# Funcion para predecir y guardar rasters multiclase.
def predict_mining_multiclass_map_rasters(
    mining_multiclass_random_forest_model: RandomForestClassifier,
    mining_multiclass_map_prediction_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_multiclass_map_prediction_config
    raster_paths = _band_paths(params)
    _ensure_rasters_exist(raster_paths)
    class_path = Path(params["outputs"]["classification_map"])
    probability_path = Path(params["outputs"]["probability_max_map"])
    class_path.parent.mkdir(parents=True, exist_ok=True)
    probability_path.parent.mkdir(parents=True, exist_ok=True)

    class_counts = {label: 0 for label in params["class_values"]}
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
            predicted, probabilities, valid_mask = _predict_window(mining_multiclass_random_forest_model, features, params)
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
        "probability_max_map": probability_path.as_posix(),
        "feature_columns": params["feature_columns"],
        "class_counts": class_counts,
        "max_probability": _probability_summary(probabilities),
        "raster": {
            "shape": shape,
            "crs": crs,
            "bounds": {"left": bounds.left, "bottom": bounds.bottom, "right": bounds.right, "top": bounds.top},
        },
    }


# Funcion para construir rutas de bandas locales.
def _band_paths(params: dict[str, Any]) -> dict[str, Path]:
    raster_dir = Path(params["raster_dir"])
    template = params["band_file_template"]
    paths = {band: raster_dir / template.format(band=band) for band in params["bands"]}
    for feature, file_name in params.get("topographic_rasters", {}).items():
        path = Path(file_name)
        paths[feature] = path if path.is_absolute() else raster_dir / path
    return paths


# Funcion para validar que existan las bandas requeridas.
def _ensure_rasters_exist(raster_paths: dict[str, Path]) -> None:
    missing = [path.as_posix() for path in raster_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"No se encontraron las bandas Sentinel-2 locales: {missing}")


# Funcion para validar que todas las bandas compartan la misma grilla.
def _validate_raster_grid(sources: dict[str, Any]) -> None:
    reference = next(iter(sources.values()))
    for band, source in sources.items():
        if source.shape != reference.shape or source.transform != reference.transform or source.crs != reference.crs:
            raise ValueError(f"La banda {band} no coincide en grilla, transformacion o CRS.")


# Funcion para leer bandas de una ventana raster.
def _read_bands(sources: dict[str, Any], window: Window, params: dict[str, Any]) -> dict[str, np.ndarray]:
    spectral_bands = set(params.get("bands", []))
    spectral_scale = params.get("reflectance_scale_factor", 0.0001) if params.get("apply_reflectance_scale", True) else 1.0
    return {
        band: source.read(1, window=window, masked=True).astype("float32").filled(np.nan)
        * (spectral_scale if band in spectral_bands else 1.0)
        for band, source in sources.items()
    }


# Funcion para construir las variables espectrales requeridas por el modelo.
def _feature_stack(bands: dict[str, np.ndarray], feature_columns: list[str]) -> dict[str, np.ndarray]:
    features = {**bands}
    if "NDVI" in feature_columns:
        features["NDVI"] = _normalized_difference(bands["B8"], bands["B4"])
    if "MSAVI" in feature_columns:
        features["MSAVI"] = _msavi(bands["B8"], bands["B4"])
    if "NDWI" in feature_columns:
        features["NDWI"] = _normalized_difference(bands["B3"], bands["B8"])
    if "BSI" in feature_columns:
        features["BSI"] = _safe_divide((bands["B11"] + bands["B4"]) - (bands["B8"] + bands["B2"]), (bands["B11"] + bands["B4"]) + (bands["B8"] + bands["B2"]))
    if "MBSI" in feature_columns:
        features["MBSI"] = _normalized_difference(bands["B11"], bands["B4"])
    if "NDSI" in feature_columns:
        features["NDSI"] = _normalized_difference(bands["B11"], bands["B3"])
    if "MSWI" in feature_columns:
        features["MSWI"] = _normalized_difference(bands["B12"], bands["B4"])
    if "NDBI" in feature_columns:
        features["NDBI"] = _normalized_difference(bands["B11"], bands["B8"])
    return {feature: features[feature] for feature in feature_columns}


# Funcion para predecir una ventana raster.
def _predict_window(model: Any, features: dict[str, np.ndarray], params: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    feature_arrays = [features[column] for column in params["feature_columns"]]
    valid_mask = np.logical_and.reduce([np.isfinite(array) for array in feature_arrays])
    shape = feature_arrays[0].shape
    class_array = np.full(shape, params.get("class_nodata", 255), dtype="uint8")
    probability_array = np.full(shape, params.get("probability_nodata", -9999.0), dtype="float32")
    if not valid_mask.any():
        return class_array, probability_array, valid_mask

    matrix = pd.DataFrame({column: features[column][valid_mask] for column in params["feature_columns"]}, columns=params["feature_columns"])
    labels = model.predict(matrix)
    class_array[valid_mask] = np.array([_class_value(label, params) for label in labels], dtype="uint8")
    if hasattr(model, "predict_proba"):
        probability_array[valid_mask] = model.predict_proba(matrix).max(axis=1).astype("float32")
    return class_array, probability_array, valid_mask


# Funcion para crear el perfil del raster categórico.
def _classification_profile(reference: Any, params: dict[str, Any]) -> dict[str, Any]:
    profile = reference.profile.copy()
    profile.update(driver="GTiff", count=1, dtype="uint8", nodata=params.get("class_nodata", 255), compress="lzw", BIGTIFF="IF_SAFER")
    return profile


# Funcion para crear el perfil del raster de probabilidad maxima.
def _probability_profile(reference: Any, params: dict[str, Any]) -> dict[str, Any]:
    profile = reference.profile.copy()
    profile.update(driver="GTiff", count=1, dtype="float32", nodata=params.get("probability_nodata", -9999.0), compress="lzw", BIGTIFF="IF_SAFER")
    return profile


# Funcion para dividir el raster en ventanas de procesamiento.
def _windows(width: int, height: int, window_size: int) -> list[Window]:
    return [
        Window(col, row, min(window_size, width - col), min(window_size, height - row))
        for row in range(0, height, window_size)
        for col in range(0, width, window_size)
    ]


# Funcion para calcular diferencia normalizada.
def _normalized_difference(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return _safe_divide(first - second, first + second)


# Funcion para calcular MSAVI.
def _msavi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    radicand = np.maximum(np.power(2 * nir + 1, 2) - 8 * (nir - red), 0)
    return (2 * nir + 1 - np.sqrt(radicand)) / 2


# Funcion para dividir evitando errores por cero.
def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(numerator, denominator, out=np.full_like(numerator, np.nan, dtype="float32"), where=denominator != 0)


# Funcion para convertir una etiqueta en valor raster.
def _class_value(label: str, params: dict[str, Any]) -> int:
    return int(params.get("class_values", {}).get(label, params.get("class_nodata", 255)))


# Funcion para contar pixeles por clase.
def _update_class_counts(class_counts: dict[str, int], class_array: np.ndarray, params: dict[str, Any]) -> None:
    for label, value in params.get("class_values", {}).items():
        class_counts[label] = class_counts.get(label, 0) + int(np.sum(class_array == value))


# Funcion para resumir probabilidades maximas.
def _probability_summary(values: np.ndarray) -> dict[str, float | int | None]:
    if values.size == 0:
        return {"count": 0, "min": None, "max": None, "mean": None}
    return {"count": int(values.size), "min": float(values.min()), "max": float(values.max()), "mean": float(values.mean())}
