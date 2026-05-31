from typing import Any

import geopandas as gpd
import pandas as pd
import rasterio


# Funcion para extraer la clase del raster multiclase en los puntos de prueba.
def build_mining_multiclass_point_validation(
    testing_sentinel2_features: pd.DataFrame,
    mining_multiclass_map_metadata: dict[str, Any],
    mining_multiclass_map_validation_config: dict[str, Any],
) -> pd.DataFrame:
    params = mining_multiclass_map_validation_config
    points = _project_points(testing_sentinel2_features, mining_multiclass_map_metadata, params)
    value_to_label = {int(value): label for label, value in params["class_values"].items()}
    with rasterio.open(mining_multiclass_map_metadata["prediction"]["classification_map"]) as source:
        values = [value[0] for value in source.sample(zip(points.geometry.x, points.geometry.y))]
        nodata = source.nodata

    result = testing_sentinel2_features.copy()
    result["map_class_value"] = values
    result[params.get("prediction_column", "predicted_map_class")] = [
        None if nodata is not None and value == nodata else value_to_label.get(int(value))
        for value in values
    ]
    result["is_valid_pixel"] = result[params.get("prediction_column", "predicted_map_class")].notna()
    result["is_correct"] = result[params["label_column"]] == result[params.get("prediction_column", "predicted_map_class")]
    result["validation_status"] = result["is_correct"].map({True: "correcto", False: "error"})
    result.loc[~result["is_valid_pixel"], "validation_status"] = "sin_datos"
    return result


# Funcion para crear puntos y proyectarlos al CRS del raster.
def _project_points(points: pd.DataFrame, map_metadata: dict[str, Any], params: dict[str, Any]) -> gpd.GeoDataFrame:
    coordinate_columns = params["coordinate_columns"]
    with rasterio.open(map_metadata["prediction"]["classification_map"]) as source:
        target_crs = source.crs
    gdf = gpd.GeoDataFrame(
        points.copy(),
        geometry=gpd.points_from_xy(points[coordinate_columns["longitude"]], points[coordinate_columns["latitude"]]),
        crs=coordinate_columns.get("source_crs", "EPSG:4326"),
    )
    return gdf.to_crs(target_crs) if target_crs else gdf

