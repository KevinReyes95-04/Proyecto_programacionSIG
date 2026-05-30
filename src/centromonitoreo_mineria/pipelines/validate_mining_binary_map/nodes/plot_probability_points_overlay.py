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
    probability_path,
    read_raster_for_plot,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_probability_points_overlay(
    mining_binary_predictions: pd.DataFrame,
    mining_binary_map_metadata: dict[str, Any],
    mining_binary_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    """Grafica la probabilidad de mineria con los puntos de prueba."""
    params = mining_binary_map_validation_config
    plot_params = params.get("probability_points_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/mining_binary_probability_points.png",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    probability, extent, crs = read_raster_for_plot(
        probability_path(mining_binary_map_metadata),
        params,
        Resampling.bilinear,
    )
    testing = project_points(mining_binary_predictions, crs, params)

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    image = axis.imshow(
        probability,
        extent=extent,
        cmap=plot_params.get("cmap", "viridis"),
        vmin=0,
        vmax=1,
    )
    figure.colorbar(
        image,
        ax=axis,
        fraction=0.036,
        pad=0.02,
        label=plot_params.get("colorbar_label", "Probabilidad Mineria"),
    )
    plot_points_by_label(
        axis,
        testing,
        params["label_column"],
        params,
        marker="o",
        size=plot_params.get("point_size", 20),
        alpha=0.9,
    )
    finish_map(axis, figure, output_path, plot_params, "Probabilidad de mineria con puntos de prueba")
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "testing_points": int(len(testing))}
