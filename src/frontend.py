import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
)


# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --navy: #101828;
        --ink: #1f2937;
        --muted: #667085;
        --blue: #2563eb;
        --cyan: #06b6d4;
        --green: #10b981;
        --amber: #f59e0b;
        --red: #ef4444;
        --panel: #ffffff;
        --soft: #f3f7fb;
        --line: #e5e7eb;
    }.

    .stApp {
        background: #F3F6FA;
        color: var(--ink);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 55%, #083344 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }

    section[data-testid="stSidebar"] * {
        color: #eef6ff !important;
    }

    .brand {
        padding: 22px 8px 18px;
    }

    .brand-logo {
        font-size: 46px;
        line-height: 1;
        margin-bottom: 12px;
    }

    .brand-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0;
        color: #ffffff;
    }

    .brand-subtitle {
        color: #a9c7df !important;
        font-size: 15px;
        margin-top: 8px;
        line-height: 1.5;
    }

    .hero{
    padding:36px;
    border-radius:20px;
    background:linear-gradient(135deg,#0F172A 0%,#1E40AF 55%,#2563EB 100%);
    color:white;
    box-shadow:0 20px 40px rgba(0,0,0,.18);
    margin-bottom:30px;
}

.hero h1{
    font-size:48px;
    font-weight:800;
    margin-bottom:12px;
}

.hero p{
    font-size:18px;
    color:#dbeafe;
}


        div[data-testid="stMetric"]{

    background:white;

    border-radius:18px;

    padding:24px;

    border:none;

    box-shadow:0 10px 25px rgba(15,23,42,.08);

    transition:.3s;

}

div[data-testid="stMetric"]:hover{

    transform:translateY(-8px);

    box-shadow:0 20px 40px rgba(37,99,235,.15);

}
    div[data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    div[data-testid="stMetricValue"] {
        color: var(--navy);
        font-weight: 800;
    }

    .status-card {
        background: rgba(255,255,255,.95);
        border: 1px solid var(--line);
        border-left: 5px solid var(--cyan);
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, .07);
        margin: 10px 0 18px;
    }

    .reason-box {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 8px;
        padding: 18px 20px;
        margin-top: 16px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, .06);
    }

    .reason-title {
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 8px;
        color: var(--navy);
    }

    .safe {
        border-left: 6px solid var(--green);
    }

    .danger {
        border-left: 6px solid var(--red);
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
        color: white;
        border: 0;
        border-radius: 8px;
        padding: .7rem 1.1rem;
        font-weight: 700;
        box-shadow: 0 12px 24px rgba(37, 99, 235, .25);
    }

    .stButton > button:hover {
        color: white;
        filter: brightness(1.03);
        border: 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,.82);
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 14px;
        margin-top: 48px;
        padding: 18px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# PATHS
# --------------------------------------------------

APP_DIR = Path(__file__).resolve().parent
CANDIDATE_ROOTS = [
    APP_DIR,
    APP_DIR.parent,
    Path.cwd(),
    Path.cwd().parent,
]


def first_existing(paths):
    for path in paths:
        if path.exists():
            return path
    return paths[0]


MODEL_PATH = first_existing([root / "best_xgb_model.pkl" for root in CANDIDATE_ROOTS])
ARCH_PATH = first_existing([root / "assets" / "architecture.png" for root in CANDIDATE_ROOTS])
SAFE_IMAGE = first_existing([root / "assets" / "Fraud_Prediction_Safe.png" for root in CANDIDATE_ROOTS])
FRAUD_IMAGE = first_existing([root / "assets" / "fraud_Prediction_Not_Safe.png" for root in CANDIDATE_ROOTS])


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    st.error(f"Model Load Error: {exc}")
    st.info("Check that best_xgb_model.pkl is in the same folder as frontend.py or one folder above it.")
    st.stop()


# --------------------------------------------------
# FEATURE PRESETS
# Model expects: Time, V1, V2, ... V28, Amount
# --------------------------------------------------

FEATURE_COLUMNS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]

NORMAL_PRESET = {
    "Time": 45000.0,
    "Amount": 42.0,
    "V1": -0.2,
    "V2": 0.15,
    "V3": 0.8,
    "V4": -0.4,
    "V5": 0.1,
    "V6": 0.2,
    "V7": -0.1,
    "V8": 0.05,
    "V9": 0.1,
    "V10": 0.2,
    "V11": -0.2,
    "V12": 0.4,
    "V13": 0.1,
    "V14": 0.3,
    "V15": 0.1,
    "V16": 0.2,
    "V17": 0.1,
    "V18": 0.1,
    "V19": 0.0,
    "V20": 0.0,
    "V21": 0.0,
    "V22": 0.0,
    "V23": 0.0,
    "V24": 0.0,
    "V25": 0.0,
    "V26": 0.0,
    "V27": 0.0,
    "V28": 0.0,
}

