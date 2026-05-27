import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    plot_postprocessed_validation_map as plot_map,
)


def plot_postprocessed_validation_map(
    postprocessed_mining_point_validation: pd.DataFrame,
    mining_binary_map_postprocessing_metadata: dict,
    postprocessed_mining_map_validation_config: dict,
) -> dict:
    """Genera mapa de validacion del resultado postprocesado."""
    return plot_map(
        point_validation=postprocessed_mining_point_validation,
        postprocessing_metadata=mining_binary_map_postprocessing_metadata,
        params=postprocessed_mining_map_validation_config,
    )
