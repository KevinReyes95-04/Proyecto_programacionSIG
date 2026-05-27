from centromonitoreo_mineria.pipelines.helper.modeling.mining_map_postprocessing import (
    postprocess_mining_binary_map as postprocess_map,
)


def postprocess_mining_binary_map(
    mining_binary_map_postprocessing_config: dict,
) -> dict:
    """Postprocesa el raster binario de mineria y genera poligonos."""
    return postprocess_map(params=mining_binary_map_postprocessing_config)
