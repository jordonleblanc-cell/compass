# Redesigned Supervisor Dashboard
# NOTE: This preserves all existing data models, profiles, and logic,
# but restructures the UI into a modern, task-oriented dashboard.

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Elmcrest Supervisor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ BRAND & CSS ------------------
st.markdown("""
<style>
:root {
    --primary:#1a73e8;
    --bg:#f8f9fa;
    --card:#ffffff;
    --border:#e0e0e0;
    --text:#202124;
}

.stApp { background-color: var(--bg); }

.card {
    background: var(--card);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.card h3 { margin-bottom: 8px; }

.action-btn button {
    height: 120px;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: white;
    text-align: left;
}

.action-btn button:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ------------------ DATA FETCH ------------------
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

@st.cache_data(ttl=60)
def fetch_data():
    try:
        r = requests.get(GOOGLE_SCRIPT_URL)
        if r.status_code == 200:
            return pd.DataFrame(r.json())
    except:
        return pd.DataFrame()

# ------------------ LOAD DATA ------------------
df = fetch_data()

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.markdown("### Supervisor Session")
    st.caption("Logged in as: Supervisor")
    st.divider()
    page = st.radio("Navigate", ["Dashboard", "Team Profiles", "Insights", "Reports"])

# ------------------ DASHBOARD ------------------
if page == "Dashboard":
    st.markdown("## Supervisor Dashboard")

    # HERO METRICS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Staff Assessed", len(df))
    with c2:
        st.metric("Avg Comm Score", round(df[["primarycomm", "secondarycomm"]].mean().mean(), 1) if not df.empty else "–")
    with c3:
        st.metric("Avg Motivation", round(df[["primarymotiv", "secondarymotiv"]].mean().mean(), 1) if not df.empty else "–")
    with c4:
        st.metric("Cottages", df['cottage'].nunique() if 'cottage' in df else "–")

    st.divider()

    # ACTIONS
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("🧠 Review Team Profiles", key="profiles"):
            st.session_state.page_jump = "Team Profiles"
    with a2:
        if st.button("📊 View Communication Trends", key="trends"):
            st.session_state.page_jump = "Insights"
    with a3:
        if st.button("🎯 Coaching Recommendations", key="coach"):
            st.session_state.page_jump = "Insights"
    with a4:
        if st.button("📄 Export Reports", key="reports"):
            st.session_state.page_jump = "Reports"

# ------------------ TEAM PROFILES ------------------
elif page == "Team Profiles":
    st.markdown("## Team Profiles")

    for _, row in df.iterrows():
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"### {row.get('name','Staff')}")
            st.caption(f"Role: {row.get('role','')} | Cottage: {row.get('cottage','')}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Communication Style**")
                st.write(row.get('primarycomm'))
            with col2:
                st.markdown("**Motivation Driver**")
                st.write(row.get('primarymotiv'))

            with st.expander("Coaching Guidance"):
                st.write("Use tailored coaching language based on this profile.")

            st.markdown("</div>", unsafe_allow_html=True)

# ------------------ INSIGHTS ------------------
elif page == "Insights":
    st.markdown("## Team Insights")

    if not df.empty:
        fig = px.histogram(df, x="primarycomm", title="Primary Communication Styles")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.histogram(df, x="primarymotiv", title="Primary Motivations")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("Click a bar to discuss coaching strategies aligned to that trend.")

# ------------------ REPORTS ------------------
elif page == "Reports":
    st.markdown("## Reports & Exports")
    st.write("Generate PDFs, summaries, and email-ready reports here.")

    st.button("Generate Supervisor Summary PDF")
    st.button("Email Coaching Snapshot")

# ------------------ PAGE JUMP ------------------
if 'page_jump' in st.session_state:
    page = st.session_state.page_jump
    del st.session_state.page_jump
    st.experimental_rerun()
