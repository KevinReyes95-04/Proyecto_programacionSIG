from typing import Any

import pandas as pd


# Funcion para resumir puntos dentro de poligonos mineros por clase.
def build_postprocessed_class_summary(
    point_validation: pd.DataFrame,
    params: dict[str, Any],
) -> pd.DataFrame:
    label_column = params["label_column"]
    summary = (
        point_validation.groupby(["dataset_split", label_column], dropna=False)
        .agg(
            total_points=("sample_id", "count"),
            points_inside_mining_polygon=("inside_mining_polygon", "sum"),
        )
        .reset_index()
    )
    summary["pct_inside_mining_polygon"] = (
        summary["points_inside_mining_polygon"] / summary["total_points"] * 100
    ).round(4)
    return summary.sort_values(["dataset_split", label_column]).reset_index(drop=True)
