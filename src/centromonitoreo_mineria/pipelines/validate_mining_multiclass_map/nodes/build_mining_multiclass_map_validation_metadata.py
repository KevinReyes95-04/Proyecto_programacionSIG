from datetime import datetime, timezone
from typing import Any

import pandas as pd


# Funcion para resumir la validacion espacial multiclase.
def build_mining_multiclass_map_validation_metadata(
    mining_multiclass_point_validation: pd.DataFrame,
    mining_multiclass_map_validation_metrics: dict[str, Any],
    mining_multiclass_validation_confusion_matrix_plot_metadata: dict[str, Any],
    mining_multiclass_validation_map_metadata: dict[str, Any],
    mining_multiclass_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_labels": mining_multiclass_map_validation_config["class_labels"],
        "total_points": int(len(mining_multiclass_point_validation)),
        "valid_points": int(mining_multiclass_map_validation_metrics["valid_points"]),
        "accuracy": mining_multiclass_map_validation_metrics["accuracy"],
        "f1_macro": mining_multiclass_map_validation_metrics["f1_macro"],
        "confusion_matrix_plot": mining_multiclass_validation_confusion_matrix_plot_metadata,
        "validation_map": mining_multiclass_validation_map_metadata,
    }

