import pandas as pd


# Funcion para construir los datasets binarios de entrenamiento y prueba.
def build_mining_binary_datasets(
    training_sentinel2_features: pd.DataFrame,
    testing_sentinel2_features: pd.DataFrame,
    mining_binary_random_forest_config: dict,
) -> tuple[dict, dict]:
    return (
        build_binary_dataset(
            table=training_sentinel2_features,
            params=mining_binary_random_forest_config,
            dataset_name="training_sentinel2_features",
        ),
        build_binary_dataset(
            table=testing_sentinel2_features,
            params=mining_binary_random_forest_config,
            dataset_name="testing_sentinel2_features",
        ),
    )


# Funcion para preparar variables y etiqueta binaria de una tabla.
def build_binary_dataset(table: pd.DataFrame, params: dict, dataset_name: str) -> dict:
    label_column = params["label_column"]
    feature_columns = params["feature_columns"]
    _validate_required_columns(table, [label_column, *feature_columns], dataset_name)
    _validate_known_labels(table, params, dataset_name)
    source = table.copy()
    source[params.get("target_column", "target")] = source[label_column].map(_label_mapping(params))
    source = source.dropna(
        subset=[params.get("target_column", "target"), *feature_columns]
    ).reset_index(drop=True)
    return {
        "name": dataset_name,
        "source": source,
        "X": source[feature_columns].astype(float),
        "y": source[params.get("target_column", "target")],
        "feature_columns": feature_columns,
    }


# Funcion para mapear clases originales a Mineria / No Mineria.
def _label_mapping(params: dict) -> dict[str, str]:
    mapping = {params["positive_label"]: params["positive_label"]}
    mapping.update({label: params["negative_label"] for label in params["negative_source_labels"]})
    return mapping


# Funcion para validar columnas obligatorias de entrada.
def _validate_required_columns(table: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing = [column for column in columns if column not in table.columns]
    if missing:
        raise ValueError(f"{dataset_name} no tiene las columnas requeridas: {missing}.")


# Funcion para validar que solo existan clases configuradas.
def _validate_known_labels(table: pd.DataFrame, params: dict, dataset_name: str) -> None:
    expected = {params["positive_label"], *params["negative_source_labels"]}
    observed = set(table[params["label_column"]].dropna().unique())
    unknown = observed - expected
    if unknown:
        raise ValueError(f"{dataset_name} tiene clases no configuradas: {sorted(unknown)}.")
