from sklearn.ensemble import RandomForestClassifier

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    train_random_forest,
)


def train_mining_binary_random_forest(
    mining_binary_training_dataset: dict,
    mining_binary_random_forest_config: dict,
) -> RandomForestClassifier:
    """Entrena el Random Forest binario."""
    return train_random_forest(
        training_dataset=mining_binary_training_dataset,
        params=mining_binary_random_forest_config,
    )
