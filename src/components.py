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
