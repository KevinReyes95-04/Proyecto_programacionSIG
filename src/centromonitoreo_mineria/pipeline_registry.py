from kedro.pipeline import Pipeline

from centromonitoreo_mineria.pipelines.analyze_sentinel2_pca.pipeline import (create_pipeline as analyze_sentinel2_pca_pipeline)
from centromonitoreo_mineria.pipelines.download_sentinel2.pipeline import (create_pipeline as download_sentinel2_pipeline)
from centromonitoreo_mineria.pipelines.extract_sentinel2_training_features.pipeline import (create_pipeline as extract_sentinel2_training_features_pipeline)
from centromonitoreo_mineria.pipelines.prepare_training_data.pipeline import (create_pipeline as prepare_training_data_pipeline)
from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.pipeline import (create_pipeline as postprocess_mining_binary_map_pipeline)
from centromonitoreo_mineria.pipelines.predict_mining_binary_map.pipeline import (create_pipeline as predict_mining_binary_map_pipeline)
from centromonitoreo_mineria.pipelines.sentinel2_spectral_indices.pipeline import (create_pipeline as sentinel2_spectral_indices_pipeline)
from centromonitoreo_mineria.pipelines.train_mining_binary_rf.pipeline import (create_pipeline as train_mining_binary_rf_pipeline)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.pipeline import (create_pipeline as validate_mining_binary_map_pipeline)
from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_map.pipeline import (create_pipeline as validate_postprocessed_mining_map_pipeline)


def register_pipelines() -> dict[str, Pipeline]:
    return {
        "analyze_sentinel2_pca": analyze_sentinel2_pca_pipeline(),
        "download_sentinel2": download_sentinel2_pipeline(),
        "extract_sentinel2_training_features": extract_sentinel2_training_features_pipeline(),
        "prepare_training_data": prepare_training_data_pipeline(),
        "postprocess_mining_binary_map": postprocess_mining_binary_map_pipeline(),
        "predict_mining_binary_map": predict_mining_binary_map_pipeline(),
        "sentinel2_spectral_indices": sentinel2_spectral_indices_pipeline(),
        "train_mining_binary_rf": train_mining_binary_rf_pipeline(),
        "validate_mining_binary_map": validate_mining_binary_map_pipeline(),
        "validate_postprocessed_mining_map": validate_postprocessed_mining_map_pipeline(),
        "__default__": download_sentinel2_pipeline() + prepare_training_data_pipeline(),
    }
