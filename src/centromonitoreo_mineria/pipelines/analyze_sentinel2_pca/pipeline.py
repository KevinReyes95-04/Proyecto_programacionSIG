from kedro.pipeline import Pipeline, node

from centromonitoreo_mineria.pipelines.analyze_sentinel2_pca.nodes import (
    build_sentinel2_pca_explained_variance,
    build_sentinel2_pca_loadings,
    build_sentinel2_pca_metadata,
    build_testing_pca_dataset,
    build_training_pca_dataset,
    fit_sentinel2_pca_model,
    plot_sentinel2_pca_scatter,
    plot_sentinel2_pca_scree,
    transform_testing_pca_scores,
    transform_training_pca_scores,
    validate_sentinel2_pca_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for Sentinel-2 PCA analysis."""
    return Pipeline(
        [
            node(
                func=validate_sentinel2_pca_config,
                inputs="params:sentinel2_pca_analysis",
                outputs="sentinel2_pca_config",
                name="validate_sentinel2_pca_config_node",
            ),
            node(
                func=build_training_pca_dataset,
                inputs=["training_sentinel2_features", "sentinel2_pca_config"],
                outputs="sentinel2_pca_training_dataset",
                name="build_sentinel2_pca_training_dataset_node",
            ),
            node(
                func=build_testing_pca_dataset,
                inputs=["testing_sentinel2_features", "sentinel2_pca_config"],
                outputs="sentinel2_pca_testing_dataset",
                name="build_sentinel2_pca_testing_dataset_node",
            ),
            node(
                func=fit_sentinel2_pca_model,
                inputs=["sentinel2_pca_training_dataset", "sentinel2_pca_config"],
                outputs="sentinel2_pca_model",
                name="fit_sentinel2_pca_model_node",
            ),
            node(
                func=transform_training_pca_scores,
                inputs=[
                    "sentinel2_pca_model",
                    "sentinel2_pca_training_dataset",
                    "sentinel2_pca_config",
                ],
                outputs="sentinel2_pca_training_scores",
                name="transform_sentinel2_pca_training_scores_node",
            ),
            node(
                func=transform_testing_pca_scores,
                inputs=[
                    "sentinel2_pca_model",
                    "sentinel2_pca_testing_dataset",
                    "sentinel2_pca_config",
                ],
                outputs="sentinel2_pca_testing_scores",
                name="transform_sentinel2_pca_testing_scores_node",
            ),
            node(
                func=build_sentinel2_pca_explained_variance,
                inputs="sentinel2_pca_model",
                outputs="sentinel2_pca_explained_variance",
                name="build_sentinel2_pca_explained_variance_node",
            ),
            node(
                func=build_sentinel2_pca_loadings,
                inputs=["sentinel2_pca_model", "sentinel2_pca_config"],
                outputs="sentinel2_pca_loadings",
                name="build_sentinel2_pca_loadings_node",
            ),
            node(
                func=plot_sentinel2_pca_scatter,
                inputs=[
                    "sentinel2_pca_training_scores",
                    "sentinel2_pca_testing_scores",
                    "sentinel2_pca_config",
                ],
                outputs="sentinel2_pca_scatter_plot_metadata",
                name="plot_sentinel2_pca_scatter_node",
            ),
            node(
                func=plot_sentinel2_pca_scree,
                inputs=["sentinel2_pca_explained_variance", "sentinel2_pca_config"],
                outputs="sentinel2_pca_scree_plot_metadata",
                name="plot_sentinel2_pca_scree_node",
            ),
            node(
                func=build_sentinel2_pca_metadata,
                inputs=[
                    "sentinel2_pca_training_dataset",
                    "sentinel2_pca_testing_dataset",
                    "sentinel2_pca_explained_variance",
                    "sentinel2_pca_scatter_plot_metadata",
                    "sentinel2_pca_scree_plot_metadata",
                    "sentinel2_pca_config",
                ],
                outputs="sentinel2_pca_metadata",
                name="build_sentinel2_pca_metadata_node",
            ),
        ]
    )
