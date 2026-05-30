from typing import Any

import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch


def draw_class_map(
    axis: Any,
    class_map: np.ndarray,
    extent: list[float],
    params: dict[str, Any],
) -> None:
    """Dibuja el raster binario postprocesado."""
    map_params = params.get("map", {})
    no_mining = map_params.get("no_mining_color", "#1A9850")
    mining = map_params.get("mining_color", "#E31A1C")
    nodata = int(params["class_nodata"])
    plot_data = np.ma.masked_where(class_map == nodata, class_map)
    cmap = ListedColormap([no_mining, mining])
    norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)
    axis.imshow(plot_data, cmap=cmap, norm=norm, extent=extent, interpolation="nearest")
    legend_items = [
        Patch(facecolor=no_mining, edgecolor="black", label=params["negative_label"]),
        Patch(facecolor=mining, edgecolor="black", label=params["class_label"]),
    ]
    axis.legend(handles=legend_items, loc=map_params.get("legend_location", "upper left"), frameon=True)


def style_cartographic_axis(
    axis: Any,
    extent: list[float],
    map_params: dict[str, Any],
    crs: str,
    metadata: dict[str, Any],
) -> None:
    """Aplica elementos cartograficos al mapa postprocesado."""
    axis.set_xlim(extent[0], extent[1])
    axis.set_ylim(extent[2], extent[3])
    axis.set_aspect("equal")
    axis.set_title(
        map_params.get("title", "Mapa postprocesado de mineria"),
        fontsize=int(map_params.get("title_font_size", 14)),
        weight="bold",
    )
    axis.set_xlabel(map_params.get("x_label", "Este (m)"))
    axis.set_ylabel(map_params.get("y_label", "Norte (m)"))
    axis.ticklabel_format(style="plain", useOffset=False)
    if map_params.get("grid", {}).get("enabled", True):
        _add_grid(axis, map_params.get("grid", {}))
    if map_params.get("north_arrow", {}).get("enabled", True):
        _add_north_arrow(axis, map_params.get("north_arrow", {}))
    if map_params.get("scale_bar", {}).get("enabled", True):
        _add_scale_bar(axis, extent, map_params.get("scale_bar", {}))
    _add_map_note(axis, map_params, crs, metadata)


def _add_grid(axis: Any, params: dict[str, Any]) -> None:
    axis.grid(
        True,
        color=params.get("color", "#303030"),
        alpha=float(params.get("alpha", 0.35)),
        linewidth=float(params.get("linewidth", 0.6)),
    )


def _add_north_arrow(axis: Any, params: dict[str, Any]) -> None:
    x = float(params.get("x", 0.93))
    y = float(params.get("y", 0.88))
    size = int(params.get("font_size", 13))
    axis.annotate(
        "N",
        xy=(x, y),
        xytext=(x, y - 0.12),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=size,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "linewidth": 1.8, "color": "black"},
    )


def _add_scale_bar(axis: Any, extent: list[float], params: dict[str, Any]) -> None:
    width = extent[1] - extent[0]
    height = extent[3] - extent[2]
    length = _nice_scale_length(width * float(params.get("fraction", 0.2)))
    x0 = extent[0] + width * float(params.get("x_fraction", 0.08))
    y0 = extent[2] + height * float(params.get("y_fraction", 0.07))
    axis.plot([x0, x0 + length], [y0, y0], color="black", linewidth=3)
    axis.plot([x0, x0], [y0 - height * 0.005, y0 + height * 0.005], color="black", linewidth=2)
    axis.plot(
        [x0 + length, x0 + length],
        [y0 - height * 0.005, y0 + height * 0.005],
        color="black",
        linewidth=2,
    )
    axis.text(
        x0 + length / 2,
        y0 + height * 0.012,
        _format_distance(length),
        ha="center",
        va="bottom",
        fontsize=int(params.get("font_size", 10)),
        weight="bold",
    )


def _add_map_note(
    axis: Any,
    map_params: dict[str, Any],
    crs: str,
    metadata: dict[str, Any],
) -> None:
    note = map_params.get("note")
    if not note:
        note = (
            f"CRS: {_short_crs_label(crs)} | Mineria: {metadata['kept_area_ha']:.2f} ha "
            f"| Unidad minima: {metadata['min_area_ha']:.2f} ha"
        )
    axis.text(
        0.01,
        -0.09,
        note,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=int(map_params.get("note_font_size", 8)),
    )


def _nice_scale_length(value: float) -> float:
    if value <= 0:
        return 1
    exponent = np.floor(np.log10(value))
    base = value / (10**exponent)
    nice_base = 1 if base < 2 else 2 if base < 5 else 5
    return float(nice_base * 10**exponent)


def _format_distance(meters: float) -> str:
    return f"{meters / 1000:g} km" if meters >= 1000 else f"{meters:g} m"


def _short_crs_label(crs: str) -> str:
    if "UTM zone 18N" in crs:
        return "WGS 84 / UTM zone 18N"
    if "EPSG:32618" in crs:
        return "EPSG:32618"
    return crs[:80]
