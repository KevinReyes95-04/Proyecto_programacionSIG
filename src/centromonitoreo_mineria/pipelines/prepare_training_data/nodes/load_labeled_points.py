from pathlib import Path
from typing import Any
import geopandas as gpd

def load_labeled_points(params: dict[str, Any]) -> gpd.GeoDataFrame:
    """Carga el shapefile de puntos etiquetados."""
    path = Path(params["labeled_points_path"])
    if not path.exists():
        raise FileNotFoundError(f"No existe el shapefile configurado: {path.as_posix()}")
    return gpd.read_file(path)
