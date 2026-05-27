from datetime import datetime, timezone
from itertools import cycle
from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.preprocessing import StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def validate_sentinel2_pca_params(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValueError("sentinel2_pca_analysis debe ser un diccionario.")
    _require_text(params.get("label_column"), "sentinel2_pca_analysis.label_column")
    _require_text_list(params.get("feature_columns"), "sentinel2_pca_analysis.feature_columns")
    n_components = params.get("n_components")
    if n_components is not None and (
        not isinstance(n_components, int) or isinstance(n_components, bool) or n_components <= 0
    ):
        raise ValueError("sentinel2_pca_analysis.n_components debe ser entero positivo o null.")
    return dict(params)


def build_pca_dataset(table: pd.DataFrame, params: dict[str, Any], dataset_name: str) -> dict[str, Any]:
    feature_columns = params["feature_columns"]
    label_column = params["label_column"]
    keep_columns = _columns_to_keep(table, params)
    _validate_required_columns(table, [label_column, *feature_columns], dataset_name)
    source = table.dropna(subset=feature_columns).copy().reset_index(drop=True)
    source[params.get("split_column", "split")] = dataset_name
    return {
        "name": dataset_name,
        "source": source,
        "X": source[feature_columns].astype(float),
        "feature_columns": feature_columns,
        "keep_columns": keep_columns,
    }


def fit_pca_model(training_dataset: dict[str, Any], params: dict[str, Any]) -> SklearnPipeline:
    model = SklearnPipeline(
        [
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=params.get("n_components"), random_state=params.get("random_state"))),
        ]
    )
    model.fit(training_dataset["X"])
    return model


def transform_pca_dataset(
    model: SklearnPipeline,
    dataset: dict[str, Any],
    params: dict[str, Any],
) -> pd.DataFrame:
    scores = model.transform(dataset["X"])
    pc_columns = _pc_columns(scores.shape[1])
    score_table = pd.DataFrame(scores, columns=pc_columns)
    source = dataset["source"]
    keep_columns = [column for column in dataset["keep_columns"] if column in source.columns]
    return pd.concat([source[keep_columns].reset_index(drop=True), score_table], axis=1)


def explained_variance_table(model: SklearnPipeline) -> pd.DataFrame:
    pca = model.named_steps["pca"]
    ratios = pca.explained_variance_ratio_
    return pd.DataFrame(
        {
            "component": _pc_columns(len(ratios)),
            "explained_variance": pca.explained_variance_,
            "explained_variance_ratio": ratios,
            "cumulative_explained_variance_ratio": ratios.cumsum(),
        }
    )


def loadings_table(model: SklearnPipeline, params: dict[str, Any]) -> pd.DataFrame:
    pca = model.named_steps["pca"]
    pc_columns = _pc_columns(pca.components_.shape[0])
    loadings = pd.DataFrame(pca.components_.T, columns=pc_columns)
    loadings.insert(0, "feature", params["feature_columns"])
    return loadings


def plot_pca_scatter(
    training_scores: pd.DataFrame,
    testing_scores: pd.DataFrame,
    params: dict[str, Any],
) -> dict[str, Any]:
    plot_params = params.get("scatter_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/sentinel2_pca_scatter.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = pd.concat([training_scores, testing_scores], ignore_index=True)
    x_component = plot_params.get("x_component", "PC1")
    y_component = plot_params.get("y_component", "PC2")
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 7])))
    _scatter_by_class(axis, data, params, x_component, y_component)
    axis.set_title(plot_params.get("title", "PCA Sentinel-2"))
    axis.set_xlabel(x_component)
    axis.set_ylabel(y_component)
    axis.grid(alpha=0.25)
    axis.legend(fontsize=plot_params.get("legend_font_size", 8), loc="best")
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix(), "x_component": x_component, "y_component": y_component}


def plot_pca_scree(explained_variance: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    plot_params = params.get("scree_plot", {})
    output_path = Path(plot_params.get("output_path", "data/08_reporting/sentinel2_pca_scree.png"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=tuple(plot_params.get("figure_size", [8, 5])))
    axis.bar(explained_variance["component"], explained_variance["explained_variance_ratio"], color=plot_params.get("bar_color", "#1379B9"))
    axis.plot(
        explained_variance["component"],
        explained_variance["cumulative_explained_variance_ratio"],
        color=plot_params.get("line_color", "#D55E00"),
        marker="o",
    )
    axis.set_title(plot_params.get("title", "Varianza explicada por PCA"))
    axis.set_xlabel(plot_params.get("x_label", "Componente"))
    axis.set_ylabel(plot_params.get("y_label", "Proporcion de varianza"))
    axis.tick_params(axis="x", rotation=45)
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=plot_params.get("dpi", 160))
    plt.close(figure)
    return {"output_path": output_path.as_posix()}


def build_pca_metadata(
    training_dataset: dict[str, Any],
    testing_dataset: dict[str, Any],
    explained_variance: pd.DataFrame,
    scatter_plot_metadata: dict[str, Any],
    scree_plot_metadata: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    label_column = params["label_column"]
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_columns": params["feature_columns"],
        "label_column": label_column,
        "n_components": int(len(explained_variance)),
        "training_rows": int(len(training_dataset["source"])),
        "testing_rows": int(len(testing_dataset["source"])),
        "training_class_counts": training_dataset["source"][label_column].value_counts().to_dict(),
        "testing_class_counts": testing_dataset["source"][label_column].value_counts().to_dict(),
        "explained_variance_ratio": explained_variance.set_index("component")["explained_variance_ratio"].to_dict(),
        "cumulative_explained_variance_ratio": explained_variance.set_index("component")[
            "cumulative_explained_variance_ratio"
        ].to_dict(),
        "scatter_plot": scatter_plot_metadata,
        "scree_plot": scree_plot_metadata,
    }


def _scatter_by_class(axis: Any, data: pd.DataFrame, params: dict[str, Any], x_component: str, y_component: str) -> None:
    label_column = params["label_column"]
    colors = cycle(params.get("scatter_plot", {}).get("colors", _default_colors()))
    for label, color in zip(sorted(data[label_column].unique()), colors):
        subset = data[data[label_column] == label]
        axis.scatter(
            subset[x_component],
            subset[y_component],
            label=label,
            color=color,
            s=params.get("scatter_plot", {}).get("point_size", 28),
            alpha=params.get("scatter_plot", {}).get("alpha", 0.75),
            edgecolors="black",
            linewidths=0.25,
        )


def _columns_to_keep(table: pd.DataFrame, params: dict[str, Any]) -> list[str]:
    configured = params.get("columns_to_keep") or list(table.columns)
    split_column = params.get("split_column", "split")
    return [column for column in [*configured, split_column] if column in table.columns or column == split_column]


def _pc_columns(count: int) -> list[str]:
    return [f"PC{index}" for index in range(1, count + 1)]


def _validate_required_columns(table: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing = [column for column in columns if column not in table.columns]
    if missing:
        raise ValueError(f"{dataset_name} no tiene las columnas requeridas: {missing}.")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacio.")


def _require_text_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} debe ser una lista de textos no vacios.")


def _default_colors() -> list[str]:
    return ["#1379B9", "#0CB354", "#FFC107", "#D55E00", "#8DD34F", "#18A8D8"]
