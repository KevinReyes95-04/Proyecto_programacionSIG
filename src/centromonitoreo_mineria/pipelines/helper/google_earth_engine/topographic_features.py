from typing import Any

from centromonitoreo_mineria.utils.earth_engine import load_ee


# Funcion para agregar DEM y pendiente a una imagen de Earth Engine.
def add_topographic_features(image: Any, params: dict[str, Any]) -> Any:
    if not params.get("enabled", False):
        return image
    return image.addBands(build_topographic_image(params))


# Funcion para construir una imagen Earth Engine con elevacion y pendiente.
def build_topographic_image(params: dict[str, Any]) -> Any:
    ee = load_ee()
    output_bands = params.get("output_bands", {})
    dem = ee.Image(params.get("dem_asset", "USGS/SRTMGL1_003")).select(
        params.get("elevation_band", "elevation")
    ).rename(output_bands.get("elevation", "DEM"))
    slope = ee.Terrain.slope(dem).rename(output_bands.get("slope", "SLOPE"))
    return dem.addBands(slope)


# Funcion para listar las bandas topograficas configuradas.
def topographic_feature_columns(params: dict[str, Any]) -> list[str]:
    if not params.get("enabled", False):
        return []
    output_bands = params.get("output_bands", {})
    return [output_bands.get("elevation", "DEM"), output_bands.get("slope", "SLOPE")]

