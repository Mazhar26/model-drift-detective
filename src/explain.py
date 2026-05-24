import numpy as np
from logger import get_logger

logger = get_logger(__name__)


def segment_analysis(train_df, live_df, column):
    """Compute segment-level distribution shift for a column."""
    try:
        # Convert safely to numeric float
        train_values = train_df[column].dropna().astype(float)
        live_values = live_df[column].dropna().astype(float)

        # Combine for consistent binning
        combined = np.concatenate([train_values, live_values])

        # Prevent edge-case crash
        if len(combined) == 0:
            return []

        bins = np.linspace(np.min(combined), np.max(combined), 6)

        train_counts, _ = np.histogram(train_values, bins)
        live_counts, _ = np.histogram(live_values, bins)

        # Normalize to percentage
        train_pct = train_counts / (train_counts.sum() + 1e-6)
        live_pct = live_counts / (live_counts.sum() + 1e-6)

        changes = (live_pct - train_pct).tolist()

        return [float(x) for x in changes]

    except Exception as e:
        logger.error("Segment analysis failed for column %s: %s", column, e)
        return []


def explain_drift(train_df, live_df):
    """
    Generate drift explanations with mean shift and segment analysis.

    Args:
        train_df: Training data DataFrame.
        live_df: Live/production data DataFrame.

    Returns:
        Dict mapping feature names to explanation details.
    """

    logger.info("Generating drift explanations")

    explanation = {}

    # Align columns safely
    common_cols = list(
        set(train_df.columns).intersection(set(live_df.columns))
    )

    for col in common_cols:

        try:
            # Skip target column
            if col == "Churn":
                continue

            # Skip non-numeric columns
            if not np.issubdtype(train_df[col].dtype, np.number):
                continue

            train_col = train_df[col].dropna()
            live_col = live_df[col].dropna()

            if len(train_col) == 0 or len(live_col) == 0:
                continue

            train_mean = float(train_col.mean())
            live_mean = float(live_col.mean())

            diff = float(live_mean - train_mean)

            explanation[col] = {
                "train_mean": train_mean,
                "live_mean": live_mean,
                "difference": diff,
                "segment_shift": segment_analysis(
                    train_df,
                    live_df,
                    col
                )
            }

            logger.debug(
                "Explained %s: shift=%.4f",
                col,
                diff
            )

        except Exception as e:
            logger.error(
                "Failed to explain column %s: %s",
                col,
                e
            )

    logger.info(
        "Drift explanation completed — %d features explained",
        len(explanation)
    )

    return explanation