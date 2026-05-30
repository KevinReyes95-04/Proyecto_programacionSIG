import pandas as pd
import pytest

from centromonitoreo_mineria.pipelines.extract_sentinel2_training_features.nodes import (
    validate_sentinel2_training_features_config,
)
from centromonitoreo_mineria.pipelines.extract_sentinel2_training_features.pipeline import (
    create_pipeline,
)
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_feature_extraction import (
    build_sentinel2_training_features_metadata,
)


def _gee_params():
    return {
        "project": "programacionsig",
        "auth_method": "oauth",
        "authenticate": False,
        "auth_mode": "localhost",
        "adc_scopes": [
            "https://www.googleapis.com/auth/earthengine",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    }


def _spectral_indices_params(**overrides):
    params = {
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "roi": {"source": "bbox", "bbox": [-74.2, 4.5, -74.0, 4.8]},
        "start_date": "2023-02-02",
        "end_date": "2023-02-03",
        "cloud_cover_max": 10,
        "cloud_mask": True,
        "cloud_mask_method": "qa60",
        "cloud_mask_scl_classes": [3, 8, 9, 10],
        "composite_method": "median",
        "bands": ["B2", "B3", "B4", "B8", "B11", "B12"],
        "scale": 10,
        "include_original_bands": True,
        "output_band_order": ["B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "BSI"],
        "indices": {
            "NDVI": {
                "enabled": True,
                "formula": "normalized_difference",
                "bands": {"first": "B8", "second": "B4"},
            },
            "BSI": {
                "enabled": True,
                "formula": "expression",
                "expression": "((swir1 + red) - (nir + blue)) / ((swir1 + red) + (nir + blue))",
                "bands": {"swir1": "B11", "red": "B4", "nir": "B8", "blue": "B2"},
            },
        },
        "local_tif_export": {
            "enabled": True,
            "input_dir": "data/04_feature/sentinel2_bands",
            "output_dir": "data/04_feature/sentinel2_bands",
            "source_band_template": "Sentinel2_{band}_Masked.tif",
            "index_file_template": "Sentinel2_{index}_Masked.tif",
        },
    }
    return params | overrides


def _training_features_params(**overrides):
    params = {
        "sentinel2_overrides": {"cloud_mask": False},
        "label_column": "Cobertura",
        "coordinate_columns": {
            "longitude": "x",
            "latitude": "y",
            "crs": "EPSG:4326",
        },
        "properties_to_keep": ["Cobertura", "x", "y"],
        "feature_columns": ["B2", "B3", "B4", "B8", "NDVI", "BSI"],
        "sample_scale": 10,
        "tile_scale": 4,
        "geometries": False,
        "drop_missing_features": True,
    }
    return params | overrides


def test_extract_sentinel2_training_features_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 4


def test_sentinel2_training_features_config_applies_overrides_and_validates_columns():
    config = validate_sentinel2_training_features_config(
        params_gee=_gee_params(),
        params_sentinel2_spectral_indices=_spectral_indices_params(),
        params_sentinel2_training_features=_training_features_params(),
    )

    assert config["gee"]["project"] == "programacionsig"
    assert config["sentinel2_spectral_indices"]["cloud_mask"] is False
    assert config["sentinel2_training_features"]["feature_columns"] == [
        "B2",
        "B3",
        "B4",
        "B8",
        "NDVI",
        "BSI",
    ]


def test_sentinel2_training_features_config_rejects_unknown_feature():
    with pytest.raises(ValueError, match="columnas no disponibles"):
        validate_sentinel2_training_features_config(
            params_gee=_gee_params(),
            params_sentinel2_spectral_indices=_spectral_indices_params(),
            params_sentinel2_training_features=_training_features_params(
                feature_columns=["B2", "BROKEN"]
            ),
        )


def test_sentinel2_training_features_metadata_counts_dropped_rows():
    source = pd.DataFrame(
        {
            "Cobertura": ["Mineria", "Vegetacion", "Mineria"],
            "x": [-74.1, -74.2, -74.3],
            "y": [7.9, 8.0, 8.1],
        }
    )
    features = pd.DataFrame(
        {
            "Cobertura": ["Mineria", "Vegetacion"],
            "x": [-74.1, -74.2],
            "y": [7.9, 8.0],
            "B2": [0.1, 0.2],
            "NDVI": [0.3, 0.4],
        }
    )
    config = {
        "sentinel2_training_features": _training_features_params(
            feature_columns=["B2", "NDVI"]
        ),
        "sentinel2_spectral_indices": _spectral_indices_params(),
    }

    metadata = build_sentinel2_training_features_metadata(
        training_labeled_points=source,
        testing_labeled_points=source.head(1),
        training_features=features,
        testing_features=features.head(1),
        config=config,
    )

    assert metadata["training"]["input_rows"] == 3
    assert metadata["training"]["output_rows"] == 2
    assert metadata["training"]["dropped_rows"] == 1
    assert metadata["feature_columns"] == ["B2", "NDVI"]
