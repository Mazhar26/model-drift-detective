from scipy.stats import ks_2samp

from config import P_VALUE_THRESHOLD, SEVERITY_HIGH_THRESHOLD, SEVERITY_MEDIUM_THRESHOLD
from logger import get_logger

logger = get_logger(__name__)


def get_severity(score):
    """
    Classify drift severity based on configurable thresholds.
    """

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
        train_df:
            Training dataset.

        live_df:
            Live / production dataset.

    Returns:
        Dictionary containing drift metrics per feature.
    """

    logger.info("Drift detection started")

    # =========================================================
    # Validate inputs
    # =========================================================

    if train_df is None or live_df is None:
        logger.error("Input dataset is None")
        return {}

    if train_df.empty or live_df.empty:
        logger.warning("One of the datasets is empty")
        return {}

    # =========================================================
    # Find common columns
    # =========================================================

    common_cols = list(set(train_df.columns).intersection(set(live_df.columns)))

    if not common_cols:
        logger.error("No common columns found")
        return {}

    drift_results = {}

    # =========================================================
    # Drift detection loop
    # =========================================================

    for col in common_cols:

        try:

            # -------------------------------------------------
            # Skip target column
            # -------------------------------------------------

            if col == "Churn":
                logger.debug("Skipping target column: %s", col)
                continue

            # -------------------------------------------------
            # Skip only raw object/string columns
            # Keep bool/int/float encoded features
            # -------------------------------------------------

            if train_df[col].dtype == "object":
                logger.debug("Skipping object column: %s", col)
                continue

            # -------------------------------------------------
            # Remove NaN values
            # -------------------------------------------------

            train_col = train_df[col].dropna()
            live_col = live_df[col].dropna()

            if len(train_col) == 0 or len(live_col) == 0:
                logger.warning("Column %s empty after NaN removal", col)
                continue

            logger.info("Processing column: %s", col)

            # -------------------------------------------------
            # KS Test
            # -------------------------------------------------

            stat, p_value = ks_2samp(train_col, live_col)

            drift_score = float(stat)

            drift_detected = bool(p_value < P_VALUE_THRESHOLD)

            severity = get_severity(drift_score)

            # -------------------------------------------------
            # Logging
            # -------------------------------------------------

            if severity == "high":

                logger.warning("High drift detected in %s (score=%.4f)", col, drift_score)

            elif severity == "medium":

                logger.warning("Medium drift detected in %s (score=%.4f)", col, drift_score)

            else:

                logger.info("Low drift in %s (score=%.4f)", col, drift_score)

            # -------------------------------------------------
            # Store results
            # -------------------------------------------------

            drift_results[col] = {
                "p_value": float(p_value),
                "drift_detected": drift_detected,
                "drift_score": drift_score,
                "severity": severity,
            }

        except Exception as e:

            logger.error("Error processing column %s: %s", col, e)

    logger.info("Drift detection completed — %d features analyzed", len(drift_results))

    return drift_results
