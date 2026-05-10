from scipy.stats import ks_2samp
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_severity(score):
    if score > 0.3:
        return "high"
    elif score > 0.1:
        return "medium"
    else:
        return "low"


def detect_drift(train_df, live_df):
    logger.info("🚀 Drift detection started")

    # ✅ Edge case 1: empty inputs
    if train_df is None or live_df is None:
        logger.error("❌ Input data is None")
        return {}

    if train_df.empty or live_df.empty:
        logger.warning("⚠️ One of the datasets is empty")
        return {}

    # ✅ Edge case 2: align columns (in case mismatch)
    common_cols = list(set(train_df.columns).intersection(set(live_df.columns)))
    if not common_cols:
        logger.error("❌ No common columns between datasets")
        return {}

    drift_results = {}

    for col in common_cols:

        try:
            # ✅ Skip non-numeric
            if not np.issubdtype(train_df[col].dtype, np.number):
                logger.info(f"Skipping non-numeric column: {col}")
                continue

            # ✅ Handle NaNs
            train_col = train_df[col].dropna()
            live_col = live_df[col].dropna()

            # Edge case: after dropna empty
            if len(train_col) == 0 or len(live_col) == 0:
                logger.warning(f"⚠️ Column {col} empty after NaN removal")
                continue

            logger.info(f"Processing column: {col}")

            stat, p_value = ks_2samp(train_col, live_col)

            drift_score = float(stat)
            drift = bool(p_value < 0.05)
            severity = get_severity(drift_score)

            if severity == "high":
                logger.warning(f"🚨 High drift detected in {col}")
            elif severity == "medium":
                logger.warning(f"⚠️ Medium drift in {col}")
            else:
                logger.info(f"✅ Low drift in {col}")

            drift_results[col] = {
                "p_value": float(p_value),
                "drift_detected": drift,
                "drift_score": drift_score,
                "severity": severity
            }

        except Exception as e:
            logger.error(f"❌ Error processing column {col}: {e}")

    logger.info("✅ Drift detection completed")

    return drift_results