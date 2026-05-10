import streamlit as st
from utils import fetch_data

st.title("🔍 Drift Explanation")

data = fetch_data("explain")

if data:
    feature = st.selectbox("Select Feature", list(data.keys()))
    info = data[feature]

    st.json(info)

    if "segment_shift" in info:
        st.bar_chart(info["segment_shift"])
else:
    st.warning("No explanation data")