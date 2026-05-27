import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    predict_random_forest,
)


def predict_mining_binary_random_forest(
    mining_binary_random_forest_model: RandomForestClassifier,
    mining_binary_testing_dataset: dict,
    mining_binary_random_forest_config: dict,
) -> pd.DataFrame:
    """Predice Mineria vs No Mineria para el conjunto de prueba."""
    return predict_random_forest(
        model=mining_binary_random_forest_model,
        testing_dataset=mining_binary_testing_dataset,
        params=mining_binary_random_forest_config,
    )
