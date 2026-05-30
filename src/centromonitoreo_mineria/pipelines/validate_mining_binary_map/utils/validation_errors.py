from typing import Any

import pandas as pd


def error_groups(points: pd.DataFrame, params: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa falsos negativos y falsos positivos para la clase mineria."""
    target = params["target_column"]
    prediction = params["prediction_column"]
    positive = params["positive_label"]
    false_negatives = points[(points[target] == positive) & (points[prediction] != positive)]
    false_positives = points[(points[target] != positive) & (points[prediction] == positive)]
    return false_negatives, false_positives
