import streamlit as st

def kpi_card(
        title,
        value,
        change,
        color="#2563EB",
        icon="💳"
):

    st.markdown(
        f"""
<div style="
background:white;
padding:24px;
border-radius:18px;
box-shadow:0 8px 25px rgba(0,0,0,.08);
border-top:6px solid {color};
transition:0.3s;
">

<div style="font-size:30px;">
{icon}
</div>

<div style="
font-size:15px;
color:#64748b;
margin-top:8px;
">

{title}

</div>

<div style="
font-size:38px;
font-weight:700;
margin-top:12px;
color:#0f172a;
">

{value}

</div>

<div style="
color:{color};
font-weight:600;
margin-top:10px;
">

{change}

</div>

</div>

""",
unsafe_allow_html=True
)