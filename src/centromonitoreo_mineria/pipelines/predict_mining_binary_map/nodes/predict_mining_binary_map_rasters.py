from sklearn.ensemble import RandomForestClassifier

from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_prediction import (
    predict_mining_map_rasters,
)


def predict_mining_binary_map_rasters(
    mining_binary_random_forest_model: RandomForestClassifier,
    mining_binary_map_prediction_config: dict,
) -> dict:
    """Predice y guarda los rasters de clase y probabilidad."""
    return predict_mining_map_rasters(
        model=mining_binary_random_forest_model,
        params=mining_binary_map_prediction_config,
    )
