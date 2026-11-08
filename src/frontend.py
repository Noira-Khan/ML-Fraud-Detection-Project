import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from components import score_bar, show_steps, stat_card  # noqa: E402
from fraud_detection_pipeline.history import (  # noqa: E402
    append_records,
    clear_history,
    load_history,
    new_record,
    summarize,
)
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
PAGES = [
    "Past payments",
    "Check one payment",
    "Check a file",
    "Model record",
    "How it fits together",
]


def payment_source(values: dict) -> str:
    def same(example: dict) -> bool:
        return all(abs(float(values.get(column, 0.0)) - float(example[column])) < 0.0001 for column in FEATURE_COLUMNS)

    if same(EVERYDAY_PURCHASE):
        return "Everyday purchase"
    if same(SUSPICIOUS_PATTERN):
        return "Suspicious pattern"
    return "Custom payment"


def remember(values: dict, result: dict) -> None:
    fingerprint = tuple(round(float(values[column]), 6) for column in FEATURE_COLUMNS)
    if st.session_state.get("saved_fingerprint") == fingerprint:
        return
    append_records(
        [
            new_record(
                source=payment_source(values),
                amount=values["Amount"],
                dataset_seconds=values["Time"],
                fraud_probability=result["fraud_probability"],
                decision=result["decision"],
            )
        ]
    )
    st.session_state.saved_fingerprint = fingerprint


def show_result(result: dict, image_path: Path) -> None:
    decision = "Review" if result["decision"] == "review" else "Allow"
    left, right = st.columns(2)
    with left:
        stat_card("Decision", decision, "A review flag does not decline the card.")
    with right:
        stat_card("Fraud score", f"{result['fraud_probability'] * 100:.2f}%", "Review starts at 95%.")
    score_bar(result["fraud_probability"])
    if result["decision"] == "review":
        st.error(result["summary"])
    else:
        st.success(result["summary"])
    if image_path.exists():
        st.image(str(image_path), width="stretch")
    st.markdown("**Why the score moved**")
    for reason in result["reasons"]:
        st.write(f"- {reason}")
    st.caption("This payment was saved under Past payments.")


def score_example(values: dict) -> None:
    try:
        result = score_mapping(values)
    except ScoringError as exc:
        st.error(str(exc))
        return
    remember(values, result)
    image = FRAUD_IMAGE if result["decision"] == "review" else SAFE_IMAGE
    show_result(result, image)


def history_frame() -> pd.DataFrame:
    try:
        return load_history()
    except Exception as exc:
        st.error(f"The saved-payment file could not be read. {exc}")
        return pd.DataFrame()


with st.sidebar:
    st.markdown("### Finance Shield")
    st.caption("Scores stay on this computer. This demo does not connect to a bank.")
    page = st.radio("Go to", PAGES)

