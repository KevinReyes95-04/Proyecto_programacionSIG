from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import initialize_earth_engine_client

def initialize_earth_engine(google_earth_engine_config: dict) -> dict:
    """Inicializa Google Earth Engine segun la configuracion del proyecto."""
    return initialize_earth_engine_client(google_earth_engine_config["gee"])
