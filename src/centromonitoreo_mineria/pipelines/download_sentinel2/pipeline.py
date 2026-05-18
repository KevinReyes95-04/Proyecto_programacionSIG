from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.download_sentinel2.nodes import (validate_google_earth_engine_config, build_sentinel2_collection,
    build_sentinel2_composite,
    build_sentinel2_download_metadata,
    export_sentinel2_to_drive,
    initialize_earth_engine,
    load_roi_geometry,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for the Sentinel-2 download process."""
    return Pipeline(
        [
            node(
                func=validate_google_earth_engine_config,
                inputs=["params:gee", "params:sentinel2_download"],
                outputs="google_earth_engine_config",
                name="validate_google_earth_engine_config_node",
            ),
            node(
                func=initialize_earth_engine,
                inputs="google_earth_engine_config",
                outputs="sentinel2_gee_context",
                name="initialize_earth_engine_node",
            ),
            node(
                func=load_roi_geometry,
                inputs=["sentinel2_gee_context", "google_earth_engine_config"],
                outputs="sentinel2_roi_geometry",
                name="load_roi_geometry_node",
            ),
            node(
                func=build_sentinel2_collection,
                inputs=["sentinel2_gee_context", "sentinel2_roi_geometry", "google_earth_engine_config"],
                outputs="sentinel2_image_collection",
                name="build_sentinel2_collection_node",
            ),
            node(
                func=build_sentinel2_composite,
                inputs=["sentinel2_image_collection", "google_earth_engine_config"],
                outputs="sentinel2_composite_image",
                name="build_sentinel2_composite_node",
            ),
            node(
                func=export_sentinel2_to_drive,
                inputs=["sentinel2_composite_image", "sentinel2_roi_geometry", "google_earth_engine_config"],
                outputs="sentinel2_drive_export_metadata",
                name="export_sentinel2_to_drive_node",
            ),
            node(
                func=build_sentinel2_download_metadata,
                inputs=["sentinel2_image_collection", "sentinel2_drive_export_metadata", "google_earth_engine_config"],
                outputs="sentinel2_download_metadata",
                name="build_sentinel2_download_metadata_node",
            ),
        ]
    )
