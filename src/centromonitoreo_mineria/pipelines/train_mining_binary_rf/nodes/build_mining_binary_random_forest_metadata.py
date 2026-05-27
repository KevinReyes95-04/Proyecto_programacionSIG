from centromonitoreo_mineria.pipelines.helper.modeling.binary_random_forest import (
    build_model_metadata,
)


def build_mining_binary_random_forest_metadata(
    mining_binary_training_dataset: dict,
    mining_binary_testing_dataset: dict,
    mining_binary_metrics: dict,
    mining_binary_confusion_matrix_plot_metadata: dict,
    mining_binary_feature_importance_plot_metadata: dict,
    mining_binary_random_forest_config: dict,
) -> dict:
    """Construye metadatos finales del modelo Random Forest binario."""
    return build_model_metadata(
        training_dataset=mining_binary_training_dataset,
        testing_dataset=mining_binary_testing_dataset,
        metrics=mining_binary_metrics,
        confusion_matrix_plot_metadata=mining_binary_confusion_matrix_plot_metadata,
        feature_importance_plot_metadata=mining_binary_feature_importance_plot_metadata,
        params=mining_binary_random_forest_config,
    )
