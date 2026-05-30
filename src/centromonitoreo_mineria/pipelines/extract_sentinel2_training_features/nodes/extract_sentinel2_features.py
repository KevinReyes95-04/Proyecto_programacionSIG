from typing import Any
import pandas as pd
from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_feature_extraction import sample_points_from_image

def extract_sentinel2_features(
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    sentinel2_training_features_image: Any,
    sentinel2_training_features_config: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrae variables Sentinel-2 para las tablas de entrenamiento y prueba."""
    params = sentinel2_training_features_config["sentinel2_training_features"]
    return (
        sample_points_from_image(
            points=training_labeled_points,
            image=sentinel2_training_features_image,
            params=params,
            dataset_name="training",
        ),
        sample_points_from_image(
            points=testing_labeled_points,
            image=sentinel2_training_features_image,
            params=params,
            dataset_name="testing",
        ),
    )
