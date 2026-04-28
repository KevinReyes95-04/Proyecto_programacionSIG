from kedro.pipeline import Pipeline, node, pipeline

from .nodes import build_spectral_features


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=build_spectral_features,
                inputs="harmonized_samples",
                outputs="feature_table",
                name="build_spectral_features_node",
            )
        ]
    )
