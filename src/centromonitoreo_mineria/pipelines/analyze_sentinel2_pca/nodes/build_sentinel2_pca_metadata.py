import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    build_pca_metadata,
)


def build_sentinel2_pca_metadata(
    sentinel2_pca_training_dataset: dict,
    sentinel2_pca_testing_dataset: dict,
    sentinel2_pca_explained_variance: pd.DataFrame,
    sentinel2_pca_scatter_plot_metadata: dict,
    sentinel2_pca_scree_plot_metadata: dict,
    sentinel2_pca_config: dict,
) -> dict:
    """Construye los metadatos finales del analisis PCA."""
    return build_pca_metadata(
        training_dataset=sentinel2_pca_training_dataset,
        testing_dataset=sentinel2_pca_testing_dataset,
        explained_variance=sentinel2_pca_explained_variance,
        scatter_plot_metadata=sentinel2_pca_scatter_plot_metadata,
        scree_plot_metadata=sentinel2_pca_scree_plot_metadata,
        params=sentinel2_pca_config,
    )
