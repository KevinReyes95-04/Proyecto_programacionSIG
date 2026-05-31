from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.validate_mining_multiclass_map.nodes import (
    build_mining_multiclass_map_validation_metadata,
    build_mining_multiclass_point_validation,
    evaluate_mining_multiclass_map_validation,
    plot_mining_multiclass_validation_confusion_matrix,
    plot_mining_multiclass_validation_map,
    validate_mining_multiclass_map_validation_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for multiclass map validation."""
    return Pipeline(
        [
            node(
                func=validate_mining_multiclass_map_validation_config,
                inputs="params:mining_multiclass_map_validation",
                outputs="mining_multiclass_map_validation_config",
                name="validate_mining_multiclass_map_validation_config_node",
            ),
            node(
                func=build_mining_multiclass_point_validation,
                inputs=[
                    "testing_sentinel2_features",
                    "mining_multiclass_map_metadata",
                    "mining_multiclass_map_validation_config",
                ],
                outputs="mining_multiclass_point_validation",
                name="build_mining_multiclass_point_validation_node",
            ),
            node(
                func=evaluate_mining_multiclass_map_validation,
                inputs=[
                    "mining_multiclass_point_validation",
                    "mining_multiclass_map_validation_config",
                ],
                outputs=[
                    "mining_multiclass_map_validation_metrics",
                    "mining_multiclass_map_validation_class_summary",
                ],
                name="evaluate_mining_multiclass_map_validation_node",
            ),
            node(
                func=plot_mining_multiclass_validation_confusion_matrix,
                inputs=[
                    "mining_multiclass_map_validation_metrics",
                    "mining_multiclass_map_validation_config",
                ],
                outputs="mining_multiclass_validation_confusion_matrix_plot_metadata",
                name="plot_mining_multiclass_validation_confusion_matrix_node",
            ),
            node(
                func=plot_mining_multiclass_validation_map,
                inputs=[
                    "mining_multiclass_point_validation",
                    "mining_multiclass_map_metadata",
                    "mining_multiclass_map_validation_config",
                ],
                outputs="mining_multiclass_validation_map_metadata",
                name="plot_mining_multiclass_validation_map_node",
            ),
            node(
                func=build_mining_multiclass_map_validation_metadata,
                inputs=[
                    "mining_multiclass_point_validation",
                    "mining_multiclass_map_validation_metrics",
                    "mining_multiclass_validation_confusion_matrix_plot_metadata",
                    "mining_multiclass_validation_map_metadata",
                    "mining_multiclass_map_validation_config",
                ],
                outputs="mining_multiclass_map_validation_metadata",
                name="build_mining_multiclass_map_validation_metadata_node",
            ),
        ]
    )

