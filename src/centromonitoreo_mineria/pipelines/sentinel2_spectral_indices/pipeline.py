from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.sentinel2_spectral_indices.nodes import (
    build_sentinel2_collection,
    build_sentinel2_composite,
    build_sentinel2_spectral_indices_metadata,
    calculate_sentinel2_spectral_indices,
    export_sentinel2_spectral_indices_to_drive,
    initialize_earth_engine,
    load_roi_geometry,
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
                func=initialize_earth_engine,
                inputs="sentinel2_spectral_indices_config",
                outputs="sentinel2_spectral_indices_gee_context",
                name="initialize_sentinel2_spectral_indices_earth_engine_node",
            ),
            node(
                func=load_roi_geometry,
                inputs=[
                    "sentinel2_spectral_indices_gee_context",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_roi_geometry",
                name="load_sentinel2_spectral_indices_roi_geometry_node",
            ),
            node(
                func=build_sentinel2_collection,
                inputs=[
                    "sentinel2_spectral_indices_gee_context",
                    "sentinel2_spectral_indices_roi_geometry",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_image_collection",
                name="build_sentinel2_spectral_indices_collection_node",
            ),
            node(
                func=build_sentinel2_composite,
                inputs=[
                    "sentinel2_spectral_indices_image_collection",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_composite_image",
                name="build_sentinel2_spectral_indices_composite_node",
            ),
            node(
                func=calculate_sentinel2_spectral_indices,
                inputs=[
                    "sentinel2_spectral_indices_composite_image",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_image",
                name="calculate_sentinel2_spectral_indices_node",
            ),
            node(
                func=export_sentinel2_spectral_indices_to_drive,
                inputs=[
                    "sentinel2_spectral_indices_image",
                    "sentinel2_spectral_indices_roi_geometry",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_drive_export_metadata",
                name="export_sentinel2_spectral_indices_to_drive_node",
            ),
            node(
                func=build_sentinel2_spectral_indices_metadata,
                inputs=[
                    "sentinel2_spectral_indices_image_collection",
                    "sentinel2_spectral_indices_drive_export_metadata",
                    "sentinel2_spectral_indices_config",
                ],
                outputs="sentinel2_spectral_indices_metadata",
                name="build_sentinel2_spectral_indices_metadata_node",
            ),
        ]
    )
