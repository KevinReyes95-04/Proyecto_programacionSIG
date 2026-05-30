from pathlib import Path
from typing import Any


def finish_map(
    axis: Any,
    figure: Any,
    output_path: Path,
    plot_params: dict[str, Any],
    default_title: str,
) -> None:
    """Aplica titulo, leyenda y guarda la figura."""
    axis.set_title(plot_params.get("title", default_title))
    axis.set_axis_off()
    axis.legend(
        fontsize=plot_params.get("legend_font_size", 7),
        loc=plot_params.get("legend_location", "best"),
    )
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
