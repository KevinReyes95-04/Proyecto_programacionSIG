from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd
from rasterio.enums import Resampling

from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.figure_output import (
    finish_map,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.point_layers import (
    plot_error_group,
    project_points,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.raster_layers import (
    classification_path,
    plot_mining_overlay,
    plot_rgb_background,
    read_raster_for_plot,
)
from centromonitoreo_mineria.pipelines.validate_mining_binary_map.utils.validation_errors import (
    error_groups,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_testing_errors_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    """Grafica falsos positivos y falsos negativos sobre el mapa clasificado."""
    params = mining_binary_map_validation_config
    plot_params = params.get("errors_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/mining_binary_testing_errors.png",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    class_map, extent, crs = read_raster_for_plot(
        classification_path(mining_binary_map_metadata),
        params,
        Resampling.nearest,
    )
    testing = project_points(mining_binary_predictions, crs, params)
    false_negatives, false_positives = error_groups(testing, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    plot_rgb_background(axis, mining_binary_map_metadata, params, class_map.shape, extent)
    plot_mining_overlay(axis, class_map, extent, params, plot_params)
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
    finish_map(axis, figure, output_path, plot_params, "Errores sobre mapa clasificado")
    plt.close(figure)
    return {
        "output_path": output_path.as_posix(),
        "false_negatives": int(len(false_negatives)),
        "false_positives": int(len(false_positives)),
    }
