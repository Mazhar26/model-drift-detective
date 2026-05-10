"""
config.py — Centralized configuration for Model Drift Detective.

All settings are loaded from environment variables with sensible defaults.
Uses python-dotenv to load .env file if present.
"""

import os
from dotenv import load_dotenv

# Load .env file (no-op if already set via Docker/CI)
load_dotenv()


# ── API Configuration ──────────────────────────────────────
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))

# ── Streamlit Configuration ────────────────────────────────
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# ── Drift Detection ───────────────────────────────────────
DEFAULT_THRESHOLD = float(os.getenv("DEFAULT_THRESHOLD", "0.1"))
P_VALUE_THRESHOLD = float(os.getenv("P_VALUE_THRESHOLD", "0.05"))
SEVERITY_HIGH_THRESHOLD = float(os.getenv("SEVERITY_HIGH_THRESHOLD", "0.3"))
SEVERITY_MEDIUM_THRESHOLD = float(os.getenv("SEVERITY_MEDIUM_THRESHOLD", "0.1"))

# ── Logging ────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# ── Data ───────────────────────────────────────────────────
DATA_PATH = os.getenv("DATA_PATH", "data/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# ── Model Parameters ──────────────────────────────────────
MODEL_N_ESTIMATORS = int(os.getenv("MODEL_N_ESTIMATORS", "100"))
MODEL_RANDOM_STATE = int(os.getenv("MODEL_RANDOM_STATE", "42"))
MODEL_MAX_DEPTH = os.getenv("MODEL_MAX_DEPTH", None)
if MODEL_MAX_DEPTH is not None:
    MODEL_MAX_DEPTH = int(MODEL_MAX_DEPTH)

MODEL_PARAMS = {
    "n_estimators": MODEL_N_ESTIMATORS,
    "random_state": MODEL_RANDOM_STATE,
    "max_depth": MODEL_MAX_DEPTH,
}
