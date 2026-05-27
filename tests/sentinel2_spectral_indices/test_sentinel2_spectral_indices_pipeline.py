import pytest

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_spectral_indices import (
    output_bands,
)
from centromonitoreo_mineria.pipelines.sentinel2_spectral_indices.nodes.validate_sentinel2_spectral_indices_config import (
    validate_sentinel2_spectral_indices_config,
)
from centromonitoreo_mineria.pipelines.sentinel2_spectral_indices.pipeline import (
    create_pipeline,
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
        "visualization": {
            "enabled": True,
            "default_style": {
                "min": -1,
                "max": 1,
                "palette": ["#000000", "#ffffff"],
            },
        },
        "drive_export": {
            "folder": "centromonitoreo_mineria",
            "file_name_prefix": "sentinel2_spectral_indices_test",
            "description": "sentinel2_spectral_indices_test",
            "file_format": "GeoTIFF",
            "align_to_reference_band": True,
            "reference_band": "B2",
            "max_pixels": 10_000_000_000,
        },
    }
    return params | overrides


def test_sentinel2_spectral_indices_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 9


def test_sentinel2_spectral_indices_config_is_validated_and_grouped():
    config = validate_sentinel2_spectral_indices_config(
        params_gee=_gee_params(),
        params_sentinel2_spectral_indices=_spectral_indices_params(),
    )

    params = config["sentinel2_spectral_indices"]
    assert config["gee"]["project"] == "programacionsig"
    assert params["indices"]["NDVI"]["formula"] == "normalized_difference"
    assert output_bands(params) == ["B2", "B3", "B4", "B8", "B11", "B12", "NDVI", "BSI"]


def test_sentinel2_spectral_indices_config_rejects_unknown_band():
    params = _spectral_indices_params(
        indices={
            "BROKEN": {
                "enabled": True,
                "formula": "normalized_difference",
                "bands": {"first": "B99", "second": "B4"},
            }
        }
    )

    with pytest.raises(ValueError, match="bandas no configuradas"):
        validate_sentinel2_spectral_indices_config(
            params_gee=_gee_params(),
            params_sentinel2_spectral_indices=params,
        )
