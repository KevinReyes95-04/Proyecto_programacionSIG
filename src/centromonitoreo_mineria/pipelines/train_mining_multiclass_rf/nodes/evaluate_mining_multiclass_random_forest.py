from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score


# Funcion para calcular metricas del modelo multiclase.
def evaluate_mining_multiclass_random_forest(
    mining_multiclass_predictions: pd.DataFrame,
    mining_multiclass_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_multiclass_random_forest_config
    target_column = params.get("target_column", "target_class")
    prediction_column = params.get("prediction_column", "predicted_class")
    labels = params["class_labels"]
    y_true = mining_multiclass_predictions[target_column]
    y_pred = mining_multiclass_predictions[prediction_column]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": labels,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)),
        "confusion_matrix": np.asarray(matrix).astype(int).tolist(),
        "classification_report": classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0),
    }

