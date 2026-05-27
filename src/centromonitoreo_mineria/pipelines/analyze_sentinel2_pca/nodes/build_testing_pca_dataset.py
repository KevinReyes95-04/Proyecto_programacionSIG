import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    build_pca_dataset,
)


def build_testing_pca_dataset(
    testing_sentinel2_features: pd.DataFrame,
    sentinel2_pca_config: dict,
) -> dict:
    """Construye el dataset PCA de prueba."""
    return build_pca_dataset(
        table=testing_sentinel2_features,
        params=sentinel2_pca_config,
        dataset_name="testing",
    )
