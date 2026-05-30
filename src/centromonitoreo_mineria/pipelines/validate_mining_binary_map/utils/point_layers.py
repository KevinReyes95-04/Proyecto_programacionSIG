from typing import Any

import geopandas as gpd
import pandas as pd


def project_points(
    points: pd.DataFrame,
    target_crs: Any,
    params: dict[str, Any],
) -> gpd.GeoDataFrame:
    """Convierte puntos tabulares a GeoDataFrame y los proyecta al CRS del raster."""
    coordinate_columns = params["coordinate_columns"]
    gdf = gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(
            points[coordinate_columns["longitude"]],
            points[coordinate_columns["latitude"]],
        ),
        crs=coordinate_columns["source_crs"],
    )
    return gdf.to_crs(target_crs) if target_crs else gdf


def plot_points_by_label(
    axis: Any,
    points: gpd.GeoDataFrame,
    label_column: str,
    params: dict[str, Any],
    marker: str,
    size: int,
    alpha: float,
) -> None:
    """Dibuja puntos categorizados por la etiqueta original."""
    colors = params.get("class_colors", {})
    for label in sorted(points[label_column].dropna().unique()):
        subset = points[points[label_column] == label]
        axis.scatter(
            subset.geometry.x,
            subset.geometry.y,
            s=size,
            marker=marker,
            c=colors.get(label, "#ffffff"),
            edgecolors="#111111",
            linewidths=0.35,
            alpha=alpha,
            label=str(label),
        )


def plot_error_group(
    axis: Any,
    points: gpd.GeoDataFrame,
    plot_params: dict[str, Any],
    key: str,
    label: str,
) -> None:
    """Dibuja un grupo de errores de validacion."""
    if points.empty:
        return
    style = plot_params.get(key, {})
    axis.scatter(
        points.geometry.x,
        points.geometry.y,
        s=style.get("point_size", 80),
        marker=style.get("marker", "X"),
        c=style.get("color", "#00FFFF"),
        edgecolors=style.get("edgecolor", "#000000"),
        linewidths=style.get("linewidth", 0.8),
        label=label,
    )
