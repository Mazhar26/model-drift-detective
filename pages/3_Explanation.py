import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("🔍 Drift Explanation")

data = fetch_data("explain")

if data:

    df = pd.DataFrame.from_dict(data, orient="index")

    st.dataframe(df)

else:
    st.warning("No explanations available")