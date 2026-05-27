import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    build_postprocessed_class_summary as build_summary,
)


def build_postprocessed_class_summary(
    postprocessed_mining_point_validation: pd.DataFrame,
    postprocessed_mining_map_validation_config: dict,
) -> pd.DataFrame:
    """Resume cuantas muestras de cada clase caen en poligonos mineros."""
    return build_summary(
        point_validation=postprocessed_mining_point_validation,
        params=postprocessed_mining_map_validation_config,
    )
