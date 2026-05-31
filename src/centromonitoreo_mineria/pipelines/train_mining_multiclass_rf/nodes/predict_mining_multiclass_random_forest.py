from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# Funcion para predecir clases y probabilidades sobre el conjunto de prueba.
def predict_mining_multiclass_random_forest(
    mining_multiclass_random_forest_model: RandomForestClassifier,
    mining_multiclass_testing_dataset: dict[str, Any],
    mining_multiclass_random_forest_config: dict[str, Any],
) -> pd.DataFrame:
    params = mining_multiclass_random_forest_config
    predictions = mining_multiclass_testing_dataset["source"].copy()
    predictions[params.get("prediction_column", "predicted_class")] = mining_multiclass_random_forest_model.predict(
        mining_multiclass_testing_dataset["X"]
    )
    if hasattr(mining_multiclass_random_forest_model, "predict_proba"):
        probabilities = mining_multiclass_random_forest_model.predict_proba(mining_multiclass_testing_dataset["X"])
        class_positions = {label: index for index, label in enumerate(mining_multiclass_random_forest_model.classes_)}
        for label in params["class_labels"]:
            predictions[_probability_column(label, params)] = (
                probabilities[:, class_positions[label]] if label in class_positions else np.zeros(len(predictions))
            )
    return predictions


# Funcion para construir nombres de columnas de probabilidad.
def _probability_column(label: str, params: dict[str, Any]) -> str:
    prefix = params.get("probability_prefix", "probability")
    return f"{prefix}_{label.lower().replace(' ', '_')}"

