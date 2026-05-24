import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("⭐ Feature Importance Shift")

data = fetch_data("importance")

df = pd.DataFrame.from_dict(data, orient="index")

st.dataframe(df)

st.bar_chart(df["change"])