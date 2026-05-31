from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.validate_mining_multiclass_map.nodes import (
    evaluate_mining_multiclass_map_validation,
    plot_mining_multiclass_validation_confusion_matrix,
)
from centromonitoreo_mineria.pipelines.validate_postprocessed_mining_multiclass_map.nodes import (
    build_postprocessed_mining_multiclass_point_validation,
    build_postprocessed_mining_multiclass_validation_metadata,
    plot_postprocessed_mining_multiclass_validation_map,
    validate_postprocessed_mining_multiclass_map_validation_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for validating the postprocessed multiclass map."""
    return Pipeline(
        [
            node(
                func=validate_postprocessed_mining_multiclass_map_validation_config,
                inputs="params:postprocessed_mining_multiclass_map_validation",
                outputs="postprocessed_mining_multiclass_map_validation_config",
                name="validate_postprocessed_mining_multiclass_map_validation_config_node",
            ),
            node(
                func=build_postprocessed_mining_multiclass_point_validation,
                inputs=[
                    "testing_sentinel2_features",
                    "mining_multiclass_map_postprocessing_metadata",
                    "postprocessed_mining_multiclass_map_validation_config",
                ],
                outputs="postprocessed_mining_multiclass_point_validation",
                name="build_postprocessed_mining_multiclass_point_validation_node",
            ),
            node(
                func=evaluate_mining_multiclass_map_validation,
                inputs=[
                    "postprocessed_mining_multiclass_point_validation",
                    "postprocessed_mining_multiclass_map_validation_config",
                ],
                outputs=[
                    "postprocessed_mining_multiclass_map_validation_metrics",
                    "postprocessed_mining_multiclass_map_validation_class_summary",
                ],
                name="evaluate_postprocessed_mining_multiclass_map_validation_node",
            ),
            node(
                func=plot_mining_multiclass_validation_confusion_matrix,
                inputs=[
                    "postprocessed_mining_multiclass_map_validation_metrics",
                    "postprocessed_mining_multiclass_map_validation_config",
                ],
                outputs="postprocessed_mining_multiclass_validation_confusion_matrix_plot_metadata",
                name="plot_postprocessed_mining_multiclass_validation_confusion_matrix_node",
            ),
            node(
                func=plot_postprocessed_mining_multiclass_validation_map,
                inputs=[
                    "postprocessed_mining_multiclass_point_validation",
                    "mining_multiclass_map_postprocessing_metadata",
                    "postprocessed_mining_multiclass_map_validation_config",
                ],
                outputs="postprocessed_mining_multiclass_validation_map_metadata",
                name="plot_postprocessed_mining_multiclass_validation_map_node",
            ),
            node(
                func=build_postprocessed_mining_multiclass_validation_metadata,
                inputs=[
                    "postprocessed_mining_multiclass_point_validation",
                    "postprocessed_mining_multiclass_map_validation_metrics",
                    "postprocessed_mining_multiclass_validation_confusion_matrix_plot_metadata",
                    "postprocessed_mining_multiclass_validation_map_metadata",
                    "postprocessed_mining_multiclass_map_validation_config",
                ],
                outputs="postprocessed_mining_multiclass_map_validation_metadata",
                name="build_postprocessed_mining_multiclass_validation_metadata_node",
            ),
        ]
    )

