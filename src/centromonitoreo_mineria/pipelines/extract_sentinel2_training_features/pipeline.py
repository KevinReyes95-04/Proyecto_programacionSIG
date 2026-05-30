from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.extract_sentinel2_training_features.nodes import (
    build_sentinel2_training_features_image,
    build_sentinel2_training_features_metadata,
    extract_sentinel2_features,
    validate_sentinel2_training_features_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for Sentinel-2 training feature tables."""
    return Pipeline(
        [
            node(
                func=validate_sentinel2_training_features_config,
                inputs=[
                    "params:gee",
                    "params:sentinel2_spectral_indices",
                    "params:sentinel2_training_features",
                ],
                outputs="sentinel2_training_features_config",
                name="validate_sentinel2_training_features_config_node",
            ),
            node(
                func=build_sentinel2_training_features_image,
                inputs="sentinel2_training_features_config",
                outputs="sentinel2_training_features_image",
                name="build_sentinel2_training_features_image_node",
            ),
            node(
                func=extract_sentinel2_features,
                inputs=[
                    "training_labeled_points",
                    "testing_labeled_points",
                    "sentinel2_training_features_image",
                    "sentinel2_training_features_config",
                ],
                outputs=["training_sentinel2_features", "testing_sentinel2_features"],
                name="extract_sentinel2_features_node",
            ),
            node(
                func=build_sentinel2_training_features_metadata,
                inputs=[
                    "training_labeled_points",
                    "testing_labeled_points",
                    "training_sentinel2_features",
                    "testing_sentinel2_features",
                    "sentinel2_training_features_config",
                ],
                outputs="sentinel2_training_features_metadata",
                name="build_sentinel2_training_features_metadata_node",
            ),
        ]
    )
