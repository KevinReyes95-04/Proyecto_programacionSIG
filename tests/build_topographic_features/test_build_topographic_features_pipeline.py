import os
from importlib.util import find_spec
from pathlib import Path
from uuid import uuid4

import numpy as np

rasterio_spec = find_spec("rasterio")
proj_dir = (Path(rasterio_spec.origin).parent / "proj_data").as_posix()
os.environ["PROJ_DATA"] = proj_dir
os.environ["PROJ_LIB"] = proj_dir

import rasterio
from rasterio.transform import from_origin

from centromonitoreo_mineria.pipelines.build_topographic_features.nodes import (
    build_topographic_features,
    validate_topographic_features_config,
)
from centromonitoreo_mineria.pipelines.build_topographic_features.pipeline import create_pipeline


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


def _sentinel2_download_params():
    return {"roi": {"source": "bbox", "bbox": [-74.2, 4.5, -74.0, 4.8]}}


def _topographic_params(workdir: Path):
    return {
        "dem_asset": "USGS/SRTMGL1_003",
        "elevation_band": "elevation",
        "output_bands": {"elevation": "DEM", "slope": "SLOPE"},
        "target_crs": "EPSG:9377",
        "download": {
            "enabled": False,
            "output_dir": workdir.as_posix(),
            "source_file": "Topography_DEM_SLOPE_raw.tif",
            "scale": 30,
        },
        "alignment": {
            "reference_raster": (workdir / "Sentinel2_B2_Masked.tif").as_posix(),
            "output_file_template": "Topography_{band}.tif",
            "resampling": "bilinear",
            "nodata_value": -9999.0,
        },
    }


def test_build_topographic_features_pipeline_has_expected_node_count():
    assert len(create_pipeline().nodes) == 2


def test_topographic_features_config_is_validated():
    workdir = _workspace_tmp()
    config = validate_topographic_features_config(
        params_gee=_gee_params(),
        params_sentinel2_download=_sentinel2_download_params(),
        params_topographic_features=_topographic_params(workdir),
    )

    assert config["topographic_features"]["output_bands"] == {"elevation": "DEM", "slope": "SLOPE"}
    assert config["topographic_features"]["download"]["enabled"] is False


def test_build_topographic_features_aligns_local_rasters():
    workdir = _workspace_tmp()
    _write_reference_raster(workdir / "Sentinel2_B2_Masked.tif")
    _write_topographic_source(workdir / "Topography_DEM_SLOPE_raw.tif")

    metadata = build_topographic_features(
        {
            "gee": _gee_params(),
            "sentinel2_download": _sentinel2_download_params(),
            "topographic_features": _topographic_params(workdir),
        }
    )

    assert len(metadata["aligned_rasters"]) == 2
    assert (workdir / "Topography_DEM.tif").exists()
    assert (workdir / "Topography_SLOPE.tif").exists()


def _write_reference_raster(path: Path) -> None:
    profile = _profile(count=1)
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(np.ones((2, 2), dtype="float32"), 1)


def _write_topographic_source(path: Path) -> None:
    profile = _profile(count=2)
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(np.array([[100, 110], [120, 130]], dtype="float32"), 1)
        dataset.write(np.array([[2, 3], [4, 5]], dtype="float32"), 2)


def _profile(count: int) -> dict:
    return {
        "driver": "GTiff",
        "height": 2,
        "width": 2,
        "count": count,
        "dtype": "float32",
        "crs": "EPSG:9377",
        "transform": from_origin(4_900_000, 2_100_000, 10, 10),
    }


def _workspace_tmp() -> Path:
    path = Path("data/02_intermediate/test_build_topographic_features") / uuid4().hex
    path.mkdir(parents=True)
    return path
