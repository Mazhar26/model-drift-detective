import streamlit as st
from utils import fetch_data

st.title("📌 System Overview")

summary = fetch_data("summary")

if summary:
    col1, col2, col3 = st.columns(3)

    col1.metric("Drifted Features", summary.get("drifted_features_count", 0))
    col2.metric("Top Feature", summary.get("top_drift_feature", "N/A"))
    col3.metric("Accuracy Drop", round(summary.get("accuracy_drop", 0), 3))

    st.success(f"Status: {summary.get('status', 'Unknown')}")
else:
    st.warning("No data available")