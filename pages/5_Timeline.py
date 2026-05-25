import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📈 Drift Timeline")

data = fetch_data("timeline")

if not data:
    st.error("🔌 Could not reach API — is the backend running?")
else:
    df = pd.DataFrame(data)

    if "step" in df.columns and "drift_score" in df.columns:
        st.line_chart(
            df.set_index("step")["drift_score"]
        )
        st.dataframe(df)
    else:
        st.warning("⚠️ Received empty or invalid timeline data.")