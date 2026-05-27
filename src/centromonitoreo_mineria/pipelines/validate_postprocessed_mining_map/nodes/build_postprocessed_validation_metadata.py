import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    build_postprocessed_validation_metadata as build_metadata,
)


def build_postprocessed_validation_metadata(
    postprocessed_mining_point_validation: pd.DataFrame,
    postprocessed_mining_class_summary: pd.DataFrame,
    postprocessed_mining_validation_plot_metadata: dict,
    mining_binary_map_postprocessing_metadata: dict,
    postprocessed_mining_map_validation_config: dict,
) -> dict:
    """Construye metadatos finales de la validacion postprocesada."""
    return build_metadata(
        point_validation=postprocessed_mining_point_validation,
        class_summary=postprocessed_mining_class_summary,
        plot_metadata=postprocessed_mining_validation_plot_metadata,
        postprocessing_metadata=mining_binary_map_postprocessing_metadata,
        params=postprocessed_mining_map_validation_config,
    )
