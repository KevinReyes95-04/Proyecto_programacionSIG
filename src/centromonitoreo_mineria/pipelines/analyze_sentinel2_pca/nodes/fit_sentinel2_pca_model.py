from sklearn.pipeline import Pipeline as SklearnPipeline

from centromonitoreo_mineria.pipelines.helper.modeling.pca_analysis import (
    fit_pca_model,
)


def fit_sentinel2_pca_model(
    sentinel2_pca_training_dataset: dict,
    sentinel2_pca_config: dict,
) -> SklearnPipeline:
    """Ajusta PCA con los datos de entrenamiento."""
    return fit_pca_model(
        training_dataset=sentinel2_pca_training_dataset,
        params=sentinel2_pca_config,
    )
