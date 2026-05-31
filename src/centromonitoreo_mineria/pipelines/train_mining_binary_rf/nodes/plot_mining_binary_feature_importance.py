from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Funcion para guardar la importancia de variables como PNG.
def plot_mining_binary_feature_importance(
    mining_binary_feature_importance: pd.DataFrame,
    mining_binary_random_forest_config: dict[str, Any],
) -> dict[str, Any]:
    plot_params = mining_binary_random_forest_config.get("feature_importance_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_feature_importance.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_n = int(plot_params.get("top_n", 20))
    data = mining_binary_feature_importance.head(top_n).sort_values("importance")
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 7])))
    axis.barh(data["feature"], data["importance"], color=plot_params.get("color", "#1379B9"))
    axis.set_xlabel(plot_params.get("x_label", "Importancia"))
    axis.set_title(plot_params.get("title", "Importancia de variables"))
    axis.grid(axis="x", alpha=0.3)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "top_n": top_n}
