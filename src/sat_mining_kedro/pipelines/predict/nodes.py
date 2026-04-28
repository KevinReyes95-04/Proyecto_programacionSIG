def run_inference(feature_table, binary_model, multiclass_model, params_prediction: dict):
    infer_df = feature_table.copy()
    feature_cols = params_prediction.get("feature_columns", [])
    X = infer_df[feature_cols]

    infer_df["pred_mining"] = binary_model.predict(X)
    infer_df["pred_landcover"] = multiclass_model.predict(X)
    return infer_df
