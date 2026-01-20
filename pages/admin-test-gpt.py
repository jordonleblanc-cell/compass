import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import time

# ------------------------------------------------------------
# SAFETY DEFAULTS
# ------------------------------------------------------------
st.set_page_config(layout="wide")

# ------------------------------------------------------------
# MOCK DATA LOADING (replace with your real loader)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    return pd.DataFrame([
        {
            "name": "Alex Morgan",
            "role": "Supervisor",
            "p_comm": "Director",
            "s_comm": "Facilitator",
            "p_mot": "Achievement",
            "s_mot": "Purpose",
        },
        {
            "name": "Jamie Lee",
            "role": "Staff",
            "p_comm": "Encourager",
            "s_comm": "Tracker",
            "p_mot": "Connection",
            "s_mot": "Growth",
        },
    ])

df = load_data()

# ------------------------------------------------------------
# PEDAGOGY GUIDE (SAFE)
# ------------------------------------------------------------
PEDAGOGY_GUIDE = {
    1: "Phase 1 focuses on safety, consistency, and baseline expectations.",
    2: "Phase 2 develops judgment, pattern recognition, and decision-making.",
    3: "Phase 3 builds ownership, delegation, and systems thinking.",
}

# ------------------------------------------------------------
# SAFE COACHING MATRIX ENGINE (NO SHARED STATE)
# ------------------------------------------------------------
def build_coaching_matrix(p_comm, s_comm, p_mot, s_mot, phase):
    phase_focus = {
        1: {
            "title": "Phase 1 – Safety & Consistency",
            "aim": "Establish predictable, safe baseline behavior.",
            "supervisor_role": "Coach closely, reduce ambiguity.",
            "common_pitfall": "Assuming competence before consistency exists.",
        },
        2: {
            "title": "Phase 2 – Judgment & Anticipation",
            "aim": "Strengthen decision-making and risk awareness.",
            "supervisor_role": "Ask for recommendations, not just updates.",
            "common_pitfall": "Rescuing too early.",
        },
        3: {
            "title": "Phase 3 – Ownership & Systems",
            "aim": "Shift from managing moments to managing systems.",
            "supervisor_role": "Delegate outcomes, not tasks.",
            "common_pitfall": "Keeping authority centralized.",
        },
    }

    moves = [
        {
            "title": "1) Set the Standard",
            "why": "Clarity reduces anxiety and rework.",
            "how": "State the expectation before discussing feelings.",
            "scripts": ["Here’s the standard we are working toward."],
            "avoid": "Hinting instead of naming expectations.",
        },
        {
            "title": "2) Transfer Ownership",
            "why": "Ownership builds accountability.",
            "how": "Ask for a recommendation with rationale.",
            "scripts": ["What do you recommend and why?"],
            "avoid": "Giving the answer too early.",
        },
        {
            "title": "3) Align Motivation",
            "why": "People perform better when work connects to values.",
            "how": "Link task to motivation driver.",
            "scripts": ["This matters because it impacts safety and trust."],
            "avoid": "Reducing work to compliance only.",
        },
        {
            "title": "4) Stress-Test Thinking",
            "why": "Anticipation prevents crisis.",
            "how": "Ask what could go wrong and how to mitigate.",
            "scripts": ["What’s the biggest risk here?"],
            "avoid": "Assuming best-case outcomes.",
        },
        {
            "title": "5) Define Escalation Triggers",
            "why": "Prevents silent failure.",
            "how": "Name when to call for help.",
            "scripts": ["Escalate immediately if X occurs."],
            "avoid": "Waiting too long to escalate.",
        },
        {
            "title": "6) Close the Loop",
            "why": "Learning requires feedback.",
            "how": "Debrief outcomes and lessons.",
            "scripts": ["What worked? What would you change?"],
            "avoid": "Skipping reflection.",
        },
    ]

    return moves, phase_focus[int(phase)]

# ------------------------------------------------------------
# IPDP RENDERER (CRASH-PROOF)
# ------------------------------------------------------------
def render_ipdp(name, role, p_comm, s_comm, p_mot, s_mot):
    st.subheader("🧠 Individual Professional Development Plan (IPDP)")
    st.caption("Each phase is independent and collapsible.")

    def render_phase(phase_num):
        with st.expander(f"Phase {phase_num}", expanded=(phase_num == 1)):
            try:
                moves, phase_card = build_coaching_matrix(
                    p_comm, s_comm, p_mot, s_mot, phase_num
                )

                with st.container(border=True):
                    st.markdown(f"### 🎯 {phase_card['title']}")
                    c1, c2, c3 = st.columns(3)
                    c1.markdown("**Aim**")
                    c1.write(phase_card["aim"])
                    c2.markdown("**Supervisor Role**")
                    c2.write(phase_card["supervisor_role"])
                    c3.markdown("**Common Pitfall**")
                    c3.write(phase_card["common_pitfall"])

                with st.expander("🧭 Coaching Matrix (6 Moves)", expanded=True):
                    left, right = st.columns(2)
                    for i, mv in enumerate(moves):
                        col = left if i % 2 == 0 else right
                        with col:
                            with st.expander(mv["title"]):
                                st.markdown("**Why this works**")
                                st.write(mv["why"])
                                st.markdown("**How to do it**")
                                st.write(mv["how"])
                                st.markdown("**Scripts**")
                                for s in mv["scripts"]:
                                    st.success(f"“{s}”")
                                st.markdown("**Avoid**")
                                st.warning(mv["avoid"])

                with st.expander("🎓 Pedagogical Deep Dive"):
                    st.info(PEDAGOGY_GUIDE.get(phase_num, ""))

            except Exception as e:
                st.error(f"Phase {phase_num} failed safely: {e}")

    render_phase(1)
    render_phase(2)
    render_phase(3)

# ------------------------------------------------------------
# PAGE BODY
# ------------------------------------------------------------
st.title("Compass – Supervisor Toolkit")

if not df.empty:
    person = st.selectbox("Select Staff Member", df["name"].tolist())
    d = df[df["name"] == person].iloc[0]

    render_ipdp(
        name=d["name"],
        role=d["role"],
        p_comm=d["p_comm"],
        s_comm=d["s_comm"],
        p_mot=d["p_mot"],
        s_mot=d["s_mot"],
    )