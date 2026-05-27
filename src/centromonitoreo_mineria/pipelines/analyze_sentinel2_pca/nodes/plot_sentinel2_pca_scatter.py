import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    plot_pca_scatter,
)


def plot_sentinel2_pca_scatter(
    sentinel2_pca_training_scores: pd.DataFrame,
    sentinel2_pca_testing_scores: pd.DataFrame,
    sentinel2_pca_config: dict,
) -> dict:
    """Genera la grafica PC1 vs PC2."""
    return plot_pca_scatter(
        training_scores=sentinel2_pca_training_scores,
        testing_scores=sentinel2_pca_testing_scores,
        params=sentinel2_pca_config,
    )
