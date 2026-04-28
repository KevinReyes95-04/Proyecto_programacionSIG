from kedro.pipeline import Pipeline, node, pipeline

from .nodes import evaluate_models


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=evaluate_models,
                inputs=["feature_table", "binary_model", "multiclass_model", "params:evaluation"],
                outputs="evaluation_report",
                name="evaluate_models_node",
            )
        ]
    )
