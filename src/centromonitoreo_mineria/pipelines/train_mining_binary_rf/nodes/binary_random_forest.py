"""Compatibilidad para imports antiguos del Random Forest binario."""

from .build_mining_binary_datasets import build_binary_dataset
from .build_mining_binary_feature_importance import (
    build_mining_binary_feature_importance as feature_importance_table,
)
from .build_mining_binary_random_forest_metadata import (
    build_mining_binary_random_forest_metadata as build_model_metadata,
)
from .evaluate_mining_binary_random_forest import (
    evaluate_mining_binary_random_forest as evaluate_binary_predictions,
)
from .plot_mining_binary_confusion_matrix import (
    plot_mining_binary_confusion_matrix as plot_confusion_matrix,
)
from .plot_mining_binary_feature_importance import (
    plot_mining_binary_feature_importance as plot_feature_importance,
)
from .predict_mining_binary_random_forest import (
    predict_mining_binary_random_forest,
)
from .train_mining_binary_random_forest import (
    train_mining_binary_random_forest as train_random_forest,
)
from .validate_mining_binary_random_forest_config import (
    validate_mining_binary_random_forest_config as validate_binary_random_forest_params,
)


# Funcion para mantener compatible el nombre antiguo de prediccion.
def predict_random_forest(model, testing_dataset, params):
    return predict_mining_binary_random_forest(
        mining_binary_random_forest_model=model,
        mining_binary_testing_dataset=testing_dataset,
        mining_binary_random_forest_config=params,
    )
