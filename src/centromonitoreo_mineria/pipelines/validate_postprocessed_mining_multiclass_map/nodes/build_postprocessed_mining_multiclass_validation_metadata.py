from datetime import datetime, timezone
from typing import Any

import pandas as pd


# Funcion para resumir la validacion del mapa multiclase postprocesado.
def build_postprocessed_mining_multiclass_validation_metadata(
    postprocessed_mining_multiclass_point_validation: pd.DataFrame,
    postprocessed_mining_multiclass_map_validation_metrics: dict[str, Any],
    postprocessed_mining_multiclass_validation_confusion_matrix_plot_metadata: dict[str, Any],
    postprocessed_mining_multiclass_validation_map_metadata: dict[str, Any],
    postprocessed_mining_multiclass_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_labels": postprocessed_mining_multiclass_map_validation_config["class_labels"],
        "total_points": int(len(postprocessed_mining_multiclass_point_validation)),
        "valid_points": int(postprocessed_mining_multiclass_map_validation_metrics["valid_points"]),
        "accuracy": postprocessed_mining_multiclass_map_validation_metrics["accuracy"],
        "f1_macro": postprocessed_mining_multiclass_map_validation_metrics["f1_macro"],
        "confusion_matrix_plot": postprocessed_mining_multiclass_validation_confusion_matrix_plot_metadata,
        "validation_map": postprocessed_mining_multiclass_validation_map_metadata,
    }

