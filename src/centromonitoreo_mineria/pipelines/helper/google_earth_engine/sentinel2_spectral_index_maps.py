from io import BytesIO
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
        return {"enabled": False, "maps": {}}

    output_dir = Path(visualization_params.get("output_dir", "data/08_reporting/sentinel2_spectral_indices_maps"))
    output_dir.mkdir(parents=True, exist_ok=True)
    maps_metadata = {}
    for index_name, index_config in params["indices"].items():
        if index_config.get("enabled", True):
            maps_metadata[index_name] = _build_index_map(
                image=image,
                region=region,
                index_name=index_name,
                index_config=index_config,
                visualization_params=visualization_params,
                output_dir=output_dir,
            )
    return {"enabled": True, "output_dir": output_dir.as_posix(), "maps": maps_metadata}


def _build_index_map(
    image: Any,
    region: Any,
    index_name: str,
    index_config: dict[str, Any],
    visualization_params: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    style = visualization_params.get("default_style", {}) | visualization_params.get("indices", {}).get(index_name, {})
    output_path = output_dir / f"{index_name.lower()}_map.png"
    try:
        thumbnail = _download_thumbnail(image.select(index_name), region, style, visualization_params)
        _save_map_figure(thumbnail, output_path, index_name, index_config, style, visualization_params)
        return {
            "output_path": output_path.as_posix(),
            "min": style["min"],
            "max": style["max"],
            "palette": style["palette"],
            "error": None,
        }
    except Exception as exc:
        if visualization_params.get("strict", False):
            raise RuntimeError(f"No se pudo graficar el indice {index_name}.") from exc
        return {
            "output_path": output_path.as_posix(),
            "min": style.get("min"),
            "max": style.get("max"),
            "palette": style.get("palette"),
            "error": str(exc),
        }


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
