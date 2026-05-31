from typing import Any

from sklearn.ensemble import RandomForestClassifier


# Funcion para entrenar el modelo Random Forest binario.
def train_mining_binary_random_forest(
    mining_binary_training_dataset: dict[str, Any],
    mining_binary_random_forest_config: dict[str, Any],
) -> RandomForestClassifier:
    model = RandomForestClassifier(**mining_binary_random_forest_config.get("random_forest", {}))
    model.fit(mining_binary_training_dataset["X"], mining_binary_training_dataset["y"])
    return model
