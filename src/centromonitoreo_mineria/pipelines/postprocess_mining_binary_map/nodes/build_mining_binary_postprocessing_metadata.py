from datetime import datetime, timezone
from typing import Any


def build_mining_binary_postprocessing_metadata(
    mining_binary_map_postprocessing_output_metadata: dict[str, Any],
    mining_binary_postprocessed_map_plot_metadata: dict[str, Any],
    mining_binary_map_postprocessing_config: dict[str, Any],
) -> dict[str, Any]:
    """Agrupa metadatos de postprocesamiento, configuracion y mapa final."""
    params = mining_binary_map_postprocessing_config
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_label": params["class_label"],
        "negative_label": params["negative_label"],
        "min_area_ha": float(params["min_area_ha"]),
        "postprocessing": mining_binary_map_postprocessing_output_metadata,
        "map": mining_binary_postprocessed_map_plot_metadata,
    }
