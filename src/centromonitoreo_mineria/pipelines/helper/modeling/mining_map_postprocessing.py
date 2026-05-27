from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import matplotlib
import numpy as np
import pandas as pd
import rasterio
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
from rasterio import features
from shapely.geometry import shape

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def validate_mining_binary_map_postprocessing_params(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_postprocessing debe ser un diccionario.")
    _require_text(params.get("classification_map"), "mining_binary_map_postprocessing.classification_map")
    _require_text(params.get("class_label"), "mining_binary_map_postprocessing.class_label")
    _require_text(params.get("negative_label"), "mining_binary_map_postprocessing.negative_label")
    _require_integer(params.get("class_value"), "mining_binary_map_postprocessing.class_value")
    _require_integer(params.get("negative_value"), "mining_binary_map_postprocessing.negative_value")
    _require_integer(params.get("class_nodata"), "mining_binary_map_postprocessing.class_nodata")
    _require_non_negative_number(params.get("min_area_ha"), "mining_binary_map_postprocessing.min_area_ha")
    if params.get("connectivity") not in {4, 8}:
        raise ValueError("mining_binary_map_postprocessing.connectivity debe ser 4 u 8.")
    _validate_outputs(params.get("outputs", {}))
    _validate_map_params(params.get("map", {}))
    return dict(params)


def postprocess_mining_binary_map(params: dict[str, Any]) -> dict[str, Any]:
    classification_path = Path(params["classification_map"])
    if not classification_path.exists():
        raise FileNotFoundError(f"No existe el mapa clasificado: {classification_path.as_posix()}")

    with rasterio.open(classification_path) as source:
        class_map = source.read(1)
        profile = source.profile.copy()
        polygons, all_patches = _extract_mining_polygons(class_map, source.transform, source.crs, params)
        filtered = polygons[polygons["area_ha"] >= float(params["min_area_ha"])].copy()
        postprocessed = _rasterize_polygons(filtered, class_map, source.transform, params)
        metadata = _write_outputs(filtered, postprocessed, profile, source.bounds, source.crs, params)

    original_pixels = int(np.sum(class_map == int(params["class_value"])))
    kept_pixels = int(np.sum(postprocessed == int(params["class_value"])))
    pixel_area_ha = _pixel_area_ha(profile["transform"])
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification_map": classification_path.as_posix(),
        "postprocessed_classification_map": metadata["postprocessed_classification_map"],
        "polygons": metadata["polygons"],
        "polygon_summary_csv": metadata["polygon_summary_csv"],
        "vector_write_status": metadata["vector_write_status"],
        "class_label": params["class_label"],
        "negative_label": params["negative_label"],
        "min_area_ha": float(params["min_area_ha"]),
        "connectivity": int(params["connectivity"]),
        "original_patches": int(len(all_patches)),
        "kept_patches": int(len(filtered)),
        "removed_patches": int(len(all_patches) - len(filtered)),
        "original_mining_pixels": original_pixels,
        "kept_mining_pixels": kept_pixels,
        "removed_mining_pixels": original_pixels - kept_pixels,
        "pixel_area_ha": pixel_area_ha,
        "kept_area_ha": float(kept_pixels * pixel_area_ha),
        "raster": metadata["raster"],
    }


