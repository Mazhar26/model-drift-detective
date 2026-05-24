from utils import fetch_data
import streamlit as st

st.title("🧠 Model Drift Detective")

data = fetch_data("summary")


st.metric("Total Features", data["total_features"])
st.metric("Drifted Features", data["drifted_features_count"])
st.metric("Accuracy Drop", round(data["accuracy_drop"], 4))

st.subheader("System Status")

status = data["status"]

if status == "High Impact Drift":
    st.error(status)
elif status == "Moderate Drift":
    st.warning(status)
else:
    st.success(status)

st.write("Top Drift Feature:", data["top_drift_feature"])