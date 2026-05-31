from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.map_overlays import (
    map_figure,
    map_output_path,
    plot_classification_base,
    save_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.point_layers import (
    plot_error_group,
    project_points,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.validation_errors import (
    error_groups,
)


# Funcion para graficar falsos positivos y falsos negativos sobre el mapa.
def plot_testing_errors_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_binary_map_validation_config
    plot_params = params.get("errors_plot", {})
    output_path = map_output_path(
        plot_params,
        "data/08_reporting/mining_binary_testing_errors.png",
    )

    figure, axis = map_figure(plot_params)
    _, _, crs = plot_classification_base(axis, mining_binary_map_metadata, params, plot_params)
    testing = project_points(mining_binary_predictions, crs, params)
    false_negatives, false_positives = error_groups(testing, params)

    axis.scatter(
        testing.geometry.x,
        testing.geometry.y,
        s=plot_params.get("context_point_size", 10),
        c="#ffffff",
        edgecolors="#333333",
        linewidths=0.3,
        alpha=0.65,
        label="Puntos test",
    )
    plot_error_group(axis, false_negatives, plot_params, "false_negative", "Mineria omitida")
    plot_error_group(axis, false_positives, plot_params, "false_positive", "Falso positivo")
    save_map(axis, figure, output_path, plot_params, "Errores sobre mapa clasificado")
    return {
        "output_path": output_path.as_posix(),
        "false_negatives": int(len(false_negatives)),
        "false_positives": int(len(false_positives)),
    }
