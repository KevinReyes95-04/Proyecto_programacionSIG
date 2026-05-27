from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_prediction import (
    plot_mining_map,
)


def plot_mining_binary_map(
    mining_binary_map_prediction_metadata: dict,
    mining_binary_map_prediction_config: dict,
) -> dict:
    """Genera una vista PNG del mapa binario de mineria."""
    return plot_mining_map(
        prediction_metadata=mining_binary_map_prediction_metadata,
        params=mining_binary_map_prediction_config,
    )
