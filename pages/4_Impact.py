import streamlit as st
from utils import fetch_data

st.title("📉 Impact Analysis")

data = fetch_data("impact")

if data:
    col1, col2, col3 = st.columns(3)

    col1.metric("Train Accuracy", round(data.get("train_accuracy", 0), 3))
    col2.metric("Live Accuracy", round(data.get("live_accuracy", 0), 3))
    col3.metric("Accuracy Drop", round(data.get("accuracy_drop", 0), 3))
else:
    st.warning("No data")