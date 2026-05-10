import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np


def load_data():
    """
    Loads Telco dataset and splits into train/live
    """

    df = pd.read_csv("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")

    # Drop ID
    df = df.drop(columns=["customerID"])

    # Target encoding
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # Convert to numeric
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Drop missing
    df = df.dropna()

    # One-hot encoding
    df = pd.get_dummies(df, drop_first=True)

    # Split
    train_df, live_df = train_test_split(df, test_size=0.3, random_state=42)

    # ---------------- DRIFT SIMULATION ----------------
    live_df = live_df.copy()

    np.random.seed(42)  # ✅ reproducibility

    # 🔥 Feature 1 — scale drift
    live_df["MonthlyCharges"] = live_df["MonthlyCharges"] * 1.2

    # 🔥 Feature 2 — shift drift
    live_df["tenure"] = live_df["tenure"] + np.random.normal(5, 2, len(live_df))

    # 🔥 Feature 3 — noise drift
    live_df["TotalCharges"] = live_df["TotalCharges"] + np.random.normal(0, 50, len(live_df))

    # 🔥 Feature 4 — small random noise across all numeric columns (excluding target)
    numeric_cols = live_df.select_dtypes(include=["float64", "int64"]).columns
    numeric_cols = [c for c in numeric_cols if c != "Churn"]

    for col in numeric_cols:
        live_df[col] = live_df[col] + np.random.normal(0, 0.01, len(live_df))

    return train_df, live_df