from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_prediction import (
    build_mining_map_metadata,
)


def build_mining_binary_map_metadata(
    mining_binary_map_prediction_metadata: dict,
    mining_binary_map_plot_metadata: dict,
    mining_binary_map_prediction_config: dict,
) -> dict:
    """Construye metadatos finales del mapa binario de mineria."""
    return build_mining_map_metadata(
        prediction_metadata=mining_binary_map_prediction_metadata,
        plot_metadata=mining_binary_map_plot_metadata,
        params=mining_binary_map_prediction_config,
    )
