from sklearn.ensemble import RandomForestClassifier


def train_binary_model(feature_table, params_binary_rf: dict):
    train_df = feature_table.dropna().copy()
    target = params_binary_rf.get("target", "mining_label")
    feature_cols = params_binary_rf.get("feature_columns", [])
    X = train_df[feature_cols]
    y = train_df[target]
    model = RandomForestClassifier(
        n_estimators=params_binary_rf.get("n_estimators", 300),
        max_depth=params_binary_rf.get("max_depth", None),
        random_state=params_binary_rf.get("random_state", 42),
        class_weight=params_binary_rf.get("class_weight", "balanced"),
        n_jobs=-1,
    )
    model.fit(X, y)
    return model
