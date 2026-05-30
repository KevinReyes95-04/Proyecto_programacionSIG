from io import BytesIO
from math import ceil
from pathlib import Path
from typing import Any

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize


def build_sentinel2_spectral_index_maps(image: Any, region: Any, params: dict[str, Any]) -> dict[str, Any]:
    visualization_params = params.get("visualization", {})
    if not visualization_params.get("enabled", True):
        return {"enabled": False, "maps": {}, "combined_map": {"enabled": False}}

    output_dir = Path(visualization_params.get("output_dir", "data/08_reporting/sentinel2_spectral_indices_maps"))
    output_dir.mkdir(parents=True, exist_ok=True)
    maps_metadata = {}
    combined_tiles = []
    for index_name, index_config in params["indices"].items():
        if index_config.get("enabled", True):
            maps_metadata[index_name], tile = _build_index_map(
                image=image,
                region=region,
                index_name=index_name,
                index_config=index_config,
                visualization_params=visualization_params,
                output_dir=output_dir,
            )
            if tile:
                combined_tiles.append(tile)
    return {
        "enabled": True,
        "output_dir": output_dir.as_posix(),
        "maps": maps_metadata,
        "combined_map": _save_combined_map(combined_tiles, output_dir, visualization_params),
    }


def _build_index_map(
    image: Any,
    region: Any,
    index_name: str,
    index_config: dict[str, Any],
    visualization_params: dict[str, Any],
    output_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    style = visualization_params.get("default_style", {}) | visualization_params.get("indices", {}).get(index_name, {})
    output_path = output_dir / f"{index_name.lower()}_map.png"
    try:
        thumbnail = _download_thumbnail(image.select(index_name), region, style, visualization_params)
        _save_map_figure(thumbnail, output_path, index_name, index_config, style, visualization_params)
        metadata = {
            "output_path": output_path.as_posix(),
            "min": style["min"],
            "max": style["max"],
            "palette": style["palette"],
            "error": None,
        }
        return metadata, {"index": index_name, "thumbnail": thumbnail}
    except Exception as exc:
        if visualization_params.get("strict", False):
            raise RuntimeError(f"No se pudo graficar el indice {index_name}.") from exc
        return {
            "output_path": output_path.as_posix(),
            "min": style.get("min"),
            "max": style.get("max"),
            "palette": style.get("palette"),
            "error": str(exc),
        }, None


def _download_thumbnail(
    index_image: Any,
    region: Any,
    style: dict[str, Any],
    visualization_params: dict[str, Any],
) -> Any:
    get_thumb_url = getattr(index_image, "getThumbURL", None)
    if get_thumb_url is None:
        get_thumb_url = getattr(index_image, "getThumbUrl")
    url = get_thumb_url(
        {
            "region": region,
            "min": style["min"],
            "max": style["max"],
            "palette": style["palette"],
            "dimensions": visualization_params.get("dimensions", 1200),
            "format": visualization_params.get("format", "png"),
        }
    )
    response = requests.get(url, timeout=visualization_params.get("timeout_seconds", 120))
    response.raise_for_status()
    return plt.imread(BytesIO(response.content), format="png")


def _save_map_figure(
    thumbnail: Any,
    output_path: Path,
    index_name: str,
    index_config: dict[str, Any],
    style: dict[str, Any],
    visualization_params: dict[str, Any],
) -> None:
    figure, axis = plt.subplots(figsize=tuple(visualization_params.get("figure_size", [8, 8])))
    axis.imshow(thumbnail)
    axis.set_axis_off()
    axis.set_title(index_config.get("name") or index_name)
    colorbar = figure.colorbar(
        plt.cm.ScalarMappable(
            norm=Normalize(vmin=style["min"], vmax=style["max"]),
            cmap=ListedColormap(style["palette"]),
        ),
        ax=axis,
        orientation=visualization_params.get("colorbar_orientation", "vertical"),
        fraction=0.046,
        pad=0.04,
    )
    colorbar.set_label(index_name)
    figure.tight_layout()
    figure.savefig(output_path, dpi=visualization_params.get("dpi", 160))
    plt.close(figure)


def _save_combined_map(
    tiles: list[dict[str, Any]],
    output_dir: Path,
    visualization_params: dict[str, Any],
) -> dict[str, Any]:
    combined_params = visualization_params.get("combined_map", {})
    if not combined_params.get("enabled", True):
        return {"enabled": False}
    if not tiles:
        return {"enabled": False, "error": "No hay indices disponibles para el mapa combinado."}

    columns = int(combined_params.get("columns", min(4, len(tiles))))
    rows = ceil(len(tiles) / columns)
    output_path = Path(combined_params.get("output_path", output_dir / "all_indices_map.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=tuple(combined_params.get("figure_size", [4 * columns, 4 * rows])),
    )
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for axis, tile in zip(axes, tiles):
        axis.imshow(tile["thumbnail"])
        axis.set_title(tile["index"])
        axis.set_axis_off()
    for axis in axes[len(tiles):]:
        axis.set_axis_off()

    figure.tight_layout()
    figure.savefig(output_path, dpi=combined_params.get("dpi", visualization_params.get("dpi", 160)))
    plt.close(figure)
    return {
        "enabled": True,
        "output_path": output_path.as_posix(),
        "indices": [tile["index"] for tile in tiles],
        "rows": rows,
        "columns": columns,
        "error": None,
    }
