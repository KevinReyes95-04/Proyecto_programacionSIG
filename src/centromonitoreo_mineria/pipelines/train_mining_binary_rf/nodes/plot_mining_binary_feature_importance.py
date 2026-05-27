import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    plot_feature_importance,
)


def plot_mining_binary_feature_importance(
    mining_binary_feature_importance: pd.DataFrame,
    mining_binary_random_forest_config: dict,
) -> dict:
    """Genera la grafica de importancia de variables."""
    return plot_feature_importance(
        importance=mining_binary_feature_importance,
        params=mining_binary_random_forest_config,
    )
