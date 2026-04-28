from sklearn.ensemble import RandomForestClassifier


def train_multiclass_model(feature_table, params_multiclass_rf: dict):
    train_df = feature_table.dropna().copy()
    target = params_multiclass_rf.get("target", "landcover_label")
    feature_cols = params_multiclass_rf.get("feature_columns", [])
    X = train_df[feature_cols]
    y = train_df[target]
    model = RandomForestClassifier(
        n_estimators=params_multiclass_rf.get("n_estimators", 400),
        max_depth=params_multiclass_rf.get("max_depth", None),
        random_state=params_multiclass_rf.get("random_state", 42),
        class_weight=params_multiclass_rf.get("class_weight", "balanced_subsample"),
        n_jobs=-1,
    )
    model.fit(X, y)
    return model
