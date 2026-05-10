from sklearn.ensemble import RandomForestClassifier

def feature_importance_analysis(train_df, live_df):
    # Split
    X_train = train_df.drop(columns=["Churn"])
    y_train = train_df["Churn"]

    X_live = live_df.drop(columns=["Churn"])
    y_live = live_df["Churn"]

    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    train_importance = model.feature_importances_

    # Retrain on live data
    model.fit(X_live, y_live)
    live_importance = model.feature_importances_

    result = {}

    for i, col in enumerate(X_train.columns):
        diff = live_importance[i] - train_importance[i]

        result[col] = {
            "train_importance": float(train_importance[i]),
            "live_importance": float(live_importance[i]),
            "change": float(diff)
        }

    return result