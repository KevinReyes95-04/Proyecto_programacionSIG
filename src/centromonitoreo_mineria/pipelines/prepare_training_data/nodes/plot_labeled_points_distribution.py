from pathlib import Path
from typing import Any
import geopandas as gpd
from centromonitoreo_mineria.pipelines.helper.point_maps import plot_points_map


# Funcion para graficar la distribucion espacial de todos los puntos etiquetados.
def plot_labeled_points_distribution(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    label_column = params["label_column"]
    plot_params = params.get("spatial_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/labeled_points_distribution.png",
        )
    )
    metadata = plot_points_map(
        labeled_points,
        output_path,
        plot_params.get("title", "Distribucion espacial de puntos etiquetados"),
        label_column,
        plot_params,
    )
    return {"label_column": label_column, **metadata}
