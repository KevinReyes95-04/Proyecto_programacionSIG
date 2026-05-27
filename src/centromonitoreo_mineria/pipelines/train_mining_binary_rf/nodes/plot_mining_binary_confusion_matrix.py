from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    plot_confusion_matrix,
)


def plot_mining_binary_confusion_matrix(
    mining_binary_metrics: dict,
    mining_binary_random_forest_config: dict,
) -> dict:
    """Genera la matriz de confusion del modelo binario."""
    return plot_confusion_matrix(
        metrics=mining_binary_metrics,
        params=mining_binary_random_forest_config,
    )
