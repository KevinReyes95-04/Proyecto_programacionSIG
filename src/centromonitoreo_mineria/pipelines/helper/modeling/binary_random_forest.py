from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def validate_binary_random_forest_params(params: dict[str, Any]) -> dict[str, Any]:
    """Valida la configuracion del clasificador Random Forest binario."""
    if not isinstance(params, dict):
        raise ValueError("mining_binary_random_forest debe ser un diccionario.")
    _require_text(params.get("label_column"), "mining_binary_random_forest.label_column")
    _require_text(params.get("positive_label"), "mining_binary_random_forest.positive_label")
    _require_text(params.get("negative_label"), "mining_binary_random_forest.negative_label")
    _require_text_list(params.get("negative_source_labels"), "mining_binary_random_forest.negative_source_labels")
    _require_text_list(params.get("feature_columns"), "mining_binary_random_forest.feature_columns")
    _validate_probability_threshold(params.get("classification_threshold", 0.5))
    _validate_random_forest_params(params.get("random_forest", {}))
    return dict(params)


def build_binary_dataset(table: pd.DataFrame, params: dict[str, Any], dataset_name: str) -> dict[str, Any]:
    """Prepara matriz de variables y etiqueta binaria para entrenamiento o prueba."""
    label_column = params["label_column"]
    feature_columns = params["feature_columns"]
    _validate_required_columns(table, [label_column, *feature_columns], dataset_name)
    _validate_known_labels(table, params, dataset_name)
    source = table.copy()
    source[params.get("target_column", "target")] = source[label_column].map(
        _label_mapping(params)
    )
    source = source.dropna(subset=[params.get("target_column", "target"), *feature_columns]).reset_index(drop=True)
    return {
        "name": dataset_name,
        "source": source,
        "X": source[feature_columns].astype(float),
        "y": source[params.get("target_column", "target")],
        "feature_columns": feature_columns,
    }


def train_random_forest(training_dataset: dict[str, Any], params: dict[str, Any]) -> RandomForestClassifier:
    """Entrena un RandomForestClassifier con los parametros configurados."""
    model = RandomForestClassifier(**params.get("random_forest", {}))
    model.fit(training_dataset["X"], training_dataset["y"])
    return model


def predict_random_forest(
    model: RandomForestClassifier,
    testing_dataset: dict[str, Any],
    params: dict[str, Any],
) -> pd.DataFrame:
    """Predice clase binaria y probabilidad de mineria sobre el conjunto de prueba."""
    predictions = testing_dataset["source"].copy()
    prediction_column = params.get("prediction_column", "predicted_target")
    probability_column = params.get("probability_column", "probability_mineria")
    if hasattr(model, "predict_proba"):
        positive_index = list(model.classes_).index(params["positive_label"])
        probability = np.asarray(model.predict_proba(testing_dataset["X"]))[:, positive_index]
        predictions[probability_column] = probability
        predictions[prediction_column] = np.where(
            probability >= params.get("classification_threshold", 0.5),
            params["positive_label"],
            params["negative_label"],
        )
    else:
        predictions[prediction_column] = model.predict(testing_dataset["X"])
    return predictions


def evaluate_binary_predictions(predictions: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    """Calcula metricas de clasificacion para el modelo binario."""
    target_column = params.get("target_column", "target")
    prediction_column = params.get("prediction_column", "predicted_target")
    labels = [params["negative_label"], params["positive_label"]]
    y_true = predictions[target_column]
    y_pred = predictions[prediction_column]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "labels": labels,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_mineria": float(precision_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "recall_mineria": float(recall_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "f1_mineria": float(f1_score(y_true, y_pred, pos_label=params["positive_label"], zero_division=0)),
        "confusion_matrix": matrix.astype(int).tolist(),
        "classification_report": classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0),
    }


def feature_importance_table(model: RandomForestClassifier, params: dict[str, Any]) -> pd.DataFrame:
    """Construye la tabla ordenada de importancia de variables."""
    feature_columns = params["feature_columns"]
    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    )
    return importance.sort_values("importance", ascending=False).reset_index(drop=True)


