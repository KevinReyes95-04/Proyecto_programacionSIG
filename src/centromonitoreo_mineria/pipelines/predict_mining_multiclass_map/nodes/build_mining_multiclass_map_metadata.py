from datetime import datetime, timezone
from typing import Any


# Funcion para resumir las salidas del mapa multiclase.
def build_mining_multiclass_map_metadata(
    mining_multiclass_map_prediction_metadata: dict[str, Any],
    mining_multiclass_map_plot_metadata: dict[str, Any],
    mining_multiclass_map_prediction_config: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_values": mining_multiclass_map_prediction_config["class_values"],
        "raster_dir": mining_multiclass_map_prediction_config["raster_dir"],
        "prediction": mining_multiclass_map_prediction_metadata,
        "plot": mining_multiclass_map_plot_metadata,
    }

