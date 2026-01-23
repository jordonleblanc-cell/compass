# Elmcrest Supervisor Platform
# Streamlit Application
# Author: Elmcrest Leadership Intelligence (Prototype)

import streamlit as st
import pandas as pd
from dataclasses import dataclass

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="🧭",
    layout="wide",
)

# ----------------------------
# Data Models
# ----------------------------
@dataclass
class StaffProfile:
    name: str
    communication_style: str
    motivation_driver: str

COMMUNICATION_STYLES = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIVATION_DRIVERS = ["Achievement", "Growth", "Purpose", "Connection"]

# ----------------------------
# Utility Logic
# ----------------------------
def generate_archetype(style, motivation):
    return f"{style} + {motivation}"

# ----------------------------
# Sidebar Navigation
# ----------------------------
st.sidebar.title("🧭 Supervisor HUD")
page = st.sidebar.radio(
    "Navigate",
    [
        "Supervisor's Guide",
        "Team DNA",
        "Conflict Mediator",
        "Career Pathfinder",
        "Organization Pulse",
    ],
)

# ----------------------------
# Supervisor's Guide
# ----------------------------
if page == "Supervisor's Guide":
    st.title("Supervisor's Guide")
    st.caption("Individualized operational manuals for staff supervision")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Staff Member Name")
        style = st.selectbox("Communication Style", COMMUNICATION_STYLES)
        motivation = st.selectbox("Motivation Driver", MOTIVATION_DRIVERS)

    with col2:
        if name:
            st.subheader("Profile Summary")
            st.metric("Archetype", generate_archetype(style, motivation))
            st.info("This archetype defines how this staff member communicates, responds to stress, and stays motivated.")

    if st.button("Generate Supervisor Guide"):
        st.success("Supervisor Guide Generated")
        st.markdown("""
        ### Heads‑Up Display (HUD)
        - **Stress Signature:** Behavior under pressure
        - **Prescription:** Supervisor actions before discipline
        - **Best Coaching Moves:** Profile‑specific strategies
        """)

# ----------------------------
# Team DNA
# ----------------------------
elif page == "Team DNA":
    st.title("Team DNA")
    st.caption("Unit‑level culture, blind spots, and risk indicators")

    uploaded = st.file_uploader("Upload team roster (CSV)", type=["csv"])

    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df, use_container_width=True)

        st.subheader("Dominant Culture")
        st.warning("Encourager‑heavy teams risk accountability drift")

        st.subheader("Missing Voices")
        st.info("No Trackers detected → documentation and follow‑through risk")

# ----------------------------
# Conflict Mediator
# ----------------------------
elif page == "Conflict Mediator":
    st.title("Conflict Mediator")
    st.caption("Predictive conflict analysis and coaching scripts")

    col1, col2 = st.columns(2)

    with col1:
        staff_a = st.selectbox("Staff A Style", COMMUNICATION_STYLES)
    with col2:
        staff_b = st.selectbox("Staff B Style", COMMUNICATION_STYLES)

    if st.button("Analyze Conflict"):
        st.error("Potential Tempo + Focus Clash Detected")
        st.markdown("""
        **Intervention Protocol**
        1. Name the mismatch
        2. Align on safety and outcomes
        3. Choose Speed vs Process for 24h
        """)

# ----------------------------
# Career Pathfinder
# ----------------------------
elif page == "Career Pathfinder":
    st.title("Career Pathfinder")
    st.caption("Readiness analysis for leadership advancement")

    current_role = st.selectbox("Current Role", ["DSP", "Supervisor", "Program Supervisor", "Manager"])
    target_role = st.selectbox("Target Role", ["Supervisor", "Program Supervisor", "Manager", "Director"])

    if st.button("Assess Readiness"):
        st.info("Gray Zone Assignment Generated")
        st.markdown("""
        **Scenario:** Policy allows discretion
        - Identify risks
        - Design mitigations
        - Define decision triggers
        - Make a defensible recommendation
        """)

# ----------------------------
# Organization Pulse
# ----------------------------
elif page == "Organization Pulse":
    st.title("Organization Pulse")
    st.caption("Agency‑wide leadership and culture diagnostics")

    st.metric("Dominant Style", "Director")
    st.metric("Top Motivation", "Purpose")

    st.subheader("Leadership Pipeline Health")
    st.error("⚠️ Cloning Bias Detected")
    st.markdown("Leadership team exceeds 60% Director profiles. Innovation and empathy risk flagged.")

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption("Elmcrest Supervisor Platform • Leadership Intelligence Prototype")
