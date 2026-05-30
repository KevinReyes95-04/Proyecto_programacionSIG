import pandas as pd

from .binary_random_forest import (
    build_binary_dataset,
)


def build_mining_binary_datasets(
    training_sentinel2_features: pd.DataFrame,
    testing_sentinel2_features: pd.DataFrame,
    mining_binary_random_forest_config: dict,
) -> tuple[dict, dict]:
    """Construye los datasets de entrenamiento y prueba para el clasificador binario."""
    return (
        build_binary_dataset(
            table=training_sentinel2_features,
            params=mining_binary_random_forest_config,
            dataset_name="training_sentinel2_features",
        ),
        build_binary_dataset(
            table=testing_sentinel2_features,
            params=mining_binary_random_forest_config,
            dataset_name="testing_sentinel2_features",
        ),
    )
