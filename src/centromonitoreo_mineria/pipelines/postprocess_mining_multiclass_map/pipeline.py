from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.postprocess_mining_multiclass_map.nodes import (
    build_mining_multiclass_postprocessing_metadata,
    plot_mining_multiclass_postprocessed_map,
    postprocess_mining_multiclass_map,
    validate_mining_multiclass_postprocessing_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for multiclass map postprocessing."""
    return Pipeline(
        [
            node(
                func=validate_mining_multiclass_postprocessing_config,
                inputs="params:mining_multiclass_map_postprocessing",
                outputs="mining_multiclass_map_postprocessing_config",
                name="validate_mining_multiclass_postprocessing_config_node",
            ),
            node(
                func=postprocess_mining_multiclass_map,
                inputs="mining_multiclass_map_postprocessing_config",
                outputs=[
                    "mining_multiclass_map_postprocessing_output_metadata",
                    "mining_multiclass_postprocessed_class_summary",
                ],
                name="postprocess_mining_multiclass_map_node",
            ),
            node(
                func=plot_mining_multiclass_postprocessed_map,
                inputs=[
                    "mining_multiclass_map_postprocessing_output_metadata",
                    "mining_multiclass_map_postprocessing_config",
                ],
                outputs="mining_multiclass_postprocessed_map_plot_metadata",
                name="plot_mining_multiclass_postprocessed_map_node",
            ),
            node(
                func=build_mining_multiclass_postprocessing_metadata,
                inputs=[
                    "mining_multiclass_map_postprocessing_output_metadata",
                    "mining_multiclass_postprocessed_class_summary",
                    "mining_multiclass_postprocessed_map_plot_metadata",
                    "mining_multiclass_map_postprocessing_config",
                ],
                outputs="mining_multiclass_map_postprocessing_metadata",
                name="build_mining_multiclass_postprocessing_metadata_node",
            ),
        ]
    )

