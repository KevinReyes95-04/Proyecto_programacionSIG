from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.nodes import (
    postprocess_mining_binary_map,
    validate_mining_binary_postprocessing_config,
)
from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.pipeline import (
    create_pipeline,
)


def _params(workdir: Path, **overrides):
    params = {
        "classification_map": (workdir / "classification.tif").as_posix(),
        "class_label": "Mineria",
        "negative_label": "No Mineria",
        "class_value": 1,
        "negative_value": 0,
        "class_nodata": 255,
        "min_area_ha": 0.02,
        "connectivity": 4,
        "all_touched": False,
        "outputs": {
            "postprocessed_classification_map": (workdir / "postprocessed.tif").as_posix(),
            "polygons": (workdir / "polygons.geojson").as_posix(),
            "polygon_layer": "mining_binary_polygons",
            "polygon_summary_csv": (workdir / "polygons.csv").as_posix(),
        },
        "map": {
            "output_path": (workdir / "map.png").as_posix(),
        },
    }
    return params | overrides


def test_postprocess_mining_binary_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 4


def test_mining_binary_map_postprocessing_config_is_validated():
    workdir = _workspace_tmp()
    config = validate_mining_binary_postprocessing_config(_params(workdir))

    assert config["class_label"] == "Mineria"
    assert config["min_area_ha"] == 0.02
    assert config["connectivity"] == 4


def test_mining_binary_map_postprocessing_rejects_invalid_connectivity():
    workdir = _workspace_tmp()
    params = _params(workdir, connectivity=6)

    with pytest.raises(ValueError, match="connectivity"):
        validate_mining_binary_postprocessing_config(params)


def test_postprocess_mining_binary_map_filters_small_patches():
    workdir = _workspace_tmp()
    _write_classification_map(workdir / "classification.tif")

    metadata = postprocess_mining_binary_map(_params(workdir))

    assert Path(metadata["postprocessed_classification_map"]).exists()
    assert Path(metadata["polygons"]).exists()
    assert Path(metadata["polygon_summary_csv"]).exists()
    assert metadata["original_patches"] == 2
    assert metadata["kept_patches"] == 1
    assert metadata["removed_patches"] == 1
    assert metadata["kept_mining_pixels"] == 3


def _write_classification_map(path: Path) -> None:
    profile = {
        "driver": "GTiff",
        "height": 4,
        "width": 4,
        "count": 1,
        "dtype": "uint8",
        "nodata": 255,
        "transform": from_origin(500000, 900000, 10, 10),
    }
    data = np.array(
        [
            [1, 1, 0, 1],
            [1, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 255],
        ],
        dtype="uint8",
    )
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(data, 1)


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_postprocess_mining_binary_map") / uuid4().hex
    path.mkdir(parents=True)
    return path
