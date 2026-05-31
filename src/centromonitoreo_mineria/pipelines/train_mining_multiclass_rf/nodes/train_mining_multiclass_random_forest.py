from typing import Any

from sklearn.ensemble import RandomForestClassifier


# Funcion para entrenar el modelo Random Forest multiclase.
def train_mining_multiclass_random_forest(
    mining_multiclass_training_dataset: dict[str, Any],
    mining_multiclass_random_forest_config: dict[str, Any],
) -> RandomForestClassifier:
    model = RandomForestClassifier(**mining_multiclass_random_forest_config.get("random_forest", {}))
    model.fit(mining_multiclass_training_dataset["X"], mining_multiclass_training_dataset["y"])
    return model

