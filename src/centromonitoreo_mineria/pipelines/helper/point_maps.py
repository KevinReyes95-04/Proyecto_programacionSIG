from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
from shapely.geometry import box

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from centromonitoreo_mineria.pipelines.helper.spatial_background import (
    add_sentinel2_background,
)


# Funcion para dibujar puntos etiquetados sobre fondo Sentinel-2 o mapa base.
def plot_points_map(
    points: gpd.GeoDataFrame,
    output_path: Path,
    title: str,
    label_column: str,
    plot_params: dict[str, Any],
    bounds: Any | None = None,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    use_sentinel2_background = plot_params.get("sentinel2_background", {}).get("enabled", False)
    use_basemap = plot_params.get("use_basemap", True) and not use_sentinel2_background
    plot_points = points.to_crs(epsg=3857) if use_basemap else points
    plot_bounds = (
        _project_bounds(bounds, points.crs, use_basemap)
        if bounds is not None
        else plot_points.total_bounds
    )

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
    if bounds is not None and not use_sentinel2_background:
        axis.set_xlim(plot_bounds[0], plot_bounds[2])
        axis.set_ylim(plot_bounds[1], plot_bounds[3])

    basemap_metadata = _add_basemap(axis, plot_params) if use_basemap else _empty_basemap_metadata()
    axis.set_title(title)
    axis.set_xlabel("Longitud" if not use_basemap else "Coordenada X Web Mercator")
    axis.set_ylabel("Latitud" if not use_basemap else "Coordenada Y Web Mercator")
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


# Funcion para proyectar limites comunes al CRS del mapa.
def _project_bounds(bounds: Any, source_crs: Any, use_basemap: bool) -> Any:
    if not use_basemap:
        return bounds
    return gpd.GeoSeries([box(*bounds)], crs=source_crs).to_crs(epsg=3857).total_bounds


# Funcion para agregar mapa base si la configuracion lo pide.
def _add_basemap(axis: Any, plot_params: dict[str, Any]) -> dict[str, Any]:
    source_name = plot_params.get("basemap_source", "CartoDB.Positron")
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


# Funcion para devolver metadatos cuando no se usa mapa base.
def _empty_basemap_metadata() -> dict[str, Any]:
    return {
        "basemap_requested": False,
        "basemap_added": False,
        "basemap_source": None,
        "basemap_error": None,
    }
