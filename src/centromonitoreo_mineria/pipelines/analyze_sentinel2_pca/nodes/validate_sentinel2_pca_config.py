from copy import deepcopy

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    validate_sentinel2_pca_params,
)


def validate_sentinel2_pca_config(params_sentinel2_pca_analysis: dict) -> dict:
    """Valida la configuracion del analisis PCA."""
    return validate_sentinel2_pca_params(deepcopy(params_sentinel2_pca_analysis))
