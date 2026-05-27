import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    build_binary_dataset,
)


def build_testing_dataset(
    testing_sentinel2_features: pd.DataFrame,
    mining_binary_random_forest_config: dict,
) -> dict:
    """Construye la matriz de prueba para Mineria vs No Mineria."""
    return build_binary_dataset(
        table=testing_sentinel2_features,
        params=mining_binary_random_forest_config,
        dataset_name="testing_sentinel2_features",
    )
