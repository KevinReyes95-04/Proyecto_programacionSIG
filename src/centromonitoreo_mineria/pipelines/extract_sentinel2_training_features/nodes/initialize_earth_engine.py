from centromonitoreo_mineria.pipelines.helper.google_earth_engine.earth_engine_initialization import (
    initialize_earth_engine_client,
)


def initialize_earth_engine(sentinel2_training_features_config: dict) -> dict:
    """Inicializa Google Earth Engine."""
    return initialize_earth_engine_client(sentinel2_training_features_config["gee"])