def plot_postprocessed_mining_map(postprocessing_metadata: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    map_params = params.get("map", {})
    output_path = Path(map_params.get("output_path", "data/08_reporting/mining_binary_postprocessed_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(postprocessing_metadata["postprocessed_classification_map"]) as source:
        class_map = source.read(1)
        extent = [source.bounds.left, source.bounds.right, source.bounds.bottom, source.bounds.top]
        crs = source.crs.to_string() if source.crs else "CRS no definido"

    figure, axis = plt.subplots(figsize=tuple(map_params.get("figure_size", [9, 9])))
    _draw_class_map(axis, class_map, extent, params)
    _style_cartographic_axis(axis, extent, map_params, crs, postprocessing_metadata)
    layout = map_params.get("layout", {})
    figure.subplots_adjust(
        left=float(layout.get("left", 0.11)),
        right=float(layout.get("right", 0.97)),
        bottom=float(layout.get("bottom", 0.12)),
        top=float(layout.get("top", 0.92)),
    )
    figure.savefig(output_path, dpi=int(map_params.get("dpi", 180)), bbox_inches="tight")
    plt.close(figure)
    return {
        "output_path": output_path.as_posix(),
        "title": map_params.get("title", "Mapa postprocesado de mineria"),
        "grid": bool(map_params.get("grid", {}).get("enabled", True)),
        "north_arrow": bool(map_params.get("north_arrow", {}).get("enabled", True)),
        "scale_bar": bool(map_params.get("scale_bar", {}).get("enabled", True)),
    }


def build_mining_binary_map_postprocessing_metadata(
    postprocessing_metadata: dict[str, Any],
    plot_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "class_label": params["class_label"],
        "negative_label": params["negative_label"],
        "min_area_ha": float(params["min_area_ha"]),
        "postprocessing": postprocessing_metadata,
        "map": plot_metadata,
    }


def _extract_mining_polygons(class_map: np.ndarray, transform: Any, crs: Any, params: dict[str, Any]) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    mask = class_map == int(params["class_value"])
    records = []
    geometries = []
    for patch_id, (geometry, value) in enumerate(features.shapes(mask.astype("uint8"), mask=mask, transform=transform, connectivity=int(params["connectivity"])), start=1):
        if int(value) != 1:
            continue
        geom = shape(geometry)
        geometries.append(geom)
        records.append(
            {
                "polygon_id": patch_id,
                "class_label": params["class_label"],
                "area_m2": float(geom.area),
                "area_ha": float(geom.area / 10000),
                "perimeter_m": float(geom.length),
            }
        )
    polygons = gpd.GeoDataFrame(records, geometry=geometries, crs=crs)
    return polygons, polygons.copy()


def _rasterize_polygons(polygons: gpd.GeoDataFrame, class_map: np.ndarray, transform: Any, params: dict[str, Any]) -> np.ndarray:
    nodata = int(params["class_nodata"])
    output = np.where(class_map == nodata, nodata, int(params["negative_value"])).astype("uint8")
    if polygons.empty:
        return output
    shapes = [(geometry, int(params["class_value"])) for geometry in polygons.geometry]
    burned = features.rasterize(
        shapes,
        out_shape=class_map.shape,
        fill=0,
        transform=transform,
        dtype="uint8",
        all_touched=bool(params.get("all_touched", False)),
    )
    output[burned == int(params["class_value"])] = int(params["class_value"])
    return output


def _write_outputs(polygons: gpd.GeoDataFrame, postprocessed: np.ndarray, profile: dict[str, Any], bounds: Any, crs: Any, params: dict[str, Any]) -> dict[str, Any]:
    outputs = params["outputs"]
    raster_path = Path(outputs["postprocessed_classification_map"])
    polygon_path = Path(outputs["polygons"])
    csv_path = Path(outputs["polygon_summary_csv"])
    for path in [raster_path, polygon_path, csv_path]:
        path.parent.mkdir(parents=True, exist_ok=True)

    raster_profile = profile.copy()
    raster_profile.update(dtype="uint8", count=1, nodata=int(params["class_nodata"]), compress="lzw", BIGTIFF="IF_SAFER")
    raster_profile.pop("blockxsize", None)
    raster_profile.pop("blockysize", None)
    with rasterio.open(raster_path, "w", **raster_profile) as target:
        target.write(postprocessed, 1)

    vector_write_status = _write_polygons(polygons, polygon_path, outputs)
    _polygon_summary(polygons).to_csv(csv_path, index=False)

    return {
        "postprocessed_classification_map": raster_path.as_posix(),
        "polygons": polygon_path.as_posix(),
        "polygon_summary_csv": csv_path.as_posix(),
        "vector_write_status": vector_write_status,
        "raster": {
            "shape": [int(postprocessed.shape[0]), int(postprocessed.shape[1])],
            "crs": crs.to_string() if crs else None,
            "bounds": {"left": bounds.left, "bottom": bounds.bottom, "right": bounds.right, "top": bounds.top},
        },
    }


def _polygon_summary(polygons: gpd.GeoDataFrame) -> pd.DataFrame:
    if polygons.empty:
        return pd.DataFrame(columns=["polygon_id", "class_label", "area_m2", "area_ha", "perimeter_m", "centroid_x", "centroid_y"])
    summary = polygons.drop(columns="geometry").copy()
    centroids = polygons.geometry.centroid
    summary["centroid_x"] = centroids.x
    summary["centroid_y"] = centroids.y
    return summary.sort_values("area_ha", ascending=False).reset_index(drop=True)


def _draw_class_map(axis: Any, class_map: np.ndarray, extent: list[float], params: dict[str, Any]) -> None:
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


def _style_cartographic_axis(axis: Any, extent: list[float], map_params: dict[str, Any], crs: str, metadata: dict[str, Any]) -> None:
    axis.set_xlim(extent[0], extent[1])
    axis.set_ylim(extent[2], extent[3])
    axis.set_aspect("equal")
    axis.set_title(map_params.get("title", "Mapa postprocesado de mineria"), fontsize=int(map_params.get("title_font_size", 14)), weight="bold")
    axis.set_xlabel(map_params.get("x_label", "Este (m)"))
    axis.set_ylabel(map_params.get("y_label", "Norte (m)"))
    axis.ticklabel_format(style="plain", useOffset=False)
    if map_params.get("grid", {}).get("enabled", True):
        grid = map_params.get("grid", {})
        axis.grid(True, color=grid.get("color", "#303030"), alpha=float(grid.get("alpha", 0.35)), linewidth=float(grid.get("linewidth", 0.6)))
    if map_params.get("north_arrow", {}).get("enabled", True):
        _add_north_arrow(axis, map_params.get("north_arrow", {}))
    if map_params.get("scale_bar", {}).get("enabled", True):
        _add_scale_bar(axis, extent, map_params.get("scale_bar", {}))
    _add_map_note(axis, map_params, crs, metadata)


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
    axis.plot([x0 + length, x0 + length], [y0 - height * 0.005, y0 + height * 0.005], color="black", linewidth=2)
    axis.text(x0 + length / 2, y0 + height * 0.012, _format_distance(length), ha="center", va="bottom", fontsize=int(params.get("font_size", 10)), weight="bold")


def _add_map_note(axis: Any, map_params: dict[str, Any], crs: str, metadata: dict[str, Any]) -> None:
    note = map_params.get("note")
    if not note:
        note = f"CRS: {_short_crs_label(crs)} | Mineria: {metadata['kept_area_ha']:.2f} ha | Unidad minima: {metadata['min_area_ha']:.2f} ha"
    axis.text(0.01, -0.09, note, transform=axis.transAxes, ha="left", va="top", fontsize=int(map_params.get("note_font_size", 8)))


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


def _pixel_area_ha(transform: Any) -> float:
    return float(abs(transform.a * transform.e) / 10000)


def _validate_outputs(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("mining_binary_map_postprocessing.outputs debe ser un diccionario.")
    for key in ("postprocessed_classification_map", "polygons", "polygon_summary_csv"):
        _require_text(outputs.get(key), f"mining_binary_map_postprocessing.outputs.{key}")


def _vector_driver(path: Path) -> str:
    return "GeoJSON" if path.suffix.lower() in {".geojson", ".json"} else "GPKG"


def _write_polygons(polygons: gpd.GeoDataFrame, polygon_path: Path, outputs: dict[str, Any]) -> str:
    layer = outputs.get("polygon_layer", "mining_binary_polygons")
    driver = _vector_driver(polygon_path)
    try:
        if driver == "GPKG":
            _remove_existing_vector(polygon_path)
            polygons.to_file(polygon_path, layer=layer, driver=driver)
        else:
            polygons.to_file(polygon_path, driver=driver)
        return "written"
    except PermissionError:
        if polygon_path.exists() and polygon_path.stat().st_size > 0:
            return "reused_existing_locked_file"
        raise


def _remove_existing_vector(path: Path) -> None:
    for candidate in [path, Path(f"{path}-wal"), Path(f"{path}-shm")]:
        if candidate.exists():
            candidate.unlink()


def _validate_map_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_map_postprocessing.map debe ser un diccionario.")
    if "output_path" in params:
        _require_text(params["output_path"], "mining_binary_map_postprocessing.map.output_path")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def _require_integer(value: Any, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} debe ser entero.")


def _require_non_negative_number(value: Any, name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} debe ser un numero mayor o igual a cero.")
