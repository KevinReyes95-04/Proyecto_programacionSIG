from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from centromonitoreo_mineria.pipelines.postprocess_mining_multiclass_map.nodes import (
    postprocess_mining_multiclass_map,
    validate_mining_multiclass_postprocessing_config,
)
from centromonitoreo_mineria.pipelines.postprocess_mining_multiclass_map.pipeline import (
    create_pipeline,
)


def test_postprocess_mining_multiclass_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 4


def test_mining_multiclass_postprocessing_config_is_validated():
    workdir = _workspace_tmp()
    config = validate_mining_multiclass_postprocessing_config(_params(workdir))

    assert config["class_nodata"] == 255
    assert config["majority_filter"]["size"] == 3


def test_mining_multiclass_postprocessing_rejects_even_filter_size():
    workdir = _workspace_tmp()
    params = _params(workdir, majority_filter={"enabled": True, "size": 4, "iterations": 1})

    with pytest.raises(ValueError, match="size"):
        validate_mining_multiclass_postprocessing_config(params)


def test_postprocess_mining_multiclass_map_smooths_isolated_pixels():
    workdir = _workspace_tmp()
    _write_classification_map(workdir / "classification.tif")

    metadata, summary = postprocess_mining_multiclass_map(_params(workdir))

    with rasterio.open(metadata["postprocessed_classification_map"]) as dataset:
        postprocessed = dataset.read(1)
    assert Path(metadata["postprocessed_classification_map"]).exists()
    assert postprocessed[1, 1] == 1
    assert postprocessed[4, 3] == 255
    assert metadata["changed_pixels"] > 0
    assert len(summary) == 6


def _params(workdir: Path, **overrides):
    params = {
        "classification_map": (workdir / "classification.tif").as_posix(),
        "class_values": {
            "Bosque Natural": 1,
            "Cuerpos de Agua": 2,
            "Mineria": 3,
            "Nubes": 4,
            "Suelo Desnudo": 5,
            "Vegetacion": 6,
        },
        "class_nodata": 255,
        "majority_filter": {"enabled": True, "size": 3, "iterations": 1},
        "outputs": {
            "postprocessed_classification_map": (workdir / "postprocessed.tif").as_posix(),
            "class_summary_csv": (workdir / "summary.csv").as_posix(),
        },
        "visualization": {
            "output_path": (workdir / "map.png").as_posix(),
        },
    }
    return params | overrides


def _write_classification_map(path: Path) -> None:
    profile = {
        "driver": "GTiff",
        "height": 5,
        "width": 5,
        "count": 1,
        "dtype": "uint8",
        "nodata": 255,
        "transform": from_origin(500000, 900000, 10, 10),
    }
    data = np.array(
        [
            [1, 1, 1, 2, 2],
            [1, 3, 1, 2, 2],
            [1, 1, 1, 5, 5],
            [6, 6, 5, 5, 5],
            [6, 6, 5, 255, 5],
        ],
        dtype="uint8",
    )
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data, 1)


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_postprocess_mining_multiclass_map") / uuid4().hex
    path.mkdir(parents=True)
    return path

