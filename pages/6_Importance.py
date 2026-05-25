import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("⭐ Feature Importance Shift")

data = fetch_data("importance")

if not data:
    st.error("🔌 Could not reach API — is the backend running?")
else:
    df = pd.DataFrame.from_dict(data, orient="index")

    if not df.empty and "change" in df.columns:
        st.dataframe(df)
        st.bar_chart(df["change"])
    else:
        st.info("No feature importance shift data available.")