import streamlit as st


def load_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #eef3f8; color: #1f2937; }
        section[data-testid="stSidebar"] {
            background: #0f172a;
            border-right: 1px solid rgba(255,255,255,.08);
        }
        section[data-testid="stSidebar"] * { color: #eef6ff !important; }
        .hero {
            padding: 28px 32px;
            border-radius: 16px;
            background: linear-gradient(135deg, #0f172a 0%, #1e40af 70%);
            color: white;
            margin-bottom: 20px;
        }
        .hero h1 { font-size: 36px; font-weight: 750; margin: 0 0 8px; color: white; }
        .hero p { font-size: 17px; color: #dbeafe; margin: 0; }
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
            border: 1px solid #e5e7eb;
            border-top: 4px solid #2563eb;
            border-radius: 12px;
            padding: 16px 18px;
            min-height: 118px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, .05);
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
        .score-fill { background: #2563eb; height: 100%; }
        </style>
        """,
        unsafe_allow_html=True,
    )
