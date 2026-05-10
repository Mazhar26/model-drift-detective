import streamlit as st
import pandas as pd
from utils import fetch_data

st.set_page_config(page_title="Model Drift Detective", layout="wide")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🧠 Model Drift Detective</h1>
<p style='text-align: center; color:#a89f91;'>
AI Monitoring • Drift Analysis • Intelligent Insights
</p>
<hr>
""", unsafe_allow_html=True)

st.caption("👉 Use sidebar pages for deep dive analysis")

# ---------------- SUMMARY ----------------
st.header("📌 Overview")

summary = fetch_data("summary")

if summary:
    col1, col2, col3 = st.columns(3)

    col1.metric("Drifted Features", summary.get("drifted_features_count", 0))
    col2.metric("Top Feature", summary.get("top_drift_feature", "N/A"))
    col3.metric("Accuracy Drop", round(summary.get("accuracy_drop", 0), 3))

    status = summary.get("status", "Unknown")

    if "High" in status:
        st.error(f"🚨 Status: {status}")
    elif "Moderate" in status:
        st.warning(f"⚠️ Status: {status}")
    else:
        st.success(f"✅ Status: {status}")
else:
    st.warning("⚠️ Could not reach API — is the backend running?")

st.markdown("---")

# ---------------- QUICK DRIFT SNAPSHOT ----------------
st.header("📊 Top Drifted Features")

drift = fetch_data("detect")

if drift:
    df = pd.DataFrame.from_dict(drift, orient="index")

    if "drift_score" in df.columns:
        df = df.sort_values(by="drift_score", ascending=False)
        st.bar_chart(df["drift_score"].head(5))
else:
    st.info("No significant drift detected")

st.markdown("---")

# ---------------- KEY RECOMMENDATIONS ----------------
st.header("🤖 Key Recommendations")

rec = fetch_data("recommend")

if rec:
    for i, (k, v) in enumerate(rec.items()):
        if i >= 3:  # show only top 3
            break

        if "🚨" in v:
            st.error(f"{k}: {v}")
        elif "⚠️" in v:
            st.warning(f"{k}: {v}")
        else:
            st.info(f"{k}: {v}")
else:
    st.info("No recommendations at this time")