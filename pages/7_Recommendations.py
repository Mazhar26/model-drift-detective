import streamlit as st
from utils import fetch_data

st.title("🛠 Recommendations")

data = fetch_data("recommend")

if data:

    for feature, recommendation in data.items():
        st.write(f"### {feature}")
        st.info(recommendation)

else:
    st.success("No recommendations needed")