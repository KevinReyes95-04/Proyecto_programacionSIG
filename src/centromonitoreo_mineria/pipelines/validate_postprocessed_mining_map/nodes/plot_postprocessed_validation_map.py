from typing import Any

import pandas as pd

from centromonitoreo_mineria.pipelines.helper.modeling.postprocessed_validation_map import (
    save_postprocessed_validation_map,
)


# Funcion para generar el mapa de validacion postprocesada.
def plot_postprocessed_validation_map(
    point_validation: pd.DataFrame,
    postprocessing_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    return save_postprocessed_validation_map(
        point_validation=point_validation,
        postprocessing_metadata=postprocessing_metadata,
        params=params,
    )
