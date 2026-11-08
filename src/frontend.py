import importlib
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import components as ui_components  # noqa: E402

importlib.reload(ui_components)
from components import (  # noqa: E402
    customer_alert,
    decision_sheet,
    page_header,
    score_bar,
    show_steps,
    stat_card,
)
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

ARCH_IMAGE = ROOT / "assets" / "architecture.png"
PAGES = [
    "Payment queue",
    "Single payment",
    "Batch file",
    "Model record",
    "Operating rules",
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


def show_result(result: dict, amount: float) -> None:
    decision = "Review" if result["decision"] == "review" else "Allow"
    left, right = st.columns(2)
    with left:
        stat_card("Disposition", decision, "Review sends the case to an analyst. The card is not declined.")
    with right:
        stat_card("Fraud score", f"{result['fraud_probability'] * 100:.2f}%", "Refer at 95% or above.")
    score_bar(result["fraud_probability"])
    customer_alert(amount, result["decision"], result["fraud_probability"] * 100)
    st.markdown("**Case notes**")
    for reason in result["reasons"]:
        st.write(f"- {reason}")
    st.caption("Filed on the payment queue.")


def score_example(values: dict) -> None:
    try:
        result = score_mapping(values)
    except ScoringError as exc:
        st.error(str(exc))
        return
    remember(values, result)
    show_result(result, float(values["Amount"]))


def history_frame() -> pd.DataFrame:
    try:
        return load_history()
    except Exception as exc:
        st.error(f"The saved-payment file could not be read. {exc}")
        return pd.DataFrame()


with st.sidebar:
    st.markdown(
        """
        <div class="desk-mark">
            <strong>FINANCE SHIELD</strong>
            <span>Card risk desk</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Dispositions stay on this workstation. This desk does not decline a card.")
    page = st.radio("Desk", PAGES)

if page == "Payment queue":
    page_header(
        "Queue",
        "Payment queue",
        "Cases scored on this workstation. Counts come only from this list.",
    )
    show_steps(
        [
            "Score a single payment or a batch file.",
            "Return here. The newest case is at the top.",
            "Filter Allow or Review. Review means an analyst should look. The card is not declined.",
        ]
    )
    history = history_frame()
    totals = summarize(history)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Cases on file", f"{totals['rows']:,}", "Scored on this workstation")
    with c2:
        stat_card("Allow", f"{totals['allow']:,}", "Under the 95% cutoff")
    with c3:
        stat_card("Review", f"{totals['review']:,}", "At or above 95%")
    with c4:
        stat_card("Review cutoff", "95%", "Same cutoff as the holdout")

    if totals["rows"] == 0:
        st.info("The queue is empty. Open Single payment and score a case.")
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

elif page == "Single payment":
    page_header(
        "Authorisation",
        "Single payment",
        "Score one card payment. Start from a desk example, or open the model inputs if you need to change them.",
    )
    show_steps(
        [
            "Choose Everyday purchase or Suspicious pattern. You do not need to type V1 to V28.",
            "Change the amount only if you want to. Amount alone usually does not flip this model.",
            "Read the disposition and the score on this page. The case is filed on the payment queue.",
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

elif page == "Batch file":
    page_header(
        "Batch",
        "Batch file",
        "Score a file of card payments. Disposition and fraud score are shown on this page.",
    )
    show_steps(
        [
            "Load the desk sample. Each row has a short note on what that payment is meant to show.",
            "Read the decision sheet on this page. Score, disposition, and the note come before the model inputs.",
            "Download the full file if you need the model inputs as well. The same cases are filed on the queue.",
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
            if "Meaning" in table.columns:
                scored.insert(0, "Meaning", table["Meaning"].astype(str).reset_index(drop=True).tolist())
            review_count = int((scored["decision"] == "review").sum())
            allow_count = int((scored["decision"] == "allow").sum())
            a, b, c = st.columns(3)
            with a:
                stat_card("Cases scored", f"{len(scored):,}", "From this file")
            with b:
                stat_card("Allow", f"{allow_count:,}", "Under 95%")
            with c:
                stat_card("Review", f"{review_count:,}", "At or above 95%")
            st.subheader("Decision sheet")
            decision_sheet(scored)
            referred = scored[scored["decision"] == "review"]
            if referred.empty:
                st.success("No case in this file reached 95%. No customer message is sent.")
            else:
                st.warning(
                    f"{len(referred):,} case(s) reached 95%. "
                    "Each one would send the customer a phone alert and an email at that moment."
                )
                first = referred.iloc[0]
                customer_alert(float(first["Amount"]), "review", float(first["fraud_probability"]) * 100)
            with st.expander("Model inputs for this file"):
                st.caption("V1 to V28 are anonymous. They are not merchant or cardholder fields.")
                st.dataframe(scored, width="stretch", hide_index=True)
            export = scored.copy()
            export.insert(0, "case", [f"FS-{number:04d}" for number in range(1, len(export) + 1)])
            st.download_button(
                "Download the decision file",
                export.to_csv(index=False).encode("utf-8"),
                file_name="finance_shield_scores.csv",
                mime="text/csv",
            )

elif page == "Model record":
    page_header(
        "Control",
        "Model record",
        "Holdout figures for the model this desk uses. They are not the counts on the payment queue.",
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

elif page == "Operating rules":
    page_header(
        "Rules",
        "How a case is scored",
        "One path: a payment or a file, the saved model, then Allow or Review on the queue.",
    )
    show_steps(
        [
            "You pick an example or a file. The full public dataset is not required.",
            "The scorer keeps thirty columns in one order: Time, V1 through V28, then Amount.",
            "The saved model returns a fraud score between 0 and 1.",
            "A score of 95% or more is marked Review. At that moment the customer gets a phone alert and an email. Anything lower is Allow, and no message is sent.",
            "The case is filed on the payment queue. The card is not blocked until a person decides.",
        ]
    )
    if ARCH_IMAGE.exists():
        st.image(str(ARCH_IMAGE), width="stretch")
    st.caption("The picture is the original pipeline sketch. The running demo stops at local scoring and the saved list.")

st.markdown(
    "<div class='footer'>Finance Shield · Card risk desk · A Review disposition does not decline the card.</div>",
    unsafe_allow_html=True,
)
