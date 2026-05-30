from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.prepare_training_data.nodes import (
    build_training_data_metadata,
    plot_labeled_points_reports,
    plot_training_testing_points_distribution,
    prepare_labeled_points,
    split_training_testing_data,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for training data preparation."""
    return Pipeline(
        [
            node(
                func=prepare_labeled_points,
                inputs="params:training_data",
                outputs="validated_labeled_points",
                name="prepare_labeled_points_node",
            ),
            node(
                func=plot_labeled_points_reports,
                inputs=["validated_labeled_points", "params:training_data"],
                outputs="labeled_points_reports_metadata",
                name="plot_labeled_points_reports_node",
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
                    "labeled_points_reports_metadata",
                    "training_testing_points_spatial_plot_metadata",
                    "params:training_data",
                ],
                outputs="training_data_metadata",
                name="build_training_data_metadata_node",
            ),
        ]
    )
