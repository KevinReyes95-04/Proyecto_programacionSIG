from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.sentinel2_spectral_indices.nodes import (
    build_sentinel2_spectral_indices_assets,
    build_sentinel2_spectral_indices_metadata,
    export_sentinel2_spectral_index_maps,
    export_sentinel2_spectral_index_tifs,
    validate_sentinel2_spectral_indices_config,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for Sentinel-2 spectral indices."""
    return Pipeline(
        [
            node(
                func=validate_sentinel2_spectral_indices_config,
                inputs=["params:gee", "params:sentinel2_spectral_indices"],
                outputs="sentinel2_spectral_indices_config",
                name="validate_sentinel2_spectral_indices_config_node",
            ),
            node(
                func=build_sentinel2_spectral_indices_assets,
                inputs="sentinel2_spectral_indices_config",
                outputs="sentinel2_spectral_indices_assets",
                name="build_sentinel2_spectral_indices_assets_node",
            ),
            node(
                func=export_sentinel2_spectral_index_maps,
                inputs=[
                    "sentinel2_spectral_indices_assets",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_maps_metadata",
                name="export_sentinel2_spectral_index_maps_node",
            ),
            node(
                func=export_sentinel2_spectral_index_tifs,
                inputs="sentinel2_spectral_indices_config",
                outputs="sentinel2_spectral_indices_tifs_metadata",
                name="export_sentinel2_spectral_index_tifs_node",
            ),
            node(
                func=build_sentinel2_spectral_indices_metadata,
                inputs=[
                    "sentinel2_spectral_indices_assets",
                    "sentinel2_spectral_indices_maps_metadata",
                    "sentinel2_spectral_indices_tifs_metadata",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_metadata",
                name="build_sentinel2_spectral_indices_metadata_node",
            ),
        ]
    )
