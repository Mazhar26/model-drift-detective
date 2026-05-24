import streamlit as st
from utils import fetch_data

st.title("📉 Drift Impact")

data = fetch_data("impact")

st.metric(
    "Validation Accuracy",
    round(data["validation_accuracy"], 4)
)

st.metric(
    "Live Accuracy",
    round(data["live_accuracy"], 4)
)

st.metric(
    "Accuracy Drop",
    round(data["accuracy_drop"], 4)
)