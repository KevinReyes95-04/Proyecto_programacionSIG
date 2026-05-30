from typing import Any
import geopandas as gpd
from centromonitoreo_mineria.pipelines.prepare_training_data.nodes.plot_labeled_points_class_distribution import plot_labeled_points_class_distribution
from centromonitoreo_mineria.pipelines.prepare_training_data.nodes.plot_labeled_points_distribution import plot_labeled_points_distribution


# Funcion para generar las graficas generales de los puntos etiquetados.
def plot_labeled_points_reports(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    return {
        "spatial": plot_labeled_points_distribution(labeled_points, params),
        "class_distribution": plot_labeled_points_class_distribution(labeled_points, params),
    }