FRAUD_PRESET = {
    "Time": 75500.0,
    "Amount": 1.0,
    "V1": -2.3,
    "V2": 1.9,
    "V3": -3.8,
    "V4": 4.2,
    "V5": -1.8,
    "V6": -1.2,
    "V7": -3.1,
    "V8": 0.7,
    "V9": -2.5,
    "V10": -5.0,
    "V11": 3.6,
    "V12": -5.4,
    "V13": 0.2,
    "V14": -6.7,
    "V15": 0.1,
    "V16": -3.1,
    "V17": -5.2,
    "V18": -1.7,
    "V19": 0.8,
    "V20": 0.4,
    "V21": 0.6,
    "V22": -0.2,
    "V23": -0.3,
    "V24": -0.4,
    "V25": 0.2,
    "V26": 0.1,
    "V27": 0.5,
    "V28": 0.2,
}


def make_feature_row(values):
    return pd.DataFrame([[values.get(col, 0.0) for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)


def predict_probability(feature_df):
    return float(model.predict_proba(feature_df)[0][1])


def explain_prediction(probability, values):
    amount = values.get("Amount", 0.0)
    risk_signals = []

    if values.get("V14", 0) < -3:
        risk_signals.append("V14 is strongly negative, which is a common fraud signal in this PCA-based dataset.")
    if values.get("V12", 0) < -3:
        risk_signals.append("V12 is unusually low, so the transaction pattern is far from normal behavior.")
    if values.get("V10", 0) < -3:
        risk_signals.append("V10 is sharply negative, adding to the fraud-like pattern.")
    if values.get("V17", 0) < -3:
        risk_signals.append("V17 is also very low, which often appears in fraudulent samples.")
    if values.get("V4", 0) > 2:
        risk_signals.append("V4 is high, which increases the model's suspicion for this transaction.")
    if amount <= 5 and probability > 0.5:
        risk_signals.append("The amount is small, but the hidden transaction pattern looks suspicious.")

    if probability > 0.5:
        if not risk_signals:
            risk_signals.append("The combined V1-V28 pattern is close to transactions the model learned as fraud.")
        return "Fraud transaction reason", risk_signals

    normal_reasons = [
        "The fraud probability is below the decision threshold of 50%.",
        "The V1-V28 pattern is closer to normal transactions than fraud transactions.",
        "No strong negative anomaly was found in major risk features such as V10, V12, V14, and V17.",
    ]
    if amount < 250:
        normal_reasons.append("The amount is not unusually large for a normal card transaction.")
    return "Normal transaction reason", normal_reasons


def show_prediction(probability, values):
    st.metric("Fraud Probability", f"{probability * 100:.2f}%")
    st.progress(min(max(probability, 0.0), 1.0))

    title, reasons = explain_prediction(probability, values)

    if probability > 0.5:
        st.error("High Risk Transaction")
        image_path = FRAUD_IMAGE
        box_class = "reason-box danger"
    else:
        st.success("Low Risk Transaction")
        image_path = SAFE_IMAGE
        box_class = "reason-box safe"

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)

    st.markdown(
        f"""
        <div class="{box_class}">
            <div class="reason-title">{title}</div>
            <ul>
                {''.join(f'<li>{reason}</li>' for reason in reasons)}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        "<div class='footer'>FraudShield AI Enterprise Platform • Version 2.0 • Designed by Noira Khan</div>",
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-logo">🏦</div>
            <div class="brand-title">FraudShield AI</div>
            <div class="brand-subtitle">Enterprise Fraud Intelligence Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Executive Dashboard",
            "Fraud Detection Engine",
            "Model Performance",
            "System Architecture",
            "Product Roadmap",
        ],
    )


# --------------------------------------------------
# EXECUTIVE DASHBOARD
# --------------------------------------------------

if page == "Executive Dashboard":
    st.markdown(
        """
        <div class="hero">
            <h1>FraudShield AI</h1>
            <p>Real-time transaction intelligence for fraud detection, risk monitoring, and executive visibility.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions Today", "1.25M", "+4.2%")
    c2.metric("Fraud Cases", "2,814", "-12%")
    c3.metric("Fraud Rate", "0.22%")
    c4.metric("Estimated Savings", "$4.2M")

    st.markdown(
        """
        <div class="status-card">
            <strong>Operational Status:</strong> Stable<br>
            <strong>Current Fraud Risk:</strong> Low<br>
            <strong>Average Decision Latency:</strong> 41 ms
        </div>
        """,
        unsafe_allow_html=True,
    )

    trend = pd.DataFrame(
        {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Fraud Cases": [1200, 1450, 1700, 1500, 1200, 900],
        }
    )

    st.subheader("Fraud Activity Trend")
    st.line_chart(trend.set_index("Month"))

    st.subheader("Today's Executive Brief")
    st.info(
        """
        1.25 Million transactions processed.

        AI prevented approximately $4.2 Million in fraud.

        False positives reduced by 12%.

        System availability is 99.98%.
        """
    )


# --------------------------------------------------
# FRAUD DETECTION
# --------------------------------------------------

elif page == "Fraud Detection Engine":
    st.markdown(
        """
        <div class="hero">
            <h1>Fraud Detection Engine</h1>
            <p>Use the presets below: Normal Sample should stay safe, Fraud Sample should trigger high risk.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["Quick Transaction Check", "Upload CSV"])

    with tab1:
        st.subheader("Demo Transaction Simulator")
        st.info("To catch fraud, choose the Fraud Sample preset. Amount and Time alone are not enough because the model was trained on Time, V1-V28, and Amount.")

        preset_name = st.radio(
            "Transaction example",
            ["Normal Sample", "Fraud Sample", "Custom"],
            horizontal=True,
        )

        if preset_name == "Fraud Sample":
            values = FRAUD_PRESET.copy()
        else:
            values = NORMAL_PRESET.copy()

        values["Amount"] = st.number_input(
            "Transaction Amount ($)",
            min_value=0.0,
            value=float(values["Amount"]),
            step=1.0,
        )

        values["Time"] = st.slider(
            "Transaction Time",
            min_value=0,
            max_value=172800,
            value=int(values["Time"]),
        )

        with st.expander("Advanced model features V1-V28"):
            left, right = st.columns(2)
            for index, feature in enumerate([f"V{i}" for i in range(1, 29)]):
                container = left if index < 14 else right
                values[feature] = container.number_input(
                    feature,
                    value=float(values.get(feature, 0.0)),
                    step=0.1,
                    format="%.4f",
                )

        st.caption("Suggested test values: use Normal Sample for a safe transaction and Fraud Sample for a fraud transaction.")

        if st.button("Run Fraud Check"):
            feature_df = make_feature_row(values)
            probability = predict_probability(feature_df)
            show_prediction(probability, values)

    with tab2:
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(), use_container_width=True)

            feature_df = df.copy()
            if "Class" in feature_df.columns:
                feature_df = feature_df.drop(columns=["Class"])

            missing = [col for col in FEATURE_COLUMNS if col not in feature_df.columns]

            if missing:
                st.error("CSV must contain these columns: Time, V1-V28, Amount.")
                st.write("Missing columns:", missing)
            elif st.button("Analyze First Transaction"):
                row_df = feature_df[FEATURE_COLUMNS].iloc[[0]]
                values = row_df.iloc[0].to_dict()
                probability = predict_probability(row_df)
                show_prediction(probability, values)


# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

elif page == "Model Performance":
    st.markdown(
        """
        <div class="hero">
            <h1>Model Performance</h1>
            <p>Performance snapshot for fraud monitoring and operational review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions", "1.25M", "+4.2%")
    c2.metric("Fraud Prevented", "$4.2M", "+9.1%")
    c3.metric("False Positives", "1.9%", "-12%")
    c4.metric("Decision Time", "41 ms", "Faster")

    performance = pd.DataFrame(
        {
            "Metric": ["Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"],
            "Score": [0.999, 0.94, 0.91, 0.92, 0.98],
        }
    )

    st.subheader("Model Quality")
    st.bar_chart(performance.set_index("Metric"))


# --------------------------------------------------
# ARCHITECTURE
# --------------------------------------------------

elif page == "System Architecture":
    st.markdown(
        """
        <div class="hero">
            <h1>FraudShield Architecture</h1>
            <p>Data ingestion, feature processing, model scoring, and decision delivery.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if ARCH_PATH.exists():
        st.image(str(ARCH_PATH), use_container_width=True)
    else:
        st.warning(f"Architecture image not found at: {ARCH_PATH}")
        st.info("Place the file at assets/architecture.png beside frontend.py.")


# --------------------------------------------------
# ROADMAP
# --------------------------------------------------

elif page == "Product Roadmap":
    st.markdown(
        """
        <div class="hero">
            <h1>Product Roadmap</h1>
            <p>Planned improvements for fraud operations, real-time scoring, and explainable AI.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
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
        """
    )


footer()
