from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.map_overlays import (
    map_figure,
    map_output_path,
    plot_probability_base,
    save_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.point_layers import (
    plot_points_by_label,
    project_points,
)


# Funcion para graficar probabilidad de mineria con puntos de prueba.
def plot_probability_points_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_binary_map_validation_config
    plot_params = params.get("probability_points_plot", {})
    output_path = map_output_path(
        plot_params,
        "data/08_reporting/mining_binary_probability_points.png",
    )

    figure, axis = map_figure(plot_params)
    _, _, crs = plot_probability_base(axis, figure, mining_binary_map_metadata, params, plot_params)
    testing = project_points(mining_binary_predictions, crs, params)
    plot_points_by_label(
        axis,
        testing,
        params["label_column"],
        params,
        marker="o",
        size=plot_params.get("point_size", 20),
        alpha=0.9,
    )
    save_map(axis, figure, output_path, plot_params, "Probabilidad de mineria con puntos de prueba")
    return {"output_path": output_path.as_posix(), "testing_points": int(len(testing))}
