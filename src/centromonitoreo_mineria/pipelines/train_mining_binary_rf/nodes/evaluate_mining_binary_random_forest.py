import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    evaluate_binary_predictions,
)


def evaluate_mining_binary_random_forest(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_random_forest_config: dict,
) -> dict:
    """Calcula metricas del Random Forest binario."""
    return evaluate_binary_predictions(
        predictions=mining_binary_predictions,
        params=mining_binary_random_forest_config,
    )
