import pandas as pd
from sklearn.pipeline import Pipeline as SklearnPipeline

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    transform_pca_dataset,
)


def transform_training_pca_scores(
    sentinel2_pca_model: SklearnPipeline,
    sentinel2_pca_training_dataset: dict,
    sentinel2_pca_config: dict,
) -> pd.DataFrame:
    """Transforma los datos de entrenamiento al espacio PCA."""
    return transform_pca_dataset(
        model=sentinel2_pca_model,
        dataset=sentinel2_pca_training_dataset,
        params=sentinel2_pca_config,
    )
