import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📊 Drift Detection")

threshold = st.slider(
    "Drift Threshold",
    0.0,
    1.0,
    0.3,
    key="drift_slider_page"
)

st.info(f"Showing features with drift > {threshold}")

data = fetch_data(
    "detect",
    params={"threshold": threshold}
)

if data:
    df = pd.DataFrame.from_dict(data, orient="index")

    if not df.empty:

        df = df.sort_values(by="drift_score", ascending=False)

        high_count = (df["severity"] == "high").sum()
        medium_count = (df["severity"] == "medium").sum()

        if high_count > 0:
            st.error(f"🚨 {high_count} High Drift Features Detected")
        elif medium_count > 0:
            st.warning(f"⚠️ {medium_count} Medium Drift Features")
        else:
            st.success("✅ System Stable")

        def color_severity(val):
            if val == "high":
                return "color: red; font-weight: bold"
            elif val == "medium":
                return "color: orange"
            else:
                return "color: green"

        styled_df = df.style.map(color_severity, subset=["severity"])

        st.dataframe(styled_df)

        st.bar_chart(df["drift_score"])

    else:
        st.warning("No features exceed the selected drift threshold")

else:
    st.warning("No drift detected")