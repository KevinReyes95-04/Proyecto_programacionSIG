import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import (
    plot_testing_errors_overlay as plot_overlay,
)


def plot_testing_errors_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict,
    mining_binary_map_validation_config: dict,
) -> dict:
    """Grafica errores de prueba sobre el mapa clasificado."""
    return plot_overlay(
        testing_predictions=mining_binary_predictions,
        map_metadata=mining_binary_map_metadata,
        params=mining_binary_map_validation_config,
    )
