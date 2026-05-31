from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.validate_mining_multiclass_map.nodes import (
    plot_mining_multiclass_validation_map,
)


# Funcion para graficar aciertos y errores sobre el mapa multiclase postprocesado.
def plot_postprocessed_mining_multiclass_validation_map(
    postprocessed_mining_multiclass_point_validation: pd.DataFrame,
    mining_multiclass_map_postprocessing_metadata: dict[str, Any],
    postprocessed_mining_multiclass_map_validation_config: dict[str, Any],
) -> dict[str, Any]:
    return plot_mining_multiclass_validation_map(
        postprocessed_mining_multiclass_point_validation,
        _prediction_metadata(mining_multiclass_map_postprocessing_metadata),
        postprocessed_mining_multiclass_map_validation_config,
    )


# Funcion para adaptar los metadatos postprocesados al formato del graficador multiclase.
def _prediction_metadata(postprocessing_metadata: dict[str, Any]) -> dict[str, Any]:
    return {"prediction": {"classification_map": postprocessing_metadata["postprocessing"]["postprocessed_classification_map"]}}

