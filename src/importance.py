from sklearn.ensemble import RandomForestClassifier

from config import MODEL_PARAMS
from logger import get_logger

logger = get_logger(__name__)


def get_feature_importance(train_df, live_df):
    # Public alias kept below for backward compatibility
    """
    Compare feature importance between
    train and live datasets.

    Args:
        train_df:
            Training dataset.

        live_df:
            Live/production dataset.

    Returns:
        Dictionary containing feature
        importance comparison results.
    """

    logger.info("Starting feature importance analysis")

    try:

        # ============================================
        # Validate datasets
        # ============================================

        if train_df.empty or live_df.empty:
            logger.warning("Empty dataset provided")
            return {}

        if "Churn" not in train_df.columns:
            logger.error("Missing target column: Churn")
            return {}

        # ============================================
        # Split features and targets
        # ============================================

        X_train = train_df.drop(columns=["Churn"])
        y_train = train_df["Churn"]

        X_live = live_df.drop(columns=["Churn"])
        y_live = live_df["Churn"]

        # ============================================
        # Train model on training data
        # ============================================

        model = RandomForestClassifier(**MODEL_PARAMS)

        model.fit(X_train, y_train)

        train_importance = model.feature_importances_

        logger.info("Training importance calculated")

        # ============================================
        # Train model on live data
        # ============================================

        model.fit(X_live, y_live)

        live_importance = model.feature_importances_

        logger.info("Live importance calculated")

        # ============================================
        # Compare importance shifts
        # ============================================

        result = {}

        for i, col in enumerate(X_train.columns):

            diff = live_importance[i] - train_importance[i]

            result[col] = {
                "train_importance": float(train_importance[i]),
                "live_importance": float(live_importance[i]),
                "change": float(diff),
            }

            if abs(diff) > 0.05:

                logger.warning("Significant importance shift in %s: %.4f", col, diff)

        logger.info("Feature importance analysis completed — %d features analyzed", len(result))

        return result

    except Exception as e:

        logger.error("Feature importance analysis failed: %s", e)

        return {}


# Alias — smoke_test.py and api/main.py import by this name
feature_importance_analysis = get_feature_importance
