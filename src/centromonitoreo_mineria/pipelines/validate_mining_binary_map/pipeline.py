from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.nodes import (
    build_mining_binary_map_validation_metadata,
    plot_classification_points_overlay,
    plot_probability_points_overlay,
    plot_testing_errors_overlay,
    validate_mining_binary_map_validation_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for visual validation of mining map."""
    return Pipeline(
        [
            node(
                func=validate_mining_binary_map_validation_config,
                inputs="params:mining_binary_map_validation",
                outputs="mining_binary_map_validation_config",
                name="validate_mining_binary_map_validation_config_node",
            ),
            node(
                func=plot_classification_points_overlay,
                inputs=[
                    "training_sentinel2_features",
                    "mining_binary_predictions",
                    "mining_binary_map_metadata",
                    "mining_binary_map_validation_config",
                ],
                outputs="mining_binary_classification_points_plot_metadata",
                name="plot_mining_binary_classification_points_overlay_node",
            ),
            node(
                func=plot_probability_points_overlay,
                inputs=[
                    "mining_binary_predictions",
                    "mining_binary_map_metadata",
                    "mining_binary_map_validation_config",
                ],
                outputs="mining_binary_probability_points_plot_metadata",
                name="plot_mining_binary_probability_points_overlay_node",
            ),
            node(
                func=plot_testing_errors_overlay,
                inputs=[
                    "mining_binary_predictions",
                    "mining_binary_map_metadata",
                    "mining_binary_map_validation_config",
                ],
                outputs="mining_binary_testing_errors_plot_metadata",
                name="plot_mining_binary_testing_errors_overlay_node",
            ),
            node(
                func=build_mining_binary_map_validation_metadata,
                inputs=[
                    "mining_binary_predictions",
                    "mining_binary_classification_points_plot_metadata",
                    "mining_binary_probability_points_plot_metadata",
                    "mining_binary_testing_errors_plot_metadata",
                    "mining_binary_map_validation_config",
                ],
                outputs="mining_binary_map_validation_metadata",
                name="build_mining_binary_map_validation_metadata_node",
            ),
        ]
    )
