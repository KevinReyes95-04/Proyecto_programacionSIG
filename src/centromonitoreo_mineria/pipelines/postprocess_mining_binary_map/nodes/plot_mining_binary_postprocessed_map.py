from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_postprocessing import (
    plot_postprocessed_mining_map,
)


def plot_mining_binary_postprocessed_map(
    mining_binary_map_postprocessing_output_metadata: dict,
    mining_binary_map_postprocessing_config: dict,
) -> dict:
    """Genera el mapa cartografico del resultado postprocesado."""
    return plot_postprocessed_mining_map(
        postprocessing_metadata=mining_binary_map_postprocessing_output_metadata,
        params=mining_binary_map_postprocessing_config,
    )
