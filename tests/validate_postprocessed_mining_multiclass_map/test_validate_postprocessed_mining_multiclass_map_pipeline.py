from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin

from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_multiclass_map.nodes import (
    build_postprocessed_mining_multiclass_point_validation,
    validate_postprocessed_mining_multiclass_map_validation_config,
)
from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_multiclass_map.pipeline import (
    create_pipeline,
)


def test_validate_postprocessed_mining_multiclass_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 6


def test_postprocessed_mining_multiclass_validation_config_is_validated():
    config = validate_postprocessed_mining_multiclass_map_validation_config(_params())

    assert config["label_column"] == "Cobertura"
    assert config["class_labels"] == ["Bosque Natural", "Mineria"]


def test_postprocessed_mining_multiclass_point_validation_samples_raster():
    workdir = _workspace_tmp()
    raster_path = workdir / "postprocessed.tif"
    _write_classification_map(raster_path)
    points = pd.DataFrame({"x": [0.5, 1.5, 2.5], "y": [2.5, 2.5, 0.5], "Cobertura": ["Bosque Natural", "Mineria", "Mineria"]})

    result = build_postprocessed_mining_multiclass_point_validation(
        points,
        {"postprocessing": {"postprocessed_classification_map": raster_path.as_posix()}},
        _params(),
    )

    assert result["predicted_map_class"].tolist() == ["Bosque Natural", "Mineria", None]
    assert result["validation_status"].tolist() == ["correcto", "correcto", "sin_datos"]


def _params():
    return {
        "label_column": "Cobertura",
        "prediction_column": "predicted_map_class",
        "class_labels": ["Bosque Natural", "Mineria"],
        "class_values": {"Bosque Natural": 1, "Mineria": 3},
        "coordinate_columns": {"longitude": "x", "latitude": "y", "source_crs": "EPSG:9377"},
    }


def _write_classification_map(path: Path) -> None:
    profile = {
        "driver": "GTiff",
        "height": 3,
        "width": 3,
        "count": 1,
        "dtype": "uint8",
        "nodata": 255,
        "crs": "EPSG:9377",
        "transform": from_origin(0, 3, 1, 1),
    }
    data = np.array([[1, 3, 1], [1, 3, 3], [1, 1, 255]], dtype="uint8")
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data, 1)


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_validate_postprocessed_mining_multiclass_map") / uuid4().hex
    path.mkdir(parents=True)
    return path

