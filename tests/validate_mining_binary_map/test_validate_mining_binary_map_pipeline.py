import pandas as pd
import pytest

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import (
    build_mining_binary_map_validation_metadata,
    validate_mining_binary_map_validation_params,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.pipeline import (
    create_pipeline,
)


def _params(**overrides):
    params = {
        "label_column": "Cobertura",
        "target_column": "target",
        "prediction_column": "predicted_target",
        "positive_label": "Mineria",
        "negative_label": "No Mineria",
        "coordinate_columns": {
            "longitude": "x",
            "latitude": "y",
            "source_crs": "EPSG:4326",
        },
    }
    return params | overrides


def test_validate_mining_binary_map_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 5


def test_mining_binary_map_validation_config_is_validated():
    config = validate_mining_binary_map_validation_params(_params())

    assert config["positive_label"] == "Mineria"
    assert config["coordinate_columns"]["longitude"] == "x"


def test_mining_binary_map_validation_config_rejects_missing_crs():
    params = _params(coordinate_columns={"longitude": "x", "latitude": "y"})

    with pytest.raises(ValueError, match="source_crs"):
        validate_mining_binary_map_validation_params(params)


def test_mining_binary_map_validation_metadata_counts_errors():
    predictions = pd.DataFrame(
        {
            "target": ["Mineria", "Mineria", "No Mineria"],
            "predicted_target": ["Mineria", "No Mineria", "Mineria"],
        }
    )

    metadata = build_mining_binary_map_validation_metadata(
        testing_predictions=predictions,
        classification_points_metadata={"output_path": "a.png"},
        probability_points_metadata={"output_path": "b.png"},
        testing_errors_metadata={"output_path": "c.png"},
        params=_params(),
    )

    assert metadata["false_negatives"] == 1
    assert metadata["false_positives"] == 1
