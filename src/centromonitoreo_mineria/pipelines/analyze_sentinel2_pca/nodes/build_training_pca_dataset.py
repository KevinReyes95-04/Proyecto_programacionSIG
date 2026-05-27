import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    build_pca_dataset,
)


def build_training_pca_dataset(
    training_sentinel2_features: pd.DataFrame,
    sentinel2_pca_config: dict,
) -> dict:
    """Construye el dataset PCA de entrenamiento."""
    return build_pca_dataset(
        table=training_sentinel2_features,
        params=sentinel2_pca_config,
        dataset_name="training",
    )
