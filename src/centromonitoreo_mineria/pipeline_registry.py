from kedro.pipeline import Pipeline

from centromonitoreo_mineria.pipelines.download_sentinel2.pipeline import (
    create_pipeline as download_sentinel2_pipeline,
)
from centromonitoreo_mineria.pipelines.prepare_training_data.pipeline import (
    create_pipeline as prepare_training_data_pipeline,
)


def register_pipelines() -> dict[str, Pipeline]:
    return {
        "download_sentinel2": download_sentinel2_pipeline(),
        "prepare_training_data": prepare_training_data_pipeline(),
        "__default__": download_sentinel2_pipeline() + prepare_training_data_pipeline(),
    }
