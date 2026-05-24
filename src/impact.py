from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from config import MODEL_PARAMS
from logger import get_logger

logger = get_logger(__name__)


def analyze_impact(train_df, live_df):
    """
    Analyze model performance degradation caused by drift.

    Workflow:
    - Train model on historical data
    - Evaluate on unseen validation data
    - Evaluate on live/drifted data
    - Compare accuracy drop

    Args:
        train_df:
            Historical training dataset

        live_df:
            Live/production dataset

    Returns:
        Dictionary containing:
        - train_accuracy (alias: validation_accuracy)
        - live accuracy
        - accuracy drop
    """

    logger.info("Starting impact analysis")

    try:

        # ============================================
        # Validate datasets
        # ============================================

        if train_df.empty or live_df.empty:
            logger.warning("Empty dataset provided")
            return {}

        if "Churn" not in train_df.columns:
            logger.error("Target column 'Churn' missing")
            return {}

        # ============================================
        # Split historical data
        # ============================================

        X = train_df.drop(columns=["Churn"])
        y = train_df["Churn"]

        X_train, X_val, y_train, y_val = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # ============================================
        # Prepare live data
        # ============================================

        X_live = live_df.drop(columns=["Churn"])
        y_live = live_df["Churn"]

        # ============================================
        # Train model
        # ============================================

        model = RandomForestClassifier(
            **MODEL_PARAMS
        )

        model.fit(X_train, y_train)

        logger.info("RandomForest model trained")

        # ============================================
        # Validation accuracy
        # ============================================

        val_pred = model.predict(X_val)

        validation_accuracy = accuracy_score(
            y_val,
            val_pred
        )

        # ============================================
        # Live accuracy
        # ============================================

        live_pred = model.predict(X_live)

        live_accuracy = accuracy_score(
            y_live,
            live_pred
        )

        # ============================================
        # Accuracy degradation
        # ============================================

        accuracy_drop = (
            validation_accuracy
            - live_accuracy
        )

        logger.info(
            "Impact analysis completed — validation=%.4f live=%.4f drop=%.4f",
            validation_accuracy,
            live_accuracy,
            accuracy_drop
        )

        return {
            "train_accuracy": float(
                validation_accuracy
            ),
            "validation_accuracy": float(
                validation_accuracy
            ),
            "live_accuracy": float(
                live_accuracy
            ),
            "accuracy_drop": float(
                accuracy_drop
            )
        }

    except Exception as e:

        logger.error(
            "Impact analysis failed: %s",
            e
        )

        return {}
