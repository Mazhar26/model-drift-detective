import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📊 Drift Detection")

# ✅ 1. Slider
threshold = st.slider(
    "Drift Threshold",
    0.0,
    1.0,
    0.3,
    key="drift_slider_page"
)

st.info(f"Showing features with drift > {threshold}")

# ✅ 2. API call using shared utility
data = fetch_data("detect", params={"threshold": threshold})

# ✅ 3. Process + Display
if data:
    df = pd.DataFrame.from_dict(data, orient="index")

    if not df.empty:

        df = df.sort_values(by="drift_score", ascending=False)

        # 🔥 Severity Summary
        high_count = (df["severity"] == "high").sum()
        medium_count = (df["severity"] == "medium").sum()

        if high_count > 0:
            st.error(f"🚨 {high_count} High Drift Features Detected")
        elif medium_count > 0:
            st.warning(f"⚠️ {medium_count} Medium Drift Features")
        else:
            st.success("✅ System Stable")

        # ✅ Clean severity labels
        def highlight_severity(val):
            if val == "high":
                return "🔴 HIGH"
            elif val == "medium":
                return "🟠 MEDIUM"
            else:
                return "🟢 LOW"

        df["severity_label"] = df["severity"].apply(highlight_severity)

        # ✅ Display table
        st.dataframe(df)

        # 📊 Chart
        st.bar_chart(df["drift_score"])

    else:
        st.warning("No features exceed the selected drift threshold")

else:
    st.warning("No drift detected")