if page == "Past payments":
    st.markdown(
        """
        <div class="hero">
            <h1>Past payments</h1>
            <p>Every payment you score in this demo is listed here. The counts come only from that saved list.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_steps(
        [
            "Score one payment, or score the included sample file.",
            "Come back to this page. The newest payment is at the top.",
            "Use the filter to see Allow, Review, or both. Review means a person should look. The card is not declined.",
        ]
    )
    history = history_frame()
    totals = summarize(history)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Saved payments", f"{totals['rows']:,}", "Scored in this demo")
    with c2:
        stat_card("Allow", f"{totals['allow']:,}", "Under the 95% cutoff")
    with c3:
        stat_card("Review", f"{totals['review']:,}", "At or above 95%")
    with c4:
        stat_card("Review cutoff", "95%", "Same cutoff as the holdout")

    if totals["rows"] == 0:
        st.info("No payments have been scored on this computer yet. Open Check one payment and choose an example.")
    else:
        choice = st.radio("Show", ["All", "Allow", "Review"], horizontal=True)
        view = history.copy()
        if choice != "All":
            view = view[view["decision"].astype(str) == choice.lower()]
        view = view.sort_values("scored_at", ascending=False)
        st.caption(f"Showing {min(len(view), 100):,} of {len(view):,} matching payments.")
        display = view.head(100).copy()
        display["When"] = display["scored_at"]
        display["Source"] = display["source"]
        display["Amount"] = display["amount"].map(lambda value: f"{float(value):,.2f}")
        display["Score"] = display["fraud_probability"].map(lambda value: f"{float(value) * 100:.2f}%")
        display["Decision"] = display["decision"].map({"allow": "Allow", "review": "Review"})
        st.dataframe(
            display[["When", "Source", "Amount", "Score", "Decision"]],
            width="stretch",
            hide_index=True,
        )
        st.download_button(
            "Download the saved list",
            history.to_csv(index=False).encode("utf-8"),
            file_name="finance_shield_history.csv",
            mime="text/csv",
        )

    st.divider()
    if st.checkbox("I want to erase the saved list on this computer"):
        if st.button("Erase saved payments"):
            clear_history()
            st.session_state.saved_fingerprint = None
            st.session_state.logged_file_token = None
            st.rerun()

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
    show_steps(
        [
            "Choose Everyday purchase or Suspicious pattern. You do not need to type V1 to V28.",
            "Change the amount only if you want to. Amount alone usually does not flip this model.",
            "Read Allow or Review. The payment is saved under Past payments.",
        ]
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
    if left.button("Everyday purchase", width="stretch"):
        use_example(EVERYDAY_PURCHASE)
        st.rerun()
    if right.button("Suspicious pattern", width="stretch"):
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
        values = {"Amount": st.session_state.amount, "Time": st.session_state.time_value}
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
    show_steps(
        [
            "Click the sample button, or upload a CSV with the thirty columns in the right order.",
            "Read how many rows are Allow and how many are Review.",
            "Download the scored file if you want a copy. The same rows are saved under Past payments.",
        ]
    )
    use_sample = st.button("Score the included sample")
    upload = st.file_uploader("Or upload a CSV", type=["csv"])

    table = None
    source = ""
    token = ""
    if use_sample:
        table = pd.read_csv(SAMPLE_PATH)
        source = "Included sample"
        token = f"sample-{st.session_state.get('sample_clicks', 0) + 1}"
        st.session_state.sample_clicks = st.session_state.get("sample_clicks", 0) + 1
    elif upload is not None:
        table = pd.read_csv(upload)
        source = upload.name
        token = f"{upload.name}:{getattr(upload, 'size', len(table))}"

    if table is not None:
        try:
            scored = score_table(table)
        except ScoringError as exc:
            st.error(str(exc))
        else:
            if token and st.session_state.get("logged_file_token") != token:
                append_records(
                    [
                        new_record(
                            source=source,
                            amount=row["Amount"],
                            dataset_seconds=row["Time"],
                            fraud_probability=row["fraud_probability"],
                            decision=row["decision"],
                        )
                        for _, row in scored.iterrows()
                    ]
                )
                st.session_state.logged_file_token = token
            review_count = int((scored["decision"] == "review").sum())
            allow_count = int((scored["decision"] == "allow").sum())
            a, b, c = st.columns(3)
            with a:
                stat_card("Rows scored", f"{len(scored):,}", "From this file")
            with b:
                stat_card("Allow", f"{allow_count:,}", "Under 95%")
            with c:
                stat_card("Review", f"{review_count:,}", "At or above 95%")
            st.dataframe(scored, width="stretch")
            st.download_button(
                "Download scores",
                scored.to_csv(index=False).encode("utf-8"),
                file_name="finance_shield_scores.csv",
                mime="text/csv",
            )
            st.caption("Review means the score is at least 95%. Nothing in the file is declined.")

elif page == "Model record":
    st.markdown(
        """
        <div class="hero">
            <h1>Model record</h1>
            <p>These are the holdout numbers printed for the saved model. They are not the counts on Past payments.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_steps(
        [
            "Read precision, recall, and F1. Those three numbers are the holdout result.",
            "Treat accuracy as a warning. A model that never catches fraud can still look about 99.8% accurate.",
            "The 95% cutoff is the cutoff that produced the numbers on this page.",
        ]
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Fraud precision", f"{HOLDOUT_RECORD['fraud_precision']:.2f}", "Of the flags, how many were fraud")
    with c2:
        stat_card("Fraud recall", f"{HOLDOUT_RECORD['fraud_recall']:.2f}", "Of the fraud, how many were caught")
    with c3:
        stat_card("Fraud F1", f"{HOLDOUT_RECORD['fraud_f1']:.2f}", "Balance of precision and recall")
    with c4:
        stat_card("Holdout fraud cases", str(HOLDOUT_RECORD["test_fraud"]), f"Out of {HOLDOUT_RECORD['test_rows']:,} test payments")
    st.markdown(
        f"""
        <div class="note">
        On the untouched test split ({HOLDOUT_RECORD['test_rows']:,} payments,
        {HOLDOUT_RECORD['test_fraud']} of them fraud), a 95% cutoff caught about 82% of the fraud
        and about 93% of the payments it flagged were fraud.
        The public file has {DATASET_RECORD['rows']:,} payments and {DATASET_RECORD['fraud']:,} fraud cases.
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
            <p>One path, from the form or a file, through the saved model, to Allow or Review, then into the local list.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    show_steps(
        [
            "You pick an example or a file. The full public dataset is not required.",
            "The scorer keeps thirty columns in one order: Time, V1 through V28, then Amount.",
            "The saved model returns a fraud score between 0 and 1.",
            "A score of 95% or more is marked Review. Anything lower is marked Allow.",
            "The decision is saved on this computer under Past payments. The card is not declined.",
        ]
    )
    if ARCH_IMAGE.exists():
        st.image(str(ARCH_IMAGE), width="stretch")
    st.caption("The picture is the original pipeline sketch. The running demo stops at local scoring and the saved list.")

st.markdown(
    "<div class='footer'>Finance Shield local demo · Noira Khan · A review flag does not decline a card.</div>",
    unsafe_allow_html=True,
)
