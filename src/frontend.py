import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fraud_detection_pipeline.scoring import (  # noqa: E402
    DATASET_RECORD,
    DECISION_THRESHOLD,
    EVERYDAY_PURCHASE,
    FEATURE_COLUMNS,
    HOLDOUT_RECORD,
    SAMPLE_PATH,
    SUSPICIOUS_PATTERN,
    ScoringError,
    score_mapping,
    score_table,
)
from theme import load_theme  # noqa: E402

st.set_page_config(page_title="Finance Shield", page_icon="🛡️", layout="wide")
load_theme()

SAFE_IMAGE = ROOT / "assets" / "fraud_Prediction_Safe.png"
FRAUD_IMAGE = ROOT / "assets" / "Fraud_Prediction_Not_Safe.png"
ARCH_IMAGE = ROOT / "assets" / "architecture.png"


def show_result(result: dict, image_path: Path) -> None:
    decision = result["decision"]
    label = "Review" if decision == "review" else "Allow"
    st.metric("Decision", label)
    st.metric("Fraud score", f"{result['fraud_probability'] * 100:.2f}%")
    st.progress(min(max(result["fraud_probability"], 0.0), 1.0))
    if decision == "review":
        st.error(result["summary"])
    else:
        st.success(result["summary"])
    if image_path.exists():
        st.image(str(image_path), width="stretch")
    st.markdown("**Why the score moved**")
    for reason in result["reasons"]:
        st.write(f"- {reason}")
    st.caption("Cutoff used for the published evaluation: 95%. A review flag does not decline the card.")


def score_example(values: dict) -> None:
    try:
        result = score_mapping(values)
    except ScoringError as exc:
        st.error(str(exc))
        return
    image = FRAUD_IMAGE if result["decision"] == "review" else SAFE_IMAGE
    show_result(result, image)


with st.sidebar:
    st.markdown("### Finance Shield")
    st.caption("A local demo for one card payment. It does not connect to a bank.")
    page = st.radio(
        "Go to",
        [
            "Start here",
            "Check one payment",
            "Check a file",
            "Model record",
            "How it fits together",
        ],
    )

