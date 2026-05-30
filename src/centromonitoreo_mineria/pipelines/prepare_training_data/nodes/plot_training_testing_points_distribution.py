from pathlib import Path
from typing import Any
import geopandas as gpd
import pandas as pd
from centromonitoreo_mineria.pipelines.helper.point_maps import plot_points_map


# Funcion para graficar los puntos de entrenamiento y prueba por separado.
def plot_training_testing_points_distribution(
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    params: dict[str, Any],
) -> dict[str, Any]:
    label_column = params["label_column"]
    plot_params = {**params.get("spatial_plot", {}), **params.get("split_spatial_plot", {})}
    training_points = _to_geodataframe(training_labeled_points, params)
    testing_points = _to_geodataframe(testing_labeled_points, params)
    bounds = _combined_bounds(training_points, testing_points)

    return {
        "training": plot_points_map(
            training_points,
            Path(plot_params["training_output_path"]),
            plot_params.get("training_title", "Distribucion espacial - entrenamiento"),
            label_column,
            plot_params,
            bounds,
        ),
        "testing": plot_points_map(
            testing_points,
            Path(plot_params["testing_output_path"]),
            plot_params.get("testing_title", "Distribucion espacial - prueba"),
            label_column,
            plot_params,
            bounds,
        ),
    }


# Funcion para reconstruir un GeoDataFrame desde la tabla CSV de puntos.
def _to_geodataframe(points: pd.DataFrame, params: dict[str, Any]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(points["longitude"], points["latitude"]),
        crs=params.get("target_crs", "EPSG:4326"),
    )


# Funcion para calcular una extension comun para entrenamiento y prueba.
def _combined_bounds(
    training_points: gpd.GeoDataFrame, testing_points: gpd.GeoDataFrame
) -> Any:
    bounds = pd.DataFrame([training_points.total_bounds, testing_points.total_bounds])
    return [
        bounds[0].min(),
        bounds[1].min(),
        bounds[2].max(),
        bounds[3].max(),
    ]
