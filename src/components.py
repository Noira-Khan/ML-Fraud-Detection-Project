import html

import streamlit as st


def stat_card(title: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-title">{html.escape(title)}</div>
            <div class="stat-value">{html.escape(value)}</div>
            <div class="stat-detail">{html.escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_steps(steps: list[str]) -> None:
    items = "".join(
        f"<li><span>{index}</span>{html.escape(text)}</li>"
        for index, text in enumerate(steps, start=1)
    )
    st.markdown(f"<ol class='steps'>{items}</ol>", unsafe_allow_html=True)


def page_header(kicker: str, title: str, summary: str) -> None:
    st.markdown(
        f"""
        <div class="desk-head">
            <div class="desk-kicker">{html.escape(kicker)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(summary)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def decision_sheet(scored, limit: int = 100) -> None:
    """Show disposition and score first. Model inputs stay out of this table."""
    shown = scored.head(limit)
    has_meaning = "Meaning" in shown.columns
    body = []
    for case_number, (_, row) in enumerate(shown.iterrows(), start=1):
        referred = str(row["decision"]) == "review"
        label = "Review" if referred else "Allow"
        badge = "refer" if referred else "clear"
        meaning = f"<td>{html.escape(str(row['Meaning']))}</td>" if has_meaning else ""
        body.append(
            "<tr>"
            f"<td>FS-{case_number:04d}</td>"
            f"<td><span class='badge {badge}'>{label}</span></td>"
            f"<td>{float(row['fraud_probability']) * 100:.2f}%</td>"
            f"<td>{float(row['Amount']):,.2f}</td>"
            f"<td>{float(row['Time']):,.0f}</td>"
            f"{meaning}"
            "</tr>"
        )
    extra = ""
    if len(scored) > limit:
        extra = f"<p class='sheet-note'>Showing the first {limit:,} of {len(scored):,} cases. The download has every row.</p>"
    st.markdown(
        f"""
        <div class="sheet-wrap">
            <table class="sheet">
                <thead>
                    <tr>
                        <th>Case</th>
                        <th>Disposition</th>
                        <th>Fraud score</th>
                        <th>Amount</th>
                        <th>Seconds</th>
                        {"<th>What it means</th>" if has_meaning else ""}
                    </tr>
                </thead>
                <tbody>
                    {''.join(body)}
                </tbody>
            </table>
        </div>
        {extra}
        """,
        unsafe_allow_html=True,
    )


def customer_alert(amount: float, decision: str, score_percent: float) -> None:
    from fraud_detection_pipeline.alerts import (
        banker_explanation,
        customer_message,
        should_notify_customer,
    )

    st.markdown("**In plain words**")
    st.write(banker_explanation(decision, score_percent))
    if not should_notify_customer(decision):
        return

    message = customer_message(amount)
    st.markdown("**What the customer gets at that moment**")
    st.caption("Preview only. This screen does not send a real alert or a real email.")
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"""
            <div class="notice phone">
                <div class="notice-kicker">Phone alert</div>
                <strong>Finance Shield</strong>
                <p>{html.escape(message["push"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="notice mail">
                <div class="notice-kicker">Email</div>
                <strong>{html.escape(message["subject"])}</strong>
                <p>{html.escape(message["email"]).replace(chr(10), "<br>")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.caption(message["when"] + " Nothing is sent when the score stays under 95%.")


def score_bar(probability: float) -> None:
    width = max(0.0, min(probability, 1.0)) * 100
    st.markdown(
        f"""
        <div class="score-track" aria-label="Fraud score">
            <div class="score-fill" style="width:{width:.2f}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
