from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score


# Funcion para calcular metricas punto-raster del mapa multiclase.
def evaluate_mining_multiclass_map_validation(
    mining_multiclass_point_validation: pd.DataFrame,
    mining_multiclass_map_validation_config: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    params = mining_multiclass_map_validation_config
    label_column = params["label_column"]
    prediction_column = params.get("prediction_column", "predicted_map_class")
    labels = params["class_labels"]
    valid = mining_multiclass_point_validation[mining_multiclass_point_validation["is_valid_pixel"]].copy()
    y_true = valid[label_column]
    y_pred = valid[prediction_column]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    metrics = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": labels,
        "total_points": int(len(mining_multiclass_point_validation)),
        "valid_points": int(len(valid)),
        "invalid_points": int((~mining_multiclass_point_validation["is_valid_pixel"]).sum()),
        "accuracy": float(accuracy_score(y_true, y_pred)) if len(valid) else None,
        "precision_macro": float(precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)) if len(valid) else None,
        "recall_macro": float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)) if len(valid) else None,
        "f1_macro": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)) if len(valid) else None,
        "confusion_matrix": np.asarray(matrix).astype(int).tolist(),
        "classification_report": classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0) if len(valid) else {},
    }
    return metrics, _class_summary(valid, labels, label_column, prediction_column)


# Funcion para resumir exactitud por clase observada.
def _class_summary(points: pd.DataFrame, labels: list[str], label_column: str, prediction_column: str) -> pd.DataFrame:
    rows = []
    for label in labels:
        subset = points[points[label_column] == label]
        correct = int((subset[label_column] == subset[prediction_column]).sum())
        total = int(len(subset))
        rows.append({"class_label": label, "total": total, "correct": correct, "accuracy": correct / total if total else None})
    return pd.DataFrame(rows)

