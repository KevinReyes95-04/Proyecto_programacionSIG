import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.mining_postprocessed_validation import (
    build_postprocessed_point_validation_table as build_table,
)


def build_postprocessed_point_validation_table(
    training_sentinel2_features: pd.DataFrame,
    testing_sentinel2_features: pd.DataFrame,
    mining_binary_map_postprocessing_metadata: dict,
    postprocessed_mining_map_validation_config: dict,
) -> pd.DataFrame:
    """Cruza puntos de entrenamiento/prueba con poligonos mineros."""
    return build_table(
        training_points=training_sentinel2_features,
        testing_points=testing_sentinel2_features,
        postprocessing_metadata=mining_binary_map_postprocessing_metadata,
        params=postprocessed_mining_map_validation_config,
    )
