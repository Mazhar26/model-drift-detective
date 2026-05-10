from scipy.stats import ks_2samp
import numpy as np
from config import SEVERITY_HIGH_THRESHOLD, SEVERITY_MEDIUM_THRESHOLD, P_VALUE_THRESHOLD
from logger import get_logger

logger = get_logger(__name__)


def get_severity(score):
    """Classify drift severity based on configurable thresholds."""
    if score > SEVERITY_HIGH_THRESHOLD:
        return "high"
    elif score > SEVERITY_MEDIUM_THRESHOLD:
        return "medium"
    else:
        return "low"


def detect_drift(train_df, live_df):
    """
    Run KS-test based drift detection on all numeric columns.

    Args:
        train_df: Training data DataFrame.
        live_df: Live/production data DataFrame.

    Returns:
        Dict mapping feature names to drift results.
    """
    logger.info("Drift detection started")

    # Edge case 1: empty inputs
    if train_df is None or live_df is None:
        logger.error("Input data is None")
        return {}

    if train_df.empty or live_df.empty:
        logger.warning("One of the datasets is empty")
        return {}

    # Edge case 2: align columns (in case mismatch)
    common_cols = list(set(train_df.columns).intersection(set(live_df.columns)))
    if not common_cols:
        logger.error("No common columns between datasets")
        return {}

    drift_results = {}

    for col in common_cols:

        try:
            # Skip non-numeric
            if not np.issubdtype(train_df[col].dtype, np.number):
                logger.debug("Skipping non-numeric column: %s", col)
                continue

            # Handle NaNs
            train_col = train_df[col].dropna()
            live_col = live_df[col].dropna()

            # Edge case: after dropna empty
            if len(train_col) == 0 or len(live_col) == 0:
                logger.warning("Column %s empty after NaN removal", col)
                continue

            logger.debug("Processing column: %s", col)

            stat, p_value = ks_2samp(train_col, live_col)

            drift_score = float(stat)
            drift = bool(p_value < P_VALUE_THRESHOLD)
            severity = get_severity(drift_score)

            if severity == "high":
                logger.warning("High drift detected in %s (score=%.4f)", col, drift_score)
            elif severity == "medium":
                logger.warning("Medium drift in %s (score=%.4f)", col, drift_score)
            else:
                logger.info("Low drift in %s (score=%.4f)", col, drift_score)

            drift_results[col] = {
                "p_value": float(p_value),
                "drift_detected": drift,
                "drift_score": drift_score,
                "severity": severity
            }

        except Exception as e:
            logger.error("Error processing column %s: %s", col, e)

    logger.info("Drift detection completed — %d features analyzed", len(drift_results))

    return drift_results
