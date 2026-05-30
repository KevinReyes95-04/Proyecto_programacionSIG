from kedro.pipeline import Pipeline, node
from centromonitoreo_mineria.pipelines.download_sentinel2.nodes import (build_sentinel2_download_assets, build_sentinel2_download_metadata, build_sentinel2_download_visualizations,
download_sentinel2_drive_export_to_local, export_sentinel2_download_to_drive, validate_sentinel2_download_config)


def create_pipeline(**kwargs) -> Pipeline:
    """Creates the Kedro pipeline for the Sentinel-2 download process."""
    return Pipeline(
        [
            node(
                func=validate_sentinel2_download_config,
                inputs=["params:gee", "params:sentinel2_download"],
                outputs="sentinel2_download_config",
                name="validate_sentinel2_download_config_node",
            ),
            node(
                func=build_sentinel2_download_assets,
                inputs="sentinel2_download_config",
                outputs="sentinel2_download_assets",
                name="build_sentinel2_download_assets_node",
            ),
            node(
                func=export_sentinel2_download_to_drive,
                inputs=["sentinel2_download_assets", "sentinel2_download_config"],
                outputs="sentinel2_drive_export_metadata",
                name="export_sentinel2_download_to_drive_node",
            ),
            node(
                func=build_sentinel2_download_metadata,
                inputs=["sentinel2_download_assets", "sentinel2_drive_export_metadata", "sentinel2_download_config"],
                outputs="sentinel2_download_metadata",
                name="build_sentinel2_download_metadata_node",
            ),
            node(
                func=download_sentinel2_drive_export_to_local,
                inputs=["sentinel2_drive_export_metadata", "sentinel2_download_config"],
                outputs="sentinel2_local_download_metadata",
                name="download_sentinel2_drive_export_to_local_node",
            ),
            node(
                func=build_sentinel2_download_visualizations,
                inputs=["sentinel2_local_download_metadata", "sentinel2_download_config"],
                outputs="sentinel2_download_visualizations_metadata",
                name="build_sentinel2_download_visualizations_node",
            ),
        ]
    )
