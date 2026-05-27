import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    feature_importance_table,
)


def build_mining_binary_feature_importance(
    mining_binary_random_forest_model: RandomForestClassifier,
    mining_binary_random_forest_config: dict,
) -> pd.DataFrame:
    """Construye la tabla de importancia de variables."""
    return feature_importance_table(
        model=mining_binary_random_forest_model,
        params=mining_binary_random_forest_config,
    )
