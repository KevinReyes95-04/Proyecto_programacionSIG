from kedro.pipeline import Pipeline, node, pipeline

from .nodes import harmonize_sources


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=harmonize_sources,
                inputs="params:raw_data",
                outputs="harmonized_samples",
                name="harmonize_sources_node",
            )
        ]
    )
