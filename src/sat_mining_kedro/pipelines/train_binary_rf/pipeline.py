from kedro.pipeline import Pipeline, node, pipeline

from .nodes import train_binary_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=train_binary_model,
                inputs=["feature_table", "params:binary_rf"],
                outputs="binary_model",
                name="train_binary_model_node",
            )
        ]
    )
