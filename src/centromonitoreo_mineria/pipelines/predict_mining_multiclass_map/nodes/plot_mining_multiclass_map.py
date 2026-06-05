from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import rasterio
from matplotlib.colors import ListedColormap

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from centromonitoreo_mineria.pipelines.helper.class_colors import CLASS_COLORS


# Funcion para guardar el mapa multiclase como PNG.
def plot_mining_multiclass_map(
    mining_multiclass_map_prediction_metadata: dict[str, Any],
    mining_multiclass_map_prediction_config: dict[str, Any],
) -> dict[str, Any]:
    params = mining_multiclass_map_prediction_config
    plot_params = params.get("visualization", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/predict_mining_multiclass_map/mining_multiclass_classification_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(mining_multiclass_map_prediction_metadata["classification_map"]) as source:
        class_map = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]

    labels = list(params["class_values"].keys())
    display = _display_array(class_map, labels, params)
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [9, 9])))
    image = axis.imshow(
        display,
        cmap=ListedColormap([plot_params.get("colors", {}).get(label, CLASS_COLORS.get(label, "#999999")) for label in labels]),
        extent=extent,
        vmin=-0.5,
        vmax=len(labels) - 0.5,
        interpolation="nearest",
    )
    colorbar = figure.colorbar(image, ax=axis, fraction=0.036, pad=0.02, ticks=range(len(labels)))
    colorbar.ax.set_yticklabels(labels)
    axis.set_title(plot_params.get("title", "Mapa multiclase de coberturas"))
    axis.set_axis_off()
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "classification_map": mining_multiclass_map_prediction_metadata["classification_map"]}


# Funcion para convertir valores raster en indices de colores.
def _display_array(class_map: np.ndarray, labels: list[str], params: dict[str, Any]) -> np.ndarray:
    display = np.full(class_map.shape, np.nan, dtype="float32")
    for index, label in enumerate(labels):
        display[class_map == int(params["class_values"][label])] = index
    return display

