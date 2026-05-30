from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_prediction import (
    predict_mining_map_rasters,
    validate_mining_binary_map_prediction_params,
)
from centromonitoreo_mineria.pipelines.predict_mining_binary_map.pipeline import (
    create_pipeline,
)


class FakeMiningModel:
    classes_ = np.array(["No Mineria", "Mineria"])

    def predict(self, matrix):
        return np.where(matrix.iloc[:, 0] > 0.3, "Mineria", "No Mineria")

    def predict_proba(self, matrix):
        assert list(matrix.columns) == ["B1", "B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "BSI"]
        positive = np.where(matrix.iloc[:, 0] > 0.3, 0.8, 0.2)
        return np.column_stack([1 - positive, positive])


def _params(tmp_path: Path, **overrides):
    params = {
        "raster_dir": tmp_path.as_posix(),
        "band_file_template": "Sentinel2_{band}_Masked.tif",
        "reference_band": "B2",
        "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B11", "B12"],
        "feature_columns": ["B1", "B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "BSI"],
        "positive_label": "Mineria",
        "negative_label": "No Mineria",
        "class_values": {"No Mineria": 0, "Mineria": 1},
        "class_nodata": 255,
        "probability_nodata": -9999.0,
        "classification_threshold": 0.4,
        "apply_reflectance_scale": False,
        "reflectance_scale_factor": 0.0001,
        "window_size": 2,
        "outputs": {
            "classification_map": (tmp_path / "classification.tif").as_posix(),
            "probability_map": (tmp_path / "probability.tif").as_posix(),
        },
    }
    return params | overrides


def test_predict_mining_binary_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 4


def test_mining_binary_map_prediction_config_is_validated():
    workdir = _workspace_tmp()
    config = validate_mining_binary_map_prediction_params(_params(workdir))

    assert config["positive_label"] == "Mineria"
    assert config["reference_band"] == "B2"
    assert config["classification_threshold"] == 0.4


def test_mining_binary_map_prediction_rejects_missing_output():
    workdir = _workspace_tmp()
    params = _params(workdir, outputs={"classification_map": "x.tif"})

    with pytest.raises(ValueError, match="probability_map"):
        validate_mining_binary_map_prediction_params(params)


def test_predict_mining_map_rasters_writes_outputs():
    workdir = _workspace_tmp()
    _write_test_bands(workdir)
    metadata = predict_mining_map_rasters(model=FakeMiningModel(), params=_params(workdir))

    assert Path(metadata["classification_map"]).exists()
    assert Path(metadata["probability_map"]).exists()
    assert metadata["class_counts"]["Mineria"] == 2
    assert metadata["class_counts"]["No Mineria"] == 2


def _write_test_bands(tmp_path: Path) -> None:
    profile = {
        "driver": "GTiff",
        "height": 2,
        "width": 2,
        "count": 1,
        "dtype": "float32",
        "transform": from_origin(-75, 8, 0.01, 0.01),
    }
    values = np.array([[0.1, 0.4], [0.2, 0.5]], dtype="float32")
    for band in ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B11", "B12"]:
        with rasterio.open(tmp_path / f"Sentinel2_{band}_Masked.tif", "w", **profile) as dataset:
            dataset.write(values, 1)


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_predict_mining_binary_map") / uuid4().hex
    path.mkdir(parents=True)
    return path
