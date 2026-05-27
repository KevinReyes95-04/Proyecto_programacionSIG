from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.postprocess_mining_binary_map.nodes import (
    build_mining_binary_postprocessing_metadata,
    plot_mining_binary_postprocessed_map,
    postprocess_mining_binary_map,
    validate_mining_binary_postprocessing_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for mining binary map postprocessing."""
    return Pipeline(
        [
            node(
                func=validate_mining_binary_postprocessing_config,
                inputs="params:mining_binary_map_postprocessing",
                outputs="mining_binary_map_postprocessing_config",
                name="validate_mining_binary_postprocessing_config_node",
            ),
            node(
                func=postprocess_mining_binary_map,
                inputs="mining_binary_map_postprocessing_config",
                outputs="mining_binary_map_postprocessing_output_metadata",
                name="postprocess_mining_binary_map_node",
            ),
            node(
                func=plot_mining_binary_postprocessed_map,
                inputs=[
                    "mining_binary_map_postprocessing_output_metadata",
                    "mining_binary_map_postprocessing_config",
                ],
                outputs="mining_binary_postprocessed_map_plot_metadata",
                name="plot_mining_binary_postprocessed_map_node",
            ),
            node(
                func=build_mining_binary_postprocessing_metadata,
                inputs=[
                    "mining_binary_map_postprocessing_output_metadata",
                    "mining_binary_postprocessed_map_plot_metadata",
                    "mining_binary_map_postprocessing_config",
                ],
                outputs="mining_binary_map_postprocessing_metadata",
                name="build_mining_binary_postprocessing_metadata_node",
            ),
        ]
    )
