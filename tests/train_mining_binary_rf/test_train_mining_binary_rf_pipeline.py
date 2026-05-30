import pandas as pd
import pytest

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    build_binary_dataset,
    predict_random_forest,
)
from centromonitoreo_mineria.pipelines.train_mining_binary_rf.nodes import (
    build_mining_binary_datasets,
    validate_mining_binary_random_forest_config,
)
from centromonitoreo_mineria.pipelines.train_mining_binary_rf.pipeline import (
    create_pipeline,
)


def _params(**overrides):
    params = {
        "label_column": "Cobertura",
        "positive_label": "Mineria",
        "negative_label": "No Mineria",
        "negative_source_labels": ["Bosque Natural", "Cuerpos de Agua", "Nubes"],
        "target_column": "target",
        "prediction_column": "predicted_target",
        "probability_column": "probability_mineria",
        "classification_threshold": 0.4,
        "feature_columns": ["B4", "B8", "NDVI"],
        "random_forest": {
            "n_estimators": 10,
            "random_state": 42,
            "class_weight": "balanced",
        },
    }
    return params | overrides


def test_train_mining_binary_rf_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 9


def test_mining_binary_random_forest_config_is_validated():
    config = validate_mining_binary_random_forest_config(_params())

    assert config["positive_label"] == "Mineria"
    assert "Nubes" in config["negative_source_labels"]
    assert config["feature_columns"] == ["B4", "B8", "NDVI"]


def test_binary_dataset_maps_nubes_to_no_mineria():
    table = pd.DataFrame(
        {
            "Cobertura": ["Mineria", "Nubes", "Bosque Natural"],
            "B4": [0.1, 0.8, 0.2],
            "B8": [0.2, 0.7, 0.6],
            "NDVI": [0.3, -0.1, 0.5],
        }
    )

    dataset = build_binary_dataset(table=table, params=_params(), dataset_name="test")

    assert dataset["y"].tolist() == ["Mineria", "No Mineria", "No Mineria"]
    assert dataset["X"].shape == (3, 3)


def test_build_mining_binary_datasets_returns_training_and_testing_sets():
    training = pd.DataFrame(
        {
            "Cobertura": ["Mineria", "Nubes"],
            "B4": [0.1, 0.8],
            "B8": [0.2, 0.7],
            "NDVI": [0.3, -0.1],
        }
    )
    testing = pd.DataFrame(
        {
            "Cobertura": ["Bosque Natural"],
            "B4": [0.2],
            "B8": [0.6],
            "NDVI": [0.5],
        }
    )

    training_dataset, testing_dataset = build_mining_binary_datasets(
        training_sentinel2_features=training,
        testing_sentinel2_features=testing,
        mining_binary_random_forest_config=_params(),
    )

    assert training_dataset["name"] == "training_sentinel2_features"
    assert testing_dataset["name"] == "testing_sentinel2_features"
    assert testing_dataset["y"].tolist() == ["No Mineria"]


def test_binary_dataset_rejects_unconfigured_class():
    table = pd.DataFrame(
        {
            "Cobertura": ["Mineria", "Ciudad"],
            "B4": [0.1, 0.8],
            "B8": [0.2, 0.7],
            "NDVI": [0.3, -0.1],
        }
    )

    with pytest.raises(ValueError, match="clases no configuradas"):
        build_binary_dataset(table=table, params=_params(), dataset_name="test")


def test_predict_random_forest_uses_configured_probability_threshold():
    class Model:
        classes_ = ["No Mineria", "Mineria"]

        def predict_proba(self, X):
            return [[0.65, 0.35], [0.55, 0.45]]

    testing_dataset = {
        "source": pd.DataFrame({"Cobertura": ["Nubes", "Mineria"]}),
        "X": pd.DataFrame({"B4": [0.1, 0.2], "B8": [0.3, 0.4], "NDVI": [0.5, 0.6]}),
    }

    predictions = predict_random_forest(
        model=Model(),
        testing_dataset=testing_dataset,
        params=_params(classification_threshold=0.4),
    )

    assert predictions["predicted_target"].tolist() == ["No Mineria", "Mineria"]
