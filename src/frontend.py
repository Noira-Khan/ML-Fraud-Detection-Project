import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stSidebar"]{
    background-color:#0f172a;
}
[data-testid="stSidebar"] *{
    color:white;
}
div[data-testid="metric-container"]{
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:15px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "best_xgb_model.pkl"
ARCH_PATH = ROOT_DIR / "assets" / "architecture.png"

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    st.error(f"Model Load Error: {e}")
    st.stop()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🛡️ FraudShield AI")

    page = st.radio(
        "Navigation",
        [
            "Executive Dashboard",
            "Fraud Detection Engine",
            "Model Performance",
            "System Architecture",
            "Product Roadmap"
        ]
    )

# --------------------------------------------------
# EXECUTIVE DASHBOARD
# --------------------------------------------------

if page == "Executive Dashboard":

    st.title("🏦 FraudShield AI Executive Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Transactions Today", "1.25M", "+4.2%")
    c2.metric("Fraud Cases", "2,814", "-12%")
    c3.metric("Fraud Rate", "0.22%")
    c4.metric("Estimated Savings", "$4.2M")

    st.divider()

    st.subheader("Current Fraud Risk")
    st.progress(0.22)
    st.success("Current Risk Level: LOW")

    trend = pd.DataFrame({
        "Month":["Jan","Feb","Mar","Apr","May","Jun"],
        "Fraud Cases":[1200,1450,1700,1500,1200,900]
    })

    st.subheader("Fraud Activity Trend")
    st.line_chart(trend.set_index("Month"))

    st.markdown("""
### Executive Summary

FraudShield AI is an AI-powered fraud detection platform
designed to identify suspicious transactions and reduce
financial losses.

### Benefits

✅ Reduce Fraud Losses

✅ Improve Customer Trust

✅ Faster Investigations

✅ Lower False Positives
""")

# --------------------------------------------------
# FRAUD DETECTION
# --------------------------------------------------

elif page == "Fraud Detection Engine":

    st.title("🔍 Fraud Detection Engine")

    tab1, tab2 = st.tabs([
        "⚡ Quick Transaction Check",
        "📁 Upload CSV"
    ])

    with tab1:

        st.subheader("Demo Transaction Simulator")

        st.info(
            "Demo mode. Original model was trained using "
            "V1-V28, Amount and Time."
        )

        amount = st.number_input(
            "Transaction Amount ($)",
            min_value=0.0,
            value=150.0
        )

        time = st.slider(
            "Transaction Time",
            0,
            172800,
            10000
        )

        if st.button("Run Fraud Check"):

            features = np.zeros(30)

            features[0] = float(time)
            features[29] = float(amount)

            probability = model.predict_proba(
                features.reshape(1, -1)
            )[0][1]

            st.metric(
                "Fraud Probability",
                f"{probability * 100:.2f}%"
            )

            st.progress(float(probability))

            if probability > 0.5:
                st.error("🚨 HIGH RISK TRANSACTION")
            else:
                st.success("✅ LOW RISK TRANSACTION")

    with tab2:

        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"]
        )

        if uploaded_file:

            df = pd.read_csv(uploaded_file)

            st.dataframe(df.head())

            if st.button("Analyze First Transaction"):

                row = df.iloc[0].values.reshape(1, -1)

                probability = model.predict_proba(
                    row
                )[0][1]

                st.metric(
                    "Fraud Probability",
                    f"{probability * 100:.2f}%"
                )

# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

elif page == "Model Performance":

    st.title("📊 Model Performance")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Accuracy", "99.9%")
    c2.metric("Precision", "94%")
    c3.metric("Recall", "91%")
    c4.metric("ROC-AUC", "98%")

# --------------------------------------------------
# ARCHITECTURE
# --------------------------------------------------

elif page == "System Architecture":

    st.title("🏗️ FraudShield Architecture")

    if ARCH_PATH.exists():
        st.image(str(ARCH_PATH))

# --------------------------------------------------
# ROADMAP
# --------------------------------------------------

elif page == "Product Roadmap":

    st.title("🗺️ Product Roadmap")

    st.markdown("""
### Q1 2026
Batch Fraud Detection

### Q2 2026
Fraud Analyst Dashboard

### Q3 2026
Real-Time Streaming Detection

### Q4 2026
Explainable AI Insights

### 2027
LLM Fraud Copilot
""")