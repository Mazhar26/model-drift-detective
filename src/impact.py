from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def analyze_impact(train_df, live_df):
    # Split features & target

    target_col = "Churn"
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]

    X_live = live_df.drop(columns=[target_col])
    y_live = live_df[target_col]

    # Train model
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate
    train_pred = model.predict(X_train)
    live_pred = model.predict(X_live)

    train_acc = accuracy_score(y_train, train_pred)
    live_acc = accuracy_score(y_live, live_pred)

    return {
        "train_accuracy": float(train_acc),
        "live_accuracy": float(live_acc),
        "accuracy_drop": float(train_acc - live_acc)
    }