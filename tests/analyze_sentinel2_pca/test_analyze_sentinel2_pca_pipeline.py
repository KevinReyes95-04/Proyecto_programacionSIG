import pandas as pd
import pytest

from centromonitoreo_mineria.pipelines.analyze_sentinel2_pca.nodes.validate_sentinel2_pca_config import (
    validate_sentinel2_pca_config,
)
from centromonitoreo_mineria.pipelines.analyze_sentinel2_pca.pipeline import (
    create_pipeline,
)
from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    build_pca_dataset,
    explained_variance_table,
    fit_pca_model,
    transform_pca_dataset,
)


def _params(**overrides):
    params = {
        "label_column": "Cobertura",
        "split_column": "split",
        "n_components": 2,
        "random_state": 42,
        "columns_to_keep": ["sample_id", "Cobertura"],
        "feature_columns": ["B4", "B8", "NDVI"],
    }
    return params | overrides


def _table():
    return pd.DataFrame(
        {
            "sample_id": ["a", "b", "c", "d"],
            "Cobertura": ["Mineria", "Nubes", "Vegetacion", "Suelo Desnudo"],
            "B4": [0.1, 0.8, 0.2, 0.5],
            "B8": [0.2, 0.7, 0.6, 0.4],
            "NDVI": [0.3, -0.1, 0.5, 0.0],
        }
    )


def test_analyze_sentinel2_pca_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 11


def test_sentinel2_pca_config_is_validated():
    config = validate_sentinel2_pca_config(_params())

    assert config["label_column"] == "Cobertura"
    assert config["n_components"] == 2
    assert config["feature_columns"] == ["B4", "B8", "NDVI"]


def test_sentinel2_pca_config_rejects_invalid_components():
    with pytest.raises(ValueError, match="n_components"):
        validate_sentinel2_pca_config(_params(n_components=0))


def test_pca_model_transforms_dataset_and_explains_variance():
    params = _params()
    dataset = build_pca_dataset(table=_table(), params=params, dataset_name="training")
    model = fit_pca_model(training_dataset=dataset, params=params)
    scores = transform_pca_dataset(model=model, dataset=dataset, params=params)
    explained = explained_variance_table(model=model)

    assert ["PC1", "PC2"] == [column for column in scores.columns if column.startswith("PC")]
    assert "split" in scores.columns
    assert len(explained) == 2
    assert explained["explained_variance_ratio"].sum() <= 1.0
