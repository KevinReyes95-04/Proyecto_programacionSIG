import pandas as pd
from sklearn.pipeline import Pipeline as SklearnPipeline

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    explained_variance_table,
)


def build_sentinel2_pca_explained_variance(
    sentinel2_pca_model: SklearnPipeline,
) -> pd.DataFrame:
    """Construye la tabla de varianza explicada."""
    return explained_variance_table(model=sentinel2_pca_model)
