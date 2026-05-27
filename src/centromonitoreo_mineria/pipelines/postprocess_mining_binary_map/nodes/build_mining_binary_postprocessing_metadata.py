from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_postprocessing import (
    build_mining_binary_map_postprocessing_metadata,
)


def build_mining_binary_postprocessing_metadata(
    mining_binary_map_postprocessing_output_metadata: dict,
    mining_binary_postprocessed_map_plot_metadata: dict,
    mining_binary_map_postprocessing_config: dict,
) -> dict:
    """Construye los metadatos finales del postprocesamiento."""
    return build_mining_binary_map_postprocessing_metadata(
        postprocessing_metadata=mining_binary_map_postprocessing_output_metadata,
        plot_metadata=mining_binary_postprocessed_map_plot_metadata,
        params=mining_binary_map_postprocessing_config,
    )
