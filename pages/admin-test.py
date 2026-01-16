import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import re
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform", 
    page_icon="📊", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- NAVIGATION HELPER ---
if "current_view" not in st.session_state:
    st.session_state.current_view = "Supervisor's Guide"

def set_view(view_name):
    st.session_state.current_view = view_name

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

BRAND_COLORS = {
    "blue": "#1a73e8",
    "green": "#34a853",
    "teal": "#12b5cb",
    "gray": "#5f6368",
    "red": "#ea4335",
    "yellow": "#fbbc04"
}

# --- 3. CSS STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

        /* --- LIGHT MODE VARIABLES --- */
        :root {
            --primary: #1a73e8;        
            --primary-hover: #1557b0;
            --background: #f8f9fa;
            --card-bg: #ffffff;
            --text-main: #202124;
            --text-sub: #5f6368;
            --border-color: #e0e0e0;
            --input-bg: #ffffff;
            --shadow: 0 2px 5px rgba(0,0,0,0.05);
            --score-track: #e8eaed;
        }

        /* --- DARK MODE VARIABLES --- */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary: #8ab4f8;
                --primary-hover: #aecbfa;
                --background: #131314;
                --card-bg: #1e1e1f;
                --text-main: #e8eaed;
                --text-sub: #9aa0a6;
                --border-color: #444746;
                --input-bg: #1e1e1f;
                --shadow: 0 4px 8px rgba(0,0,0,0.4);
                --score-track: #5f6368;
            }
        }

        /* --- GLOBAL RESETS & TYPOGRAPHY --- */
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
            color: var(--text-main) !important;
            background-color: var(--background);
        }
        
        .stApp {
            background-color: var(--background);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Google Sans', sans-serif !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }

        /* --- COMPONENTS --- */

        /* Hide Sidebar Nav */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg);
            border-right: 1px solid var(--border-color);
        }

        /* Hero Box */
        .hero-box {
            background: linear-gradient(135deg, var(--primary) 0%, #1557b0 100%);
            padding: 40px;
            border-radius: 16px;
            color: white !important;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(26, 115, 232, 0.2);
        }
        .hero-title {
            color: white !important;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 8px;
            font-family: 'Google Sans', sans-serif;
        }
        .hero-subtitle {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 1.1rem;
            max-width: 800px;
            line-height: 1.5;
        }

        /* Navigation Buttons (Big Tiles) */
        div[data-testid="column"] .stButton button {
            background-color: var(--card-bg);
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            height: 140px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            padding: 24px;
            white-space: pre-wrap;
            text-align: left;
            transition: all 0.2s ease-in-out;
            border-radius: 16px;
        }
        div[data-testid="column"] .stButton button:hover {
            transform: translateY(-3px);
            border-color: var(--primary);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            color: var(--primary) !important;
        }
        div[data-testid="column"] .stButton button p {
            font-family: 'Google Sans', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
        }

        /* Standard Buttons */
        .stButton button:not([style*="height: 140px"]) {
            background-color: var(--primary);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-family: 'Google Sans', sans-serif;
            transition: background-color 0.2s;
            padding: 0.5rem 1rem;
        }
        .stButton button:not([style*="height: 140px"]):hover {
            background-color: var(--primary-hover);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        /* Inputs & Selectboxes */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: var(--input-bg) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            min-height: 45px;
        }
        
        /* Containers */
        div[data-testid="stContainer"] {
            border-radius: 12px;
        }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }

        /* Login Card */
        .login-card {
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 450px;
            margin: 80px auto;
            border: 1px solid var(--border-color);
            color: var(--text-main);
        }
        .login-title {
            color: var(--primary) !important;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .login-subtitle {
            color: var(--text-sub) !important;
            margin-bottom: 30px;
            font-size: 1rem;
        }
        .back-link {
            text-decoration: none;
            color: var(--text-sub);
            font-weight: 600;
            transition: color 0.2s;
            display: inline-block;
            margin-bottom: 20px;
        }
        .back-link:hover { color: var(--primary); }

        /* Expander Headers */
        .streamlit-expanderHeader {
            font-weight: 600;
            color: var(--text-main);
            background-color: var(--card-bg);
            border-radius: 8px;
        }

        /* Custom Phase Card */
        .phase-card {
            background-color: var(--card-bg);
            padding: 20px;
            border-left: 5px solid var(--primary);
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: var(--shadow);
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA FETCHING & STATE MANAGEMENT ---
@st.cache_data(ttl=60)
def fetch_staff_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200: return response.json()
        return []
    except: return []

def submit_data_to_google(payload):
    try:
        data_to_send = {
            "action": "save",
            "name": payload['name'],
            "email": payload.get('email', ''),
            "role": payload['role'],
            "cottage": payload['cottage'],
            "scores": {
                "primaryComm": payload['p_comm'],
                "secondaryComm": payload['s_comm'],
                "primaryMotiv": payload['p_mot'],
                "secondaryMotiv": payload['s_mot']
            }
        }
        response = requests.post(GOOGLE_SCRIPT_URL, json=data_to_send)
        if response.status_code == 200: return True
        return False
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

if 'staff_df' not in st.session_state:
    raw_data = fetch_staff_data()
    df_raw = pd.DataFrame(raw_data)
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.lower().str.strip() 
        if 'role' in df_raw.columns: df_raw['role'] = df_raw['role'].astype(str).str.strip()
        if 'cottage' in df_raw.columns: df_raw['cottage'] = df_raw['cottage'].astype(str).str.strip()
        if 'name' in df_raw.columns: df_raw['name'] = df_raw['name'].astype(str).str.strip()
    st.session_state.staff_df = df_raw

df_all = st.session_state.staff_df

# --- 5. SECURITY & LOGIN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_user_role" not in st.session_state: st.session_state.current_user_role = None
if "current_user_cottage" not in st.session_state: st.session_state.current_user_cottage = None
if "current_user_name" not in st.session_state: st.session_state.current_user_name = None

def check_password():
    MASTER_PW = st.secrets.get("ADMIN_PASSWORD", "admin2025")
    PS_PW = st.secrets.get("PS_PASSWORD", "ps2025")
    SS_PW = st.secrets.get("SS_PASSWORD", "ss2025")
    
    input_pw = st.session_state.password_input
    selected_user = st.session_state.user_select
    authorized = False
    
    if selected_user == "Administrator":
        if input_pw == MASTER_PW:
            authorized = True
            st.session_state.current_user_name = "Administrator"
            st.session_state.current_user_role = "Admin"
            st.session_state.current_user_cottage = "All"
        else:
            st.error("Incorrect Administrator Password.")
            return

    elif not df_all.empty:
        user_row = df_all[df_all['name'] == selected_user].iloc[0]
        role_raw = user_row.get('role', 'YDP')
        cottage_raw = user_row.get('cottage', 'All')
        if input_pw == MASTER_PW: authorized = True
        else:
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except: individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip(): authorized = True
            elif not authorized:
                if "Program Supervisor" in role_raw or "Director" in role_raw or "Manager" in role_raw:
                    if input_pw == PS_PW: authorized = True
                    else: st.error("Incorrect Access Code."); return
                elif "Shift Supervisor" in role_raw:
                    if input_pw == SS_PW: authorized = True
                    else: st.error("Incorrect Access Code."); return
                else: st.error("Access Restricted. Please contact your administrator."); return

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else: st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""
        <div style="position: absolute; top: 20px; left: 20px;">
            <a href="/" target="_self" class="back-link">← Back to Assessment</a>
        </div>
        <div class='login-card'>
            <div class='login-title'>Supervisor Access</div>
            <div class='login-subtitle'>Select your name and enter your role's access code to manage your team.</div>
    """, unsafe_allow_html=True)
    if not df_all.empty and 'name' in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Director"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Who are you?", user_names, key="user_select")
    else: st.selectbox("Who are you?", ["Administrator"], key="user_select")
    st.text_input("Access Code", type="password", key="password_input", on_change=check_password)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. DATA FILTERING ENGINE (RBAC) ---
def get_filtered_dataframe():
    user_role = str(st.session_state.current_user_role)
    user_cottage = str(st.session_state.current_user_cottage)
    current_user = str(st.session_state.current_user_name)
    current_df = st.session_state.staff_df

    if user_role == "Admin" or current_user == "Administrator" or "Director" in user_role or "Manager" in user_role:
        return current_df
    
    filtered_df = current_df.copy()
    if 'cottage' in current_df.columns and user_cottage != "All":
          filtered_df = filtered_df[filtered_df['cottage'] == user_cottage]
    
    if 'role' in current_df.columns:
        if "Program Supervisor" in user_role: pass
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
        elif "YDP" in user_role: filtered_df = filtered_df[filtered_df['name'] == current_user]

    return filtered_df

df = get_filtered_dataframe()

with st.sidebar:
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    st.divider()
    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# SUPERVISOR TOOL LOGIC STARTS HERE
# ==========================================

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# --- MASTER DATA PROFILES ---
COMM_PROFILES = {
    "Director": {
        "bullets": [
            "**Clarity:** They prioritize the 'bottom line' over the backstory, speaking in headlines to ensure immediate understanding.",
            "**Speed:** They process information rapidly and expect others to keep up, preferring a quick 80% solution over a delayed 100% solution.",
            "**Conflict:** They view conflict as a tool for problem-solving rather than a relationship breaker."
        ],
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately; avoid 'sandwiching' feedback with small talk.",
            "**Focus on Outcomes:** Tell them what needs to be achieved, but leave the how to them.",
            "**Respect Autonomy:** Give them space to operate independently; tight oversight feels like distrust."
        ]
    },
    "Encourager": {
        "bullets": [
            "**Verbal Processing:** They think out loud and prefer talking through problems rather than reading about them.",
            "**Optimism:** They naturally focus on the potential and the positive. They sell the vision effectively.",
            "**Relationship-First:** They influence people through liking and charisma. They prioritize the 'vibe'."
        ],
        "supervising_bullets": [
            "**Allow Discussion:** Give them a few minutes to chat and connect; cutting them off too early kills morale.",
            "**Ask for Specifics:** They speak in generalities ('It's going great!'). Ask 'What specifically is going great?'",
            "**Follow Up in Writing:** They may agree enthusiastically in the moment but forget the details."
        ]
    },
    "Facilitator": {
        "bullets": [
            "**Listening:** They gather all perspectives before speaking. They are the quiet ones in the meeting.",
            "**Consensus:** They prefer group agreement over unilateral action. They want everyone on the bus.",
            "**Process:** They value how a decision is made as much as the decision itself. They hate chaos."
        ],
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before asking for a decision. Send the agenda early.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless deliberation.",
            "**Solicit Opinion:** Ask them explicitly what they think. They will not fight for airtime."
        ]
    },
    "Tracker": {
        "bullets": [
            "**Detail-Oriented:** They communicate in data and precise details. They value accuracy above all else.",
            "**Risk-Averse:** They are cautious, avoiding definitive statements until they are 100% sure.",
            "**Process-Driven:** They are the guardians of the handbook. They quote the manual to settle disputes."
        ],
        "supervising_bullets": [
            "**Be Specific:** Do not use vague language. Give them the metric: 'Increase accuracy by 10%.'",
            "**Provide Data:** If you want to persuade them, bring the numbers and the facts.",
            "**Written Instructions:** Follow up verbal conversations with an email to provide a paper trail."
        ]
    }
}

MOTIV_PROFILES = {
    "Achievement": {
        "bullets": ["**Scoreboard:** Needs to know if winning.", "**Completion:** Loves checking boxes.", "**Efficiency:** Hates waste."],
        "strategies_bullets": ["**Visual Goals:** Dashboards.", "**Public Wins:** Acknowledge competence.", "**Autonomy:** Let them design the path."],
        "celebrate_bullets": ["Efficiency", "Clarity", "Resilience"],
        "celebrate_deep_dive": "**Recognition Language: Competence & Impact.**\nThey don't want a generic 'good job.' They want you to notice the specific problem they solved. \n\n*Script:* 'I saw how you reorganized the log system; it saved the team 20 minutes tonight. That was brilliant efficiency.'"
    },
    "Growth": {
        "bullets": ["**Curiosity:** Wants the 'why'.", "**Future-Focused:** Eye on next step.", "**Feedback:** Craves correction."],
        "strategies_bullets": ["**Stretch Assignments:** Push them.", "**Career Pathing:** Map the future.", "**Mentorship:** Connect with leaders."],
        "celebrate_bullets": ["Insight", "Development", "Courage"],
        "celebrate_deep_dive": "**Recognition Language: Trajectory & Potential.**\nPraise the *change* in their behavior, not just the result. Validate their struggle and learning. \n\n*Script:* 'I noticed you handled that crisis differently than last month. You stayed calm and followed the protocol perfectly. Your growth here is obvious.'"
    },
    "Purpose": {
        "bullets": ["**Values-Driven:** Moral compass.", "**Advocacy:** Fights for underdog.", "**Meaning:** Needs the 'why'."],
        "strategies_bullets": ["**The Why:** Connect to mission.", "**Storytelling:** Share impact.", "**Ethics:** Validate concerns."],
        "celebrate_bullets": ["Integrity", "Advocacy", "Consistency"],
        "celebrate_deep_dive": "**Recognition Language: Mission & Values.**\nConnect their work to the human story. Show them the invisible impact on the child's life. \n\n*Script:* 'Because you stayed late to talk to that youth, they felt safe enough to sleep tonight. You are the reason this program works.'"
    },
    "Connection": {
        "bullets": ["**Belonging:** Team is family.", "**Harmony:** Absorbs tension.", "**Support:** Helps peers."],
        "strategies_bullets": ["**Face Time:** In-person matters.", "**Team Rituals:** Build culture.", "**Personal Care:** Ask about life."],
        "celebrate_bullets": ["Loyalty", "Stabilization", "Culture"],
        "celebrate_deep_dive": "**Recognition Language: Belonging & Effort.**\nPraise their contribution to the team's health. Value the person, not just the worker. \n\n*Script:* 'The team vibe is so much better when you are on shift. Thank you for always looking out for your peers. We are lucky to have you.'"
    }
}

INTEGRATED_PROFILES = {
    # 1. DIRECTOR COMBINATIONS
    "Director-Achievement": {
        "title": "The Executive General",
        "synergy": "Operational Velocity. They don't just want to lead; they want to win. They cut through noise to identify the most efficient path to success.",
        "support": "**Operational Risk:** Name the operational risk of moving fast. Say, 'We can do this quickly if we build in these guardrails.' This validates their speed while protecting the agency from errors.",
        "thriving": "**Rapid Decision Architecture:** They make calls with partial information, preventing the team from freezing in analysis paralysis.\n**Objective Focus:** They separate story from fact, focusing on behaviors and outcomes.",
        "struggling": "**The Steamroller Effect:** They announce decisions without checking if the team is emotionally ready.\n**Burnout by Intensity:** They assume everyone has their stamina and push until the team breaks.",
        "interventions": ["**Phase 1: The Pause Button:** Force a deliberate delay between thought and action.", "**Phase 2: Narrative Leadership:** Coach them to script the 'Why' before they speak.", "**Phase 3: Multiplier Effect:** Train them to sit on their hands while deputies lead."],
        "questions": ["How are you defining success today beyond just metrics?", "What is one win you can celebrate right now?", "Are you driving the team too hard?"],
        "advancement": "**Delegate Effectively:** Give away tasks to prove they can build a team.\n**Allow Safe Failure:** Let the team struggle so they can learn.\n**Focus on Strategy:** Move from the 'how' to the 'why'.",
        "phase_1_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Director-Growth": {
        "title": "The Restless Improver",
        "synergy": "Transformational Leadership. They don't just manage the shift; they want to upgrade it. They see potential in every staff member and are willing to push hard to unlock it.",
        "support": "**Connect Goals:** Link their personal growth goals to youth outcomes and the mission. Help them see that 'getting better' isn't just about their resume, but about serving the client better.",
        "thriving": "**Diagnostic Speed:** They quickly identify the root causes of failures rather than treating symptoms.\n**Fearless Innovation:** They are willing to break the status quo to find a better way.",
        "struggling": "**The Pace Mismatch:** They get visibly frustrated with slow learners or bureaucracy.\n**'Fix-It' Fatigue:** They are constantly pointing out flaws and forgetting to validate what is working.",
        "interventions": ["**Phase 1: Validation:** Mandate that they validate the current effort before suggesting improvements.", "**Phase 2: Change Management:** Require a 'stakeholder analysis' for their next idea.", "**Phase 3: Capacity Building:** Shift them from idea generator to facilitator."],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "What are you learning from this struggle?"],
        "advancement": "**Delegate Effectively:** Stop being the 'fixer', become the 'developer.'\n**Allow Safe Failure:** Resist the urge to jump in and correct every mistake.\n**Focus on Strategy:** Design tomorrow's solutions.",
        "phase_1_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Director-Purpose": {
        "title": "The Mission Defender",
        "synergy": "Ethical Courage. They provide the moral backbone for the team, ensuring expediency never trumps integrity. They are the conscience of the unit and will speak truth to power.",
        "support": "**Share Values:** Share your own core values so they trust your leadership. They need to know you are 'one of the good guys.'\n**Operational Risk:** Frame slowing down as 'protecting the mission.'",
        "thriving": "**Unshakeable Advocacy:** They act immediately against injustice.\n**Clarity of 'Why':** They contextualize the grind for the staff.",
        "struggling": "**Righteous Rigidity:** They struggle to see the gray areas, viewing everything as black and white.\n**The Martyr Complex:** They overwork because they don't trust others to care enough.",
        "interventions": ["**Phase 1: The Gray Zone:** Practice identifying validity in opposing viewpoints.", "**Phase 2: Sustainable Advocacy:** Coach them to use a 'Tier System' for battles.", "**Phase 3: Cultural Architecture:** Move from fighting battles to building systems."],
        "questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?"],
        "advancement": "**Delegate Effectively:** Build a team that protects children.\n**Allow Safe Failure:** Trust that others also care.\n**Focus on Strategy:** Build systems that prevent injustice.",
        "phase_1_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial. You don't need a one-hour meeting; you need five minutes of real connection.\n**Backing:** Be candid about where you can back them up (air cover).",
        "thriving": "**Decisive Care:** They fix problems for people immediately.\n**Crisis Stabilization:** They become the calm human shield during a crisis.",
        "struggling": "**Us vs. Them:** They become hostile toward outsiders (admin, other units).\n**Over-Functioning:** They do everyone's job to protect them.",
        "interventions": ["**Phase 1: Delegation of Care:** Stop being the only fixer; assign care tasks to others.", "**Phase 2: Organizational Citizenship:** Expand the circle of loyalty to the whole agency.", "**Phase 3: Mentorship:** Transition from Captain to Admiral."],
        "questions": ["Are you avoiding this conversation to be kind, or to be safe?", "How can you be direct and caring at the same time?", "Are you protecting them from growth?"],
        "advancement": "**Delegate Effectively:** Stop being 'camp parent.'\n**Allow Safe Failure:** Learn the team is resilient.\n**Focus on Strategy:** Expand loyalty to the whole agency.",
        "phase_1_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The 'Bottom Line' Opener", "Move 2: The Autonomy Check", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    # 2. ENCOURAGER COMBINATIONS
    "Encourager-Achievement": {
        "title": "The Coach",
        "synergy": "Inspirational Performance. They make hard work feel like a game. They believe the team can win and their energy is contagious.",
        "support": "**Reality Checks:** Be the ground to their sky. Validate their enthusiasm but ask 'What is the plan if this goes wrong?'\n**Focus:** Help them pick one lane. They want to achieve everything at once.",
        "thriving": "**Team Morale:** The unit has high energy and believes they are the best.\n**Rallying:** They can turn a bad shift around with a pep talk.",
        "struggling": "**Overselling:** They promise things they can't deliver.\n**Disorganization:** They leave a wake of administrative chaos.",
        "interventions": ["**Phase 1: Follow-Through:** Focus on finishing.", "**Phase 2: Data Discipline:** Move from 'feeling' to 'fact.'", "**Phase 3: Grooming Talent:** Challenge them to let others shine."],
        "questions": ["How do we keep this energy up when things get boring?", "What are the specific steps to get to that vision?", "Who is doing the work: you or the team?"],
        "advancement": "**Detail Management:** Prove they can handle the boring stuff.\n**Listening:** Learn to sit back and let others speak.\n**Consistency:** Prove they can maintain performance when excitement fades.",
        "phase_1_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Encourager-Growth": {
        "title": "The Mentor",
        "synergy": "Developmental Charisma. They see the gold in people and talk it out of them. They make people feel smarter and more capable just by being around them.",
        "support": "**Structure:** Provide the trellis for their vine. Help them focus their creative energy.\n**Patience:** Remind them that growth is messy and non-linear.",
        "thriving": "**Talent Magnet:** People want to work for them because they feel grown.\n**Culture of Learning:** Mistakes are celebrated as learning opportunities.",
        "struggling": "**Shiny Object Syndrome:** They chase a new initiative every week.\n**Avoidance of Hard Conversations:** They want to inspire, not correct.",
        "interventions": ["**Phase 1: Closing the Loop:** Force them to finish what they start.", "**Phase 2: Difficult Feedback:** Role-play giving 'hard' feedback.", "**Phase 3: Systems of Growth:** Turn their informal mentoring into a formal curriculum."],
        "questions": ["Who are you investing in, and who are you ignoring?", "How do we turn this idea into a habit?", "Are you avoiding the hard truth to be nice?"],
        "advancement": "**Execution:** Prove they can implement, not just ideate.\n**Toughness:** Prove they can make the hard personnel calls.\n**Focus:** Prove they can stick to a boring plan.",
        "phase_1_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Encourager-Purpose": {
        "title": "The Heart of the Mission",
        "synergy": "Passionate Advocacy. They are the soul of the unit. They keep the emotional flame alive. They lead with raw emotion and belief.",
        "support": "**Emotional Boundaries:** Help them distinguish between caring and carrying.\n**Validation:** Frequently affirm that their heart is a strength, not a weakness.",
        "thriving": "**Cultural Carrier:** They set the emotional tone for the entire workspace.\n**Advocate:** They are fearless in speaking up for kids.",
        "struggling": "**Emotional Flooding:** They get so wrapped up in the 'story' that they lose objectivity.\n**Us vs. The System:** They can whip the team into a frenzy against 'cold' administration.",
        "interventions": ["**Phase 1: Boundaries:** Teach them to leave work at work.", "**Phase 2: Fact-Checking:** Force them to separate emotion from data.", "**Phase 3: Channeling Passion:** Give them a platform where passion is an asset."],
        "questions": ["Is this feeling a fact?", "How can you care without carrying?", "Are you whipping the team up or calming them down?"],
        "advancement": "**Objectivity:** Prove they can make dispassionate decisions.\n**Policy:** Understand the legal/fiscal reasons behind rules.\n**Resilience:** Bounce back without drama.",
        "phase_1_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Encourager-Connection": {
        "title": "The Team Builder",
        "synergy": "Social Cohesion. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy. They lead by making the workplace feel like a community.",
        "support": "**Hard Decisions:** Step in to be the 'bad guy' so they don't have to burn social capital.\n**Focus:** Remind them that work is the goal, fun is the method.",
        "thriving": "**Zero Turnover:** People stay because they love the team.\n**Conflict Resolution:** They talk things out and smooth over rough edges.",
        "struggling": "**The Country Club:** Too much socializing, not enough work.\n**Gossip:** Their need to be 'in the know' can spiral into drama.",
        "interventions": ["**Phase 1: Professionalism:** Define the line between 'friend' and 'colleague'.", "**Phase 2: Inclusive Leadership:** Challenge them to connect with the staff member they like least.", "**Phase 3: Task Focus:** Assign a project that requires solitude."],
        "questions": ["Are we having fun, or are we working?", "Who is on the outside of the circle?", "Are you avoiding the conflict to keep the peace?"],
        "advancement": "**Separation:** Prove they can lead without needing to be liked.\n**Confidentiality:** Prove they can keep secrets.\n**Productivity:** Prove they can drive results, not just vibes.",
        "phase_1_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Relational Buffer", "Move 2: The Vision Connect", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    # 3. FACILITATOR COMBINATIONS
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "synergy": "Methodical Progress. They don't sprint; they march with purpose and precision. They get the team to the finish line by ensuring everyone knows their role.",
        "support": "**Decision Speed:** Push them to decide even when they don't have 100% consensus.\n**Validation:** Praise the quiet work of organization.",
        "thriving": "**Consistent Wins:** They hit the metrics every month without drama.\n**Efficient Meetings:** They run meetings where everyone feels heard.",
        "struggling": "**Analysis Paralysis:** They want to achieve the goal but want everyone to agree on how.\n**Frustration with Chaos:** They hate last-minute changes.",
        "interventions": ["**Phase 1: Speaking Up:** Call on them first in meetings.", "**Phase 2: Imperfect Action:** Assign a task with an impossible deadline.", "**Phase 3: Direct Delegation:** Challenge them to assign tasks without asking."],
        "questions": ["What is the 'good enough' decision right now?", "Are you waiting for everyone to agree?", "How can we move forward even if it's messy?"],
        "advancement": "**Speed:** Make faster decisions with less data.\n**Conflict:** Call out underperformance directly.\n**Vision:** Look beyond the checklist.",
        "phase_1_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Facilitator-Growth": {
        "title": "The Patient Gardener",
        "synergy": "Organic Development. They don't force growth; they create the conditions for it. They are incredibly patient with difficult staff or youth.",
        "support": "**Urgency:** You must provide the urgency, or they will let things grow forever.\n**Outcome Focus:** Remind them that growth must eventually result in performance.",
        "thriving": "**Turnaround Specialist:** They can take a failing staff member and slowly rehabilitate them.\n**Deep Listening:** They understand the nuance of the unit.",
        "struggling": "**Tolerance of Mediocrity:** They give people too many chances.\n**Slow to Launch:** They study the problem forever without fixing it.",
        "interventions": ["**Phase 1: Timelines:** Put a date on development goals.", "**Phase 2: Judgment:** Practice evaluating performance objectively.", "**Phase 3: Pruning:** They must terminate or discipline a staff member."],
        "questions": ["How long is too long to wait for improvement?", "Is this person actually growing, or are we just hoping?", "What is the cost to the team of keeping this person?"],
        "advancement": "**Decisiveness:** Act on the data, not just the hope.\n**Speed:** Move faster than feels comfortable.\n**Standards:** Hold the line on quality without apology.",
        "phase_1_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Facilitator-Purpose": {
        "title": "The Moral Compass",
        "synergy": "Principled Consensus. They are the quiet conscience of the team. They ensure that the team doesn't just get things done, but gets them done right.",
        "support": "**Validation of Values:** Regularly affirm their role as the ethical standard-bearer.\n**Decision Frameworks:** Give them a framework for making 'imperfect' decisions.",
        "thriving": "**Ethical Anchor:** They center the boat in the storm.\n**Unified Team:** They create a team culture where everyone feels respected.",
        "struggling": "**Moral Paralysis:** They refuse to make a decision because no option is perfectly ethical.\n**Passive Resistance:** Instead of arguing openly, they simply don't do the things they disagree with.",
        "interventions": ["**Phase 1: The '51% Decision':** Teach them that in leadership, you often have to move with only 51% certainty.", "**Phase 2: Voice Training:** Challenge them to speak their dissent in the meeting.", "**Phase 3: Operational Ethics:** Task them with creating a system that institutionalizes their values."],
        "questions": ["What moral tension are you holding right now?", "How can you speak up for your values effectively?", "Are you staying neutral when you should take a stand?"],
        "advancement": "**Decisiveness:** Make hard calls when necessary.\n**Public Speaking:** Get comfortable projecting their voice.\n**Pragmatism:** Understand business realities alongside ethical ones.",
        "phase_1_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Facilitator-Connection": {
        "title": "The Peacemaker",
        "synergy": "Harmonious Inclusion. They create a psychological safety net for the team. They lead by relationship, ensuring that staff feel loved, supported, and heard.",
        "support": "**Conflict Coaching:** Role-play hard conversations with them to build muscle memory.\n**Permission to Disappoint:** Explicitly tell them 'It is okay if they are mad at you.'",
        "thriving": "**High Retention:** People rarely leave their team because it feels good to work there.\n**Psychological Safety:** Staff admit mistakes freely.",
        "struggling": "**The Doormat:** They let staff walk all over them to avoid a fight.\n**Exhaustion:** They carry everyone's emotional baggage.",
        "interventions": ["**Phase 1: Direct Address:** Require them to have one direct, hard conversation per week.", "**Phase 2: Disappointing Others:** Challenge them to make a decision they know will be unpopular.", "**Phase 3: Self-Protection:** Teach them to set boundaries on their time and empathy."],
        "questions": ["What boundaries do you need to set?", "Are you listening too much and leading too little?", "Who is taking care of you?"],
        "advancement": "**Conflict:** Prove they can handle a fight without crumbling.\n**Separation:** Prove they can lead friends.\n**Results:** Prove they value outcomes as much as feelings.",
        "phase_1_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Advance Warning", "Move 2: The Process Map", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    # 4. TRACKER COMBINATIONS
    "Tracker-Achievement": {
        "title": "The Architect",
        "synergy": "Systematic Perfection. They build the systems that allow the team to succeed. They are the engineers of the unit.",
        "support": "**Clarity:** Be hyper-clear about expectations. Ambiguity is torture for them.\n**Time:** Give them time to do it right.",
        "thriving": "**Flawless Execution:** Their paperwork is perfect and their data is clean.\n**System Builder:** They create new trackers that save time.",
        "struggling": "**Rigidity:** They refuse to bend the rules even when it makes sense.\n**Micromanagement:** They hover to ensure it is done 'perfectly'.",
        "interventions": ["**Phase 1: Flexibility:** Challenge them to identify one rule that can be bent.", "**Phase 2: People over Process:** Require them to mentor a disorganized staff member.", "**Phase 3: Big Picture:** Ask them to explain why the system exists."],
        "questions": ["How can you measure effort, not just outcome?", "Are you valuing the data more than the person?", "Where is flexibility needed right now?"],
        "advancement": "**Flexibility:** Handle chaos without breaking.\n**Delegation:** Trust others to do the work.\n**Warmth:** Connect with people, not just papers.",
        "phase_1_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Scoreboard", "Move 4: The Sprint", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Tracker-Growth": {
        "title": "The Technical Expert",
        "synergy": "Knowledge Mastery. They are the walking encyclopedia of the agency. They know every rule, every regulation, and every loophole.",
        "support": "**Resources:** Give them access to information. Do not gatekeep data.\n**Challenge:** Give them a problem no one else can solve.",
        "thriving": "**Problem Solver:** They fix technical issues that stump everyone else.\n**Teacher:** They patiently explain complex systems.",
        "struggling": "**Arrogance:** They make others feel stupid for not knowing the rules.\n**Over-Complication:** They design systems that are too complex.",
        "interventions": ["**Phase 1: Simplification:** Challenge them to explain a complex idea simply.", "**Phase 2: Emotional Intelligence:** Require them to mentor based on potential, not knowledge.", "**Phase 3: Strategic Vision:** Ask them to solve a problem with no 'right' answer."],
        "questions": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "Are you correcting or coaching?"],
        "advancement": "**Communication:** Speak simply and clearly.\n**Empathy:** Care about people who aren't experts.\n**Strategy:** Think about the 'why', not just the 'how'.",
        "phase_1_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Stretch", "Move 4: The Debrief", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Tracker-Purpose": {
        "title": "The Guardian",
        "synergy": "Protective Compliance. They believe that following the rules is the highest form of caring. They protect the mission by ensuring the agency never gets in trouble.",
        "support": "**Explanation:** Explain the 'why' behind every change in policy.\n**Validation:** Validate their fears and concerns.",
        "thriving": "**Safety Net:** They catch the errors that would cause a lawsuit.\n**Moral Consistency:** They ensure we do what we say we do.",
        "struggling": "**Bureaucracy:** They use rules to block necessary action.\n**Fear-Mongering:** They constantly predict disaster.",
        "interventions": ["**Phase 1: Risk Assessment:** Ask them to rate risk 1-10.", "**Phase 2: The 'Why' of Flexibility:** Show them a case where breaking a rule saved a kid.", "**Phase 3: Solution Focus:** Don't let them bring a problem without a solution."],
        "questions": ["How can you protect the mission without being rigid?", "Are you using rules to manage your anxiety?", "Is this rule serving the child right now?"],
        "advancement": "**Risk Tolerance:** Take a calculated risk.\n**Flexibility:** Adapt to change without panic.\n**Vision:** See the forest, not just the trees.",
        "phase_1_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Impact Story", "Move 4: The Why", "Move 5: The Delegation", "Move 6: The Systems Think"]
    },
    "Tracker-Connection": {
        "title": "The Reliable Rock",
        "synergy": "Servant Consistency. They show their love for the team by doing the work perfectly. They are the backbone of the unit.",
        "support": "**Notice the Details:** Notice when they refill the copier or clean the breakroom.\n**Change Management:** Hold their hand through change.",
        "thriving": "**Steady Presence:** They are always there, always on time.\n**Helper:** They use their skills to help others succeed.",
        "struggling": "**Overwhelmed:** They say 'yes' to everything and drown in details.\n**Passive Aggressive:** If they feel unappreciated, they withdraw.",
        "interventions": ["**Phase 1: Saying No:** Practice saying 'no' to a request.", "**Phase 2: Vocalizing Needs:** Ask them what they need in every meeting.", "**Phase 3: Leading Change:** Ask them to help a new person adapt."],
        "questions": ["How can you show care in a way they understand?", "Are you doing too much for others?", "Do they know you care?"],
        "advancement": "**Voice:** Speak up in a meeting.\n**Boundaries:** Stop over-functioning.\n**Flexibility:** Handle a new way of doing things.",
        "phase_1_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Safety Net", "Move 6: The Binary Feedback"],
        "phase_2_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Scenario Drill", "Move 6: The Pattern Spot"],
        "phase_3_moves": ["Move 1: The Data Dive", "Move 2: The Risk Assessment", "Move 3: The Peer Mentor", "Move 4: The Team Check", "Move 5: The Delegation", "Move 6: The Systems Think"]
    }
}

# --- NEW: HUD PROFILES (SECTION 6) ---
HUD_PROFILES = {
    "Director-Achievement": {
        "stress_sig": "**The 'Steamroller' Mode.**\nThey stop asking questions and start issuing commands. They will physically take over tasks from staff to 'just get it done.' They become visibly irritated by pauses or processing time.",
        "root_cause": "**Fear of Failure (Inefficiency).**\nTo them, speed equals competence. When the team slows down, they feel the goal slipping away, triggering an anxiety response that looks like aggression.",
        "prescription": [
            "**Remove a Barrier:** Identify one administrative hurdle blocking them and kill it immediately. This proves you are an ally to their speed.",
            "**The 'Short Win':** Give them a task they can complete and close in 24 hours to restore their sense of agency.",
            "**Direct Communication:** Do not 'sandwich' feedback. Look them in the eye and say, 'You are moving too fast. Slow down.' They respect the directness."
        ],
        "why_rx": "This restores their sense of control. By removing a barrier, you validate their need for speed. By giving direct feedback, you speak their language of efficiency."
    },
    "Director-Growth": {
        "stress_sig": "**The 'Intellectual Bully' Mode.**\nThey become hyper-critical of others' ideas. They may roll their eyes or sigh when staff don't understand concepts quickly. They withdraw from 'low-level' tasks.",
        "root_cause": "**Fear of Stagnation.**\nThey need to feel like they are advancing. When stuck in routine or surrounded by 'slow' learners, they feel trapped, triggering disdain.",
        "prescription": [
            "**The 'Brain Candy':** Assign them a complex, unsolved problem (e.g., 'Figure out why the 3rd shift schedule keeps breaking').",
            "**Autonomy Check:** Ask 'Where do you feel micromanaged?' and back off in that area.",
            "**Future Focus:** Spend 5 minutes talking about their career path, not just the current crisis."
        ],
        "why_rx": "This feeds their need for competence. Giving them a hard problem validates their intelligence. Talking about the future relieves the panic of being 'stuck' in the present."
    },
    "Director-Purpose": {
        "stress_sig": "**The 'Righteous Crusader' Mode.**\nThey become moralistic and judgmental. They frame every disagreement as 'You don't care about the kids.' They may violate policy to 'do the right thing.'",
        "root_cause": "**Fear of Betrayal (of the Mission).**\nThey view efficiency and rules as secondary to the mission. When the system blocks the mission, they view the system as the enemy.",
        "prescription": [
            "**Validate the Anger:** Say, 'You are right, it is unfair that we can't do X.' Align with their heart before correcting their method.",
            "**Connect Rule to Mission:** Explain how the policy actually *protects* the child long-term.",
            "**Give a Mission Win:** Share a specific story of how their leadership helped a youth recently."
        ],
        "why_rx": "This restores their trust in *you*. By validating their anger, you prove you aren't 'one of the bad guys.' By connecting the rule to the mission, you make compliance an act of advocacy."
    },
    "Director-Connection": {
        "stress_sig": "**The 'Mama Bear' Mode.**\nThey become fiercely protective of their team, attacking outsiders (including you) who critique them. They hide their team's mistakes to 'keep them safe.'",
        "root_cause": "**Fear of Harm to the Tribe.**\nThey see themselves as the shield. Stress makes them tighten the perimeter. They view accountability as an attack.",
        "prescription": [
            "**Reassure Safety:** Explicitly state, 'I am not here to fire anyone. I want to help them.'",
            "**Support the Leader:** Ask 'How are YOU doing?' before asking about the team. They rarely get asked.",
            "**Unified Front:** Show them that you are on their side against the chaos, not against them."
        ],
        "why_rx": "This lowers their defenses. When they know the team is safe, they can stop fighting you. Asking about *them* breaks their martyr complex."
    },
    "Encourager-Achievement": {
        "stress_sig": "**The 'Over-Promiser' Mode.**\nThey say 'yes' to everything to please everyone, become manic/scattered, and then crash when they drop balls. They hide failures with toxic positivity.",
        "root_cause": "**Fear of Disappointing Others.**\nThey equate 'winning' with 'making everyone happy.' They can't prioritize because every 'no' feels like a failure.",
        "prescription": [
            "**The 'No' Permission:** Explicitly take things off their plate. 'You are not allowed to do X this week.'",
            "**Visual Scoreboard:** Show them they are winning in specific areas so they stop trying to win everywhere.",
            "**Celebrate Limits:** Praise them when they set a boundary."
        ],
        "why_rx": "This relieves their guilt. When *you* say 'no' for them, they don't feel like they are letting people down. A scoreboard narrows their focus to what actually matters."
    },
    "Encourager-Growth": {
        "stress_sig": "**The 'Shiny Object' Mode.**\nThey start 10 new initiatives and finish none. They become bored with routine and detach from daily grind tasks. They avoid deep work.",
        "root_cause": "**Fear of Boredom.**\nThey run on dopamine and novelty. When the work gets hard or boring, they seek a new 'fun' idea to escape.",
        "prescription": [
            "**One Thing Rule:** 'You cannot start project B until project A is 100% finished.'",
            "**Gamify the Boring:** Turn routine tasks into a challenge or game.",
            "**Mentorship:** Have them teach a skill to a new hire. The social aspect of teaching makes the boring content fun again."
        ],
        "why_rx": "This creates guardrails for their energy. The 'One Thing Rule' forces completion. Mentorship turns a solitary task (doing) into a social task (teaching), which re-engages them."
    },
    "Encourager-Purpose": {
        "stress_sig": "**The 'Emotional Flood' Mode.**\nThey take client trauma home. They cry easily or become irrationally angry at 'the system.' They burn out from compassion fatigue.",
        "root_cause": "**Fear of Helplessness.**\nThey feel the pain of the world and feel powerless to stop it. This leads to overwhelming despair.",
        "prescription": [
            "**Mandatory Decompression:** Order them to take a break/leave early after a crisis.",
            "**The 'Good Enough' Speech:** Remind them that their presence is the intervention, not the cure.",
            "**Success Stories:** Force them to list 3 things that went *right* today to rebalance their perspective."
        ],
        "why_rx": "This interrupts the spiral. Mandatory breaks prevent them from martyring themselves. Success stories force their brain to scan for hope, counteracting the despair."
    },
    "Encourager-Connection": {
        "stress_sig": "**The 'Gossip' Mode.**\nThey vent inappropriately to peers instead of managing up. They form cliques. They avoid conflict to the point of negligence.",
        "root_cause": "**Fear of Rejection.**\nStress makes them seek alliance and validation. They prioritize feeling 'in' over doing 'right.'",
        "prescription": [
            "**Structure the Venting:** Give them 5 minutes to vent to *you* so they don't do it to the team.",
            "**Social Time:** Schedule a team lunch or coffee. Feed the need for connection healthily.",
            "**Direct Reassurance:** Tell them, 'I value you,' so they don't have to fish for it."
        ],
        "why_rx": "This meets their need for connection in a healthy way. Venting to *you* creates safety without toxicity. Reassurance calms their fear of rejection."
    },
    "Facilitator-Achievement": {
        "stress_sig": "**The 'Analysis Paralysis' Mode.**\nThey stall endlessly, asking for more data or 'one more meeting' to ensure the decision is perfect. They refuse to commit.",
        "root_cause": "**Fear of Being Wrong.**\nThey want to achieve the goal (Achievement) but want everyone to agree (Facilitator). The tension freezes them.",
        "prescription": [
            "**The 'Good Enough' Call:** Tell them, 'We are going with Option B. I am making the call.' Absolve them of the risk.",
            "**Deadlines:** Set tight, artificial deadlines to force action.",
            "**Focus on Progress:** Praise the *step* taken, not just the final result."
        ],
        "why_rx": "This removes the risk. By taking the decision out of their hands, you free them to execute. Deadlines prevent infinite processing."
    },
    "Facilitator-Growth": {
        "stress_sig": "**The 'Academic' Mode.**\nThey retreat into theory. They want to discuss the 'philosophy of care' while the unit is in chaos. They avoid the messy reality of the floor.",
        "root_cause": "**Fear of Incompetence.**\nThey feel overwhelmed by the chaos, so they retreat to the intellectual world where they feel safe and competent.",
        "prescription": [
            "**Concrete Tasks:** Give them a physical task (e.g., 'Organize the supply closet') to get them out of their head.",
            "**Time-Boxed Discussion:** 'We have 5 minutes to discuss theory, then we act.'",
            "**Validate Wisdom:** Ask for their insight, then ask them to apply it immediately."
        ],
        "why_rx": "This grounds them. Physical tasks reduce anxiety. Time-boxing honors their intellect but forces it into action."
    },
    "Facilitator-Purpose": {
        "stress_sig": "**The 'Moral Gridlock' Mode.**\nThey refuse to choose between two bad options (e.g., calling police vs. unsafe unit). They freeze because neither option feels 'right.'",
        "root_cause": "**Fear of Compromising Values.**\nThey see the gray area as a moral failing. They want a pure solution that doesn't exist.",
        "prescription": [
            "**The 'Least Bad' Frame:** Reframe the decision: 'Option A is the least harmful path. Taking it is the moral choice.'",
            "**Shared Burden:** 'We are making this decision together. You are not alone in this.'",
            "**Focus on Intent:** Remind them that their heart is in the right place."
        ],
        "why_rx": "This reframes the moral dilemma. It allows them to act without feeling like they have sold out. Sharing the burden reduces the moral weight on their shoulders."
    },
    "Facilitator-Connection": {
        "stress_sig": "**The 'Hiding' Mode.**\nThey physically disappear (office door closed, busy work) to avoid the tension on the floor. They refuse to give bad news.",
        "root_cause": "**Fear of Conflict.**\nStress makes them terrified of upsetting anyone. They withdraw to protect themselves from negative emotion.",
        "prescription": [
            "**Joint Leadership:** 'Let's go talk to the team together.' Don't make them do it alone.",
            "**Scripting:** Write down exactly what they need to say so they don't have to improvise.",
            "**Safe Space:** Ask 'What are you afraid will happen if you speak up?'"
        ],
        "why_rx": "This provides safety in numbers. They don't have to face the conflict alone. Scripting removes the anxiety of 'saying the wrong thing.'"
    },
    "Tracker-Achievement": {
        "stress_sig": "**The 'Micro-Manager' Mode.**\nThey obsess over formatting, minor rules, and tiny details. They redo others' work because 'it wasn't right.'",
        "root_cause": "**Fear of Loss of Control.**\nWhen stressed, they try to control the only thing they can: the details. It gives them a false sense of safety.",
        "prescription": [
            "**Define 'Done':** Explicitly state what 'good enough' looks like. Stop them from polishing.",
            "**Assign 'Big' Goals:** Redirect their drive to a larger project so they stop nitpicking.",
            "**Mandatory Handoff:** Force them to delegate a task and *not* check it."
        ],
        "why_rx": "This recalibrates their standard. 'Defining Done' stops the infinite loop. Big goals give them a healthier outlet for their Achievement drive."
    },
    "Tracker-Growth": {
        "stress_sig": "**The 'Superiority' Mode.**\nThey hoard information and act condescending to those who don't know the rules. 'I guess I have to do everything.'",
        "root_cause": "**Fear of Dependency.**\nThey feel unsafe relying on 'incompetent' people. They protect themselves by proving they are the smartest in the room.",
        "prescription": [
            "**The 'Teacher' Role:** Ask them to train the team. Turn their hoarding into sharing.",
            "**Acknowledge Expertise:** Publicly validate their knowledge so they don't feel the need to prove it.",
            "**Challenge with Ambiguity:** Give them a problem that has no rulebook answer to force flexibility."
        ],
        "why_rx": "This turns a negative (hoarding) into a positive (teaching). Validating their expertise lowers their insecurity, making them nicer to work with."
    },
    "Tracker-Purpose": {
        "stress_sig": "**The 'Policy Police' Mode.**\nThey weaponize the rules to stop work. 'We can't do that, it's against regulation 4.2.' They block progress.",
        "root_cause": "**Fear of Catastrophe.**\nThey believe that one slip-up will destroy the agency/mission. Rules are their safety blanket against disaster.",
        "prescription": [
            "**Risk Assessment:** Ask 'What is the actual likelihood of that bad thing happening?' Help them calibrate.",
            "**Safe Exceptions:** 'I am authorizing this exception. I will sign off on it.' Taking the liability removes their fear.",
            "**Connect Rule to Why:** Explain the spirit of the law, not just the letter."
        ],
        "why_rx": "This restores perspective. Calibrating risk stops the catastrophic thinking. Taking liability allows them to relax their guard."
    },
    "Tracker-Connection": {
        "stress_sig": "**The 'Silent Martyr' Mode.**\nThey do all the grunt work silently, then seethe with resentment when no one notices. Passive-aggressive sighs.",
        "root_cause": "**Fear of Being Unappreciated.**\nThey want to be helpful but feel invisible. They work harder to get noticed, then resent the work.",
        "prescription": [
            "**Public Visibility:** Praise their specific work in front of the team. 'Thank you for organizing that.'",
            "**Role Clarity:** Tell them exactly what is *not* their job so they stop over-functioning.",
            "**Ask for Voice:** 'You've been quiet. What are you seeing that we are missing?'"
        ],
        "why_rx": "This heals the resentment. Visibility proves they are valued. Role clarity gives them permission to stop suffering."
    }
}

# --- PLACEHOLDERS FOR MISSING DATA ---
SUPERVISOR_CLASH_MATRIX = {}
CAREER_PATHWAYS = {}
TEAM_CULTURE_GUIDE = {}
MISSING_VOICE_GUIDE = {}
MOTIVATION_GAP_GUIDE = {}
PEDAGOGY_GUIDE = {
    1: "**The Teaching Method: Direct Instruction.**\nAt this stage, they don't know what they don't know. Stop asking 'What do you think?' and start showing 'This is how we do it.' Use the 'I do, We do, You do' model.",
    2: "**The Teaching Method: Guided Scaffolding.**\nThey have the knowledge but lack the muscle memory. Your role is the 'Safety Net.' Let them try, fail safely, and debrief immediately. Shift from instruction to feedback.",
    3: "**The Teaching Method: Socratic Empowerment.**\nThey know the 'how'; now they need the 'why' and the 'what if.' Stop giving answers. Ask 'What would you do?' and 'What are the risks?' to build their executive functioning."
}

# --- HELPER FUNCTIONS FOR VISUALS ---

def create_comm_quadrant_chart(comm_style):
    """Creates a 2D scatter plot placing the style in a Task/People vs Fast/Slow quadrant."""
    
    coords = {
        "Director": {"x": -0.5, "y": 0.5, "color": BRAND_COLORS['red']},
        "Encourager": {"x": 0.5, "y": 0.5, "color": BRAND_COLORS['yellow']},
        "Tracker": {"x": -0.5, "y": -0.5, "color": BRAND_COLORS['blue']},
        "Facilitator": {"x": 0.5, "y": -0.5, "color": BRAND_COLORS['green']}
    }
    
    data = coords.get(comm_style, {"x":0, "y":0, "color": "gray"})
    
    fig = go.Figure()
    
    # Add quadrants background
    fig.add_shape(type="rect", x0=-1, y0=0, x1=0, y1=1, fillcolor="rgba(234, 67, 53, 0.1)", line_width=0, layer="below") # Director (Red)
    fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=1, fillcolor="rgba(251, 188, 4, 0.1)", line_width=0, layer="below") # Encourager (Yellow)
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=0, y1=0, fillcolor="rgba(26, 115, 232, 0.1)", line_width=0, layer="below") # Tracker (Blue)
    fig.add_shape(type="rect", x0=0, y0=-1, x1=1, y1=0, fillcolor="rgba(52, 168, 83, 0.1)", line_width=0, layer="below") # Facilitator (Green)

    # Add center lines
    fig.add_vline(x=0, line_width=1, line_color="gray")
    fig.add_hline(y=0, line_width=1, line_color="gray")

    # Add the Point
    fig.add_trace(go.Scatter(
        x=[data['x']], y=[data['y']],
        mode='markers+text',
        marker=dict(size=25, color=data['color'], line=dict(width=2, color='white')),
        text=[comm_style], textposition="bottom center",
        textfont=dict(size=14, family="Arial", weight="bold")
    ))

    # Annotations (Axis Labels)
    fig.add_annotation(x=0, y=1.1, text="FAST / ACTION", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=0, y=-1.1, text="SLOW / PROCESS", showarrow=False, font=dict(size=10, color="gray"))
    fig.add_annotation(x=-1.1, y=0, text="TASK", showarrow=False, textangle=-90, font=dict(size=10, color="gray"))
    fig.add_annotation(x=1.1, y=0, text="PEOPLE", showarrow=False, textangle=90, font=dict(size=10, color="gray"))

    fig.update_layout(
        xaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.2, 1.2], showgrid=False, zeroline=False, visible=False),
        margin=dict(l=20, r=20, t=20, b=20),
        height=250,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_motiv_gauge(motiv_style):
    """Creates a simple gauge chart indicating the primary 'fuel' source."""
    
    color_map = {
        "Achievement": BRAND_COLORS['blue'],
        "Growth": BRAND_COLORS['green'],
        "Purpose": BRAND_COLORS['red'],
        "Connection": BRAND_COLORS['yellow']
    }
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 90,
        title = {'text': f"{motiv_style} Drive"},
        gauge = {
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': color_map.get(motiv_style, "gray")},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 100], 'color': "rgba(232, 240, 254, 0.5)"}],
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
    return fig

def create_integrated_compass(comm, motiv):
    # Coordinates: X = People(pos)/Task(neg), Y = Change(pos)/Stability(neg)
    comm_map = {
        "Director": {"x": -6, "y": 6}, "Encourager": {"x": 6, "y": 6},
        "Facilitator": {"x": 6, "y": -6}, "Tracker": {"x": -6, "y": -6}
    }
    mot_map = {
        "Achievement": {"x": -3, "y": 4}, "Growth": {"x": 2, "y": 7},
        "Purpose": {"x": 5, "y": 3}, "Connection": {"x": 7, "y": -2}
    }
    
    c_pt = comm_map.get(comm, {"x":0,"y":0})
    m_pt = mot_map.get(motiv, {"x":0,"y":0})
    
    # Average the points to find the "Integrated Center"
    final_x = (c_pt["x"] + m_pt["x"]) / 2
    final_y = (c_pt["y"] + m_pt["y"]) / 2
    
    fig = go.Figure()
    
    # Background Quadrants with semantic colors
    fig.add_shape(type="rect", x0=-10, y0=0, x1=0, y1=10, fillcolor="#fce8e6", line_width=0, layer="below") # Red tint (Driver)
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, fillcolor="#fef7e0", line_width=0, layer="below") # Yellow tint (Influencer)
    fig.add_shape(type="rect", x0=-10, y0=-10, x1=0, y1=0, fillcolor="#e8f0fe", line_width=0, layer="below") # Blue tint (Analyzer)
    fig.add_shape(type="rect", x0=0, y0=-10, x1=10, y1=0, fillcolor="#e6f4ea", line_width=0, layer="below") # Green tint (Stabilizer)

    # Axes Lines
    fig.add_hline(y=0, line_color="gray", line_width=1)
    fig.add_vline(x=0, line_color="gray", line_width=1)
    
    # The Point
    fig.add_trace(go.Scatter(
        x=[final_x], y=[final_y],
        mode='markers+text',
        marker=dict(size=25, color='#1a73e8', line=dict(width=3, color='white')),
        text=["YOU"], textposition="middle center",
        textfont=dict(color='white', size=10, weight='bold')
    ))
    
    # Labels
    fig.add_annotation(x=0, y=11, text="CHANGE / SPEED", showarrow=False, font=dict(size=10, color="gray", weight="bold"))
    fig.add_annotation(x=0, y=-11, text="STABILITY / PROCESS", showarrow=False, font=dict(size=10, color="gray", weight="bold"))
    fig.add_annotation(x=-11, y=0, text="TASK", showarrow=False, textangle=-90, font=dict(size=10, color="gray", weight="bold"))
    fig.add_annotation(x=11, y=0, text="PEOPLE", showarrow=False, textangle=90, font=dict(size=10, color="gray", weight="bold"))

    fig.update_layout(
        xaxis=dict(range=[-12, 12], visible=False, fixedrange=True),
        yaxis=dict(range=[-12, 12], visible=False, fixedrange=True),
        margin=dict(l=10, r=10, t=20, b=20),
        height=250,
        plot_bgcolor='white',
        showlegend=False
    )
    return fig

# --- LOGIC HELPER FOR SECTION 5 EXPANSION ---
def get_leadership_mechanics(comm, motiv):
    """
    Returns specific 'Training' insights for Section 5 based on profile intersection.
    Contains detailed, actionable coaching data.
    """
    mech = {}
    
    # 1. Decision Style (Communication Based)
    if comm == "Director": 
        mech['decision'] = "**Decisive & Direct (The Accelerator).** You prefer the '80% solution now' over the '100% solution later.' You view hesitation as weakness. **Training Tip:** Force yourself to ask 'What am I missing?' before pulling the trigger to prevent blind spots."
    elif comm == "Encourager": 
        mech['decision'] = "**Intuitive & Collaborative (The Processor).** You process decisions verbally and socially. You need to talk it out to know what you think. **Training Tip:** Write down the pros/cons *before* discussing them to separate objective fact from emotional enthusiasm."
    elif comm == "Facilitator": 
        mech['decision'] = "**Methodical & Inclusive (The Stabilizer).** You seek consensus and process. You want everyone on the bus before driving. **Training Tip:** Set a strict deadline for the decision (e.g., 'By 3 PM') to prevent analysis paralysis. A good decision today is better than a perfect one next week."
    elif comm == "Tracker": 
        mech['decision'] = "**Analytical & Cautious (The Auditor).** You rely on data, precedent, and policy. You fear being wrong more than being slow. **Training Tip:** Identify 'one-way door' decisions (irreversible) vs 'two-way door' decisions (reversible). Practice moving faster on the reversible ones."
    else: 
        mech['decision'] = "Balanced decision style."

    # 2. Influence Tactic (Communication Based)
    if comm == "Director": 
        mech['influence'] = "**Authority & Logic.** You influence by stating the destination clearly and moving with confidence. **Training Tip:** Explain the 'Why' behind the 'What.' Your team needs the backstory to buy in; otherwise, your direction feels like a dictatorship."
    elif comm == "Encourager": 
        mech['influence'] = "**Charisma & Vision.** You influence by selling the emotional upside and building relationships. **Training Tip:** Back up your vision with specific data points. Skeptics need proof, not just passion, to follow you."
    elif comm == "Facilitator": 
        mech['influence'] = "**Empowerment & Listening.** You influence by making others feel heard and valued. **Training Tip:** Don't confuse 'agreement' with 'alignment.' Sometimes you must direct, not just suggest. Practice saying, 'I have heard you, and this is the decision.'"
    elif comm == "Tracker": 
        mech['influence'] = "**Expertise & Accuracy.** You influence by citing the rules, the history, and the facts. **Training Tip:** Connect the rule to the human impact (safety/care). People follow rules better when they understand how the rule protects the child."
    else: 
        mech['influence'] = "Diplomatic influence."

    # 3. Trust Builder (Motivation Based)
    if motiv == "Achievement": 
        mech['trust'] = "**Competence.** People trust you because you get results and solve problems. **Training Tip:** Admit when you are struggling. Vulnerability builds trust where competence only builds respect. Let them see you sweat occasionally."
    elif motiv == "Growth": 
        mech['trust'] = "**Evolution.** People trust you because you help them improve and see their potential. **Training Tip:** Ensure your feedback ratio is 3:1 (positive to constructive). If you only coach them to be better, they may feel they are never 'good enough' for you."
    elif motiv == "Purpose": 
        mech['trust'] = "**Integrity.** People trust you because you stand for values and the mission. **Training Tip:** Be careful not to judge those who are more pragmatic. Acknowledge the messy reality of operations without compromising your core ethics."
    elif motiv == "Connection": 
        mech['trust'] = "**Safety.** People trust you because you have their back and care about them as humans. **Training Tip:** Demonstrate that you can handle bad news without crumbling. Your stability is their safety. If you panic, they panic."
    else: 
        mech['trust'] = "Consistent behavior."
    
    return mech

# 5c. INTEGRATED PROFILES (Expanded & 10 Coaching Questions Logic)
def generate_profile_content(comm, motiv):
    combo_key = f"{comm}-{motiv}"
    c_data = COMM_PROFILES.get(comm, {})
    m_data = MOTIV_PROFILES.get(motiv, {})
    i_data = INTEGRATED_PROFILES.get(combo_key, {})

    avoid_map = {
        "Director": [
            "**Wasting time with small talk:** This signals disrespect for their time.",
            "**Vague answers:** They interpret ambiguity as incompetence.",
            "**Micromanaging:** This signals you don't trust their capability."
        ],
        "Encourager": [
            "**Public criticism:** This feels like a rejection of their identity.",
            "**Ignoring feelings:** They view emotion as data; ignoring it misses the point.",
            "**Transactional talk:** Skipping the 'hello' makes them feel used."
        ],
        "Facilitator": [
            "**Pushing for instant decisions:** This feels reckless and unsafe to them.",
            "**Aggressive confrontation:** This shuts them down instantly.",
            "**Dismissing group concerns:** This violates their core value of fairness."
        ],
        "Tracker": [
            "**Vague instructions:** This triggers anxiety about 'doing it wrong'.",
            "**Asking to break policy:** This feels unethical and unsafe to them.",
            "**Chaos/Disorganization:** They cannot respect a leader who is messy."
        ]
    }

    return {
        "s1_b": c_data.get('bullets'),
        "s2_b": c_data.get('supervising_bullets'),
        "s3_b": m_data.get('bullets'),
        "s4_b": m_data.get('strategies_bullets'),
        "s5_title": i_data.get('title', f"The {comm}-{motiv}"),
        "s5_synergy": i_data.get('synergy', 'Balanced Approach'),
        "s6": i_data.get('support', ''),
        "s7": i_data.get('thriving', ''),
        "s8": i_data.get('struggling', ''),
        "s9_b": i_data.get('interventions', []),
        "s10_b": m_data.get('celebrate_bullets'),
        "s10_deep": m_data.get('celebrate_deep_dive', ''),
        "coaching": i_data.get('questions', []),
        "advancement": i_data.get('advancement', ''),
        "cheat_do": c_data.get('supervising_bullets'),
        "cheat_avoid": avoid_map.get(comm, []),
        "cheat_fuel": m_data.get('strategies_bullets'),
        # Pass the phase moves dict
        "phase_1_moves": i_data.get('phase_1_moves', []),
        "phase_2_moves": i_data.get('phase_2_moves', []),
        "phase_3_moves": i_data.get('phase_3_moves', [])
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def send_pdf_via_email(to_email, subject, body, pdf_bytes, filename="Guide.pdf"):
    try:
        sender_email = st.secrets.get("EMAIL_USER")
        sender_password = st.secrets.get("EMAIL_PASSWORD")
        if not sender_email or not sender_password: return False, "Email credentials not configured."
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        part = MIMEBase('application', "octet-stream")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email Error: {str(e)}"

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (26, 115, 232); green = (52, 168, 83); red = (234, 67, 53); black = (0, 0, 0)
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(5)
    
    data = generate_profile_content(p_comm, p_mot)

    # --- CHEAT SHEET SECTION ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Rapid Interaction Cheat Sheet", ln=True, fill=True, align='C')
    pdf.ln(2)

    def print_cheat_column(title, items, color_rgb):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*color_rgb)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        for item in items:
            clean_item = item.replace("**", "")
            pdf.multi_cell(0, 5, clean_text(f"- {clean_item}"))
        pdf.ln(2)

    print_cheat_column("DO THIS (Communication):", data['cheat_do'], green)
    print_cheat_column("AVOID THIS (Triggers):", data['cheat_avoid'], red)
    print_cheat_column("FUEL (Motivation):", data['cheat_fuel'], blue)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Horizontal line
    pdf.ln(5)

    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True); pdf.ln(2)
        pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
        
        if body:
            clean_body = body.replace("**", "").replace("* ", "- ")
            pdf.multi_cell(0, 5, clean_text(clean_body))
        
        if bullets:
            pdf.ln(1)
            for b in bullets:
                pdf.cell(5, 5, "-", 0, 0)
                clean_b = b.replace("**", "") 
                pdf.multi_cell(0, 5, clean_text(clean_b))
        pdf.ln(4)

    # Sections 1-10
    add_section(f"1. Communication Profile: {p_comm}", None, data['s1_b']) 
    add_section("2. Supervising Their Communication", None, data['s2_b'])
    add_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    add_section("4. Motivating This Staff Member", None, data['s4_b'])
    add_section("5. Integrated Leadership Profile", f"{data['s5_title']}\n\n{data['s5_synergy']}") 
    add_section("6. How You Can Best Support Them", data['s6'])
    add_section("7. What They Look Like When Thriving", data['s7'])
    add_section("8. What They Look Like When Struggling", data['s8'])
    add_section("9. Individual Professional Development Plan (IPDP)", None, data['s9_b'])
    add_section("10. What You Should Celebrate", None, data['s10_b'])

    # 11. Coaching Questions
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "11. Coaching Questions", ln=True, fill=True); pdf.ln(2)
    pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
    for i, q in enumerate(data['coaching']):
        pdf.multi_cell(0, 5, clean_text(f"{i+1}. {q}"))
    pdf.ln(4)

    # 12. Advancement
    add_section("12. Helping Them Prepare for Advancement", data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---")
    st.markdown(f"### 📘 Supervisory Guide: {name}")
    st.caption(f"Role: {role} | Profile: {p_comm} ({s_comm}) • {p_mot} ({s_mot})")
    
    with st.expander("⚡ Rapid Interaction Cheat Sheet", expanded=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown("##### ✅ Do This")
            for b in data['cheat_do']: st.success(b.replace("**", ""))
        with cc2:
            st.markdown("##### ⛔ Avoid This")
            for avoid in data['cheat_avoid']: st.error(avoid.replace("**", ""))
        with cc3:
            st.markdown("##### 🔋 Fuel")
            for b in data['cheat_fuel']: st.info(b.replace("**", ""))

    st.divider()
    
    def show_list(bullets):
        if bullets:
            for b in bullets: st.markdown(f"- {b}")

    # --- SECTION 1 & 2: COMMUNICATION ---
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"1. Communication: {p_comm}")
        show_list(data['s1_b'])
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("2. Supervising Strategies")
        show_list(data['s2_b'])
    
    with c2:
        with st.container(border=True):
            st.markdown(f"**Style Map: {p_comm}**")
            fig = create_comm_quadrant_chart(p_comm)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # --- SECTION 3 & 4: MOTIVATION ---
    c3, c4 = st.columns([1, 2])
    with c3:
        with st.container(border=True):
            st.markdown(f"**Primary Driver**")
            fig_g = create_motiv_gauge(p_mot)
            st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})
    with c4:
        st.subheader(f"3. Motivation: {p_mot}")
        show_list(data['s3_b'])
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("4. How to Motivate")
        show_list(data['s4_b'])

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 5: INTEGRATED PROFILE CARD (EXPANDED) ---
    with st.container(border=True):
        st.markdown(f"<div style='text-align: center; margin-bottom: 10px;'><span style='background-color: #e8f0fe; color: #1a73e8; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;'>SECTION 5: INTEGRATION</span></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #202124; margin-top: 0;'>{data['s5_title']}</h2>", unsafe_allow_html=True)
        
        i1, i2 = st.columns([1.5, 1])
        
        with i1:
            st.markdown("#### 🔗 The Synergy")
            st.info(f"**{data['s5_synergy']}**")
            
            # NEW TRAINING CONTENT: Mechanics
            st.markdown("#### ⚙️ Leadership Mechanics")
            # Get expanded training data dynamically based on intersection
            mech = get_leadership_mechanics(p_comm, p_mot) 
            
            st.markdown(f"**1. Decision Style:** {mech['decision']}")
            st.markdown(f"**2. Influence Tactic:** {mech['influence']}")
            st.markdown(f"**3. Trust Builder:** {mech['trust']}")

        with i2:
            st.markdown(f"**🧭 Leadership Compass**")
            fig_compass = create_integrated_compass(p_comm, p_mot)
            st.plotly_chart(fig_compass, use_container_width=True, config={'displayModeBar': False})
            st.caption("The compass plots your bias: Task vs. People (X-Axis) and Change vs. Stability (Y-Axis).")
    
    # --- SECTION 6: THE SUPERVISOR'S HUD (REWORKED & EXPANDED) ---
    st.subheader("6. The Supervisor's HUD (Heads-Up Display)")
    st.caption("A dashboard for maintaining this staff member's engagement and preventing burnout. Check these indicators monthly.")

    # Get contextual data based on INTEGRATED profile
    hud_context = HUD_PROFILES.get(f"{p_comm}-{p_mot}", {
        "stress_sig": "Behavior change under pressure.", 
        "root_cause": "Misalignment of needs.", 
        "prescription": ["Check in regularly.", "Clarify expectations."]
    })

    # 1. Stress Signature
    with st.container(border=True):
        st.markdown("#### 🚨 Stress Signature (Early Warning System)")
        
        col_sig, col_rx = st.columns([1, 1])
        with col_sig:
            st.error(f"**The Signal (Watch for this):**\n{hud_context['stress_sig']}")
            st.markdown(f"**Root Cause Analysis:**\n{hud_context['root_cause']}")
            
        with col_rx:
            st.success(f"**The Prescription (Do This):**")
            # We use the generic Rx list but explain WHY it works for this specific combination below
            rx_list = hud_context.get('prescription', [])
            for r in rx_list:
                st.write(f"• {r}")
            
            # Add "Why this works" if available (it wasn't in original structure but requested context)
            if 'why_rx' in hud_context:
                st.info(f"**Why this works for them:**\n{hud_context['why_rx']}")

    # 2. Environment Audit
    env_data = {
        "Director": {"friction": "Red Tape & Inefficiency", "fix": "Give them a 'Fast Pass' on minor approvals where possible."},
        "Encourager": {"friction": "Isolation & Coldness", "fix": "Create 'water cooler' moments and team touchpoints."},
        "Facilitator": {"friction": "Rushed Conflict & Unfairness", "fix": "Ensure all voices are heard before closing a decision."},
        "Tracker": {"friction": "Chaos & Ambiguity", "fix": "Provide written agendas and clear protocols."}
    }
    
    fuel_data = {
        "Achievement": {"fuel": "Visual Progress", "fix": "Create a scoreboard or checklist they can mark 'Done'."},
        "Growth": {"fuel": "New Challenges", "fix": "Assign a problem they haven't solved before."},
        "Purpose": {"fuel": "Mission Connection", "fix": "Share a specific story of how they helped a youth."},
        "Connection": {"fuel": "Belonging", "fix": "Publicly acknowledge their value to the team."}
    }

    fric = env_data.get(p_comm, {})
    fuel = fuel_data.get(p_mot, {})

    with st.container(border=True):
        st.markdown("#### 🛠️ Environment Audit (Retention Check)")
        
        ac1, ac2 = st.columns(2)
        with ac1:
            st.metric("Top Friction (The Kryptonite)", fric.get('friction'))
            st.markdown(f"**How to remove it:**\n{fric.get('fix')}")
            st.caption("Why: Friction here causes them to check out mentally.")
        with ac2:
            st.metric("Top Fuel (The Superpower)", fuel.get('fuel'))
            st.markdown(f"**How to inject it:**\n{fuel.get('fix')}")
            st.caption("Why: This is what sustains them through hard shifts.")

    # 3. Crisis Protocol
    crisis_data = {
        "Director": {
            "script": "I am giving you the ball. Run with it. I will block for you.",
            "why": "Restores their sense of control and action (Agency). They panic when they feel helpless; this gives them power back."
        },
        "Encourager": {
            "script": "We are in this together. I have your back. Let's do this.",
            "why": "Restores their sense of safety and connection (Belonging). They panic when they feel alone; this proves they are not."
        },
        "Facilitator": {
            "script": "I need you to trust my call on this one. We will debrief later.",
            "why": "Relieves them of the pressure to find consensus in an emergency (Absolution). They panic about being 'unfair'; this takes the moral weight off them."
        },
        "Tracker": {
            "script": "Follow the protocol. I am responsible for the outcome.",
            "why": "Relieves them of the fear of liability or error (Protection). They panic about breaking rules; this shifts liability to you."
        }
    }
    
    c_dat = crisis_data.get(p_comm, {})

    with st.container(border=True):
        st.markdown("#### 🆘 Crisis Protocol (Break Glass in Emergency)")
        st.info(f"**Say exactly this:** \"{c_dat.get('script')}\"")
        st.markdown(f"**Why it works:** {c_dat.get('why')}")


    # --- SECTION 7 & 8: THRIVING VS STRUGGLING ---
    col_t, col_s = st.columns(2)
    with col_t:
        with st.container(border=True):
            st.subheader("✅ 7. When Thriving")
            st.write(data['s7'])
    with col_s:
        with st.container(border=True):
            st.subheader("⚠️ 8. When Struggling")
            st.write(data['s8'])

    st.divider()

    # --- SECTION 9: INDIVIDUAL PROFESSIONAL DEVELOPMENT PLAN (IPDP) - DYNAMIC ---
    st.subheader("9. Individual Professional Development Plan (IPDP)")
    st.caption("A development-first framework for coaching growth, alignment, and performance over time.")
    
    # Phase Selector
    phase_state_key = f"ipdp_phase__{name}".replace(" ", "_")
    if phase_state_key not in st.session_state: st.session_state[phase_state_key] = 1
    
    sel_num = st.radio("Select Phase:", [1, 2, 3], format_func=lambda x: f"Phase {x}", horizontal=True, key=phase_state_key)

    # Fetch Dynamic Moves for this specific phase from the Integrated Profile Data
    phase_moves_key = f"phase_{sel_num}_moves"
    my_moves = data.get(phase_moves_key, [])
    
    # If for some reason moves are missing, fallback to generic
    if not my_moves:
        my_moves = [
            "Move 1: Establish Routine", "Move 2: Clarify Standard",
            "Move 3: Validate Effort", "Move 4: Connect to Goal",
            "Move 5: Safe Failure", "Move 6: Feedback Loop"
        ]
    
    # Display Matrix
    st.markdown("#### 🧭 Coaching Matrix: 6 High-Impact Moves (Tailored)")
    
    colA, colB, colC = st.columns(3)
    
    # Move 1 & 2
    with colA:
        with st.container(border=True):
            # Split "Move X: Title" from body if present, otherwise just show text
            parts = my_moves[0].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 1"
            body = parts[1] if len(parts) > 1 else my_moves[0]
            st.markdown(f"**{title}**")
            st.caption(body)
            
            st.markdown("---")
            
            parts = my_moves[1].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 2"
            body = parts[1] if len(parts) > 1 else my_moves[1]
            st.markdown(f"**{title}**")
            st.caption(body)
            
    # Move 3 & 4
    with colB:
        with st.container(border=True):
            parts = my_moves[2].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 3"
            body = parts[1] if len(parts) > 1 else my_moves[2]
            st.markdown(f"**{title}**")
            st.caption(body)
            
            st.markdown("---")
            
            parts = my_moves[3].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 4"
            body = parts[1] if len(parts) > 1 else my_moves[3]
            st.markdown(f"**{title}**")
            st.caption(body)
            
    # Move 5 & 6
    with colC:
        with st.container(border=True):
            parts = my_moves[4].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 5"
            body = parts[1] if len(parts) > 1 else my_moves[4]
            st.markdown(f"**{title}**")
            st.caption(body)
            
            st.markdown("---")
            
            parts = my_moves[5].split(": ", 1)
            title = parts[0] if len(parts) > 1 else "Move 6"
            body = parts[1] if len(parts) > 1 else my_moves[5]
            st.markdown(f"**{title}**")
            st.caption(body)

    st.markdown("#### 🎓 Pedagogical Deep Dive")
    st.info(PEDAGOGY_GUIDE.get(sel_num, "Guide and support consistent growth."))
    
    # Original PDF Download Button (Logic preserved)
    pdf_bytes = _build_ipdp_summary_pdf(name, role, sel_num) # Reusing existing function for PDF
    st.download_button(f"🖨️ Download Phase {sel_num} Plan (PDF)", pdf_bytes, f"{name}_IPDP.pdf", "application/pdf", use_container_width=True)


    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 10: CELEBRATION (TROPHY CASE) ---
    st.subheader("10. What To Celebrate")
    
    # 1. Primary Bullets
    cel_cols = st.columns(3)
    if data['s10_b']:
        for i, item in enumerate(data['s10_b']):
            clean_item = item.replace("**", "")
            with cel_cols[i % 3]:
                st.markdown(f"🏆 **{clean_item}**")
    
    st.markdown("")
    
    # 2. Deep Dive Box
    with st.container(border=True):
        st.markdown(f"### 💬 How to Speak Their Language")
        st.markdown(data['s10_deep'])


    st.divider()

    # --- SECTION 11: COACHING QUESTIONS ---
    st.subheader("11. Coaching Questions")
    with st.container(border=True):
        if data['coaching']:
            for i, q in enumerate(data['coaching']):
                qc1, qc2 = st.columns([0.05, 0.95])
                with qc1: st.markdown(f"**{i+1}.**")
                with qc2: st.markdown(f"{q}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- SECTION 12: ADVANCEMENT (NEXT LEVEL) ---
    st.subheader("12. Preparing for Advancement")
    adv_text = data['advancement']
    if adv_text:
        adv_points = adv_text.split('\n\n')
        ac1, ac2, ac3 = st.columns(3)
        cols = [ac1, ac2, ac3]
        for i, point in enumerate(adv_points):
            if i < 3:
                with cols[i]:
                    if "**" in point:
                        parts = point.split("**")
                        title = parts[1] if len(parts) > 1 else "Focus Area"
                        body = parts[2] if len(parts) > 2 else point
                        st.metric(label=title, value="Readiness Check")
                        st.caption(body)
                    else:
                        st.info(point)

# --- 6. MAIN APP LOGIC ---
# Reset Helpers
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None; st.session_state.messages = []
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- HERO SECTION ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Elmcrest Leadership Intelligence</div>
    <div class="hero-subtitle">
        Your command center for staff development. Select a tool below to begin.
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION BUTTONS ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("📝 Supervisor's Guide\n\nCreate 12-point coaching manuals.", use_container_width=True): set_view("Supervisor's Guide")
with nav_col2:
    if st.button("🧬 Team DNA\n\nAnalyze unit culture & blindspots.", use_container_width=True): set_view("Team DNA")
with nav_col3:
    if st.button("⚖️ Conflict Mediator\n\nScripts for tough conversations.", use_container_width=True): set_view("Conflict Mediator")
with nav_col4:
    if st.button("🚀 Career Pathfinder\n\nPromotion readiness tests.", use_container_width=True): set_view("Career Pathfinder")
st.markdown("###")
if st.button("📈 Organization Pulse (See All Data)", use_container_width=True): set_view("Org Pulse")
st.markdown("---")

# --- VIEW CONTROLLER ---

# 1. Supervisor's Guide
if st.session_state.current_view == "Supervisor's Guide":
    st.subheader("📝 Supervisor's Guide")
    
    sub1, sub2, sub3 = st.tabs(["Database", "Manual Generator", "📥 Input Offline Data"])
    
    # --- DATABASE TAB ---
    with sub1:
        if not df.empty:
            filtered_staff_list = df.to_dict('records')
            options = {f"{s['name']} ({s['role']})": s for s in filtered_staff_list}
            staff_options_list = list(options.keys())
            
            current_selection = st.session_state.get("t1_staff_select")
            default_index = None
            if current_selection in staff_options_list:
                default_index = staff_options_list.index(current_selection)

            with st.container(border=True):
                sel = st.selectbox(
                    "Select Staff", 
                    staff_options_list, 
                    index=default_index, 
                    key="t1_staff_select",
                    placeholder="Choose a staff member..."
                )
                
                if sel:
                    d = options[sel]
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                    
                    if st.button("Generate Guide", type="primary", use_container_width=True):
                        st.session_state.generated_pdf = create_supervisor_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                        st.session_state.generated_filename = f"Guide_{d['name'].replace(' ', '_')}.pdf"
                        st.session_state.generated_name = d['name']
                        display_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])

            if "generated_pdf" in st.session_state and st.session_state.get("generated_name") == d['name']:
                st.divider()
                st.markdown("#### 📤 Actions")
                ac1, ac2 = st.columns([1, 2])
                
                with ac1:
                    st.download_button(
                        label="📥 Download PDF", 
                        data=st.session_state.generated_pdf, 
                        file_name=st.session_state.generated_filename, 
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with ac2:
                    with st.popover("📧 Email to Me", use_container_width=True):
                        email_input = st.text_input("Recipient Email", placeholder="name@elmcrest.org")
                        if st.button("Send Email"):
                            if email_input:
                                with st.spinner("Sending..."):
                                    success, msg = send_pdf_via_email(
                                        to_email=email_input,
                                        subject=f"Supervisor Guide: {d['name']}",
                                        body=f"Attached is the Compass Supervisor Guide for {d['name']}.",
                                        pdf_bytes=st.session_state.generated_pdf,
                                        filename=st.session_state.generated_filename
                                    )
                                    if success: st.success(msg)
                                    else: st.error(msg)
                            else:
                                st.warning("Please enter an email address.")
                
            st.button("Reset", on_click=reset_t1)

    # --- MANUAL TAB ---
    with sub2:
        with st.container(border=True):
            st.info("Use this tab to generate a PDF for someone who isn't in the database yet, without saving them.")
            with st.form("manual"):
                c1,c2 = st.columns(2)
                mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
                mpc = c1.selectbox("Comm", COMM_TRAITS); mpm = c2.selectbox("Motiv", MOTIV_TRAITS)
                
                if st.form_submit_button("Generate PDF Only") and mn:
                    pdf_manual = create_supervisor_guide(mn, mr, mpc, None, mpm, None)
                    fname_manual = f"Guide_{mn.replace(' ', '_')}.pdf"
                    st.session_state.manual_pdf = pdf_manual
                    st.session_state.manual_fname = fname_manual
                    display_guide(mn, mr, mpc, None, mpm, None)

        if "manual_pdf" in st.session_state:
            st.divider()
            ac1, ac2 = st.columns([1, 2])
            with ac1:
                st.download_button("📥 Download PDF", st.session_state.manual_pdf, st.session_state.manual_fname, "application/pdf", use_container_width=True)
            with ac2:
                with st.popover("📧 Email to Me", use_container_width=True):
                    email_input_m = st.text_input("Recipient Email", key="manual_email")
                    if st.button("Send Email", key="btn_manual_email"):
                        if email_input_m:
                            with st.spinner("Sending..."):
                                success, msg = send_pdf_via_email(
                                    email_input_m,
                                    f"Supervisor Guide: {mn}",
                                    f"Attached is the manually generated Compass Guide for {mn}.",
                                    st.session_state.manual_pdf,
                                    st.session_state.manual_fname
                                )
                            if success: st.success(msg)
                            else: st.error(msg)

    # --- INPUT OFFLINE DATA TAB ---
    with sub3:
        with st.container(border=True):
            st.markdown("### 📥 Input Offline Results")
            st.info("Use this form to enter results from paper assessments. This will save the data to the Google Sheet and update the database.")
            
            with st.form("offline_input_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    off_name = st.text_input("Staff Name (Required)")
                    off_email = st.text_input("Email (Optional)")
                    off_role = st.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor", "Clinician", "TSS Staff", "Other"])
                    off_cottage = st.selectbox("Program/Cottage", ["Building 10", "Cottage 2", "Cottage 3", "Cottage 7", "Cottage 8", "Cottage 9", "Cottage 11", "Euclid", "Overnight", "Skeele Valley", "TSS Staff", "Other"])
                with col_b:
                    st.markdown("**Assessment Results**")
                    off_p_comm = st.selectbox("Primary Communication", COMM_TRAITS, key="off_pc")
                    off_s_comm = st.selectbox("Secondary Communication", COMM_TRAITS, key="off_sc")
                    off_p_mot = st.selectbox("Primary Motivation", MOTIV_TRAITS, key="off_pm")
                    off_s_mot = st.selectbox("Secondary Motivation", MOTIV_TRAITS, key="off_sm")
                
                st.markdown("---")
                if st.form_submit_button("💾 Save to Database", type="primary"):
                    if off_name:
                        with st.spinner("Saving to Google Sheets..."):
                            payload = {
                                "name": off_name, "email": off_email, "role": off_role, "cottage": off_cottage,
                                "p_comm": off_p_comm, "s_comm": off_s_comm, "p_mot": off_p_mot, "s_mot": off_s_mot
                            }
                            success = submit_data_to_google(payload)
                            if success:
                                st.success(f"Successfully saved {off_name}!")
                                new_row = payload.copy()
                                st.session_state.staff_df = pd.concat([st.session_state.staff_df, pd.DataFrame([new_row])], ignore_index=True)
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to save. Please check your internet connection or the Google Script URL.")
                    else:
                        st.error("Name is required.")

# 2. TEAM DNA
elif st.session_state.current_view == "Team DNA":
    st.subheader("🧬 Team DNA")
    if not df.empty:
        with st.container(border=True):
            teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        
        if teams:
            tdf = df[df['name'].isin(teams)]
            
            # Helper for weighted calculation (Primary=1.0, Secondary=0.5)
            def calculate_weighted_counts(dframe, p_col, s_col):
                p = dframe[p_col].value_counts() * 1.0
                s = dframe[s_col].value_counts() * 0.5
                return p.add(s, fill_value=0).sort_values(ascending=False)

            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    # Weighted Communication
                    comm_counts = calculate_weighted_counts(tdf, 'p_comm', 's_comm')
                    st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, title="Communication Mix", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
                
                # DOMINANT CULTURE ANALYSIS
                if not comm_counts.empty:
                    dom_style = comm_counts.idxmax()
                    # Calculate dominance based on share of total weighted points
                    ratio = comm_counts.max() / comm_counts.sum()
                    
                    if ratio > 0.4: # Slightly lower threshold for weighted dominance
                        guide = TEAM_CULTURE_GUIDE.get(dom_style, {})
                        with st.container(border=True):
                            st.warning(f"⚠️ **Dominant Culture:** This team is {int(ratio*100)}% **{dom_style}** (incl. secondary styles).")
                            with st.expander(f"📖 Managing the {guide.get('title', dom_style)}", expanded=True):
                                st.markdown(f"**The Vibe:**\n{guide.get('impact_analysis')}")
                                st.markdown(guide.get('management_strategy'))
                                st.markdown(f"**📋 Meeting Protocol:**\n{guide.get('meeting_protocol')}")
                                st.info(f"**🎉 Team Building Idea:** {guide.get('team_building')}")
                    else:
                        # BALANCED CULTURE
                        guide = TEAM_CULTURE_GUIDE.get("Balanced", {})
                        with st.container(border=True):
                            st.info("**Balanced Culture:** No single style dominates significantly. This reduces blindspots but may increase friction.")
                            with st.expander("📖 Managing a Balanced Team", expanded=True):
                                st.markdown("""**The Balanced Friction:**
                                A diverse team has no blind spots, but it speaks 4 different languages. Your role is **The Translator**.
                                * **Translate Intent:** 'The Director isn't being mean; they are being efficient.' 'The Tracker isn't being difficult; they are being safe.'
                                * **Rotate Leadership:** Let the Director lead the crisis; let the Encourager lead the debrief; let the Tracker lead the audit.
                                * **Meeting Protocol:** Use structured turn-taking (Round Robin) so the loudest voice doesn't always win.""")

                # MISSING VOICE ANALYSIS
                # Check presence in Primary OR Secondary
                p_present = set(tdf['p_comm'].unique())
                s_present = set(tdf['s_comm'].unique())
                all_present = p_present.union(s_present)
                
                missing_styles = set(COMM_TRAITS) - all_present
                
                if missing_styles:
                    with st.container(border=True):
                        st.error(f"🚫 **Missing Voices:** {', '.join(missing_styles)}")
                        cols = st.columns(len(missing_styles))
                        for idx, style in enumerate(missing_styles):
                            with cols[idx]:
                                data = MISSING_VOICE_GUIDE.get(style, {})
                                st.markdown(f"**Without a {style}:**")
                                st.write(data.get('risk'))
                                st.success(f"**Supervisor Fix:** {data.get('fix')}")

            with c2:
                with st.container(border=True):
                    # Weighted Motivation
                    mot_counts = calculate_weighted_counts(tdf, 'p_mot', 's_mot')
                    st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
                
                # MOTIVATION GAP ANALYSIS
                if not mot_counts.empty:
                    dom_mot = mot_counts.idxmax()
                    with st.container(border=True):
                        st.subheader(f"⚠️ Motivation Gap: {dom_mot} Driven")
                        
                        # Fetch data from new dictionary
                        mot_guide = MOTIVATION_GAP_GUIDE.get(dom_mot, {})
                        if mot_guide:
                            st.warning(mot_guide['warning'])
                            with st.expander("💡 Coaching Strategy for this Driver", expanded=True):
                                st.markdown(mot_guide['coaching'])
            
            st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    if not df.empty:
        # Sidebar for API Key
        with st.sidebar:
            # Try to get key from secrets (support both names)
            secret_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
            
            # Input field (defaults to secret if found)
            user_api_key = st.text_input(
                "🔑 Gemini API Key", 
                value=st.session_state.get("gemini_key_input", secret_key),
                type="password",
                help="Get a key at aistudio.google.com"
            )
            
            # Persist input to session state
            if user_api_key:
                st.session_state.gemini_key_input = user_api_key
                st.success("✅ API Key Active")
            else:
                st.error("❌ No API Key Found")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            p1 = c1.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1")
            p2 = c2.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            
            # Extract Primary AND Secondary styles
            s1_p, s1_s = d1['p_comm'], d1['s_comm']
            m1_p, m1_s = d1['p_mot'], d1['s_mot']
            
            s2_p, s2_s = d2['p_comm'], d2['s_comm']
            m2_p, m2_s = d2['p_mot'], d2['s_mot']
            
            st.divider()
            # Display full profile in header
            st.subheader(f"{s1_p}/{s1_s} (Sup) vs. {s2_p}/{s2_s} (Staff)")
            
            # Updated Logic to display BOTH Primary and Secondary clashes
            if s1_p in SUPERVISOR_CLASH_MATRIX and s2_p in SUPERVISOR_CLASH_MATRIX[s1_p]:
                clash_p = SUPERVISOR_CLASH_MATRIX[s1_p][s2_p]
                
                # Retrieve Secondary Clash if applicable
                clash_s = None
                if s1_s and s2_s and s1_s in SUPERVISOR_CLASH_MATRIX and s2_s in SUPERVISOR_CLASH_MATRIX.get(s1_s, {}):
                    clash_s = SUPERVISOR_CLASH_MATRIX[s1_s][s2_s]

                with st.expander("🔍 **Psychological Deep Dive (Primary & Secondary)**", expanded=True):
                    
                    # Create Tabs for the two layers of conflict
                    t_prime, t_sec = st.tabs([f"🔥 Major Tension ({s1_p} vs {s2_p})", f"🌊 Minor Tension ({s1_s} vs {s2_s})"])
                    
                    # --- TAB 1: PRIMARY (STRESS) ---
                    with t_prime:
                        st.caption(f"This dynamic dominates during **crises, deadlines, and high-pressure moments**.")
                        st.markdown(f"**The Core Tension:** {clash_p['tension']}")
                        st.markdown(f"{clash_p['psychology']}")
                        st.markdown("**🚩 Watch For (Stress Behaviors):**")
                        for w in clash_p['watch_fors']: st.markdown(f"- {w}")
                        
                        st.divider()
                        c_a, c_b = st.columns(2)
                        with c_a:
                            st.markdown("##### 🛠️ Coaching Protocol")
                            for i in clash_p['intervention_steps']: st.info(i)
                        with c_b:
                            st.markdown("##### 🗣️ Conflict Scripts")
                            script_tabs = st.tabs(list(clash_p['scripts'].keys()))
                            for i, (cat, text) in enumerate(clash_p['scripts'].items()):
                                with script_tabs[i]:
                                    st.success(f"\"{text}\"")

                    # --- TAB 2: SECONDARY (ROUTINE) ---
                    with t_sec:
                        if clash_s:
                            st.caption(f"This dynamic influences **routine planning, low-stress interactions, and daily workflow**.")
                            st.markdown(f"**The Core Tension:** {clash_s['tension']}")
                            st.markdown(f"{clash_s['psychology']}")
                            st.markdown("**🚩 Watch For (Subtle Friction):**")
                            for w in clash_s['watch_fors']: st.markdown(f"- {w}")
                            
                            st.divider()
                            st.markdown("##### 🛠️ Routine Adjustments")
                            for i in clash_s['intervention_steps']: 
                                # Formatting slightly differently to distinguish from primary protocol
                                clean_step = i.replace("**", "").replace("1. ", "").replace("2. ", "").replace("3. ", "")
                                st.markdown(f"- {clean_step}")
                        else:
                            st.info("Secondary styles are undefined or identical. Focus on the Primary dynamic.")

            else:
                st.info("No specific conflict protocol exists for this combination yet. They likely work well together!")
            
            # --- AI SUPERVISOR BOT ---
            st.markdown("---")
            with st.container(border=True):
                st.subheader("🤖 AI Supervisor Assistant (Enhanced Context)")
                
                # Determine active key from variable
                active_key = user_api_key
                
                if active_key:
                    st.caption(f"Powered by Gemini 2.5 Flash | analyzing full profile dynamics.")
                else:
                    st.caption("Basic Mode | Add an API Key in the sidebar to unlock full AI capabilities.")
                
                st.info("⬇️ **Type your question in the chat bar at the bottom of the screen.**")
                
                # Initialize history specifically for this view if not present
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Display messages
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # -------------------------------------------
                # LOGIC ENGINE: HYBRID (Rule-Based + Gemini)
                # -------------------------------------------
                # Updated function to accept full profiles
                def get_smart_response(query, p2_name, s2_p, s2_s, m2_p, m2_s, s1_p, s1_s, m1_p, m1_s, key):
                    # Prepare Context Data (Primary)
                    comm_data = COMM_PROFILES.get(s2_p, {})
                    mot_data = MOTIV_PROFILES.get(m2_p, {})
                    
                    # If API Key exists, use Gemini
                    if key:
                        try:
                            # Enhanced System Prompt with Secondary Styles
                            system_prompt = f"""
                            You are an expert Leadership Coach for a youth care agency.
                            You are advising a Supervisor on how to manage a staff member named {p2_name}.
                            
                            **Staff Member Profile ({p2_name}):**
                            - **Communication:** Primary: {s2_p}, Secondary: {s2_s}
                            - **Motivation:** Primary: {m2_p}, Secondary: {m2_s}
                            - **Thriving Behaviors (Primary):** {comm_data.get('bullets', [])}
                            
                            **Supervisor Profile (You):**
                            - **Communication:** Primary: {s1_p}, Secondary: {s1_s}
                            - **Motivation:** Primary: {m1_p}, Secondary: {m1_s}
                            
                            **Your Goal:** Answer the user's question by analyzing the dynamic between these specific profiles.
                            - Incorporate the *Secondary* styles to add nuance (e.g., A Director with a Facilitator secondary is softer than a pure Director).
                            - Identify potential friction points between the Supervisor's style and the Staff's style.
                            - Give concise, actionable advice suitable for a residential care environment.
                            """
                            
                            # API Call to Gemini 2.5 Flash (Standard Endpoint)
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
                            payload = {
                                "contents": [{
                                    "parts": [{"text": system_prompt + "\n\nUser Question: " + query}]
                                }]
                            }
                            headers = {'Content-Type': 'application/json'}
                            
                            # Retry logic for 503 (Overloaded) errors
                            max_retries = 3
                            for attempt in range(max_retries):
                                response = requests.post(url, headers=headers, data=json.dumps(payload))
                                
                                if response.status_code == 200:
                                    return response.json()['candidates'][0]['content']['parts'][0]['text']
                                elif response.status_code == 503:
                                    # Server overloaded, wait and retry
                                    time.sleep(2 ** (attempt + 1)) # Exponential backoff: 2s, 4s, 8s
                                    continue
                                else:
                                    return f"⚠️ **AI Error ({response.status_code}):** {response.text}. Falling back to basic database."
                            
                            return "⚠️ **AI Service Busy:** The model is currently overloaded. Falling back to basic database."
                        
                        except Exception as e:
                            return f"⚠️ **Connection Error:** {str(e)}. Falling back to basic database."

                    # FALLBACK: Rule-Based Logic (No API Key)
                    query = query.lower()
                    response = ""
                    
                    if "who is" in query or "tell me about" in query or "profile" in query:
                         response += f"**Profile Overview:** {p2_name} is a **{s2_p}/{s2_s}** driven by **{m2_p}/{m2_s}**.\n\n"
                         response += "**Primary Style:**\n"
                         for b in comm_data.get('bullets', []):
                             response += f"- {b}\n"

                    elif "strengths" in query or "good at" in query:
                        response += f"**Strengths:** As a {s2_p}, they excel at: \n"
                        for b in comm_data.get('bullets', []):
                            response += f"- {b}\n"

                    elif "feedback" in query or "critical" in query or "correct" in query:
                        response += f"**On giving feedback to a {s2_p}:**\n"
                        for b in comm_data.get('supervising_bullets', []):
                            response += f"- {b}\n"
                    
                    elif "motivate" in query or "burnout" in query:
                        response += f"**To motivate a {m2_p} driver:**\n"
                        for b in mot_data.get('strategies_bullets', []):
                            response += f"- {b}\n"
                    
                    else:
                        debug_key_info = f"Key detected: {key[:4]}..." if key else "No API Key detected"
                        response = f"I can help you manage {p2_name}. Try asking about:\n- How to give **feedback**\n- How to **motivate** them\n- How to handle **conflict**\n\n*Note: {debug_key_info}. Please check the sidebar.*"
                    
                    return response

                # Input
                if prompt := st.chat_input(f"Ask about {p2}..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Consulting the Compass Database..."):
                            # Pass all profile data to the AI
                            bot_reply = get_smart_response(prompt, p2, s2_p, s2_s, m2_p, m2_s, s1_p, s1_s, m1_p, m1_s, active_key)
                            st.markdown(bot_reply)
                    
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        elif p1 and p2 and p1 == p2:
             st.warning("⚠️ You selected the same person twice. Please select two **different** staff members to analyze a conflict.")
             
        st.button("Reset", key="reset_t3", on_click=reset_t3)

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    if not df.empty:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            cand = c1.selectbox("Candidate", df['name'].unique(), index=None, key="career")
            # [CHANGE] Added "Director" to the list of target roles
            role = c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager", "Director"], index=None, key="career_target")
        
        if cand and role:
            d = df[df['name']==cand].iloc[0]
            style = d['p_comm']
            path = CAREER_PATHWAYS.get(style, {}).get(role)
            if path:
                st.info(f"**Shift:** {path['shift']}")
                
                with st.container(border=True):
                    st.markdown("### 🧠 The Psychological Block")
                    st.markdown(f"**Why it's hard:** {path['why']}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    with st.container(border=True):
                        st.markdown("##### 🗣️ The Conversation")
                        st.write(path['conversation'])
                        if 'supervisor_focus' in path: st.warning(f"**Watch For:** {path['supervisor_focus']}")
                with c_b:
                    with st.container(border=True):
                        st.markdown("##### ✅ Assignment")
                        st.write(f"**Setup:** {path['assignment_setup']}")
                        st.write(f"**Task:** {path['assignment_task']}")
                        st.divider()
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flags:** {path['red_flags']}")
                if 'debrief_questions' in path:
                    with st.expander("🧠 Post-Assignment Debrief Questions"):
                        for q in path['debrief_questions']: st.markdown(f"- {q}")
            st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        # --- DATA PREP (Weighted) ---
        total_staff = len(df)
        
        def calculate_weighted_pct(dframe, p_col, s_col):
            p = dframe[p_col].value_counts() * 1.0
            s = dframe[s_col].value_counts() * 0.5
            total = p.add(s, fill_value=0)
            return (total / total.sum()) * 100

        comm_counts = calculate_weighted_pct(df, 'p_comm', 's_comm').sort_values(ascending=False)
        mot_counts = calculate_weighted_pct(df, 'p_mot', 's_mot').sort_values(ascending=False)
        
        # Top Metrics
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            if not comm_counts.empty:
                dom_comm = comm_counts.idxmax()
                dom_mot = mot_counts.idxmax()
                c1.metric("Dominant Style", f"{dom_comm} ({int(comm_counts.max())}%)")
                c2.metric("Top Driver", f"{dom_mot} ({int(mot_counts.max())}%)") 
                c3.metric("Total Staff Analyzed", total_staff)
            
        st.divider()
        
        # --- VISUALS ---
        c_a, c_b = st.columns(2)
        with c_a: 
            with st.container(border=True):
                st.markdown("##### 🗣️ Communication Mix")
                # Use pre-calculated weighted counts for the chart
                fig_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']])
                st.plotly_chart(fig_comm, use_container_width=True)
        with c_b: 
            with st.container(border=True):
                st.markdown("##### 🔋 Motivation Drivers")
                fig_mot = px.bar(x=mot_counts.values, y=mot_counts.index, orientation='h', color_discrete_sequence=[BRAND_COLORS['blue']])
                st.plotly_chart(fig_mot, use_container_width=True)

        st.divider()
        st.header("🔍 Deep Organizational Analysis")
        
        tab1, tab2, tab3 = st.tabs(["🛡️ Culture Risk Assessment", "🔥 Motivation Strategy", "🌱 Leadership Pipeline Health"])
        
        # --- TAB 1: CULTURE RISK ---
        with tab1:
            with st.container(border=True):
                st.markdown(f"### The {dom_comm}-Dominant Culture")
                
                if dom_comm == "Director":
                    st.error("🚨 **Risk Area: The Efficiency Trap**")
                    st.write("Your organization is heavily weighted towards action, speed, and results. While this means you get things done, you are at high risk for **'Burn and Turn.'**")
                    st.markdown("""
                    **The Blindspot:**
                    * **Low Empathy:** Staff likely feel that 'management doesn't care about us, only the numbers.'
                    * **Steamrolling:** Quiet voices (Facilitators/Trackers) are likely being ignored in meetings because they don't speak fast enough.
                    * **Crisis Addiction:** The culture likely rewards firefighting more than fire prevention.
                    
                    **🛡️ Coaching Strategy for Leadership:**
                    1.  **Mandate 'Cooling Off' Periods:** Do not allow major decisions to be made in the same meeting they are proposed. Force a 24-hour pause to let slower processors think.
                    2.  **Artificial Empathy:** You must operationalize care. Start every meeting with 5 minutes of personal check-ins. It will feel like a waste of time to you; it is oxygen to your staff.
                    3.  **Protect the Dissenters:** Explicitly ask the quietest person in the room for their opinion. They see the risks you are missing.
                    """)
                
                elif dom_comm == "Encourager":
                    st.warning("⚠️ **Risk Area: The 'Nice' Trap**")
                    st.write("Your organization prioritizes harmony, relationships, and good vibes. While morale is likely good, you are at high risk for **'Toxic Tolerance.'**")
                    st.markdown("""
                    **The Blindspot:**
                    * **Lack of Accountability:** Poor performance is tolerated because no one wants to be 'mean.'
                    * **The 'Cool Parent' Syndrome:** Leaders want to be liked more than they want to be respected.
                    * **Hidden Conflict:** Because open conflict is avoided, issues go underground (gossip, passive-aggression).
                    
                    **🛡️ Coaching Strategy for Leadership:**
                    1.  **Redefine Kindness:** Coach your leaders that holding people accountable is *kind* because it helps them succeed. Allowing failure is cruel.
                    2.  **Standardize Feedback:** Create a rigid structure for performance reviews so leaders can't opt-out of hard conversations.
                    3.  **Focus on the 'Who':** When making hard decisions, frame it as protecting the *team* (the collective 'who') from the toxicity of the individual.
                    """)
                
                elif dom_comm == "Facilitator":
                    st.info("🐢 **Risk Area: The Consensus Trap**")
                    st.write("Your organization values fairness, listening, and inclusion. While people feel heard, you are at risk for **'Analysis Paralysis.'**")
                    st.markdown("""
                    **The Blindspot:**
                    * **Slow Decisions:** You likely have meetings about meetings. Urgent problems fester while you wait for everyone to agree.
                    * **The 'Lowest Common Denominator':** Solutions are often watered down to ensure no one is offended.
                    * **Crisis Failure:** In an emergency, the team may freeze, waiting for a vote when they need a command.
                    
                    **🛡️ Coaching Strategy for Leadership:**
                    1.  **The 51% Rule:** Establish a rule that once you have 51% certainty (or 51% consensus), you move. Perfection is the enemy of done.
                    2.  **Disagree and Commit:** Teach the culture that it is okay to disagree with a decision but still support its execution 100%.
                    3.  **Assign 'Decision Owners':** Stop making decisions by committee. Assign one person to decide, and the committee only *advises*.
                    """)
                
                elif dom_comm == "Tracker":
                    st.warning("🛑 **Risk Area: The Bureaucracy Trap**")
                    st.write("Your organization values safety, precision, and rules. While you are compliant, you are at risk for **'Stagnation.'**")
                    st.markdown("""
                    **The Blindspot:**
                    * **Innovation Death:** New ideas are killed by 'policy' before they can be tested.
                    * **Rigidity:** Staff may escalate youth behaviors because they prioritize enforcing a minor rule over maintaining the relationship.
                    * **Fear Based:** The culture is likely driven by a fear of getting in trouble rather than a desire to do good.
                    
                    **🛡️ Coaching Strategy for Leadership:**
                    1.  **'Safe to Fail' Zones:** Explicitly designate areas where staff are allowed to experiment and fail without consequence.
                    2.  **The 'Why' Test:** Challenge every rule. If a staff member cannot explain *why* a rule exists (beyond 'it's in the book'), they aren't leading; they are robot-ing.
                    3.  **Reward Adaptation:** Publicly praise staff who *bent* a rule to save a situation (safely). Show that judgment is valued over blind compliance.
                    """)

        # --- TAB 2: MOTIVATION STRATEGY ---
        with tab2:
            with st.container(border=True):
                st.markdown(f"### The Drive: {dom_mot}")
                
                if dom_mot == "Achievement":
                    st.success("🏆 **Strategy: The Scoreboard**")
                    st.write("Your team runs on winning. They need to know they are succeeding based on objective data.")
                    st.markdown("""
                    * **The Danger:** If goals are vague or 'feelings-based,' they will disengage.
                    * **The Fix:** Visualize success. Put charts on the wall. Track days without incidents. Give out awards for 'Most Shifts Covered' or 'Best Audit Score'.
                    * **Language:** Use words like *Goal, Target, Win, Speed, Elite.*
                    """)
                elif dom_mot == "Connection":
                    st.info("🤝 **Strategy: The Tribe**")
                    st.write("Your team runs on belonging. They will work harder for each other than for the 'company.'")
                    st.markdown("""
                    * **The Danger:** If they feel isolated or if management feels 'cold,' they will quit. Toxic peers destroy this culture fast.
                    * **The Fix:** Invest in food, team outings, and face time. Start meetings with personal connection.
                    * **Language:** Use words like *Family, Team, Support, Together, Safe.*
                    """)
                elif dom_mot == "Purpose":
                    st.warning("🔥 **Strategy: The Mission**")
                    st.write("Your team runs on meaning. They are here to change lives, not just collect a paycheck.")
                    st.markdown("""
                    * **The Danger:** If they feel the work is just 'paperwork' or 'warehousing kids,' they will burn out or rebel.
                    * **The Fix:** Connect EVERY task to the youth. 'We do this paperwork so [Youth Name] can get funding for his placement.' Share success stories constantly.
                    * **Language:** Use words like *Impact, Mission, Change, Justice, Future.*
                    """)
                elif dom_mot == "Growth":
                    st.success("🌱 **Strategy: The Ladder**")
                    st.write("Your team runs on competence. They want to get better, smarter, and more skilled.")
                    st.markdown("""
                    * **The Danger:** If they feel stagnant or bored, they will leave for a new challenge.
                    * **The Fix:** create 'Micro-Promotions.' Give them special titles (e.g., 'Safety Captain'). Send them to trainings. Map out their career path visually.
                    * **Language:** Use words like *Skill, Level Up, Career, Master, Learn.*
                    """)

        # --- TAB 3: PIPELINE HEALTH ---
        with tab3:
            with st.container(border=True):
                st.markdown("### Leadership Pipeline Analysis")
                if 'role' in df.columns:
                    # Compare Leadership Composition to General Staff
                    leaders = df[df['role'].isin(['Program Supervisor', 'Shift Supervisor', 'Manager'])]
                    if not leaders.empty:
                        # Use weighted counts for Leadership Analysis as well
                        l_counts = calculate_weighted_pct(leaders, 'p_comm', 's_comm').sort_values(ascending=False)
                        
                        st.write("**Leadership Diversity Check:**")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.caption("Leadership Team Mix")
                            st.dataframe(l_counts)
                        with c2:
                            st.caption("General Staff Mix")
                            st.dataframe(comm_counts)
                        
                        # Clone Warning
                        dom_lead = l_counts.idxmax()
                        if l_counts.max() > 60:
                            st.error(f"🚫 **Warning: Cloning Bias Detected**")
                            st.write(f"Your leadership team is over 60% **{dom_lead}**. You are likely promoting people who 'look like you' (communication-wise).")
                            st.write("This creates a massive blind spot. If all leaders are Directors, who is listening to the staff? If all leaders are Encouragers, who is making the hard calls?")
                            st.info("**Recommendation:** actively recruit for the *opposite* style for your next leadership opening.")
                    else:
                        st.info("No leadership roles identified in the data set to analyze.")
                else:
                    st.warning("Role data missing. Cannot analyze pipeline.")
    else: st.warning("No data available.")
