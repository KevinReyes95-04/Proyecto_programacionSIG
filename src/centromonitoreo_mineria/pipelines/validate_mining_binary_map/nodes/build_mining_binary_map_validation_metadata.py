import pandas as pd
from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_validation import build_mining_binary_map_validation_metadata as build_metadata


def build_mining_binary_map_validation_metadata(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_classification_points_plot_metadata: dict,
    mining_binary_probability_points_plot_metadata: dict,
    mining_binary_testing_errors_plot_metadata: dict,
    mining_binary_map_validation_config: dict,
) -> dict:
    """Construye metadatos de validacion visual del mapa binario."""
    return build_metadata(
        testing_predictions=mining_binary_predictions,
        classification_points_metadata=mining_binary_classification_points_plot_metadata,
        probability_points_metadata=mining_binary_probability_points_plot_metadata,
        testing_errors_metadata=mining_binary_testing_errors_plot_metadata,
        params=mining_binary_map_validation_config,
    )
