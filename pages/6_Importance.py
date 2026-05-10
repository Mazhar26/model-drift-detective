import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📊 Feature Importance")

data = fetch_data("importance")

if isinstance(data, dict):
    df = pd.DataFrame.from_dict(data, orient="index")

    if "change" in df.columns:
        df = df[abs(df["change"]) > 0.01]

        if not df.empty:
            st.dataframe(df)
            st.bar_chart(df["change"])
        else:
            st.warning("No significant changes")
else:
    st.warning("No data")