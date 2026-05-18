from pathlib import Path
from typing import Any
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_labeled_points_distribution(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    """Genera una grafica de distribucion espacial de puntos por clase."""
    label_column = params["label_column"]
    plot_params = params.get("spatial_plot", {})
    output_path = Path(
        plot_params.get(
            "output_path",
            "data/08_reporting/labeled_points_distribution.png",
        )
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    use_basemap = plot_params.get("use_basemap", True)
    plot_points = labeled_points.to_crs(epsg=3857) if use_basemap else labeled_points
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 8])))
    plot_points.plot(
        ax=axis,
        column=label_column,
        categorical=True,
        legend=True,
        markersize=plot_params.get("point_size", 12),
        alpha=plot_params.get("alpha", 0.8),
    )

    basemap_added = False
    basemap_error = None
    if use_basemap:
        try:
            import contextily as ctx

            source = ctx.providers
            for source_part in plot_params.get("basemap_source", "CartoDB.Positron").split("."):
                source = getattr(source, source_part)
            ctx.add_basemap(
                axis,
                source=source,
                zoom=plot_params.get("basemap_zoom", "auto"),
            )
            basemap_added = True
        except Exception as exc:
            basemap_error = str(exc)
            if plot_params.get("basemap_strict", False):
                raise RuntimeError("No se pudo agregar el mapa base.") from exc

    axis.set_title(
        plot_params.get("title", "Distribucion espacial de puntos etiquetados")
    )
    axis.set_xlabel("Longitud" if not use_basemap else "Coordenada X Web Mercator")
    axis.set_ylabel("Latitud" if not use_basemap else "Coordenada Y Web Mercator")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)

    return {
        "output_path": output_path.as_posix(),
        "label_column": label_column,
        "point_count": int(len(labeled_points)),
        "class_counts": labeled_points[label_column].value_counts().to_dict(),
        "basemap_requested": use_basemap,
        "basemap_added": basemap_added,
        "basemap_source": plot_params.get("basemap_source", "CartoDB.Positron"),
        "basemap_error": basemap_error,
    }
