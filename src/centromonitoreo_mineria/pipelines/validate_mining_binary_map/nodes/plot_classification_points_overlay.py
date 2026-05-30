from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd
from rasterio.enums import Resampling

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.figure_output import (
    finish_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.point_layers import (
    plot_points_by_label,
    project_points,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.raster_layers import (
    classification_path,
    plot_mining_overlay,
    plot_rgb_background,
    read_raster_for_plot,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_classification_points_overlay(
    training_sentinel2_features: pd.DataFrame,
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    """Grafica el mapa clasificado con puntos de entrenamiento y prueba."""
    params = mining_binary_map_validation_config
    plot_params = params.get("classification_points_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/mining_binary_classification_points.png",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    class_map, extent, crs = read_raster_for_plot(
        classification_path(mining_binary_map_metadata),
        params,
        Resampling.nearest,
    )
    training = project_points(training_sentinel2_features, crs, params)
    testing = project_points(mining_binary_predictions, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    plot_rgb_background(axis, mining_binary_map_metadata, params, class_map.shape, extent)
    plot_mining_overlay(axis, class_map, extent, params, plot_params)
    plot_points_by_label(
        axis,
        training,
        params["label_column"],
        params,
        marker="o",
        size=plot_params.get("training_point_size", 12),
        alpha=0.75,
    )
    plot_points_by_label(
        axis,
        testing,
        params["label_column"],
        params,
        marker="^",
        size=plot_params.get("testing_point_size", 18),
        alpha=0.95,
    )
    finish_map(axis, figure, output_path, plot_params, "Clasificacion binaria con puntos")
    plt.close(figure)
    return {
        "output_path": output_path.as_posix(),
        "training_points": int(len(training)),
        "testing_points": int(len(testing)),
    }
