import streamlit as st
import pandas as pd
from utils import fetch_data

st.title("📈 Drift Timeline")

# ── Tab layout: Real History vs Simulated ──
tab1, tab2 = st.tabs(["📊 Drift History", "🔬 Simulated Timeline"])

# ── Tab 1: Real drift history from SQLite ──
with tab1:
    st.subheader("Historical Drift Checks")

    # Run Drift Check button
    if st.button("🔍 Run Drift Check Now", key="run_drift_check"):
        with st.spinner("Running drift detection..."):
            result = fetch_data("detect", params={"threshold": 0.0})
            if result:
                st.success(f"✅ Drift check complete — {len(result)} features analyzed")
            else:
                st.warning("⚠️ Drift check returned no results")

    # Fetch history data
    history = fetch_data("history")

    if history:
        df = pd.DataFrame(history)

        # Metrics row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Checks", len(df))
        col2.metric("Avg Drift Score", round(df["avg_drift_score"].mean(), 4))
        col3.metric("Last Severity", df.iloc[0]["severity"].upper() if len(df) > 0 else "N/A")

        # Chart
        if "timestamp" in df.columns and "avg_drift_score" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")
            st.line_chart(df.set_index("timestamp")["avg_drift_score"])

        # Table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No drift history yet. Click 'Run Drift Check Now' to start tracking!")

    # Trend data
    st.subheader("📉 Daily Trend")
    trend = fetch_data("history/trend")

    if trend:
        trend_df = pd.DataFrame(trend)
        if not trend_df.empty:
            st.bar_chart(trend_df.set_index("date")["avg_drift_score"])
    else:
        st.info("No trend data available yet")

# ── Tab 2: Simulated timeline (original) ──
with tab2:
    st.subheader("Simulated Drift Over Time")

    data = fetch_data("timeline")

    if data:
        df = pd.DataFrame(data)
        st.line_chart(df.set_index("step")["drift_score"])
    else:
        st.warning("No timeline data")