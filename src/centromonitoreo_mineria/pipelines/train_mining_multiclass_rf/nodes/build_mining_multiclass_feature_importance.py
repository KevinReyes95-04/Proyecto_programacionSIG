from typing import Any

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


# Funcion para construir la tabla de importancia de variables.
def build_mining_multiclass_feature_importance(
    mining_multiclass_random_forest_model: RandomForestClassifier,
    mining_multiclass_random_forest_config: dict[str, Any],
) -> pd.DataFrame:
    importance = pd.DataFrame(
        {
            "feature": mining_multiclass_random_forest_config["feature_columns"],
            "importance": mining_multiclass_random_forest_model.feature_importances_,
        }
    )
    return importance.sort_values("importance", ascending=False).reset_index(drop=True)

