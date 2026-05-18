from datetime import datetime, timezone
from typing import Any
import geopandas as gpd
import pandas as pd

def build_training_data_metadata(
    labeled_points: gpd.GeoDataFrame,
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    spatial_plot_metadata: dict[str, Any],
    class_distribution_plot_metadata: dict[str, Any],
    training_testing_spatial_plot_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Construye metadatos reproducibles del particionamiento."""
    label_column = params["label_column"]
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": params["labeled_points_path"],
        "label_column": label_column,
        "target_crs": params.get("target_crs"),
        "total_points": int(len(labeled_points)),
        "training_points": int(len(training_labeled_points)),
        "testing_points": int(len(testing_labeled_points)),
        "test_size": params.get("test_size", 0.2),
        "random_state": params.get("random_state", 42),
        "stratify": params.get("stratify", True),
        "class_counts": labeled_points[label_column].value_counts().to_dict(),
        "spatial_plot": spatial_plot_metadata,
        "class_distribution_plot": class_distribution_plot_metadata,
        "training_testing_spatial_plot": training_testing_spatial_plot_metadata,
    }
