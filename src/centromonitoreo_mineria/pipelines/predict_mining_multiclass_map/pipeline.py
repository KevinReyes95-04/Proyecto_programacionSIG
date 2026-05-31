from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.predict_mining_multiclass_map.nodes import (
    build_mining_multiclass_map_metadata,
    plot_mining_multiclass_map,
    predict_mining_multiclass_map_rasters,
    validate_mining_multiclass_map_prediction_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for multiclass mining map prediction."""
    return Pipeline(
        [
            node(
                func=validate_mining_multiclass_map_prediction_config,
                inputs="params:mining_multiclass_map_prediction",
                outputs="mining_multiclass_map_prediction_config",
                name="validate_mining_multiclass_map_prediction_config_node",
            ),
            node(
                func=predict_mining_multiclass_map_rasters,
                inputs=["mining_multiclass_random_forest_model", "mining_multiclass_map_prediction_config"],
                outputs="mining_multiclass_map_prediction_metadata",
                name="predict_mining_multiclass_map_rasters_node",
            ),
            node(
                func=plot_mining_multiclass_map,
                inputs=["mining_multiclass_map_prediction_metadata", "mining_multiclass_map_prediction_config"],
                outputs="mining_multiclass_map_plot_metadata",
                name="plot_mining_multiclass_map_node",
            ),
            node(
                func=build_mining_multiclass_map_metadata,
                inputs=[
                    "mining_multiclass_map_prediction_metadata",
                    "mining_multiclass_map_plot_metadata",
                    "mining_multiclass_map_prediction_config",
                ],
                outputs="mining_multiclass_map_metadata",
                name="build_mining_multiclass_map_metadata_node",
            ),
        ]
    )

