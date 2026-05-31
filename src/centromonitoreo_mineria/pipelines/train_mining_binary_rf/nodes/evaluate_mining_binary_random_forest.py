from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


# Funcion para calcular metricas del modelo binario.
def evaluate_mining_binary_random_forest(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_binary_random_forest_config
    target_column = params.get("target_column", "target")
    prediction_column = params.get("prediction_column", "predicted_target")
    labels = [params["negative_label"], params["positive_label"]]
    y_true = mining_binary_predictions[target_column]
    y_pred = mining_binary_predictions[prediction_column]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": labels,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_mineria": float(precision_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "recall_mineria": float(recall_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "f1_mineria": float(f1_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "confusion_matrix": np.asarray(matrix).astype(int).tolist(),
        "classification_report": classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0),
    }
