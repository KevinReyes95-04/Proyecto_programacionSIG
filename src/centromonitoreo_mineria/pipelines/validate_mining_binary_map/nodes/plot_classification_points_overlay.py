import pandas as pd
from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import plot_classification_points_overlay as plot_overlay


def plot_classification_points_overlay(
    training_sentinel2_features: pd.DataFrame,
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict,
    mining_binary_map_validation_config: dict,
) -> dict:
    """Grafica clasificacion con puntos de entrenamiento y prueba."""
    return plot_overlay(
        training_points=training_sentinel2_features,
        testing_predictions=mining_binary_predictions,
        map_metadata=mining_binary_map_metadata,
        params=mining_binary_map_validation_config,
    )
