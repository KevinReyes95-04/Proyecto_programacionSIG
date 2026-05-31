from datetime import datetime, timezone
from typing import Any


# Funcion para resumir configuracion, datos y resultados del modelo.
def build_mining_binary_random_forest_metadata(
    mining_binary_training_dataset: dict[str, Any],
    mining_binary_testing_dataset: dict[str, Any],
    mining_binary_metrics: dict[str, Any],
    mining_binary_confusion_matrix_plot_metadata: dict[str, Any],
    mining_binary_feature_importance_plot_metadata: dict[str, Any],
    mining_binary_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_binary_random_forest_config
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": "RandomForestClassifier",
        "label_column": params["label_column"],
        "positive_label": params["positive_label"],
        "negative_label": params["negative_label"],
        "negative_source_labels": params["negative_source_labels"],
        "feature_columns": params["feature_columns"],
        "classification_threshold": params.get("classification_threshold", 0.5),
        "random_forest": params.get("random_forest", {}),
        "training_rows": int(len(mining_binary_training_dataset["source"])),
        "testing_rows": int(len(mining_binary_testing_dataset["source"])),
        "training_target_counts": mining_binary_training_dataset["y"].value_counts().to_dict(),
        "testing_target_counts": mining_binary_testing_dataset["y"].value_counts().to_dict(),
        "metrics": mining_binary_metrics,
        "confusion_matrix_plot": mining_binary_confusion_matrix_plot_metadata,
        "feature_importance_plot": mining_binary_feature_importance_plot_metadata,
    }
