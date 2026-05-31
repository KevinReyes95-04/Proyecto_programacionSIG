from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.map_overlays import (
    map_figure,
    map_output_path,
    plot_classification_base,
    save_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.point_layers import (
    plot_points_by_label,
    project_points,
)


# Funcion para graficar mapa clasificado con puntos de entrenamiento y prueba.
def plot_classification_points_overlay(
    training_sentinel2_features: pd.DataFrame,
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_binary_map_validation_config
    plot_params = params.get("classification_points_plot", {})
    output_path = map_output_path(
        plot_params,
        "data/08_reporting/mining_binary_classification_points.png",
    )

    figure, axis = map_figure(plot_params)
    _, _, crs = plot_classification_base(axis, mining_binary_map_metadata, params, plot_params)
    training = project_points(training_sentinel2_features, crs, params)
    testing = project_points(mining_binary_predictions, crs, params)

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
    save_map(axis, figure, output_path, plot_params, "Clasificacion binaria con puntos")
    return {
        "output_path": output_path.as_posix(),
        "training_points": int(len(training)),
        "testing_points": int(len(testing)),
    }
