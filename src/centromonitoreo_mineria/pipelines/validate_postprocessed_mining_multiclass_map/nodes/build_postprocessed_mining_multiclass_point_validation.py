from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_multiclass_map.nodes import (
    build_mining_multiclass_point_validation,
)


# Funcion para extraer clases postprocesadas en los puntos de prueba.
def build_postprocessed_mining_multiclass_point_validation(
    testing_sentinel2_features: pd.DataFrame,
    mining_multiclass_map_postprocessing_metadata: dict[str, Any],
    postprocessed_mining_multiclass_map_validation_config: dict[str, Any],
) -> pd.DataFrame:
    return build_mining_multiclass_point_validation(
        testing_sentinel2_features,
        _prediction_metadata(mining_multiclass_map_postprocessing_metadata),
        postprocessed_mining_multiclass_map_validation_config,
    )


# Funcion para adaptar los metadatos postprocesados al formato del validador multiclase.
def _prediction_metadata(postprocessing_metadata: dict[str, Any]) -> dict[str, Any]:
    return {"prediction": {"classification_map": postprocessing_metadata["postprocessing"]["postprocessed_classification_map"]}}

