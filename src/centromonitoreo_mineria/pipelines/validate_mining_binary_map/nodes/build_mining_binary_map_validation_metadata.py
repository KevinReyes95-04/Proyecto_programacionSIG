from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.validation_errors import (
    error_groups,
)


def build_mining_binary_map_validation_metadata(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_classification_points_plot_metadata: dict[str, Any],
    mining_binary_probability_points_plot_metadata: dict[str, Any],
    mining_binary_testing_errors_plot_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    """Resume errores y salidas graficas de la validacion visual del mapa."""
    false_negatives, false_positives = error_groups(
        mining_binary_predictions,
        mining_binary_map_validation_config,
    )
    return {
        "positive_label": mining_binary_map_validation_config["positive_label"],
        "testing_rows": int(len(mining_binary_predictions)),
        "false_negatives": int(len(false_negatives)),
        "false_positives": int(len(false_positives)),
        "classification_points_plot": mining_binary_classification_points_plot_metadata,
        "probability_points_plot": mining_binary_probability_points_plot_metadata,
        "testing_errors_plot": mining_binary_testing_errors_plot_metadata,
    }
