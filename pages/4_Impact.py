import streamlit as st
from utils import fetch_data

st.title("📉 Drift Impact")

data = fetch_data("impact")

if not data:
    st.error("🔌 Could not reach API — is the backend running?")
else:
    st.metric(
        "Validation Accuracy",
        round(data.get("validation_accuracy", 0.0), 4)
    )

    st.metric(
        "Live Accuracy",
        round(data.get("live_accuracy", 0.0), 4)
    )

    st.metric(
        "Accuracy Drop",
        round(data.get("accuracy_drop", 0.0), 4)
    )