def plot_confusion_matrix(metrics: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Guarda la matriz de confusion como imagen y retorna sus metadatos."""
    plot_params = params.get("confusion_matrix_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_confusion_matrix.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix = np.array(metrics["confusion_matrix"])
    labels = metrics["labels"]
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [6, 5])))
    image = axis.imshow(matrix, cmap=plot_params.get("cmap", "Blues"))
    axis.figure.colorbar(image, ax=axis)
    axis.set_xticks(range(len(labels)), labels=labels)
    axis.set_yticks(range(len(labels)), labels=labels)
    axis.set_xlabel(plot_params.get("x_label", "Prediccion"))
    axis.set_ylabel(plot_params.get("y_label", "Observado"))
    axis.set_title(plot_params.get("title", "Matriz de confusion"))
    _annotate_matrix(axis, matrix)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "labels": labels}


def plot_feature_importance(importance: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    """Guarda la grafica de importancia de variables y retorna sus metadatos."""
    plot_params = params.get("feature_importance_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/mining_binary_feature_importance.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_n = int(plot_params.get("top_n", 20))
    data = importance.head(top_n).sort_values("importance")
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 7])))
    axis.barh(data["feature"], data["importance"], color=plot_params.get("color", "#1379B9"))
    axis.set_xlabel(plot_params.get("x_label", "Importancia"))
    axis.set_title(plot_params.get("title", "Importancia de variables"))
    axis.grid(axis="x", alpha=0.3)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "top_n": top_n}


def build_model_metadata(
    training_dataset: dict[str, Any],
    testing_dataset: dict[str, Any],
    metrics: dict[str, Any],
    confusion_matrix_plot_metadata: dict[str, Any],
    feature_importance_plot_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Resume configuracion, datos y resultados del entrenamiento."""
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": "RandomForestClassifier",
        "label_column": params["label_column"],
        "positive_label": params["positive_label"],
        "negative_label": params["negative_label"],
        "negative_source_labels": params["negative_source_labels"],
        "feature_columns": params["feature_columns"],
        "classification_threshold": params.get("classification_threshold", 0.5),
        "random_forest": params.get("random_forest", {}),
        "training_rows": int(len(training_dataset["source"])),
        "testing_rows": int(len(testing_dataset["source"])),
        "training_target_counts": training_dataset["y"].value_counts().to_dict(),
        "testing_target_counts": testing_dataset["y"].value_counts().to_dict(),
        "metrics": metrics,
        "confusion_matrix_plot": confusion_matrix_plot_metadata,
        "feature_importance_plot": feature_importance_plot_metadata,
    }


def _label_mapping(params: dict[str, Any]) -> dict[str, str]:
    mapping = {params["positive_label"]: params["positive_label"]}
    mapping.update({label: params["negative_label"] for label in params["negative_source_labels"]})
    return mapping


def _validate_required_columns(table: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing = [column for column in columns if column not in table.columns]
    if missing:
        raise ValueError(f"{dataset_name} no tiene las columnas requeridas: {missing}.")


def _validate_known_labels(table: pd.DataFrame, params: dict[str, Any], dataset_name: str) -> None:
    expected = {params["positive_label"], *params["negative_source_labels"]}
    observed = set(table[params["label_column"]].dropna().unique())
    unknown = observed - expected
    if unknown:
        raise ValueError(f"{dataset_name} tiene clases no configuradas: {sorted(unknown)}.")


def _annotate_matrix(axis: Any, matrix: np.ndarray) -> None:
    threshold = matrix.max() / 2 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            color = "white" if matrix[row, column] > threshold else "black"
            axis.text(column, row, str(matrix[row, column]), ha="center", va="center", color=color)


def _validate_random_forest_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict):
        raise ValueError("mining_binary_random_forest.random_forest debe ser un diccionario.")
    for key in ("n_estimators", "min_samples_leaf", "min_samples_split"):
        value = params.get(key)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            raise ValueError(f"mining_binary_random_forest.random_forest.{key} debe ser entero positivo.")


def _validate_probability_threshold(value: Any) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError("mining_binary_random_forest.classification_threshold debe estar entre 0 y 1.")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")
