import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import (
    plot_probability_points_overlay as plot_overlay,
)


def plot_probability_points_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict,
    mining_binary_map_validation_config: dict,
) -> dict:
    """Grafica probabilidad de mineria con puntos de prueba."""
    return plot_overlay(
        testing_predictions=mining_binary_predictions,
        map_metadata=mining_binary_map_metadata,
        params=mining_binary_map_validation_config,
    )
