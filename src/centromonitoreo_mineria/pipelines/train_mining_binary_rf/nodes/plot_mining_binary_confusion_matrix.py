from pathlib import Path
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Funcion para guardar la matriz de confusion como PNG.
def plot_mining_binary_confusion_matrix(
    mining_binary_metrics: dict[str, Any],
    mining_binary_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    plot_params = mining_binary_random_forest_config.get("confusion_matrix_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_confusion_matrix.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = np.array(mining_binary_metrics["confusion_matrix"])
    labels = mining_binary_metrics["labels"]
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [6, 5])))
    image = axis.imshow(matrix, cmap=plot_params.get("cmap", "Blues"))
    axis.figure.colorbar(image, ax=axis)
    axis.set_xticks(range(len(labels)), labels=labels)
    axis.set_yticks(range(len(labels)), labels=labels)
    axis.set_xlabel(plot_params.get("x_label", "Prediccion"))
    axis.set_ylabel(plot_params.get("y_label", "Observado"))
    axis.set_title(plot_params.get("title", "Matriz de confusion"))
    _annotate_matrix(axis, matrix)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "labels": labels}


# Funcion para escribir los valores dentro de la matriz.
def _annotate_matrix(axis: Any, matrix: np.ndarray) -> None:
    threshold = matrix.max() / 2 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            color = "white" if matrix[row, column] > threshold else "black"
            axis.text(column, row, str(matrix[row, column]), ha="center", va="center", color=color)
