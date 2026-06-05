from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
from shapely.geometry import box

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from centromonitoreo_mineria.pipelines.helper.spatial_background import (
    add_sentinel2_background,
)
from centromonitoreo_mineria.pipelines.helper.class_colors import (
    CLASS_COLORS,
    FALLBACK_CLASS_COLORS,
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
    class_colors = _class_colors(plot_params)
    plotted_classes = _plot_classes(axis, plot_points, label_column, plot_params, class_colors)
    if bounds is not None and not use_sentinel2_background:
        axis.set_xlim(plot_bounds[0], plot_bounds[2])
        axis.set_ylim(plot_bounds[1], plot_bounds[3])

    basemap_metadata = _add_basemap(axis, plot_params) if use_basemap else _empty_basemap_metadata()
    axis.set_title(title)
    axis.set_xlabel("Longitud" if not use_basemap else "Coordenada X Web Mercator")
    axis.set_ylabel("Latitud" if not use_basemap else "Coordenada Y Web Mercator")
    axis.grid(True, alpha=0.25)
    _add_legend(axis, plotted_classes, class_colors, plot_params)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)

    return {
        "output_path": output_path.as_posix(),
        "point_count": int(len(points)),
        "class_counts": points[label_column].value_counts().to_dict(),
        "class_colors": {class_name: class_colors[class_name] for class_name in plotted_classes},
        **basemap_metadata,
        **sentinel2_background_metadata,
    }


# Funcion para graficar cada clase con un color fijo y sin repetir paleta.
def _plot_classes(
    axis: Any,
    plot_points: gpd.GeoDataFrame,
    label_column: str,
    plot_params: dict[str, Any],
    class_colors: dict[str, str],
) -> list[str]:
    plotted_classes = _ordered_classes(plot_points, label_column, plot_params)
    for index, class_name in enumerate(plotted_classes):
        if class_name not in class_colors:
            class_colors[class_name] = FALLBACK_CLASS_COLORS[index % len(FALLBACK_CLASS_COLORS)]
        subset = plot_points[plot_points[label_column] == class_name]
        subset.plot(
            ax=axis,
            color=class_colors[class_name],
            markersize=plot_params.get("point_size", 28),
            alpha=plot_params.get("alpha", 0.9),
            edgecolor=plot_params.get("point_edgecolor", "black"),
            linewidth=plot_params.get("point_linewidth", 0.55),
            label=class_name,
        )
    return plotted_classes


# Funcion para resolver colores de clase desde la configuracion.
def _class_colors(plot_params: dict[str, Any]) -> dict[str, str]:
    configured_colors = plot_params.get("class_colors", {})
    return CLASS_COLORS | configured_colors


# Funcion para ordenar las clases de la leyenda y del dibujo.
def _ordered_classes(
    points: gpd.GeoDataFrame,
    label_column: str,
    plot_params: dict[str, Any],
) -> list[str]:
    classes = list(points[label_column].dropna().unique())
    class_order = plot_params.get("class_order") or list(CLASS_COLORS)
    ordered = [class_name for class_name in class_order if class_name in classes]
    ordered += sorted(class_name for class_name in classes if class_name not in ordered)
    return ordered


# Funcion para construir una leyenda con marcadores del mismo tamano visual.
def _add_legend(
    axis: Any,
    plotted_classes: list[str],
    class_colors: dict[str, str],
    plot_params: dict[str, Any],
) -> None:
    marker_size = plot_params.get("legend_marker_size", 9)
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            label=class_name,
            markerfacecolor=class_colors[class_name],
            markeredgecolor=plot_params.get("point_edgecolor", "black"),
            markeredgewidth=plot_params.get("point_linewidth", 0.55),
            markersize=marker_size,
            alpha=plot_params.get("alpha", 0.9),
        )
        for class_name in plotted_classes
    ]
    axis.legend(handles=handles, loc=plot_params.get("legend_location", "lower left"), framealpha=0.78)


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
