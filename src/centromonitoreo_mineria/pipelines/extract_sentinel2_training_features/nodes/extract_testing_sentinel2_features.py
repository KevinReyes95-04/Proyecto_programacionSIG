from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_feature_extraction import (
    sample_points_from_image,
)


def extract_testing_sentinel2_features(
    testing_labeled_points: pd.DataFrame,
    sentinel2_training_features_image: Any,
    sentinel2_training_features_config: dict,
) -> pd.DataFrame:
    """Extrae variables Sentinel-2 para los puntos de prueba."""
    return sample_points_from_image(
        points=testing_labeled_points,
        image=sentinel2_training_features_image,
        params=sentinel2_training_features_config["sentinel2_training_features"],
        dataset_name="testing",
    )
