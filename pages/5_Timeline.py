import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📈 Drift Timeline")

data = fetch_data("timeline")

df = pd.DataFrame(data)

st.line_chart(
    df.set_index("step")["drift_score"]
)

st.dataframe(df)