import streamlit as st


def load_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f3f5f8; color: #1c2834; }
        section[data-testid="stSidebar"] {
            background: #0b1f33;
            border-right: 1px solid #071422;
        }
        section[data-testid="stSidebar"] * { color: #e7eef6 !important; }
        .desk-mark { padding: 8px 4px 18px; border-bottom: 1px solid rgba(255,255,255,.12); margin-bottom: 16px; }
        .desk-mark strong { display: block; font-size: 18px; letter-spacing: .04em; }
        .desk-mark span { display: block; color: #9fb3c8 !important; font-size: 13px; margin-top: 4px; }
        .desk-head {
            background: white;
            border: 1px solid #d9e0e8;
            border-left: 4px solid #0b1f33;
            padding: 18px 22px;
            margin-bottom: 16px;
        }
        .desk-kicker {
            color: #5c6b7a;
            font-size: 12px;
            letter-spacing: .08em;
            text-transform: uppercase;
            font-weight: 700;
        }
        .desk-head h1 { font-size: 28px; font-weight: 700; margin: 4px 0 6px; color: #0b1f33; }
        .desk-head p { margin: 0; color: #3d4d5c; font-size: 15px; }
        .note {
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 5px solid #2563eb;
            border-radius: 10px;
            padding: 14px 16px;
            margin: 8px 0 16px;
        }
        .stButton > button {
            background: #2563eb;
            color: white;
            border: 0;
            border-radius: 8px;
            font-weight: 650;
        }
        .stButton > button:hover { color: white; background: #1d4ed8; }
        .footer { text-align: center; color: #64748b; font-size: 14px; margin-top: 36px; }
        .stat-card {
            background: white;
            border: 1px solid #d9e0e8;
            border-top: 3px solid #0b1f33;
            border-radius: 2px;
            padding: 14px 16px;
            min-height: 108px;
        }
        .stat-title { color: #64748b; font-size: 14px; }
        .stat-value { color: #0f172a; font-size: 32px; font-weight: 750; margin-top: 6px; }
        .stat-detail { color: #475569; font-size: 13px; margin-top: 6px; }
        ol.steps {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 8px 16px 8px 8px;
            margin: 0 0 18px;
            list-style: none;
        }
        ol.steps li {
            display: flex;
            gap: 12px;
            align-items: flex-start;
            padding: 10px 8px;
            color: #1f2937;
        }
        ol.steps li span {
            flex: 0 0 28px;
            height: 28px;
            border-radius: 999px;
            background: #dbeafe;
            color: #1e40af;
            font-weight: 750;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .score-track {
            background: #e5e7eb;
            border-radius: 999px;
            height: 14px;
            overflow: hidden;
            margin: 8px 0 16px;
        }
        .score-fill { background: #0b1f33; height: 100%; }
        .sheet-wrap { overflow-x: auto; background: white; border: 1px solid #d9e0e8; margin: 8px 0 12px; }
        table.sheet { width: 100%; border-collapse: collapse; font-size: 14px; }
        table.sheet th {
            text-align: left;
            background: #0b1f33;
            color: white;
            padding: 10px 12px;
            font-weight: 650;
        }
        table.sheet td { padding: 10px 12px; border-bottom: 1px solid #e6ebf0; color: #1c2834; }
        .badge { display: inline-block; padding: 3px 8px; font-weight: 700; font-size: 12px; letter-spacing: .04em; }
        .badge.clear { background: #e5f6ee; color: #0f6b45; }
        .badge.refer { background: #fff4df; color: #8a5a00; }
        .sheet-note { color: #5c6b7a; font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
