from typing import Any
import geopandas as gpd

def validate_labeled_points(
    labeled_points: gpd.GeoDataFrame, params: dict[str, Any]
) -> gpd.GeoDataFrame:
    """Valida la columna de etiqueta, geometria y CRS de los puntos."""
    label_column = params["label_column"]
    if label_column not in labeled_points.columns:
        raise ValueError(f"No existe la columna de etiqueta: {label_column}")
    if labeled_points.crs is None:
        raise ValueError("El shapefile no tiene CRS. Revisa el archivo .prj.")
    if not labeled_points.geometry.geom_type.isin(["Point", "MultiPoint"]).all():
        raise ValueError("El shapefile debe contener solo puntos o multipuntos.")

    points = labeled_points.dropna(subset=[label_column]).copy()
    points[label_column] = points[label_column].astype(str).str.strip()
    points = points[points[label_column] != ""]
    if points.empty:
        raise ValueError(f"No hay puntos con valores validos en {label_column}.")

    target_crs = params.get("target_crs")
    return points.to_crs(target_crs) if target_crs else points