if page == "Start here":
    st.markdown(
        """
        <div class="hero">
            <h1>Finance Shield</h1>
            <p>See whether one card payment would be allowed or sent to a person for review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="note">
        This screen uses the saved model in this project. It is not a live payments feed,
        and the figures on the old dashboard were not measurements from that feed.
        The counts below come from the public credit-card file and the holdout written in the training notebook.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Payments in the file", f"{DATASET_RECORD['rows']:,}")
    c2.metric("Fraud cases in the file", f"{DATASET_RECORD['fraud']:,}")
    c3.metric("Fraud share", "0.1727%")
    c4.metric("Review cutoff", "95%")
    st.subheader("Try it in one step")
    st.write(
        "Open **Check one payment**, then choose **Everyday purchase** or **Suspicious pattern**. "
        "You do not need the original 284,807-row file, and you do not need to type V1 to V28."
    )
    st.write(
        "The model only sees Time, an amount, and 28 anonymous numbers from the public dataset. "
        "It cannot see the merchant, the country, or the cardholder."
    )

elif page == "Check one payment":
    st.markdown(
        """
        <div class="hero">
            <h1>Check one payment</h1>
            <p>Start from an example. Open the advanced fields only if you want to change the anonymous numbers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    def use_example(example: dict) -> None:
        st.session_state.amount = float(example["Amount"])
        st.session_state.time_value = float(example["Time"])
        for name in FEATURE_COLUMNS[1:-1]:
            st.session_state[name] = float(example.get(name, 0.0))
        st.session_state.ready_to_score = True

    if "amount" not in st.session_state:
        use_example(EVERYDAY_PURCHASE)
        st.session_state.ready_to_score = False

    left, right = st.columns(2)
    if left.button("Everyday purchase", use_container_width=True):
        use_example(EVERYDAY_PURCHASE)
        st.rerun()
    if right.button("Suspicious pattern", use_container_width=True):
        use_example(SUSPICIOUS_PATTERN)
        st.rerun()

    st.number_input("Amount", min_value=0.0, step=1.0, key="amount")
    st.number_input(
        "Seconds since the first payment in the dataset",
        min_value=0.0,
        max_value=172800.0,
        step=100.0,
        key="time_value",
    )
    with st.expander("Anonymous features V1 to V28"):
        st.caption("These are not card fields you would see at a till. V14 carries most of this model's weight.")
        grid_left, grid_right = st.columns(2)
        for index, name in enumerate(FEATURE_COLUMNS[1:-1]):
            column = grid_left if index < 14 else grid_right
            column.number_input(name, step=0.1, format="%.4f", key=name)

    if st.button("Score this payment"):
        st.session_state.ready_to_score = True

    if st.session_state.get("ready_to_score"):
        values = {
            "Amount": st.session_state.amount,
            "Time": st.session_state.time_value,
        }
        for name in FEATURE_COLUMNS[1:-1]:
            values[name] = st.session_state[name]
        score_example(values)

elif page == "Check a file":
    st.markdown(
        """
        <div class="hero">
            <h1>Check a file</h1>
            <p>Score the included two-row sample, or upload a file with Time, V1 to V28, and Amount.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    use_sample = st.button("Score the included sample")
    upload = st.file_uploader("Or upload a CSV", type=["csv"])

    table = None
    if use_sample:
        table = pd.read_csv(SAMPLE_PATH)
    elif upload is not None:
        table = pd.read_csv(upload)

    if table is not None:
        try:
            scored = score_table(table)
        except ScoringError as exc:
            st.error(str(exc))
        else:
            review_count = int((scored["decision"] == "review").sum())
            allow_count = int((scored["decision"] == "allow").sum())
            a, b, c = st.columns(3)
            a.metric("Rows scored", f"{len(scored):,}")
            b.metric("Allow", f"{allow_count:,}")
            c.metric("Review", f"{review_count:,}")
            st.dataframe(scored, width="stretch")
            st.download_button(
                "Download scores",
                scored.to_csv(index=False).encode("utf-8"),
                file_name="finance_shield_scores.csv",
                mime="text/csv",
            )
            st.caption(f"Review means the score is at least {DECISION_THRESHOLD:.0%}. Nothing in the file is declined.")

elif page == "Model record":
    st.markdown(
        """
        <div class="hero">
            <h1>Model record</h1>
            <p>These are the holdout numbers printed for the saved model. Accuracy is shown only so it is not mistaken for the result.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fraud precision", f"{HOLDOUT_RECORD['fraud_precision']:.2f}")
    c2.metric("Fraud recall", f"{HOLDOUT_RECORD['fraud_recall']:.2f}")
    c3.metric("Fraud F1", f"{HOLDOUT_RECORD['fraud_f1']:.2f}")
    c4.metric("Holdout fraud cases", str(HOLDOUT_RECORD["test_fraud"]))
    st.markdown(
        f"""
        <div class="note">
        On the untouched test split ({HOLDOUT_RECORD['test_rows']:,} payments,
        {HOLDOUT_RECORD['test_fraud']} of them fraud), a 95% cutoff caught about 82% of the fraud
        and about 93% of the payments it flagged were fraud.
        A model that called every payment legitimate would still be about 99.8% accurate
        and would catch nothing. Accuracy is not the number to lead with.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "Logistic regression on the same split, after balancing, reached about 0.92 recall "
        "and only about 0.06 precision. It caught fraud by flagging a large share of good payments. "
        "The saved tree model is the one that kept precision near 0.93."
    )
    st.caption(HOLDOUT_RECORD["source"])
    st.caption(
        "A cross-validation score near 0.9999 was computed on rebalanced training rows. "
        "That number is not this holdout."
    )

elif page == "How it fits together":
    st.markdown(
        """
        <div class="hero">
            <h1>How a score is produced</h1>
            <p>One path, from the form or a file, through the saved model, to Allow or Review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "1. You pick an example or a file. The full public dataset is not required to run this demo."
    )
    st.write("2. The scorer keeps thirty columns in one order: Time, V1 through V28, then Amount.")
    st.write("3. The saved XGBoost model returns a fraud score between 0 and 1.")
    st.write("4. A score of 95% or more is marked Review. Anything lower is marked Allow.")
    st.write("5. The screen explains the main features. It does not block a payment.")
    if ARCH_IMAGE.exists():
        st.image(str(ARCH_IMAGE), width="stretch")
    st.caption("The picture is the original pipeline sketch. The running demo stops at local scoring.")

st.markdown(
    "<div class='footer'>Finance Shield local demo · Noira Khan · A review flag does not decline a card.</div>",
    unsafe_allow_html=True,
)
