import streamlit as st
from utils import fetch_data

st.title("🤖 Recommendations")

data = fetch_data("recommend")

if data:
    for k, v in data.items():
        if "🚨" in v:
            st.error(f"{k}: {v}")
        elif "⚠️" in v:
            st.warning(f"{k}: {v}")
        else:
            st.info(f"{k}: {v}")
else:
    st.warning("No recommendations")