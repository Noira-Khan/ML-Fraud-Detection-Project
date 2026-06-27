import streamlit as st

def load_theme():

    st.markdown("""
<style>

/* --------------------------------------------------
GENERAL
-------------------------------------------------- */

html, body {
    font-family: "Inter", sans-serif;
    background: #EEF3F8;
}

/* Main App Background */
.stApp{
    background-color:#EEF3F8;
}

/* Main content padding */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    padding-left:3rem;
    padding-right:3rem;
}

/* --------------------------------------------------
SIDEBAR
-------------------------------------------------- */

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] *{
    color:white;
}

[data-testid="stSidebarNav"]{
    display:none;
}

/* --------------------------------------------------
HEADER
-------------------------------------------------- */

.main-title{
    font-size:46px;
    font-weight:700;
    color:#0F172A;
}

.subtitle{
    color:#64748B;
    font-size:18px;
    margin-top:-10px;
}

/* --------------------------------------------------
KPI CARDS
-------------------------------------------------- */

div[data-testid="metric-container"]{

    background:white;

    border-radius:16px;

    padding:22px;

    border:1px solid #E2E8F0;

    box-shadow:0px 6px 18px rgba(15,23,42,0.08);

    transition:all .25s ease;

}

div[data-testid="metric-container"]:hover{

    transform:translateY(-5px);

    box-shadow:0px 12px 28px rgba(37,99,235,.15);

}

/* --------------------------------------------------
BUTTONS
-------------------------------------------------- */

.stButton>button{

    background:#2563EB;

    color:white;

    border:none;

    border-radius:10px;

    height:50px;

    width:100%;

    font-weight:600;

}

.stButton>button:hover{

    background:#1D4ED8;

}

/* --------------------------------------------------
SUCCESS BOX
-------------------------------------------------- */

.stSuccess{

    border-radius:12px;

}

/* --------------------------------------------------
INFO BOX
-------------------------------------------------- */

.stInfo{

    border-radius:12px;

}

/* --------------------------------------------------
TABLES
-------------------------------------------------- */

thead tr th{

    background:#0F172A;

    color:white;

}

/* --------------------------------------------------
FOOTER
-------------------------------------------------- */

.footer{

    margin-top:60px;

    padding:15px;

    text-align:center;

    color:#64748B;

    font-size:14px;

}

</style>
""", unsafe_allow_html=True)