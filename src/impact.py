from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from config import MODEL_PARAMS
from logger import get_logger

logger = get_logger(__name__)


def analyze_impact(train_df, live_df):
    """
    Analyze accuracy impact of drift by comparing train vs live performance.

    Args:
        train_df: Training data DataFrame.
        live_df: Live/production data DataFrame.

    Returns:
        Dict with train_accuracy, live_accuracy, and accuracy_drop.
    """
    logger.info("Starting impact analysis")

    # Split features & target
    target_col = "Churn"
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]

    X_live = live_df.drop(columns=[target_col])
    y_live = live_df[target_col]

    # Train model with configurable parameters
    model = RandomForestClassifier(**MODEL_PARAMS)
    model.fit(X_train, y_train)
    logger.debug("Model trained with params: %s", MODEL_PARAMS)

    # Evaluate
    train_pred = model.predict(X_train)
    live_pred = model.predict(X_live)

    train_acc = accuracy_score(y_train, train_pred)
    live_acc = accuracy_score(y_live, live_pred)
    drop = float(train_acc - live_acc)

    logger.info(
        "Impact analysis complete — train=%.4f, live=%.4f, drop=%.4f",
        train_acc, live_acc, drop
    )

    if drop > 0.1:
        logger.warning("Significant accuracy drop detected: %.4f", drop)

    return {
        "train_accuracy": float(train_acc),
        "live_accuracy": float(live_acc),
        "accuracy_drop": drop
    }