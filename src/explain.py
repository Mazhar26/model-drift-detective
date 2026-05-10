import numpy as np


def segment_analysis(train_df, live_df, column):
    try:
        # Combine both datasets for consistent bins
        combined = np.concatenate([train_df[column].dropna(), live_df[column].dropna()])

        bins = np.linspace(np.min(combined), np.max(combined), 6)

        train_counts, _ = np.histogram(train_df[column], bins)
        live_counts, _ = np.histogram(live_df[column], bins)

        # Normalize to percentage
        train_pct = train_counts / (train_counts.sum() + 1e-6)
        live_pct = live_counts / (live_counts.sum() + 1e-6)

        changes = (live_pct - train_pct).tolist()

        return [float(x) for x in changes]

    except Exception:
        return []


def explain_drift(train_df, live_df):
    explanation = {}

    # ✅ Align columns safely
    common_cols = list(set(train_df.columns).intersection(set(live_df.columns)))

    for col in common_cols:
        try:
            # ❌ Skip non-numeric + target
            if train_df[col].dtype == 'object' or col == "Churn":
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
                "segment_shift": segment_analysis(train_df, live_df, col)
            }

        except Exception:
            continue

    return explanation