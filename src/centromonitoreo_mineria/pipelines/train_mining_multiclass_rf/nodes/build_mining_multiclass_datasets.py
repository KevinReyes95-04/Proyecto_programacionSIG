from typing import Any

import pandas as pd


# Funcion para construir los datasets multiclase de entrenamiento y prueba.
def build_mining_multiclass_datasets(
    training_sentinel2_features: pd.DataFrame,
    testing_sentinel2_features: pd.DataFrame,
    mining_multiclass_random_forest_config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        build_multiclass_dataset(training_sentinel2_features, mining_multiclass_random_forest_config, "training_sentinel2_features"),
        build_multiclass_dataset(testing_sentinel2_features, mining_multiclass_random_forest_config, "testing_sentinel2_features"),
    )


# Funcion para preparar variables y etiqueta de una tabla multiclase.
def build_multiclass_dataset(table: pd.DataFrame, params: dict[str, Any], dataset_name: str) -> dict[str, Any]:
    label_column = params["label_column"]
    target_column = params.get("target_column", "target_class")
    feature_columns = params["feature_columns"]
    _validate_required_columns(table, [label_column, *feature_columns], dataset_name)
    _validate_known_labels(table, params, dataset_name)
    source = table.copy()
    source[target_column] = source[label_column]
    source = source.dropna(subset=[target_column, *feature_columns]).reset_index(drop=True)
    return {
        "name": dataset_name,
        "source": source,
        "X": source[feature_columns].astype(float),
        "y": source[target_column],
        "feature_columns": feature_columns,
        "class_labels": params["class_labels"],
    }


# Funcion para validar columnas obligatorias de entrada.
def _validate_required_columns(table: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing = [column for column in columns if column not in table.columns]
    if missing:
        raise ValueError(f"{dataset_name} no tiene las columnas requeridas: {missing}.")


# Funcion para validar que solo existan clases configuradas.
def _validate_known_labels(table: pd.DataFrame, params: dict[str, Any], dataset_name: str) -> None:
    expected = set(params["class_labels"])
    observed = set(table[params["label_column"]].dropna().unique())
    unknown = observed - expected
    if unknown:
        raise ValueError(f"{dataset_name} tiene clases no configuradas: {sorted(unknown)}.")

