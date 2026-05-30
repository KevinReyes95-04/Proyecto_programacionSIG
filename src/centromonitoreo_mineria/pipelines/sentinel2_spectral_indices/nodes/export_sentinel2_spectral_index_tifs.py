from centromonitoreo_mineria.pipelines.helper.google_earth_engine.sentinel2_local_index_tifs import write_sentinel2_index_tifs


def export_sentinel2_spectral_index_tifs(sentinel2_spectral_indices_config: dict) -> dict:
    """Genera GeoTIFF locales de los indices espectrales Sentinel-2."""
    # Funcion para exportar los indices espectrales como GeoTIFF locales.
    return write_sentinel2_index_tifs(
        sentinel2_spectral_indices_config["sentinel2_spectral_indices"]
    )
