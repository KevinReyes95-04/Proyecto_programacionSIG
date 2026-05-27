import json
from pathlib import Path
from uuid import uuid4

import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    build_postprocessed_class_summary,
    build_postprocessed_point_validation_table,
    validate_postprocessed_mining_map_validation_params,
)
from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_map.pipeline import (
    create_pipeline,
)


def _params(workdir: Path):
    return {
        "label_column": "Cobertura",
        "positive_label": "Mineria",
        "negative_label": "No Mineria",
        "coordinate_columns": {"longitude": "x", "latitude": "y"},
        "outputs": {
            "point_validation": (workdir / "point_validation.csv").as_posix(),
            "class_summary": (workdir / "class_summary.csv").as_posix(),
        },
    }


def test_validate_postprocessed_mining_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 5


def test_postprocessed_mining_map_validation_config_is_validated():
    workdir = _workspace_tmp()
    config = validate_postprocessed_mining_map_validation_params(_params(workdir))

    assert config["positive_label"] == "Mineria"
    assert config["coordinate_columns"]["longitude"] == "x"


def test_postprocessed_point_validation_table_assigns_binary_statuses():
    workdir = _workspace_tmp()
    polygon_path = workdir / "polygons.geojson"
    _write_polygon(polygon_path)
    metadata = _metadata(polygon_path)
    training = pd.DataFrame(
        {
            "sample_id": ["tr_1", "tr_2"],
            "Cobertura": ["Mineria", "Bosque Natural"],
            "x": [0.5, 3.0],
            "y": [0.5, 3.0],
        }
    )
    testing = pd.DataFrame(
        {
            "sample_id": ["te_1", "te_2"],
            "Cobertura": ["Mineria", "Nubes"],
            "x": [3.0, 0.5],
            "y": [3.0, 0.5],
        }
    )

    table = build_postprocessed_point_validation_table(training, testing, metadata, _params(workdir))
    summary = build_postprocessed_class_summary(table, _params(workdir))

    assert table["validation_status"].tolist() == ["TP", "TN", "FN", "FP"]
    assert int(summary["total_points"].sum()) == 4
    assert int(summary["points_inside_mining_polygon"].sum()) == 2


def _write_polygon(path: Path) -> None:
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"polygon_id": 1, "class_label": "Mineria"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                },
            }
        ],
    }
    path.write_text(json.dumps(geojson), encoding="utf-8")


def _metadata(polygon_path: Path):
    return {
        "postprocessing": {
            "polygons": polygon_path.as_posix(),
            "postprocessed_classification_map": (polygon_path.parent / "map.tif").as_posix(),
            "kept_area_ha": 1.0,
            "raster": {"crs": None},
        }
    }


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_validate_postprocessed_mining_map") / uuid4().hex
    path.mkdir(parents=True)
    return path
