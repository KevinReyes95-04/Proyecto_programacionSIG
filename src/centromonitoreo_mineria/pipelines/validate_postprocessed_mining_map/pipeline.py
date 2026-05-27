from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_map.nodes import (
    build_postprocessed_class_summary,
    build_postprocessed_point_validation_table,
    build_postprocessed_validation_metadata,
    plot_postprocessed_validation_map,
    validate_postprocessed_mining_map_validation_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for validating the postprocessed mining map."""
    return Pipeline(
        [
            node(
                func=validate_postprocessed_mining_map_validation_config,
                inputs="params:postprocessed_mining_map_validation",
                outputs="postprocessed_mining_map_validation_config",
                name="validate_postprocessed_mining_map_validation_config_node",
            ),
            node(
                func=build_postprocessed_point_validation_table,
                inputs=[
                    "training_sentinel2_features",
                    "testing_sentinel2_features",
                    "mining_binary_map_postprocessing_metadata",
                    "postprocessed_mining_map_validation_config",
                ],
                outputs="postprocessed_mining_point_validation",
                name="build_postprocessed_mining_point_validation_table_node",
            ),
            node(
                func=build_postprocessed_class_summary,
                inputs=[
                    "postprocessed_mining_point_validation",
                    "postprocessed_mining_map_validation_config",
                ],
                outputs="postprocessed_mining_class_summary",
                name="build_postprocessed_mining_class_summary_node",
            ),
            node(
                func=plot_postprocessed_validation_map,
                inputs=[
                    "postprocessed_mining_point_validation",
                    "mining_binary_map_postprocessing_metadata",
                    "postprocessed_mining_map_validation_config",
                ],
                outputs="postprocessed_mining_validation_plot_metadata",
                name="plot_postprocessed_mining_validation_map_node",
            ),
            node(
                func=build_postprocessed_validation_metadata,
                inputs=[
                    "postprocessed_mining_point_validation",
                    "postprocessed_mining_class_summary",
                    "postprocessed_mining_validation_plot_metadata",
                    "mining_binary_map_postprocessing_metadata",
                    "postprocessed_mining_map_validation_config",
                ],
                outputs="postprocessed_mining_map_validation_metadata",
                name="build_postprocessed_mining_map_validation_metadata_node",
            ),
        ]
    )
