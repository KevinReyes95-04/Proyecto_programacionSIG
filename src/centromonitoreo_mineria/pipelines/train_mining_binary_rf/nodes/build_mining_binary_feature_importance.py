from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# Funcion para construir la tabla de importancia de variables.
def build_mining_binary_feature_importance(
    mining_binary_random_forest_model: RandomForestClassifier,
    mining_binary_random_forest_config: dict[str, Any],
) -> pd.DataFrame:
    feature_columns = mining_binary_random_forest_config["feature_columns"]
    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": mining_binary_random_forest_model.feature_importances_,
        }
    )
    return importance.sort_values("importance", ascending=False).reset_index(drop=True)
