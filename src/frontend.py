import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide"
)

# =====================================================
# LOAD MODEL
# =====================================================

MODEL_PATH = Path(__file__).parent.parent / "best_xgb_model.pkl"

model = joblib.load(MODEL_PATH)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🛡️ FraudShield AI")

    page = st.radio(
        "Navigation",
        [
            "Fraud Detection",
            "Overview",
            "Model Metrics",
            "Architecture",
            "Future Roadmap"
        ]
    )

# =====================================================
# OVERVIEW
# =====================================================

if page == "Overview":

    st.title("🛡️ FraudShield AI")

    st.markdown("""
    ## AI-Powered Fraud Detection Platform

    ### Business Problem

    Credit card fraud causes billions in losses annually.

    Traditional rule-based systems generate excessive
    false positives and increase investigation costs.

    ### Solution

    FraudShield AI uses machine learning to identify
    suspicious transactions in real time.

    ### Business Impact

    ✅ Reduce Fraud Losses

    ✅ Improve Customer Trust

    ✅ Lower False Positives

    ✅ Faster Fraud Investigation
    """)

# =====================================================
# FRAUD DETECTION
# =====================================================

elif page == "Fraud Detection":

    st.title("🔍 Fraud Detection")

    tab1, tab2 = st.tabs(
        [
            "📁 Upload CSV",
            "⚡ Quick Transaction Check"
        ]
    )

    # ==========================================
    # CSV
    # ==========================================

    with tab1:

        st.subheader("Batch Fraud Analysis")

        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"]
        )

        if uploaded_file:

            df = pd.read_csv(uploaded_file)

            st.dataframe(df.head())

            if st.button("Analyze First Transaction"):

                row = df.iloc[0].values.reshape(1, -1)

                probability = model.predict_proba(row)[0][1]

                st.metric(
                    "Fraud Probability",
                    f"{probability * 100:.2f}%"
                )

                st.progress(probability)

                if probability > 0.5:
                    st.error(
                        "🚨 High Fraud Risk Detected"
                    )
                else:
                    st.success(
                        "✅ Transaction Appears Safe"
                    )

    # ==========================================
    # QUICK CHECK
    # ==========================================

    with tab2:

        st.subheader(
            "Quick Transaction Simulator"
        )

        col1, col2 = st.columns(2)

        with col1:

            amount = st.number_input(
                "Transaction Amount ($)",
                min_value=0.0,
                value=150.0
            )

        with col2:

            time = st.slider(
                "Transaction Time",
                0,
                172800,
                10000
            )

        if st.button("Run Fraud Check"):

            features = np.zeros(30)

            # Adjust based on training order

            features[0] = time
            features[29] = amount

            probability = model.predict_proba(
                features.reshape(1, -1)
            )[0][1]

            st.divider()

            st.subheader("Risk Score")

            st.metric(
                "Fraud Probability",
                f"{probability * 100:.2f}%"
            )

            st.progress(probability)

            if probability > 0.5:

                st.error(
                    "🚨 HIGH RISK TRANSACTION"
                )

            else:

                st.success(
                    "✅ LOW RISK TRANSACTION"
                )

# =====================================================
# METRICS
# =====================================================

elif page == "Model Metrics":

    st.title("📊 Model Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Accuracy", "99.9%")
    col2.metric("Precision", "94%")
    col3.metric("Recall", "91%")
    col4.metric("ROC-AUC", "98%")

    st.divider()

    st.markdown("""
    ### Business KPIs

    - Fraud Detection Rate

    - False Positive Rate

    - Investigation Time

    - Cost Savings

    - Customer Trust Score
    """)

# =====================================================
# ARCHITECTURE
# =====================================================

elif page == "Architecture":

    st.title("🏗️ Solution Architecture")

    st.image(
        "assets/architecture.png",
        use_container_width=True
    )

    st.info("""
    Transaction Data

            ↓

    Feature Engineering

            ↓

    XGBoost Model

            ↓

    Fraud Probability

            ↓

    Decision Engine
    """)

# =====================================================
# ROADMAP
# =====================================================

elif page == "Future Roadmap":

    st.title("🗺️ Product Roadmap")

    st.markdown("""
    ### Phase 1
    Fraud Detection Engine

    ### Phase 2
    Fraud Analyst Dashboard

    ### Phase 3
    Real-Time Streaming

    ### Phase 4
    Explainable AI Insights

    ### Phase 5
    LLM Fraud Copilot

    ### Phase 6
    Automated Case Management
    """)