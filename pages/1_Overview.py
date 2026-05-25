from utils import fetch_data
import streamlit as st

st.title("🧠 Model Drift Detective")

data = fetch_data("summary")

if not data:
    st.error("🔌 Could not reach API — is the backend running?")
else:
    st.metric("Total Features", data.get("total_features", 0))
    st.metric("Drifted Features", data.get("drifted_features_count", 0))
    st.metric("Accuracy Drop", round(data.get("accuracy_drop", 0.0), 4))

    st.subheader("System Status")

    status = data.get("status", "Unknown")

    if status == "High Impact Drift":
        st.error(status)
    elif status == "Moderate Drift":
        st.warning(status)
    else:
        st.success(status)

    st.write("Top Drift Feature:", data.get("top_drift_feature"))