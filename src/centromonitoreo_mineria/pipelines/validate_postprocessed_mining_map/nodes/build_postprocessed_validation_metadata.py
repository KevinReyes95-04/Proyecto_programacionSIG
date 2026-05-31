from datetime import datetime, timezone
from typing import Any

import pandas as pd


# Funcion para construir metadatos finales de la validacion postprocesada.
def build_postprocessed_validation_metadata(
    point_validation: pd.DataFrame,
    class_summary: pd.DataFrame,
    plot_metadata: dict[str, Any],
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    status_counts = point_validation["validation_status"].value_counts().to_dict()
    testing = point_validation[point_validation["dataset_split"] == "testing"]
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "positive_label": params["positive_label"],
        "negative_label": params["negative_label"],
        "total_points": int(len(point_validation)),
        "training_points": int((point_validation["dataset_split"] == "training").sum()),
        "testing_points": int(len(testing)),
        "status_counts": {key: int(value) for key, value in status_counts.items()},
        "testing_status_counts": {key: int(value) for key, value in testing["validation_status"].value_counts().to_dict().items()},
        "class_summary_rows": int(len(class_summary)),
        "postprocessed_area_ha": postprocessing_metadata["postprocessing"]["kept_area_ha"],
        "polygons": postprocessing_metadata["postprocessing"]["polygons"],
        "plot": plot_metadata,
    }
