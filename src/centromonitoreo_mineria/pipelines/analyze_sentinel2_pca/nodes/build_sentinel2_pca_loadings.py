import pandas as pd
from sklearn.pipeline import Pipeline as SklearnPipeline

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    loadings_table,
)


def build_sentinel2_pca_loadings(
    sentinel2_pca_model: SklearnPipeline,
    sentinel2_pca_config: dict,
) -> pd.DataFrame:
    """Construye la tabla de cargas PCA."""
    return loadings_table(model=sentinel2_pca_model, params=sentinel2_pca_config)
