from datetime import datetime, timezone
from typing import Any

import pandas as pd


# Funcion para agrupar las salidas del postprocesamiento multiclase.
def build_mining_multiclass_postprocessing_metadata(
    mining_multiclass_map_postprocessing_output_metadata: dict[str, Any],
    mining_multiclass_postprocessed_class_summary: pd.DataFrame,
    mining_multiclass_postprocessed_map_plot_metadata: dict[str, Any],
    mining_multiclass_map_postprocessing_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_values": mining_multiclass_map_postprocessing_config["class_values"],
        "postprocessing": mining_multiclass_map_postprocessing_output_metadata,
        "class_summary": mining_multiclass_postprocessed_class_summary.to_dict(orient="records"),
        "plot": mining_multiclass_postprocessed_map_plot_metadata,
    }

