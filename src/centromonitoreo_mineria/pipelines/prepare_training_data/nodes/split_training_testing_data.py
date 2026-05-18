from typing import Any
import geopandas as gpd
import pandas as pd
from sklearn.model_selection import train_test_split


def split_training_testing_data(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parte los puntos etiquetados en entrenamiento y prueba."""
    label_column = params["label_column"]
    stratify = labeled_points[label_column] if params.get("stratify", True) else None
    train, test = train_test_split(
        labeled_points,
        test_size=params.get("test_size", 0.2),
        random_state=params.get("random_state", 42),
        stratify=stratify,
    )
    return _to_table(train, label_column), _to_table(test, label_column)


def _to_table(points: gpd.GeoDataFrame, label_column: str) -> pd.DataFrame:
    table = pd.DataFrame(points.drop(columns="geometry")).copy()
    table["longitude"] = points.geometry.x.to_numpy()
    table["latitude"] = points.geometry.y.to_numpy()
    table["geometry_wkt"] = points.geometry.to_wkt().to_numpy()
    return table.reset_index(drop=True)
