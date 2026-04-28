from sklearn.metrics import classification_report


def evaluate_models(feature_table, binary_model, multiclass_model, params_evaluation: dict):
    df = feature_table.dropna().copy()

    binary_target = params_evaluation.get("binary_target", "mining_label")
    multiclass_target = params_evaluation.get("multiclass_target", "landcover_label")
    feature_cols = params_evaluation.get("feature_columns", [])

    X = df[feature_cols]

    binary_pred = binary_model.predict(X)
    multiclass_pred = multiclass_model.predict(X)

    return {
        "binary": classification_report(df[binary_target], binary_pred, output_dict=True),
        "multiclass": classification_report(df[multiclass_target], multiclass_pred, output_dict=True),
    }
