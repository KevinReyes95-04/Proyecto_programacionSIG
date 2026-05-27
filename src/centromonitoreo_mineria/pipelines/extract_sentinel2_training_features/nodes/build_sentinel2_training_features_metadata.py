import pandas as pd

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_feature_extraction import (
    build_sentinel2_training_features_metadata as build_metadata,
)


def build_sentinel2_training_features_metadata(
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    training_sentinel2_features: pd.DataFrame,
    testing_sentinel2_features: pd.DataFrame,
    sentinel2_training_features_config: dict,
) -> dict:
    """Construye metadatos de las tablas Sentinel-2 extraidas."""
    return build_metadata(
        training_labeled_points=training_labeled_points,
        testing_labeled_points=testing_labeled_points,
        training_features=training_sentinel2_features,
        testing_features=testing_sentinel2_features,
        config=sentinel2_training_features_config,
    )
