from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import pandas as pd
from shapely.geometry import box

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from centromonitoreo_mineria.pipelines.prepare_training_data.helpers.spatial_background import (
    add_sentinel2_background,
)


def plot_training_testing_points_distribution(
    training_labeled_points: pd.DataFrame,
    testing_labeled_points: pd.DataFrame,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Genera mapas separados para los puntos de entrenamiento y prueba."""
    label_column = params["label_column"]
    plot_params = {**params.get("spatial_plot", {}), **params.get("split_spatial_plot", {})}
    training_points = _to_geodataframe(training_labeled_points, params)
    testing_points = _to_geodataframe(testing_labeled_points, params)
    bounds = _combined_bounds(training_points, testing_points)

    return {
        "training": _plot_points(
            training_points,
            Path(plot_params["training_output_path"]),
            plot_params.get("training_title", "Distribucion espacial - entrenamiento"),
            label_column,
            plot_params,
            bounds,
        ),
        "testing": _plot_points(
            testing_points,
            Path(plot_params["testing_output_path"]),
            plot_params.get("testing_title", "Distribucion espacial - prueba"),
            label_column,
            plot_params,
            bounds,
        ),
    }


def _to_geodataframe(points: pd.DataFrame, params: dict[str, Any]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(points["longitude"], points["latitude"]),
        crs=params.get("target_crs", "EPSG:4326"),
    )


def _plot_points(
    points: gpd.GeoDataFrame,
    output_path: Path,
    title: str,
    label_column: str,
    plot_params: dict[str, Any],
    bounds: Any,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    use_sentinel2_background = plot_params.get("sentinel2_background", {}).get("enabled", False)
    use_basemap = plot_params.get("use_basemap", True) and not use_sentinel2_background
    plot_points = points.to_crs(epsg=3857) if use_basemap else points
    plot_bounds = gpd.GeoSeries([box(*bounds)], crs=points.crs)
    plot_bounds = plot_bounds.to_crs(epsg=3857).total_bounds if use_basemap else bounds

    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    sentinel2_background_metadata = add_sentinel2_background(
        axis=axis,
        plot_params=plot_params,
        target_crs=plot_points.crs,
        points_bounds=plot_bounds,
    )
    plot_points.plot(
        ax=axis,
        column=label_column,
        categorical=True,
        legend=True,
        markersize=plot_params.get("point_size", 12),
        alpha=plot_params.get("alpha", 0.8),
        edgecolor=plot_params.get("point_edgecolor", "black"),
        linewidth=plot_params.get("point_linewidth", 0.4),
    )
    if not use_sentinel2_background:
        axis.set_xlim(plot_bounds[0], plot_bounds[2])
        axis.set_ylim(plot_bounds[1], plot_bounds[3])
    basemap_metadata = _add_basemap(axis, plot_params) if use_basemap else _empty_basemap_metadata()
    axis.set_title(title)
    axis.set_xlabel("Coordenada X Web Mercator" if use_basemap else "Longitud")
    axis.set_ylabel("Coordenada Y Web Mercator" if use_basemap else "Latitud")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)

    return {
        "output_path": output_path.as_posix(),
        "point_count": int(len(points)),
        "class_counts": points[label_column].value_counts().to_dict(),
        **basemap_metadata,
        **sentinel2_background_metadata,
    }


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


def _add_basemap(axis: Any, plot_params: dict[str, Any]) -> dict[str, Any]:
    source_name = plot_params.get("basemap_source", "Esri.WorldImagery")
    try:
        import contextily as ctx

        source = ctx.providers
        for source_part in source_name.split("."):
            source = getattr(source, source_part)
        ctx.add_basemap(axis, source=source, zoom=plot_params.get("basemap_zoom", "auto"))
        return {
            "basemap_requested": True,
            "basemap_added": True,
            "basemap_source": source_name,
            "basemap_error": None,
        }
    except Exception as exc:
        if plot_params.get("basemap_strict", False):
            raise RuntimeError("No se pudo agregar el mapa base.") from exc
        return {
            "basemap_requested": True,
            "basemap_added": False,
            "basemap_source": source_name,
            "basemap_error": str(exc),
        }


def _empty_basemap_metadata() -> dict[str, Any]:
    return {
        "basemap_requested": False,
        "basemap_added": False,
        "basemap_source": None,
        "basemap_error": None,
    }
