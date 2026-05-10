from sklearn.ensemble import RandomForestClassifier
from config import MODEL_PARAMS
from logger import get_logger

logger = get_logger(__name__)


def feature_importance_analysis(train_df, live_df):
    """
    Compare feature importance between train and live models.

    Args:
        train_df: Training data DataFrame.
        live_df: Live/production data DataFrame.

    Returns:
        Dict mapping feature names to importance comparison.
    """
    logger.info("Starting feature importance analysis")

    # Split
    X_train = train_df.drop(columns=["Churn"])
    y_train = train_df["Churn"]

    X_live = live_df.drop(columns=["Churn"])
    y_live = live_df["Churn"]

    # Train model on training data
    model = RandomForestClassifier(**MODEL_PARAMS)
    model.fit(X_train, y_train)
    train_importance = model.feature_importances_
    logger.debug("Train model importance computed")

    # Retrain on live data
    model.fit(X_live, y_live)
    live_importance = model.feature_importances_
    logger.debug("Live model importance computed")

    result = {}

    for i, col in enumerate(X_train.columns):
        diff = live_importance[i] - train_importance[i]

        result[col] = {
            "train_importance": float(train_importance[i]),
            "live_importance": float(live_importance[i]),
            "change": float(diff)
        }

        if abs(diff) > 0.05:
            logger.warning("Significant importance shift in %s: %.4f", col, diff)

    logger.info("Feature importance analysis completed — %d features", len(result))
    return result