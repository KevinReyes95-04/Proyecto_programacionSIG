from pathlib import Path

import pytest

from centromonitoreo_mineria.pipelines.download_sentinel2.nodes import (
    validate_sentinel2_download_config,
)
from centromonitoreo_mineria.pipelines.download_sentinel2.pipeline import (
    create_pipeline,
)
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.drive_export import (
    build_drive_export_params,
    params_for_band_export,
)


BBOX = [-74.2, 4.5, -74.0, 4.8]
SERVICE_ACCOUNT_KEY = Path(__file__).with_name("service-account.json")


def _gee_params(**overrides):
    params = {
        "project": "programacionsig",
        "auth_method": "oauth",
        "authenticate": False,
        "auth_mode": "localhost",
        "adc_scopes": [
            "https://www.googleapis.com/auth/earthengine",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    }
    return params | overrides


def _sentinel2_params(**overrides):
    params = {
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "roi": {"source": "bbox", "bbox": BBOX},
        "start_date": "2025-08-01",
        "end_date": "2025-08-31",
        "cloud_cover_max": 10,
        "cloud_mask": True,
        "cloud_mask_method": "qa60",
        "cloud_mask_scl_classes": [3, 8, 9, 10],
        "composite_method": "median",
        "bands": [
            "B1",
            "B2",
            "B3",
            "B4",
            "B5",
            "B6",
            "B7",
            "B8",
            "B8A",
            "B9",
            "B11",
            "B12",
        ],
        "scale": 10,
        "drive_export": {
            "folder": "centromonitoreo_mineria",
            "file_name_prefix": "Sentinel2",
            "description": "Sentinel2",
            "file_format": "GeoTIFF",
            "file_per_band": True,
            "band_file_name_template": "{file_name_prefix}_{band}_Masked",
            "band_description_template": "{description}_{band}_Masked",
            "align_to_reference_band": True,
            "reference_band": "B2",
            "max_pixels": 10_000_000_000,
        },
    }
    return params | overrides


def test_download_sentinel2_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 5


def test_sentinel2_download_config_is_validated_and_grouped():
    config = validate_sentinel2_download_config(
        params_gee=_gee_params(),
        params_sentinel2_download=_sentinel2_params(),
    )

    assert config["gee"]["project"] == "programacionsig"
    assert config["gee"]["auth_method"] == "oauth"
    assert config["sentinel2_download"]["roi"]["source"] == "bbox"
    assert config["sentinel2_download"]["cloud_mask"] is True
    assert config["sentinel2_download"]["cloud_mask_method"] == "qa60"
    assert config["sentinel2_download"]["bands"] == [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B8A",
        "B9",
        "B11",
        "B12",
    ]


def test_sentinel2_download_config_accepts_service_account():
    config = validate_sentinel2_download_config(
        params_gee=_gee_params(
            auth_method="service_account",
            service_account_email="gee-runner@programacionsig.iam.gserviceaccount.com",
            service_account_key_path=str(SERVICE_ACCOUNT_KEY),
        ),
        params_sentinel2_download=_sentinel2_params(),
    )

    assert config["gee"]["auth_method"] == "service_account"
    assert config["gee"]["service_account_key_path"] == str(SERVICE_ACCOUNT_KEY)


@pytest.mark.parametrize(
    ("gee_overrides", "download_overrides", "match"),
    [
        ({"auth_method": "token"}, {}, "auth_method"),
        ({}, {"roi": {"source": "wkt", "bbox": BBOX}}, "roi.source"),
        ({}, {"cloud_cover_max": 101}, "cloud_cover_max"),
        ({}, {"cloud_mask": "yes"}, "cloud_mask"),
        ({}, {"bands": ["B2", "B10"]}, "B10"),
    ],
)
def test_sentinel2_download_config_rejects_invalid_values(
    gee_overrides, download_overrides, match
):
    with pytest.raises(ValueError, match=match):
        validate_sentinel2_download_config(
            params_gee=_gee_params(**gee_overrides),
            params_sentinel2_download=_sentinel2_params(**download_overrides),
        )


def test_drive_export_params_are_built_from_configuration():
    params = build_drive_export_params(
        image="image",
        region={"type": "Polygon"},
        params={
            "scale": 20,
            "crs": "EPSG:32618",
            "drive_export": _sentinel2_params()["drive_export"]
            | {
                "shard_size": 256,
                "file_dimensions": [4096, 4096],
                "skip_empty_tiles": True,
                "cloud_optimized": True,
                "priority": 100,
            },
        },
    )

    expected = {
        "image": "image",
        "folder": "centromonitoreo_mineria",
        "fileNamePrefix": "Sentinel2",
        "description": "Sentinel2",
        "fileFormat": "GeoTIFF",
        "fileDimensions": (4096, 4096),
        "formatOptions": {"cloudOptimized": True},
    }
    assert {key: params[key] for key in expected} == expected


def test_band_export_params_are_built_from_configuration():
    params = _sentinel2_params()
    band_params = params_for_band_export(params=params, band="B4")

    assert band_params["bands"] == ["B4"]
    assert band_params["drive_export"]["file_name_prefix"] == "Sentinel2_B4_Masked"
    assert band_params["drive_export"]["description"] == "Sentinel2_B4_Masked"
