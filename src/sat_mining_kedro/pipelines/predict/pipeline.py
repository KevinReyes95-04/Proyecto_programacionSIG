from kedro.pipeline import Pipeline, node, pipeline

from .nodes import run_inference


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=run_inference,
                inputs=["feature_table", "binary_model", "multiclass_model", "params:prediction"],
                outputs="prediction_table",
                name="run_inference_node",
            )
        ]
    )
