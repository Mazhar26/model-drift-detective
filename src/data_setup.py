import pandas as pd
from sklearn.model_selection import train_test_split

from logger import get_logger

logger = get_logger(__name__)


def preprocess_data(df):
    """
    Clean and preprocess raw Telco dataset.

    Args:
        df:
            Raw dataframe.

    Returns:
        Processed dataframe.
    """

    logger.info("Starting preprocessing")

    # -----------------------------------
    # Drop unnecessary columns
    # -----------------------------------

    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])

    # -----------------------------------
    # Convert target column
    # -----------------------------------

    df["Churn"] = df["Churn"].map({
        "Yes": 1,
        "No": 0
    })

    # -----------------------------------
    # Numeric conversion
    # -----------------------------------

    df["TotalCharges"] = pd.to_numeric(
        df["TotalCharges"],
        errors="coerce"
    )

    # -----------------------------------
    # Remove missing values
    # -----------------------------------

    missing_before = df.isna().sum().sum()

    if missing_before > 0:
        logger.warning(
            "Missing values detected: %d",
            missing_before
        )

    df = df.dropna()

    # -----------------------------------
    # Encode categoricals
    # -----------------------------------

    df = pd.get_dummies(
        df,
        drop_first=True
    )

    logger.info(
        "Preprocessing completed — shape=%s",
        df.shape
    )

    return df


def inject_drift(live_df):
    """
    Inject synthetic drift into live dataset.

    Args:
        live_df:
            Live dataframe.

    Returns:
        Drifted dataframe.
    """

    logger.info("Injecting synthetic drift")

    live_df = live_df.copy()

    # -----------------------------------
    # Simulate billing drift
    # -----------------------------------

    live_df["MonthlyCharges"] *= 1.3

    # -----------------------------------
    # Simulate customer retention drift
    # -----------------------------------

    live_df["tenure"] *= 0.8

    logger.info("Synthetic drift injection completed")

    return live_df


def load_data():
    """
    Load and prepare Telco churn dataset.

    Returns:
        train_df:
            Historical training dataset.

        live_df:
            Simulated production/live dataset.
    """

    logger.info("Loading Telco dataset")

    # -----------------------------------
    # Read CSV
    # -----------------------------------

    df = pd.read_csv(
        "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    )

    logger.info(
        "Dataset loaded — shape=%s",
        df.shape
    )

    # -----------------------------------
    # Preprocess
    # -----------------------------------

    df = preprocess_data(df)

    # -----------------------------------
    # Train/live split
    # -----------------------------------

    train_df, live_df = train_test_split(
        df,
        test_size=0.3,
        random_state=42
    )

    logger.info(
        "Dataset split — train=%s live=%s",
        train_df.shape,
        live_df.shape
    )

    # -----------------------------------
    # Inject synthetic drift
    # -----------------------------------

    live_df = inject_drift(live_df)

    logger.info("Data loading pipeline completed")

    return train_df, live_df