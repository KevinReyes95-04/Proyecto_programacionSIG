from datetime import datetime, timezone
from typing import Any


# Funcion para resumir las salidas del entrenamiento multiclase.
def build_mining_multiclass_random_forest_metadata(
    mining_multiclass_training_dataset: dict[str, Any],
    mining_multiclass_testing_dataset: dict[str, Any],
    mining_multiclass_metrics: dict[str, Any],
    mining_multiclass_confusion_matrix_plot_metadata: dict[str, Any],
    mining_multiclass_feature_importance_plot_metadata: dict[str, Any],
    mining_multiclass_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": "RandomForestClassifier",
        "classes": mining_multiclass_random_forest_config["class_labels"],
        "feature_columns": mining_multiclass_random_forest_config["feature_columns"],
        "training_rows": int(len(mining_multiclass_training_dataset["source"])),
        "testing_rows": int(len(mining_multiclass_testing_dataset["source"])),
        "metrics": mining_multiclass_metrics,
        "plots": {
            "confusion_matrix": mining_multiclass_confusion_matrix_plot_metadata,
            "feature_importance": mining_multiclass_feature_importance_plot_metadata,
        },
    }

