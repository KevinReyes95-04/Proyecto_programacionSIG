from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.build_topographic_features.nodes import (
    build_topographic_features,
    plot_topographic_feature_maps,
    validate_topographic_features_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for topographic features."""
    return Pipeline(
        [
            node(
                func=validate_topographic_features_config,
                inputs=["params:gee", "params:sentinel2_download", "params:topographic_features"],
                outputs="topographic_features_config",
                name="validate_topographic_features_config_node",
            ),
            node(
                func=build_topographic_features,
                inputs="topographic_features_config",
                outputs="topographic_features_metadata",
                name="build_topographic_features_node",
            ),
            node(
                func=plot_topographic_feature_maps,
                inputs=["topographic_features_metadata", "topographic_features_config"],
                outputs="topographic_feature_maps_metadata",
                name="plot_topographic_feature_maps_node",
            ),
        ]
    )

