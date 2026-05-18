from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.prepare_training_data.nodes import (
    build_training_data_metadata,
    load_labeled_points,
    plot_labeled_points_class_distribution,
    plot_labeled_points_distribution,
    plot_training_testing_points_distribution,
    split_training_testing_data,
    validate_labeled_points,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for training data preparation."""
    return Pipeline(
        [
            node(
                func=load_labeled_points,
                inputs="params:training_data",
                outputs="labeled_points",
                name="load_labeled_points_node",
            ),
            node(
                func=validate_labeled_points,
                inputs=["labeled_points", "params:training_data"],
                outputs="validated_labeled_points",
                name="validate_labeled_points_node",
            ),
            node(
                func=plot_labeled_points_distribution,
                inputs=["validated_labeled_points", "params:training_data"],
                outputs="labeled_points_spatial_plot_metadata",
                name="plot_labeled_points_distribution_node",
            ),
            node(
                func=plot_labeled_points_class_distribution,
                inputs=["validated_labeled_points", "params:training_data"],
                outputs="labeled_points_class_distribution_plot_metadata",
                name="plot_labeled_points_class_distribution_node",
            ),
            node(
                func=split_training_testing_data,
                inputs=["validated_labeled_points", "params:training_data"],
                outputs=["training_labeled_points", "testing_labeled_points"],
                name="split_training_testing_data_node",
            ),
            node(
                func=plot_training_testing_points_distribution,
                inputs=[
                    "training_labeled_points",
                    "testing_labeled_points",
                    "params:training_data",
                ],
                outputs="training_testing_points_spatial_plot_metadata",
                name="plot_training_testing_points_distribution_node",
            ),
            node(
                func=build_training_data_metadata,
                inputs=[
                    "validated_labeled_points",
                    "training_labeled_points",
                    "testing_labeled_points",
                    "labeled_points_spatial_plot_metadata",
                    "labeled_points_class_distribution_plot_metadata",
                    "training_testing_points_spatial_plot_metadata",
                    "params:training_data",
                ],
                outputs="training_data_metadata",
                name="build_training_data_metadata_node",
            ),
        ]
    )
