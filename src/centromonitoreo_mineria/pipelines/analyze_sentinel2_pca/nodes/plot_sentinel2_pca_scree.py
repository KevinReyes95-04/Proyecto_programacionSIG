import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    plot_pca_scree,
)


def plot_sentinel2_pca_scree(
    sentinel2_pca_explained_variance: pd.DataFrame,
    sentinel2_pca_config: dict,
) -> dict:
    """Genera la grafica de varianza explicada."""
    return plot_pca_scree(
        explained_variance=sentinel2_pca_explained_variance,
        params=sentinel2_pca_config,
    )
