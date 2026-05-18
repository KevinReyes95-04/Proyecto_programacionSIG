from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import initialize_earth_engine_client

def initialize_earth_engine(sentinel2_spectral_indices_config: dict) -> dict:
    """Inicializa Google Earth Engine para calcular indices Sentinel-2."""
    return initialize_earth_engine_client(sentinel2_spectral_indices_config["gee"])
