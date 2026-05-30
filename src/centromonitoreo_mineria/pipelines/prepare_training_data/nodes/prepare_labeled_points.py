from pathlib import Path
from typing import Any
import geopandas as gpd


# Funcion para cargar, limpiar y reproyectar los puntos etiquetados.
def prepare_labeled_points(params: dict[str, Any]) -> gpd.GeoDataFrame:
    path = Path(params["labeled_points_path"])
    if not path.exists():
        raise FileNotFoundError(f"No existe el shapefile configurado: {path.as_posix()}")

    points = gpd.read_file(path)
    label_column = params["label_column"]
    if label_column not in points.columns:
        raise ValueError(f"No existe la columna de etiqueta: {label_column}")
    if points.crs is None:
        raise ValueError("El shapefile no tiene CRS. Revisa el archivo .prj.")
    if not points.geometry.geom_type.isin(["Point", "MultiPoint"]).all():
        raise ValueError("El shapefile debe contener solo puntos o multipuntos.")

    points = points.dropna(subset=[label_column]).copy()
    points[label_column] = points[label_column].astype(str).str.strip()
    points = points[points[label_column] != ""]
    if points.empty:
        raise ValueError(f"No hay puntos con valores validos en {label_column}.")

    return points.to_crs(params["target_crs"]) if params.get("target_crs") else points
