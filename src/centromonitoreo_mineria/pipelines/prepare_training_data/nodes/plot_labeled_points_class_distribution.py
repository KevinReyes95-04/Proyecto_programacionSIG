from itertools import cycle
from pathlib import Path
from textwrap import fill
from typing import Any

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_labeled_points_class_distribution(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    """Genera una grafica de cantidad de muestras por clase."""
    label_column = params["label_column"]
    plot_params = params.get("class_distribution_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/labeled_points_class_distribution.png",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    counts = _ordered_class_counts(labeled_points, label_column, plot_params)
    colors = _colors(plot_params.get("colors", []), len(counts))
    labels = [fill(label, width=plot_params.get("label_wrap_width", 16)) for label in counts.index]

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [10, 6])))
    bars = axis.bar(labels, counts.to_numpy(), color=colors)
    axis.bar_label(bars, padding=3, fontsize=plot_params.get("value_font_size", 9))
    axis.set_title(plot_params.get("title", "Conjunto de datos"))
    axis.set_xlabel(plot_params.get("x_label", "Cobertura"))
    axis.set_ylabel(plot_params.get("y_label", "Numero de muestras"))
    axis.grid(axis="y", alpha=0.3)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)

    return {
        "output_path": output_path.as_posix(),
        "label_column": label_column,
        "class_counts": counts.to_dict(),
    }


def _ordered_class_counts(
    labeled_points: gpd.GeoDataFrame, label_column: str, plot_params: dict[str, Any]
) -> Any:
    counts = labeled_points[label_column].value_counts()
    class_order = plot_params.get("class_order")
    if class_order:
        ordered_classes = [name for name in class_order if name in counts.index]
        ordered_classes += sorted(name for name in counts.index if name not in ordered_classes)
        return counts.loc[ordered_classes]
    return counts.sort_index().sort_values(ascending=False, kind="stable")


def _colors(colors: list[str], count: int) -> list[str]:
    default_colors = ["#8DD34F", "#0CB354", "#1379B9", "#FFC107", "#F5F500", "#18A8D8"]
    return [color for _, color in zip(range(count), cycle(colors or default_colors))]
