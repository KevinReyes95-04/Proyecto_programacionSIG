from kedro.pipeline import Pipeline, node, pipeline

from .nodes import train_multiclass_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=train_multiclass_model,
                inputs=["feature_table", "params:multiclass_rf"],
                outputs="multiclass_model",
                name="train_multiclass_model_node",
            )
        ]
    )
