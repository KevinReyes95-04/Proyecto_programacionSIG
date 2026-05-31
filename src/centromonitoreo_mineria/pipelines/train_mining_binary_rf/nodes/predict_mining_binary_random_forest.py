from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# Funcion para predecir mineria y probabilidad sobre el conjunto de prueba.
def predict_mining_binary_random_forest(
    mining_binary_random_forest_model: RandomForestClassifier,
    mining_binary_testing_dataset: dict[str, Any],
    mining_binary_random_forest_config: dict[str, Any],
) -> pd.DataFrame:
    params = mining_binary_random_forest_config
    predictions = mining_binary_testing_dataset["source"].copy()
    prediction_column = params.get("prediction_column", "predicted_target")
    probability_column = params.get("probability_column", "probability_mineria")
    if hasattr(mining_binary_random_forest_model, "predict_proba"):
        positive_index = list(mining_binary_random_forest_model.classes_).index(params["positive_label"])
        probability = np.asarray(
            mining_binary_random_forest_model.predict_proba(mining_binary_testing_dataset["X"])
        )[:, positive_index]
        predictions[probability_column] = probability
        predictions[prediction_column] = np.where(
            probability >= params.get("classification_threshold", 0.5),
            params["positive_label"],
            params["negative_label"],
        )
    else:
        predictions[prediction_column] = mining_binary_random_forest_model.predict(
            mining_binary_testing_dataset["X"]
        )
    return predictions
