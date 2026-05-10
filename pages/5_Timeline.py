import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📈 Drift Timeline")

data = fetch_data("timeline")

if data:
    df = pd.DataFrame(data)
    st.line_chart(df.set_index("step")["drift_score"])
else:
    st.warning("No timeline data")