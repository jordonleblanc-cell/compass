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
            "**Clarity:** They prioritize the 'bottom line' over the backstory, speaking in headlines to ensure immediate understanding. Supervisors should not mistake their brevity for rudeness.",
            "**Speed:** They process information rapidly and expect others to keep up, preferring a quick 80% solution over a delayed 100% solution. They are likely to interrupt if they feel a conversation is dragging or becoming repetitive, signaling their desire to move on. Supervisors should be prepared to move quickly through agenda items to maintain their engagement. They view pause and hesitation as a lack of confidence or competence in others.",
            "**Conflict:** They view conflict as a tool for problem-solving rather than a relationship breaker. They do not take disagreement personally and respect those who push back with logic. They are comfortable addressing issues head-on and may perceive hesitation in others as weakness or lack of preparation. For them, friction is necessary to sharpen ideas."
        ],
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately; avoid 'sandwiching' feedback with small talk. They value their time and yours, and they respect supervisors who treat time as a resource. If you have five minutes of content, do not stretch it to thirty. They will tune out if they feel you are 'padding' the conversation.",
            "**Focus on Outcomes:** Tell them what needs to be achieved, but leave the how to them. Focusing on the end result empowers them to find the most efficient path. Over-explaining the process will make them feel micromanaged and stifled. They trust their own ability to navigate the map; they just need you to identify the destination.",
            "**Respect Autonomy:** Give them space to operate independently; tight oversight feels like distrust to a Director. Check in at agreed-upon milestones rather than hovering constantly. Trust that they will come to you if they hit a roadblock they cannot remove themselves. Their silence usually means they are working, not that they are lost."
        ]
    },
    "Encourager": {
        "bullets": [
            "**Verbal Processing:** They think out loud and prefer talking through problems rather than reading about them. They are articulate and inspiring. They need to hear their own voice to know what they think. They process information externally and socially.",
            "**Optimism:** They naturally focus on the potential and the positive. They sell the vision effectively but may gloss over the gritty details. They see the glass as overflowing. They are the cheerleaders of the organization.",
            "**Relationship-First:** They influence people through liking and charisma. They prioritize the 'vibe' of the interaction. They want you to like them before they want you to understand them. They build bridges before they cross them."
        ],
        "supervising_bullets": [
            "**Allow Discussion:** Give them a few minutes to chat and connect; cutting them off too early kills their morale. They need the relational runway to take off. Small talk is big work for them.",
            "**Ask for Specifics:** They speak in generalities ('It's going great!'). Ask 'What specifically is going great?' to get the data. You must drill down to find the reality beneath the enthusiasm. Force them to define their terms.",
            "**Follow Up in Writing:** They may agree enthusiastically in the moment but forget the details. Always send a recap email. Their memory is often tied to the emotion of the moment, not the facts. Document the boring parts for them."
        ]
    },
    "Facilitator": {
        "bullets": [
            "**Listening:** They gather all perspectives before speaking. They are the quiet ones in the meeting who are taking notes. They want the full picture before they commit to an opinion. They value input from every chair in the room to ensure nothing is missed.",
            "**Consensus:** They prefer group agreement over unilateral action. They view a 5-4 vote as a failure to align the team properly. They want everyone on the bus before the bus moves forward. They work hard to bring dissenters along to create a unified front.",
            "**Process:** They value how a decision is made as much as the decision itself. They hate chaos and shooting from the hip without a plan. They want a clear agenda, a timeline, and a protocol to follow. They find comfort in the structure of a well-organized meeting."
        ],
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before asking for a decision. Send the agenda 24 hours in advance so they can prepare. They hate being put on the spot and forced to react instantly. They need to process internally before they speak publicly to ensure they are accurate.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless deliberation. Without a deadline, they will process forever in search of the perfect consensus. You must close the window of discussion to ensure progress. Give them a specific time to stop thinking and start acting.",
            "**Solicit Opinion:** Ask them explicitly what they think during meetings. They will not fight for airtime against louder voices. You have to hand them the microphone to get their valuable insight. Their silence does not mean they have nothing to say; it means they are waiting to be asked."
        ]
    },
    "Tracker": {
        "bullets": [
            "**Detail-Oriented:** They communicate in spreadsheets, data, and precise details. They value accuracy above all else and will correct you if you are wrong. They want to be right, not just understood. They find safety in the specifics and mistrust vagueness.",
            "**Risk-Averse:** They are cautious in their speech, avoiding definitive statements until they are 100% sure. They will often say 'let me check on that' rather than guessing. They view guessing as lying or irresponsibility. They speak carefully and deliberately.",
            "**Process-Driven:** They talk about how we do things, not just what we do. They are the guardians of the handbook and the policy manual. They believe the rules exist to save us from chaos. They quote the manual to settle disputes."
        ],
        "supervising_bullets": [
            "**Be Specific:** Do not use vague language like 'do it better' or 'work harder.' Give them the metric: 'Increase accuracy by 10%.' They cannot hit a target they cannot see. Use numbers, not feelings, to drive behavior.",
            "**Provide Data:** If you want to persuade them, bring the numbers and the facts. Emotional appeals will bounce off them. They respect logic, evidence, and precedent. Show them the proof that your idea works.",
            "**Written Instructions:** Follow up every verbal conversation with an email. They trust the written word more than the spoken word. It provides a paper trail they crave for security. Document the ask to ensure alignment."
        ]
    }
}

MOTIV_PROFILES = {
    "Achievement": {
        "bullets": [
            "**Scoreboard:** They need to know if they are winning or losing at any given moment. Ambiguity is their enemy; they need quantifiable metrics to judge their own performance. Without a clear definition of success, they may become anxious or disengaged. They are driven by the comparison of 'where we were' vs 'where we are.'",
            "**Completion:** They derive energy from finishing tasks and closing loops. An endless list of open-ended projects drains them; they need the dopamine hit of marking a task 'done.' Ensure they have a mix of short-term wins alongside long-term goals. If a project has no end in sight, they will manufacture a conclusion or lose interest.",
            "**Efficiency:** They hate wasted time and redundancy more than almost anything else. If a meeting has no clear purpose, they will resent attending. They are motivated by streamlining processes and removing bottlenecks. They will work harder to build a system that saves time than they will to just do the work."
        ],
        "strategies_bullets": [
            "**Visual Goals:** Use charts, dashboards, or checklists they can physically mark off. Seeing their progress visually reinforces their sense of forward momentum. Set up a system where they can self-monitor their data without needing to ask you. The visual representation of 'done' is a powerful psychological reward for them.",
            "**Public Wins:** Acknowledge their success in front of peers, highlighting competence and results. They value respect for their capability more than praise for their personality. Be specific about what they achieved, using data whenever possible. General praise like 'good job' means less to them than 'you improved efficiency by 20%.'",
            "**Autonomy:** Give them the goal and let them design the strategy. This appeals to their desire for control and efficiency. When they succeed using their own methods, their buy-in to the organization deepens significantly. It proves to them that you trust their competence."
        ],
        "celebrate_bullets": [
            "**Efficiency:** Celebrate specific instances where they solved a complex logistical puzzle quickly. Quantify the time or money they saved.",
            "**Clarity:** Celebrate their ability to draw a hard line or make a tough call.",
            "**Resilience:** Celebrate their ability to bounce back immediately and focus on solutions."
        ],
        "celebrate_deep_dive": "**Recognition Language: Competence & Impact.**\nThey don't want a generic 'good job.' They want you to notice the specific problem they solved. \n\n*Script:* 'I saw how you reorganized the log system; it saved the team 20 minutes tonight. That was brilliant efficiency.'"
    },
    "Growth": {
        "bullets": [
            "**Curiosity:** They are driven to understand the 'why' and 'how' behind every rule. They will not accept 'because we've always done it this way' as an answer. This curiosity is an asset for innovation but can feel like insubordination to insecure leaders. They need to take the machine apart to see how it works.",
            "**Future-Focused:** They view their current role primarily as a stepping stone to the next challenge. They need to see a clear trajectory for their career or they will look elsewhere. They are constantly scanning the horizon for what is next, which keeps them ambitious but potentially dissatisfied with the present. They live in the future tense.",
            "**Feedback:** They crave constructive correction over empty praise. Telling them 'good job' is less effective than telling them 'here is how you could do that 10% better.' They view criticism as free consulting for their personal brand and professional development. They want to be sharper, not just happier."
        ],
        "strategies_bullets": [
            "**Stretch Assignments:** Assign tasks slightly above their current skill level. They are bored by mastery; they need to feel the tension of potential failure to stay engaged. Give them problems that no one else has solved yet.",
            "**Career Pathing:** Discuss their professional future regularly, not just at annual reviews. Map out exactly how their current work contributes to their 5-year plan. Be honest about what skills they lack for the next level so they have a target to aim for.",
            "**Mentorship:** Connect them with leaders they admire inside or outside the organization. They learn through observation and proximity to power/intellect. Facilitate introductions to senior leadership as a reward for performance."
        ],
        "celebrate_bullets": [
            "**Insight:** Celebrate specific moments where they identified a root cause others missed.",
            "**Development:** Celebrate a staff member who visibly improved under their guidance.",
            "**Courage:** Celebrate their willingness to try a new approach, even if it failed."
        ],
        "celebrate_deep_dive": "**Recognition Language: Trajectory & Potential.**\nPraise the *change* in their behavior, not just the result. Validate their struggle and learning. \n\n*Script:* 'I noticed you handled that crisis differently than last month. You stayed calm and followed the protocol perfectly. Your growth here is obvious.'"
    },
    "Purpose": {
        "bullets": [
            "**Values-Driven:** They filter every decision through the lens of 'Is this right?' They are less concerned with 'Is this profitable?' or 'Is this efficient?' If a directive violates their internal code, they will resist it, often openly and fiercely. They act as the moral conscience of the room.",
            "**Advocacy:** They are wired to fight for the underdog. They naturally align themselves with the most vulnerable person in the room (the client, the new staff member). They see themselves as the shield against a cold system. They will risk their own standing to protect someone else.",
            "**Meaning:** They need the 'why' connected to client well-being. They cannot work for a paycheck alone; they must believe their work matters. If they lose connection to the mission, they burn out instantly. They need to feel they are part of a crusade, not just a company."
        ],
        "strategies_bullets": [
            "**The Why:** Explain the mission behind every mandate. Never say 'because I said so' or 'because it's policy.' Connect the rule directly to how it keeps a child safe or helps a family heal. If they understand the noble purpose, they will endure any hardship.",
            "**Storytelling:** Share narratives of redemption and impact. They are fueled by stories of success against the odds. Remind them of the specific lives they have touched. Use qualitative data to show them their impact.",
            "**Ethics:** Allow space to voice moral concerns. Do not shut down their ethical questions; validate them. Even if you cannot change the decision, acknowledging their moral struggle builds trust. They need to know their leader has a soul."
        ],
        "celebrate_bullets": [
            "**Integrity:** Celebrate moments where they made a hard choice because it was the right thing to do.",
            "**Advocacy:** Celebrate when they gave a voice to the voiceless.",
            "**Consistency:** Celebrate their unwavering commitment to care."
        ],
        "celebrate_deep_dive": "**Recognition Language: Mission & Values.**\nConnect their work to the human story. Show them the invisible impact on the child's life. \n\n*Script:* 'Because you stayed late to talk to that youth, they felt safe enough to sleep tonight. You are the reason this program works.'"
    },
    "Connection": {
        "bullets": [
            "**Belonging:** They view the team as a family. Their primary goal is to ensure everyone feels they belong. They are the first to welcome new hires and the last to leave a party. They define success by the tightness of the circle.",
            "**Harmony:** They are sensitive to tension and will absorb it to protect others. A fight on the unit ruins their entire day. They want everyone to get along, but unlike the Peacemaker, they will fight to impose peace if necessary.",
            "**Support:** They are motivated by helping peers. They will stay late to help a coworker even if their own work is done. They see service to the team as their primary job description."
        ],
        "strategies_bullets": [
            "**Face Time:** Prioritize in-person check-ins. They value the relationship with you more than the tasks you assign. A text message is okay, but a face-to-face conversation is gold. They need to see your eyes to trust you.",
            "**Team Rituals:** Encourage meals, huddles, and traditions. Give them the space to create culture. They thrive when the team has a shared identity and shared experiences.",
            "**Personal Care:** Ask about life outside work. They bring their whole self to work and expect you to care about it. Knowing their kids' names or their hobbies matters deeply to them."
        ],
        "celebrate_bullets": [
            "**Loyalty:** Celebrate their standing up for the team.",
            "**Stabilization:** Celebrate their physical presence calming a room.",
            "**Culture:** Celebrate the strong identity of the unit. Praise the low turnover or the high morale."
        ],
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
        "synergy": "Social Cohesion. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy.",
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
        ]
    },
    "Director-Growth": {
        "stress_sig": "**The 'Intellectual Bully' Mode.**\nThey become hyper-critical of others' ideas. They may roll their eyes or sigh when staff don't understand concepts quickly. They withdraw from 'low-level' tasks.",
        "root_cause": "**Fear of Stagnation.**\nThey need to feel like they are advancing. When stuck in routine or surrounded by 'slow' learners, they feel trapped, triggering disdain.",
        "prescription": [
            "**The 'Brain Candy':** Assign them a complex, unsolved problem (e.g., 'Figure out why the 3rd shift schedule keeps breaking').",
            "**Autonomy Check:** Ask 'Where do you feel micromanaged?' and back off in that area.",
            "**Future Focus:** Spend 5 minutes talking about their career path, not just the current crisis."
        ]
    },
    "Director-Purpose": {
        "stress_sig": "**The 'Righteous Crusader' Mode.**\nThey become moralistic and judgmental. They frame every disagreement as 'You don't care about the kids.' They may violate policy to 'do the right thing.'",
        "root_cause": "**Fear of Betrayal (of the Mission).**\nThey view efficiency and rules as secondary to the mission. When the system blocks the mission, they view the system as the enemy.",
        "prescription": [
            "**Validate the Anger:** Say, 'You are right, it is unfair that we can't do X.' Align with their heart before correcting their method.",
            "**Connect Rule to Mission:** Explain how the policy actually *protects* the child long-term.",
            "**Give a Mission Win:** Share a specific story of how their leadership helped a youth recently."
        ]
    },
    "Director-Connection": {
        "stress_sig": "**The 'Mama Bear' Mode.**\nThey become fiercely protective of their team, attacking outsiders (including you) who critique them. They hide their team's mistakes to 'keep them safe.'",
        "root_cause": "**Fear of Harm to the Tribe.**\nThey see themselves as the shield. Stress makes them tighten the perimeter. They view accountability as an attack.",
        "prescription": [
            "**Reassure Safety:** Explicitly state, 'I am not here to fire anyone. I want to help them.'",
            "**Support the Leader:** Ask 'How are YOU doing?' before asking about the team. They rarely get asked.",
            "**Unified Front:** Show them that you are on their side against the chaos, not against them."
        ]
    },
    "Encourager-Achievement": {
        "stress_sig": "**The 'Over-Promiser' Mode.**\nThey say 'yes' to everything to please everyone, become manic/scattered, and then crash when they drop balls. They hide failures with toxic positivity.",
        "root_cause": "**Fear of Disappointing Others.**\nThey equate 'winning' with 'making everyone happy.' They can't prioritize because every 'no' feels like a failure.",
        "prescription": [
            "**The 'No' Permission:** Explicitly take things off their plate. 'You are not allowed to do X this week.'",
            "**Visual Scoreboard:** Show them they are winning in specific areas so they stop trying to win everywhere.",
            "** celebrate Limits:** Praise them when they set a boundary."
        ]
    },
    "Encourager-Growth": {
        "stress_sig": "**The 'Shiny Object' Mode.**\nThey start 10 new initiatives and finish none. They become bored with routine and detach from daily grind tasks. They avoid deep work.",
        "root_cause": "**Fear of Boredom.**\nThey run on dopamine and novelty. When the work gets hard or boring, they seek a new 'fun' idea to escape.",
        "prescription": [
            "**One Thing Rule:** 'You cannot start project B until project A is 100% finished.'",
            "**Gamify the Boring:** Turn routine tasks into a challenge or game.",
            "** mentorship:** Have them teach a skill to a new hire. The social aspect of teaching makes the boring content fun again."
        ]
    },
    "Encourager-Purpose": {
        "stress_sig": "**The 'Emotional Flood' Mode.**\nThey take client trauma home. They cry easily or become irrationally angry at 'the system.' They burn out from compassion fatigue.",
        "root_cause": "**Fear of Helplessness.**\nThey feel the pain of the world and feel powerless to stop it. This leads to overwhelming despair.",
        "prescription": [
            "**Mandatory Decompression:** Order them to take a break/leave early after a crisis.",
            "**The 'Good Enough' Speech:** Remind them that their presence is the intervention, not the cure.",
            "**Success Stories:** Force them to list 3 things that went *right* today to rebalance their perspective."
        ]
    },
    "Encourager-Connection": {
        "stress_sig": "**The 'Gossip' Mode.**\nThey vent inappropriately to peers instead of managing up. They form cliques. They avoid conflict to the point of negligence.",
        "root_cause": "**Fear of Rejection.**\nStress makes them seek alliance and validation. They prioritize feeling 'in' over doing 'right.'",
        "prescription": [
            "**Structure the Venting:** Give them 5 minutes to vent to *you* so they don't do it to the team.",
            "**Social Time:** Schedule a team lunch or coffee. Feed the need for connection healthily.",
            "**Direct Reassurance:** Tell them, 'I value you,' so they don't have to fish for it."
        ]
    },
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "stress_sig": "**The 'Analysis Paralysis' Mode.**\nThey stall endlessly, asking for more data or 'one more meeting' to ensure the decision is perfect. They refuse to commit.",
        "root_cause": "**Fear of Being Wrong.**\nThey want to achieve the goal (Achievement) but want everyone to agree (Facilitator). The tension freezes them.",
        "prescription": [
            "**The 'Good Enough' Call:** Tell them, 'We are going with Option B. I am making the call.' Absolve them of the risk.",
            "**Deadlines:** Set tight, artificial deadlines to force action.",
            "**Focus on Progress:** Praise the *step* taken, not just the final result."
        ]
    },
    "Facilitator-Growth": {
        "stress_sig": "**The 'Academic' Mode.**\nThey retreat into theory. They want to discuss the 'philosophy of care' while the unit is in chaos. They avoid the messy reality of the floor.",
        "root_cause": "**Fear of Incompetence.**\nThey feel overwhelmed by the chaos, so they retreat to the intellectual world where they feel safe and competent.",
        "prescription": [
            "**Concrete Tasks:** Give them a physical task (e.g., 'Organize the supply closet') to get them out of their head.",
            "**Time-Boxed Discussion:** 'We have 5 minutes to discuss theory, then we act.'",
            "**Validate Wisdom:** Ask for their insight, then ask them to apply it immediately."
        ]
    },
    "Facilitator-Purpose": {
        "stress_sig": "**The 'Moral Gridlock' Mode.**\nThey refuse to choose between two bad options (e.g., calling police vs. unsafe unit). They freeze because neither option feels 'right.'",
        "root_cause": "**Fear of Compromising Values.**\nThey see the gray area as a moral failing. They want a pure solution that doesn't exist.",
        "prescription": [
            "**The 'Least Bad' Frame:** Reframe the decision: 'Option A is the least harmful path. Taking it is the moral choice.'",
            "**Shared Burden:** 'We are making this decision together. You are not alone in this.'",
            "**Focus on Intent:** Remind them that their heart is in the right place."
        ]
    },
    "Facilitator-Connection": {
        "stress_sig": "**The 'Hiding' Mode.**\nThey physically disappear (office door closed, busy work) to avoid the tension on the floor. They refuse to give bad news.",
        "root_cause": "**Fear of Conflict.**\nStress makes them terrified of upsetting anyone. They withdraw to protect themselves from negative emotion.",
        "prescription": [
            "**Joint Leadership:** 'Let's go talk to the team together.' Don't make them do it alone.",
            "**Scripting:** Write down exactly what they need to say so they don't have to improvise.",
            "**Safe Space:** Ask 'What are you afraid will happen if you speak up?'"
        ]
    },
    "Tracker-Achievement": {
        "stress_sig": "**The 'Micro-Manager' Mode.**\nThey obsess over formatting, minor rules, and tiny details. They redo others' work because 'it wasn't right.'",
        "root_cause": "**Fear of Loss of Control.**\nWhen stressed, they try to control the only thing they can: the details. It gives them a false sense of safety.",
        "prescription": [
            "**Define 'Done':** Explicitly state what 'good enough' looks like. Stop them from polishing.",
            "**Assign 'Big' Goals:** Redirect their drive to a larger project so they stop nitpicking.",
            "**Mandatory Handoff:** Force them to delegate a task and *not* check it."
        ]
    },
    "Tracker-Growth": {
        "stress_sig": "**The 'Superiority' Mode.**\nThey hoard information and act condescending to those who don't know the rules. 'I guess I have to do everything.'",
        "root_cause": "**Fear of Dependency.**\nThey feel unsafe relying on 'incompetent' people. They protect themselves by proving they are the smartest in the room.",
        "prescription": [
            "**The 'Teacher' Role:** Ask them to train the team. Turn their hoarding into sharing.",
            "**Acknowledge Expertise:** Publicly validate their knowledge so they don't feel the need to prove it.",
            "**Challenge with Ambiguity:** Give them a problem that has no rulebook answer to force flexibility."
        ]
    },
    "Tracker-Purpose": {
        "stress_sig": "**The 'Policy Police' Mode.**\nThey weaponize the rules to stop work. 'We can't do that, it's against regulation 4.2.' They block progress.",
        "root_cause": "**Fear of Catastrophe.**\nThey believe that one slip-up will destroy the agency/mission. Rules are their safety blanket against disaster.",
        "prescription": [
            "**Risk Assessment:** Ask 'What is the actual likelihood of that bad thing happening?' Help them calibrate.",
            "**Safe Exceptions:** 'I am authorizing this exception. I will sign off on it.' Taking the liability removes their fear.",
            "**Connect Rule to Why:** Explain the spirit of the law, not just the letter."
        ]
    },
    "Tracker-Connection": {
        "stress_sig": "**The 'Silent Martyr' Mode.**\nThey do all the grunt work silently, then seethe with resentment when no one notices. Passive-aggressive sighs.",
        "root_cause": "**Fear of Being Unappreciated.**\nThey want to be helpful but feel invisible. They work harder to get noticed, then resent the work.",
        "prescription": [
            "**Public Visibility:** Praise their specific work in front of the team. 'Thank you for organizing that.'",
            "**Role Clarity:** Tell them exactly what is *not* their job so they stop over-functioning.",
            "**Ask for Voice:** 'You've been quiet. What are you seeing that we are missing?'"
        ]
    }
}

# --- PLACEHOLDERS FOR MISSING DATA ---
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Director": {
            "tension": "Power Struggle (Control vs. Control)",
            "psychology": "When two Directors clash, it's a battle for dominance. Both value speed, autonomy, and being 'right.' The conflict usually isn't personal; it's structural.",
            "watch_fors": ["**The Public Showdown:** Arguing in front of the team to establish who is 'Alpha'.", "**Malicious Compliance:** 'Fine, I'll do it your way, but I'll watch it fail.'", "**Siloing:** Dividing the team into 'My Crew' vs. 'Your Crew'."],
            "intervention_steps": ["**1. Define Swim Lanes:** Explicitly divide the turf.", "**2. The 'Disagree and Commit' Pact:** Agree to back each other in public.", "**3. Scheduled Friction:** Set a weekly meeting to debate strategy behind closed doors."],
            "scripts": {
                "Opening": "**Script:** \"We are both strong leaders, but right now we are canceling each other out. We need to align forces instead of colliding.\"\n\n**Rationale:** Acknowledges their power immediately to prevent a status battle. Framing it as 'canceling out' highlights the inefficiency, which Directors hate.",
                "Validation": "**Script:** \"I respect your drive and your need for autonomy. I know you want the best for this program and you want it done fast.\"\n\n**Rationale:** Validates their core intent (speed and impact) so they don't feel the need to defend their motives.",
                "The Pivot": "**Script:** \"When we battle for control, we create confusion for the team. We need to stop competing for authority and start coordinating our attacks on the problem.\"\n\n**Rationale:** Shifts the opponent from 'You' to 'The Problem.' Directors will unite against a common enemy (confusion).",
                "Crisis": "**Script:** \"We don't have time for a power struggle. In this specific instance, I need you to execute my play. We can debrief the strategy later.\"\n\n**Rationale:** Appeals to urgency. Uses command language ('execute my play') which Directors respect in emergencies.",
                "Feedback": "**Script:** \"I need you to trust me to handle my lane. When you step in without asking, it undermines my authority, not just the task.\"\n\n**Rationale:** Defines the boundary in terms of authority and trust, which are the currencies Directors trade in."
            }
        },
        "Encourager": {
            "tension": "Efficiency vs. Empathy (Safety as Control vs. Safety as Connection)",
            "psychology": "You (Director) find safety in speed and checking boxes. They (Encourager) find safety in connection and harmony. You view 'feelings' as distractions; they view them as the work. They feel steamrolled by your brevity; you feel slowed down by their need to chat.",
            "watch_fors": ["**The 'Shut Down':** They go silent to protect themselves from your intensity.", "**The 'Smile & Nod':** They agree to a deadline they can't meet just to end the interaction.", "**Venting:** They process their hurt feelings with peers."],
            "intervention_steps": ["**1. Disarm the Threat:** Lower your volume. Start with the person, not the task.", "**2. Translate Intent:** State that your intensity is about the *problem*, not them.", "**3. The 'Sandwich' Reframe:** They need the relational affirmation to hear the feedback."],
            "scripts": {
                "Opening": "**Script:** \"I want to talk about the task, but I sense some hesitation. How are you doing with this assignment?\"\n\n**Rationale:** Forces the Director to pause and check the 'human gauge.' Encouragers need to feel seen before they can work.",
                "Validation": "**Script:** \"I know my style can feel intense or abrupt. I value your connection with the team and how much you care about the vibe.\"\n\n**Rationale:** The Supervisor owns their own intensity (disarming the threat) and validates the Encourager's superpower (connection).",
                "The Pivot": "**Script:** \"However, we need to solve this problem efficiently. My directness is about fixing the issue quickly, not about being upset with you.\"\n\n**Rationale:** Clarifies intent. Encouragers often mistake speed for anger. This separates the task from the relationship.",
                "Crisis": "**Script:** \"I need to be very direct right now because of the safety risk. It isn't personal, it's operational. Please trust my intent.\"\n\n**Rationale:** Pre-frames the intensity as safety-driven, protecting the relationship from the upcoming command.",
                "Feedback": "**Script:** \"I value you. To grow, I need you to hear hard news without feeling attacked. Can we separate the 'what' from the 'who' for a moment?\"\n\n**Rationale:** Encouragers conflate performance with identity. This script explicitly asks them to separate the two."
            }
        },
        "Facilitator": {
            "tension": "Speed vs. Process (Urgency vs. Fairness)",
            "psychology": "You (Director) value 'Done'. They (Facilitator) value 'Fair'. You see their desire for consensus as 'Analysis Paralysis'. They see your quick decisions as reckless. You fight for results; they fight for legitimacy.",
            "watch_fors": ["**The 'We Need to Talk':** They schedule meetings to delay decisions.", "**Passive Resistance:** They won't argue, but they won't execute the plan.", "**Moral High Ground:** They frame your speed as 'uncaring'."],
            "intervention_steps": ["**1. Define the Sandbox:** Give them a clear deadline (e.g., 'Decide by 3 PM').", "**2. Assign the 'Who':** Limit who they need to consult.", "**3. The 'Good Enough' Agreement:** Remind them a good decision today is better than a perfect one next week."],
            "scripts": {
                "Opening": "**Script:** \"I know this feels rushed and you want more time to process. I want to respect that need.\"\n\n**Rationale:** Validates the Facilitator's need for process, preventing them from digging in their heels.",
                "Validation": "**Script:** \"I value that you want everyone to be heard and that you are thinking about the long-term impact.\"\n\n**Rationale:** Acknowledges that their hesitation comes from wisdom/care, not laziness.",
                "The Pivot": "**Script:** \"The risk is that if we don't decide by noon, we lose the option entirely. We have to prioritize speed over consensus right now.\"\n\n**Rationale:** Reframes 'speed' as a necessity to save the option. Appeals to the risk of doing nothing.",
                "Crisis": "**Script:** \"In this moment, the time for debate has passed. I have to make the call to keep us safe. Please follow my lead.\"\n\n**Rationale:** Sets a hard boundary. Facilitators respect safety; framing the command as a safety necessity overrides their need for consensus.",
                "Feedback": "**Script:** \"Your desire for consensus is a strength, but sometimes it becomes a bottleneck. I need you to be willing to make a call even if people aren't 100% happy.\"\n\n**Rationale:** Identifies the specific behavior (bottlenecking) while affirming the intent (consensus)."
            }
        },
        "Tracker": {
            "tension": "Innovation vs. Compliance (Change vs. Safety)",
            "psychology": "You (Director) want to break the status quo to get results. They (Tracker) want to protect the status quo to ensure safety. You see them as the 'Department of No.' They see you as a liability.",
            "watch_fors": ["**The Rulebook Defense:** Quoting policy to stop new ideas.", "**The 'Yes, But':** Finding 10 reasons why it will fail.", "**Anxiety:** Your speed makes them visibly nervous."],
            "intervention_steps": ["**1. The Pre-Mortem:** Ask them to list the risks, then solve them together.", "**2. Honor the Detail:** Do not dismiss their accuracy.", "**3. Trial Runs:** Frame changes as temporary experiments."],
            "scripts": {
                "Opening": "**Script:** \"I have a new idea, and I need your eyes on it to make sure it's safe before we launch.\"\n\n**Rationale:** Invites the Tracker in as an expert rather than an obstacle. Gives them a specific role (safety check).",
                "Validation": "**Script:** \"I appreciate your attention to detail. You keep us compliant and prevent me from making reckless mistakes.\"\n\n**Rationale:** Validates their anxiety (fear of mistakes) and frames it as a value-add.",
                "The Pivot": "**Script:** \"We need to find a way to make this work, not just reasons why it won't. How can we do this safely, rather than just saying 'no'?\"\n\n**Rationale:** Shifts them from 'Blocker' mode to 'Problem Solver' mode.",
                "Crisis": "**Script:** \"I am taking full responsibility for this decision. I need you to trust me on the risk assessment right now.\"\n\n**Rationale:** Trackers fear getting in trouble. Taking full responsibility alleviates their anxiety.",
                "Feedback": "**Script:** \"I need you to help me find the 'Yes.' Don't just tell me why we can't do it; tell me what it would take to make it possible.\"\n\n**Rationale:** Coaches them to use their knowledge to enable the mission, not just protect the policy."
            }
        }
    },
    "Encourager": {
        "Encourager": {
            "tension": "Artificial Harmony (Nice vs. Nice)",
            "psychology": "The vibe is amazing, but accountability is low. You both value harmony so much that you avoid hard conversations. Issues fester underground. You become 'Toxic Protectors,' shielding the team from reality.",
            "watch_fors": ["**The Vent Session:** Complaining without action.", "**The 'Reply All' Apology:** Apologizing for enforcing rules.", "**Ghosting:** Avoiding staff rather than correcting them."],
            "intervention_steps": ["**1. The 'Safety' Contract:** Agree that giving feedback is safe.", "**2. Assign the 'Bad Guy':** Rotate who delivers bad news.", "**3. Focus on the Victim:** Remind each other of the youth suffering due to lack of structure."],
            "scripts": {
                "Opening": "**Script:** \"I hate having this conversation because I value our friendship, but we need to talk about the work.\"\n\n**Rationale:** Acknowledges the awkwardness (which is the elephant in the room) to clear the air.",
                "Validation": "**Script:** \"I know we both want the team to be happy and for the vibe to be good.\"\n\n**Rationale:** Reaffirms shared values so the feedback doesn't feel like a betrayal.",
                "The Pivot": "**Script:** \"But by not addressing this performance issue, we are actually hurting the team. We are letting the standards slip, which isn't fair to the hard workers.\"\n\n**Rationale:** Reframes 'accountability' as an act of care for the *rest* of the team.",
                "Crisis": "**Script:** \"We can't hug our way out of this. We have to be firm or safety will be compromised.\"\n\n**Rationale:** A stark reality check that 'nice' is not the right tool for 'safe'.",
                "Feedback": "**Script:** \"I feel like we are dancing around the issue to be nice. Let's just say it directly so we can fix it and move on.\"\n\n**Rationale:** Calls out the 'nice trap' explicitly and invites directness."
            }
        },
        "Director": {
            "tension": "Warmth vs. Competence (Being Liked vs. Being Effective)",
            "psychology": "You (Encourager) interpret their brevity as anger. They (Director) interpret your need for chat as incompetence or padding. You feel unsafe; they feel slowed down.",
            "watch_fors": ["**Apologizing:** You apologizing for giving them work.", "**Taking it Personally:** Feeling hurt by their directness.", "**Avoidance:** Emailing instead of talking to avoid the friction."],
            "intervention_steps": ["**1. Cut the Fluff:** Start with the headline.", "**2. Stand Your Ground:** If they push back, state your reasoning calmly.", "**3. Ask for Input:** Frame the relationship issue as a problem to be solved."],
            "scripts": {
                "Opening": "**Script:** \"I'm going to get straight to the point because I know you value efficiency.\"\n\n**Rationale:** Signals that you respect their time, which gains their attention immediately.",
                "Validation": "**Script:** \"I know you are focused on getting this done and you want results.\"\n\n**Rationale:** Validates their driver (Achievement) so they don't dismiss you as 'soft'.",
                "The Pivot": "**Script:** \"However, the way you spoke to the team caused a shutdown. You got the task done, but you damaged the relationship we need for next time.\"\n\n**Rationale:** Frames the 'feelings' issue as a pragmatic 'effectiveness' issue. Directors listen to effectiveness.",
                "Crisis": "**Script:** \"Stop. Listen to me. This is a safety issue and I need you to hear me.\"\n\n**Rationale:** Uses short, command-style sentences. Matches their energy intensity.",
                "Feedback": "**Script:** \"You are right on the facts, but wrong on the approach. If they don't trust you, they won't follow you next time.\"\n\n**Rationale:** Shows them that their 'winning' style is actually 'losing' the team."
            }
        },
        "Facilitator": {
            "tension": "Energy Mismatch (Vibes vs. Process)",
            "psychology": "You (Encourager) want enthusiasm and connection. They (Facilitator) want calm and structure. You feel they are disengaged or low-energy. They feel you are chaotic and exhausting.",
            "watch_fors": ["**Withdrawal:** They stop talking to escape your high energy.", "**Over-Talking:** You talk to fill the silence, making them withdraw further.", "**Misinterpretation:** You think their quietness means they are mad."],
            "intervention_steps": ["**1. Slow Down:** Match their energy level. Lower your volume.", "**2. Ask Specifics:** Don't ask 'How are you feeling?' Ask 'What do you think about X?'", "**3. Respect the Pause:** Wait 5 seconds after asking a question."],
            "scripts": {
                "Opening": "**Script:** \"I want to slow down and hear your thoughts. I feel like I've been doing all the talking.\"\n\n**Rationale:** Signals a shift in energy. Gives them permission to enter the conversation.",
                "Validation": "**Script:** \"I know I bring a lot of energy to the room and that can be overwhelming.\"\n\n**Rationale:** Owns the dynamic so the Facilitator doesn't feel responsible for the disconnect.",
                "The Pivot": "**Script:** \"I need you to tell me if I'm moving too fast or missing a detail. Your silence makes me nervous—I need to know what you are really thinking.\"\n\n**Rationale:** Vulnerability. Admitting their silence makes you nervous invites them to help you by speaking.",
                "Crisis": "**Script:** \"I need you to speak up right now, even if you aren't 100% sure. I need your gut check.\"\n\n**Rationale:** Lowers the bar for entry. They don't need a perfect answer, just a gut check.",
                "Feedback": "**Script:** \"When you go silent, I feel like you are checking out. I need your voice in the room, not just your presence.\"\n\n**Rationale:** Frames their silence as a lack of connection, which motivates the Facilitator to re-engage."
            }
        },
        "Tracker": {
            "tension": "Order vs. Chaos (Flexibility vs. Rules)",
            "psychology": "You (Encourager) prioritize morale and exceptions. They (Tracker) prioritize the rulebook. You feel nitpicked and controlled. They feel unsafe because you are 'loose' with the rules.",
            "watch_fors": ["**The Email Audit:** They send you long lists of errors.", "**Ignoring Details:** You stop reading their emails because they are 'negative'.", "**Passive-Aggression:** They follow your 'bad' instructions maliciously."],
            "intervention_steps": ["**1. Honor the Rule:** Start by agreeing the rule is important.", "**2. Frame the Exception:** Explain that you are bending the rule for a *person*, not because you are lazy.", "**3. Ask for Help:** Ask them to help you organize the chaos."],
            "scripts": {
                "Opening": "**Script:** \"I know this looks messy to you and you're worried about the procedure.\"\n\n**Rationale:** Validates their anxiety about disorder immediately.",
                "Validation": "**Script:** \"I value that you keep us compliant and safe. I know the rules matter.\"\n\n**Rationale:** Affirms their role as protector, reducing their need to fight you.",
                "The Pivot": "**Script:** \"In this moment, I need to prioritize the relationship over the paperwork. We will fix the form, but first we have to fix the trust.\"\n\n**Rationale:** Explains the hierarchy of needs. Relationship > Paperwork (in this moment).",
                "Crisis": "**Script:** \"We will fix the form later. Right now, handle the kid. The relationship is the intervention.\"\n\n**Rationale:** Gives them permission to let go of the rule by defining the new priority.",
                "Feedback": "**Script:** \"I need you to be flexible without feeling like we are breaking the law. Sometimes the right thing to do isn't in the handbook.\"\n\n**Rationale:** Challenges their rigid thinking by appealing to a higher moral purpose."
            }
        }
    },
    "Facilitator": {
        "Facilitator": {
            "tension": "Process Paralysis (Talk vs. Talk)",
            "psychology": "The infinite loop. You both want to make sure everyone is heard. You both dislike polarization. The result is meetings that never end and decisions that never happen.",
            "watch_fors": ["**The 'Let's Circle Back':** Delaying decisions.", "**The Meeting About the Meeting:** Planning to plan.", "**Consensus Addiction:** Refusing to move without 100% agreement."],
            "intervention_steps": ["**1. The 'Shot Clock':** Set a timer for the decision.", "**2. Limit Input:** Agree to only consult 2 people, not everyone.", "**3. The 'Good Enough' Pact:** Agree that 80% certainty is enough."],
            "scripts": {
                "Opening": "**Script:** \"We are over-thinking this and spinning in circles.\"\n\n**Rationale:** Naming the dynamic breaks the loop. Someone has to call it out.",
                "Validation": "**Script:** \"I value that we are being thorough and want everyone on board.\"\n\n**Rationale:** Validates the intent so they don't feel guilty about moving fast.",
                "The Pivot": "**Script:** \"But we are stuck. We need to pick a direction even if it isn't perfect. Doing nothing is becoming a decision itself.\"\n\n**Rationale:** Reframes inaction as a risky decision. Facilitators dislike risk.",
                "Crisis": "**Script:** \"Process is over. I am making the call. We can debrief the feelings later.\"\n\n**Rationale:** Takes the burden of the decision off the peer. 'I am making the call' frees them.",
                "Feedback": "**Script:** \"We need to stop asking for permission and start giving direction. The team is waiting for us to lead.\"\n\n**Rationale:** Reminds them of their responsibility to the team, which motivates them."
            }
        },
        "Director": {
            "tension": "Pace Mismatch (Consensus vs. Action)",
            "psychology": "You (Facilitator) want to talk it out. They (Director) want to get it done. You feel steamrolled and disrespected. They feel slowed down and frustrated by 'pointless' discussion.",
            "watch_fors": ["**Going Rogue:** They act without your permission to 'save time'.", "**Tuning Out:** They stop listening in meetings.", "**The Takeover:** They start running your meeting because you are 'too slow'."],
            "intervention_steps": ["**1. Bottom Line Up Front:** Start with the decision, then discuss.", "**2. Give Autonomy:** Define the goal and let them run.", "**3. Be Firm:** Do not let them interrupt the process if the process is necessary."],
            "scripts": {
                "Opening": "**Script:** \"I know you want to move fast and just get this done.\"\n\n**Rationale:** Validates the Director's drive, showing you aren't oblivious to the clock.",
                "Validation": "**Script:** \"I appreciate your bias for action. You drive us forward.\"\n\n**Rationale:** Frames their impatience as a positive trait (drive).",
                "The Pivot": "**Script:** \"However, we need to align the team first or we will crash. If we don't get buy-in now, we will pay for it later with resistance.\"\n\n**Rationale:** Uses a pragmatic argument: 'Speed now = Crash later.' Directors hate crashing.",
                "Crisis": "**Script:** \"I hear you. But the decision is X. We are moving.\"\n\n**Rationale:** Matching their directness. Short sentences signal authority.",
                "Feedback": "**Script:** \"You are moving faster than the team can follow. Slow down to speed up. If you lose them, you aren't leading, you're just walking alone.\"\n\n**Rationale:** Hits them where it hurts: Ineffectiveness. Walking alone is failed leadership."
            }
        },
        "Encourager": {
            "tension": "Fairness vs. Favor (Process vs. Vibe)",
            "psychology": "You (Facilitator) try to create a fair system where everyone is treated equally. They (Encourager) try to create a happy family where everyone feels liked. You clash when you try to enforce a rule for equity, and they try to bend it to save a relationship. You view them as playing favorites; they view you as cold or bureaucratic.",
            "watch_fors": [
                "**The 'Nice' Trap:** You both avoid conflict, so performance issues are ignored until they explode.",
                "**The Talk Loop:** You listen to gather perspective; they talk to process. Meetings run overtime with no action items.",
                "**Vibe over Fact:** They sell you an optimistic story ('It's going great!'). You want to believe the team is aligned, so you don't dig for the data."
            ],
            "intervention_steps": [
                "**1. Data over Feeling:** They speak in generalities. You must force them to bring specific numbers/facts to supervision.",
                "**2. The 'Bad Guy' Agreement:** You both struggle to be the enforcer. Explicitly agree on who delivers the bad news so you don't both ghost the issue.",
                "**3. Written Action Items:** They forget details after the emotion fades. You value process. End every meeting with a written list of tasks."
            ],
            "scripts": {
                "Opening": "**Script:** \"I love the energy you bring, but we need to look at the numbers and the plan.\"\n\n**Rationale:** Separation of 'Energy' and 'Plan.' You validate the person but pivot to the task.",
                "Validation": "**Script:** \"I know you want to protect the team's morale and keep everyone happy.\"\n\n**Rationale:** Validates their motive so they don't feel 'caught' avoiding the work.",
                "The Pivot": "**Script:** \"But by letting this slide, we are being unfair to the staff who follow the rules. Fairness means holding everyone to the same standard.\"\n\n**Rationale:** Appeals to the Facilitator's core value: Fairness. Playing favorites is unfair.",
                "Crisis": "**Script:** \"We can't worry about feelings right now. We follow the protocol. Safety is the priority.\"\n\n**Rationale:** Externalizes the authority to the 'Protocol.' It makes the rule the bad guy, not you.",
                "Feedback": "**Script:** \"You are great at the relationship, but I need you to be better at the paperwork/follow-through. The team needs structure as much as they need love.\"\n\n**Rationale:** Frames structure as a form of care, which appeals to the Encourager."
            }
        },
        "Tracker": {
            "tension": "Consensus vs. Compliance (People vs. Policy)",
            "psychology": "You (Facilitator) want to talk it out. They (Tracker) want to get it done. You feel steamrolled and disrespected. They feel slowed down and frustrated by 'pointless' discussion.",
            "watch_fors": ["**The Policy War:** You quote the handbook; they quote 'team sentiment'.", "**Ignoring:** You ignoring their emails because they feel like nagging.", "**Anxiety:** They get anxious when you say 'let's just see how it goes'."],
            "intervention_steps": ["**1. Validate the Rule:** Acknowledge the policy first.", "**2. Contextualize the Exception:** Explain *why* this specific situation requires a bend.", "**3. Define the New Boundary:** Create a temporary rule so they feel safe."],
            "scripts": {
                "Opening": "**Script:** \"I know this plan deviates from SOP, and I want to explain why.\"\n\n**Rationale:** Heads off the objection immediately. Shows you know the rule exists.",
                "Validation": "**Script:** \"I appreciate you keeping us compliant. You are our safety net.\"\n\n**Rationale:** Defines their role as 'Safety Net' rather than 'Nag.'",
                "The Pivot": "**Script:** \"In this specific case, following the rule strictly will cause escalation. We need to look at the context, not just the text.\"\n\n**Rationale:** Introduces 'Context' as a variable that matters as much as the rule.",
                "Crisis": "**Script:** \"I am taking responsibility for this exception. Log it.\"\n\n**Rationale:** 'Log it' gives them a task and a way to protect themselves. 'Taking responsibility' removes their risk.",
                "Feedback": "**Script:** \"I need you to see the gray areas. Leadership happens in the exceptions.\"\n\n**Rationale:** Philosophically reframes leadership. Rules manage the norm; leaders manage the exception."
            }
        }
    },
    "Tracker": {
        "Tracker": {
            "tension": "The Micro-War (Detail vs. Detail)",
            "psychology": "It becomes a court case over the interpretation of a rule. You both dig into details to prove you are 'technically correct.' The team gets lost in the minutiae.",
            "watch_fors": ["**The Email War:** Sending evidence-filled emails instead of talking.", "**Malicious Audit:** Looking for errors in each other's work.", "**Stalemate:** Refusing to move until policy is clarified."],
            "intervention_steps": ["**1. Zoom Out:** Stop talking about the rule. Talk about the goal.", "**2. Pick a Lane:** Divide compliance tasks.", "**3. The 'Human Override':** Remind each other systems serve people."],
            "scripts": {
                "Opening": "**Script:** \"We are getting lost in the weeds and arguing over details.\"\n\n**Rationale:** Names the dynamic (The Weeds). Trackers hate inefficiency, and this argument is inefficient.",
                "Validation": "**Script:** \"I know we both want to do this exactly right.\"\n\n**Rationale:** Confirms shared intent (Accuracy). We are on the same side.",
                "The Pivot": "**Script:** \"Is this critical to safety, or just a preference? We are spending $100 of energy on a $10 problem.\"\n\n**Rationale:** Cost-Benefit Analysis. Trackers respond to logic and resource allocation.",
                "Crisis": "**Script:** \"The procedure doesn't matter right now. Safety matters. Drop the checklist and look at the situation.\"\n\n**Rationale:** Re-prioritizes the ultimate rule: Safety.",
                "Feedback": "**Script:** \"We need to stop using the rulebook as a weapon against each other.\"\n\n**Rationale:** A hard truth. Using rules to win an argument is weaponization, not leadership."
            }
        },
        "Director": {
            "tension": "Control vs. Autonomy (Rules vs. Results)",
            "psychology": "You (Tracker) want compliance and safety. They (Director) want speed and results. You try to rein them in with rules; they try to run past you. You view them as a loose cannon; they view you as a bottleneck.",
            "watch_fors": ["**Asking Forgiveness:** They do it their way and apologize later.", "**Over-Auditing:** You check their work excessively to 'catch' them.", "**Power Struggles:** Fighting over who has the final say on an SOP."],
            "intervention_steps": ["**1. The 'Why' Explanation:** Don't just say 'No.' Explain the specific risk.", "**2. Pick Your Battles:** Only fight them on safety/legal issues, not preferences.", "**3. Give Them a Lane:** Define where they have total freedom."],
            "scripts": {
                "Opening": "**Script:** \"I need to pump the brakes on this idea before we crash.\"\n\n**Rationale:** Uses driving metaphors ('pump the brakes') which imply speed/movement, speaking their language.",
                "Validation": "**Script:** \"I know you want to get this done fast and see results.\"\n\n**Rationale:** Validates their driver (Results).",
                "The Pivot": "**Script:** \"But if we skip this step, we risk a lawsuit/safety failure. I'm not trying to stop you; I'm trying to keep you safe.\"\n\n**Rationale:** Reframes 'Stopping' as 'Protecting.' Directors hate being stopped, but they like being safe.",
                "Crisis": "**Script:** \"Stop. This is a compliance violation. We cannot do this.\"\n\n**Rationale:** Hard stop. No fluff. Directors respect a hard wall if it's real.",
                "Feedback": "**Script:** \"I want to help you win, but you have to let me safety-check the plan first. Don't view me as an obstacle.\"\n\n**Rationale:** Explicitly asks to be viewed as an ally, not a bottleneck."
            }
        },
        "Encourager": {
            "tension": "Task vs. Relationship (Business vs. Social)",
            "psychology": "You (Tracker) focus on the error. They (Encourager) focus on the effort. You feel they are sloppy and unprofessional. They feel you are cold and mean. You speak data; they speak emotion.",
            "watch_fors": ["**Tears:** They cry or shut down when you give feedback.", "**The Silent Treatment:** They withdraw warmth to punish you.", "**The 'Nice' Defense:** They excuse errors because 'they tried hard'."],
            "intervention_steps": ["**1. Start with Warmth:** You must ask 'How are you?' before 'Here is the error.'", "**2. The Compliment Sandwich:** It feels fake to you, but it is necessary for them.", "**3. Focus on Support:** Frame the correction as 'helping them succeed.'"],
            "scripts": {
                "Opening": "**Script:** \"I want to help you get this right so you don't have to redo it later.\"\n\n**Rationale:** Frames the correction as 'Help,' not 'Punishment.'",
                "Validation": "**Script:** \"I know you are working hard for the team and you care about them.\"\n\n**Rationale:** Validates Effort. Trackers usually ignore effort if the result is wrong; you must acknowledge it here.",
                "The Pivot": "**Script:** \"However, this documentation error puts us at risk. Being 'nice' doesn't help if we lose funding.\"\n\n**Rationale:** Connects the boring detail (documentation) to the emotional outcome (losing funding/hurting the team).",
                "Crisis": "**Script:** \"I need you to focus on the details right now. Empathy won't fix this audit finding.\"\n\n**Rationale:** A reality check. Sometimes facts > feelings.",
                "Feedback": "**Script:** \"When you ignore the details, it makes more work for the team. True care includes accuracy.\"\n\n**Rationale:** Redefines 'Care.' If they care about the team, they should care about the details."
            }
        },
        "Facilitator": {
            "tension": "Rules vs. Context (Black & White vs. Gray)",
            "psychology": "You (Tracker) want to follow the book. They (Facilitator) want to consider the context and feelings of the group. You see them as wishy-washy and inconsistent. They see you as rigid and uncaring.",
            "watch_fors": ["**The Policy Debate:** You quote the handbook; they quote 'team sentiment'.", "**Stalled Decisions:** They won't enforce a rule because 'it's complicated'.", "**Frustration:** You feel like the only one holding the standard."],
            "intervention_steps": ["**1. Define the Hard Line:** Agree on which rules are non-negotiable.", "**2. Allow the Gray:** Agree on which rules are up for interpretation.", "**3. United Front:** Do not disagree on policy in front of staff."],
            "scripts": {
                "Opening": "**Script:** \"We need to be clear on the standard. Ambiguity is dangerous.\"\n\n**Rationale:** Trackers hate ambiguity. Stating that it is 'dangerous' appeals to the Facilitator's desire to protect the group.",
                "Validation": "**Script:** \"I know you want to be fair to everyone and hear all sides.\"\n\n**Rationale:** Validates their process (Fairness).",
                "The Pivot": "**Script:** \"But a rule that isn't enforced isn't a rule. If we make an exception every time, we don't have a policy.\"\n\n**Rationale:** Logical argument. Facilitators value systems; show them the system is breaking.",
                "Crisis": "**Script:** \"We follow the protocol. We can debrief feelings later.\"\n\n**Rationale:** Separates 'Action' from 'Processing.' Do the action now; process the feelings later.",
                "Feedback": "**Script:** \"I need you to back me up when I enforce the policy. Don't undermine the rules to keep the peace.\"\n\n**Rationale:** Direct request for support. Facilitators want to be supportive; tell them how."
            }
        }
    }
}

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "**From 'Individual Hero' to 'Orchestra Conductor':** This transition requires a fundamental rewiring of how you define value. As a YDP, you were the MVP—the fastest, strongest problem solver who could dive into any chaos and fix it. Your worth was tied to your personal output. As a Supervisor, your 'hero' instincts are now a liability. If you dive in, you leave the team without a leader. You must shift from being the player who scores the points to the coach who designs the plays. This means suppressing the urge to 'just do it myself' and instead investing energy into directing, observing, and correcting others. Your new win condition is not 'I fixed it,' but 'The team fixed it because I guided them.'",
            "why": "This is an identity crisis. As a YDP, the Director was valued for their speed, their ability to put out fires, and their 'do it myself' competence. They were the MVP player. Now, as a supervisor, their job is to stay on the sidelines and call the plays. They often feel useless when they aren't physically doing the work. They fear that if they don't step in, the team will fail or be too slow. This anxiety drives them to micromanage or 'rescue' the team, which stunts the team's growth and leads to supervisor burnout.",
            "conversation": "**The 'Hands in Pockets' Talk:**\n\n'Your value has changed. Yesterday, I paid you to be the fastest runner on the field. Today, I am paying you to make sure everyone else knows where to run. \n\nEvery time you jump in to fix a problem for a staff member, you are stealing a learning opportunity from them. You are teaching them that they don't need to be competent because you will save them. \n\nI need you to practice 'strategic patience.' Watch them struggle for 30 seconds before you intervene. Guide them with questions ('What do you think we should do?'), not commands. Your goal is to make yourself unnecessary.'",
            "assignment_setup": "This assignment is designed to force the Director to lead through influence rather than action. It removes their ability to use their physical competence as a crutch.",
            "assignment_task": "**The 'Chair' Challenge:**\nFor one hour during a busy shift, you must sit in a chair in the hallway or dayroom. You are not allowed to physically intervene in any routine task (chores, transitions, minor conflicts) unless there is an imminent safety threat.\n\nYou must direct the team verbally from your chair. If a staff member asks 'What should I do?', you must answer with a question: 'What is your plan?'",
            "success_indicators": "1. The Supervisor remained in the chair for the full hour.\n2. The team successfully completed routine tasks without the Supervisor doing them.\n3. The Supervisor used coaching questions instead of barking orders.\n4. The Supervisor remained calm even when things were done slower than they would have done them.",
            "red_flags": "1. They jumped up to 'fix' a minor issue (e.g., a messy table).\n2. They shouted orders across the room instead of coaching.\n3. The team stood around waiting for instructions instead of taking initiative.\n4. The Supervisor expressed visible frustration or anger at the team's speed.",
            "supervisor_focus": "Watch for their anxiety levels. Are they vibrating with the need to 'do'? Debrief that anxiety—it's the core of their development."
        },
        "Program Supervisor": {
            "shift": "**From 'Operational General' to 'Strategic Architect':** You have mastered the art of the daily grind, but the Program Supervisor role demands a longer horizon. You can no longer just fight today's battles; you must design the war strategy for next year. This shift requires you to stop prioritizing immediate efficiency over long-term health. You must learn to value the 'soft' work—culture building, emotional mentoring, and slow policy implementation—as much as the 'hard' work of audits and schedules. If you run the program like a machine, you will burn out the parts (your people). You must learn to be a gardener: preparing the soil, planting seeds, and waiting patiently for growth, rather than pulling on plants to make them grow faster.",
            "why": "Directors excel at execution. They love checking boxes and hitting daily targets. However, the Program Supervisor role requires long-term thinking, culture building, and developing people over months, not minutes. They struggle to see the value in 'soft' work like mentoring or culture building because it doesn't have an immediate, visible result. They risk running a highly efficient program that burns out staff because they treat people like parts of a machine.",
            "conversation": "**The 'Gardener' Analogy:**\n\n'You are excellent at building machines, but a team is a garden. You can't force a plant to grow faster by pulling on it. You have to create the right environment—soil, sun, water—and wait.\n\nYour job is no longer just to hit the metrics today. Your job is to build a team that can hit the metrics a year from now. This means you have to prioritize mentoring over doing. You have to tolerate short-term inefficiency for long-term growth. If you burn out your people to hit a number, you have failed.'",
            "assignment_setup": "This assignment forces the Director to slow down and focus entirely on another person's growth, removing the dopamine hit of 'getting things done' themselves.",
            "assignment_task": "**The Mentor Project:**\nSelect one high-potential but struggling staff member. Your goal is to teach them ONE specific administrative or leadership skill (e.g., running a shift debrief, auditing a file) over the course of two weeks.\n\nYou cannot do the task for them. You must meet with them, explain the 'why,' demonstrate the 'how,' and then observe them doing it, providing feedback. Your success is measured solely by *their* ability to do the task independently by Friday.",
            "success_indicators": "1. The staff member can perform the task independently and correctly.\n2. The staff member reports feeling supported, not judged.\n3. The Director can articulate the staff member's learning style and barriers.\n4. The Director spent significant time listening, not just talking.",
            "red_flags": "1. The Director just did the task for them to 'save time'.\n2. The staff member feels steamrolled or criticized.\n3. The Director complains that the staff member is 'too slow' or 'doesn't get it'.\n4. The Director cannot explain *why* the staff member struggled, only *that* they struggled."
        },
        "Manager": {
            "shift": "**From 'Battle Commander' to 'Diplomat & Strategist':** As a Program Supervisor, you led the troops. As a Manager, you lead the Generals. You can no longer rely on 'command and control' because your direct reports (Program Supervisors) are strong leaders who need autonomy. Your value shifts from 'solving the problem' to 'managing the politics and resources so *they* can solve the problem.' You must move from tactical execution to organizational strategy. You have to care about the agency's liability, public image, and budget as much as the kids. You must learn to lose small battles to win the war.",
            "why": "Directors want to fix the crisis *now*. At the Manager level, 'fixing it now' might cause a lawsuit or a budget crisis later. They struggle with the red tape and the indirect influence. They get frustrated that they can't just 'order' a Program Supervisor to change culture. They have to learn to influence through questions and vision, not just authority.",
            "conversation": "**The 'Chess Player' Talk:**\n\n'You are used to playing checkers—fast moves, jumping opponents, clear wins. Management is chess. You have to think five moves ahead.\n\nYour job is no longer to run the floor. Your job is to protect the agency so the floor can exist. This means you will spend less time with kids and more time with spreadsheets, lawyers, and angry parents. You have to be okay with not being the hero in the moment. You are the architect of the system.'",
            "assignment_setup": "This assignment forces them to solve a problem where 'speed' and 'command' are not the answers—where they must navigate complexity and competing interests.",
            "assignment_task": "**The Strategic Compromise:**\nIdentify a conflict between two Program Supervisors (e.g., resource sharing, staffing, or policy interpretation). Do not solve it for them.\n\nFacilitate a resolution where *both* sides feel heard and the solution serves the *agency*, not just one program. You cannot issue a directive. You must negotiate a treaty.",
            "success_indicators": "1. A resolution was reached that aligns with agency policy.\n2. Both Program Supervisors felt respected.\n3. The Director did not just 'pick a winner' based on who was faster/louder.\n4. They considered the long-term impact on agency culture.",
            "red_flags": "1. They just barked an order to end the conflict.\n2. They picked the side of the PS who is most like them (another Director).\n3. They ignored the emotional fallout of the decision.\n4. They complained that 'this is a waste of time'."
        },
        "Director": {
            "shift": "**From 'Strategist' to 'Enterprise Leader':** You now oversee a diverse ecosystem: AOBH, TIPS, EPIC, Student Advocates, and TSS. Each has a different language, funding stream, and culture. Your natural instinct is to 'run' the one you know best (likely Residential) and ignore the others. The shift requires you to govern the whole, not just your favorite part. You must resist the urge to step down into operations and instead focus on the 'connective tissue' between these departments. Your value is no longer in running a program; it is in creating synergy between programs.",
            "why": "Directors are used to being the expert in the room. Now they oversee areas (like EPIC or TIPS) where they may not be the subject matter expert. They often micromanage the Residential side because it feels safe, while neglecting the satellite programs. This leads to silos and 'forgotten' departments.",
            "conversation": "**The 'Portfolio Manager' Talk:**\n\n'You are not just the Residential Director anymore; you are the Director of Services. That means TIPS, EPIC, and Advocates are your children too.\n\nWhen you spend 80% of your time on AOBH because it's loud, you are neglecting the future growth of the agency. I need you to stop playing favorites with your time. You have to trust your Managers to run the units so you can build the bridges between them.'",
            "assignment_setup": "This assignment forces them to look at the agency horizontally (across departments) rather than vertically (down into the weeds).",
            "assignment_task": "**The Synergy Project:**\nIdentify a gap where two departments are not communicating (e.g., AOBH youth not utilizing EPIC services effectively). \n\nDesign a structural bridge—not just a meeting, but a process or policy—that forces collaboration between them. You must get the leaders of both divisions to agree to it.",
            "success_indicators": "1. The solution involved input from both 'silos'.\n2. They delegated the execution to the managers of those areas.\n3. They focused on the *system* of referral/hand-off, not just one case.\n4. They can articulate the value proposition for *both* departments.",
            "red_flags": "1. They just ordered AOBH to 'do more'.\n2. They ignored the unique constraints of TIPS/EPIC.\n3. They tried to run the meeting themselves instead of empowering the leaders.\n4. They viewed the satellite programs as 'lesser' than Residential."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "**From 'Best Friend' to 'Respected Leader':** This is the most emotionally taxing shift you will make. Your natural strength is connection, and you likely built your influence by being the person everyone feels safe with—the 'Best Friend.' Leadership requires you to trade some of that intimacy for respect. You must accept that you cannot be both their peer and their boss. The shift involves realizing that true kindness is not about keeping people happy in the moment; it is about holding them to a standard that keeps them employed and the youth safe. You must move from 'protecting feelings' to 'protecting the mission,' even if that means making your friends uncomfortable.",
            "why": "This is the hardest shift for an Encourager. Their primary motivation is Connection—they want to be liked and part of the tribe. Becoming a supervisor separates them from the peer group. They fear that if they give feedback or enforce rules, they will be rejected or seen as 'mean.' This leads to the 'Cool Parent' trap, where they let standards slide to buy affection, eventually losing the team's respect and safety.",
            "conversation": "**The 'Kindness vs. Niceness' Distinction:**\n\n'You are prioritizing being *nice* over being *kind*. \n\nBeing nice is about saving yourself from awkwardness. It's selfish. \nBeing kind is about telling someone the truth so they can be successful. It's selfless.\n\nWhen you let a peer break a rule because you don't want to upset them, you are setting them up to be fired by me later. That is not friendship. True care is holding them to a standard that keeps them employed and keeps kids safe. You have to be willing to be 'the bad guy' to be a good leader.'",
            "assignment_setup": "This assignment confronts the Encourager's biggest fear: direct conflict with a peer. It forces them to choose respect over popularity.",
            "assignment_task": "**The Audit & Feedback Loop:**\nChoose a peer who you are close with. Perform a strict audit of their documentation or shift duties. Find at least one meaningful error or area for improvement.\n\nYou must deliver this feedback face-to-face. You cannot sugarcoat it, joke about it, or blame management ('My boss is making me tell you this'). You must own the feedback: 'I noticed this, and I need you to fix it because it impacts safety.'",
            "success_indicators": "1. The feedback was direct, clear, and serious.\n2. The Encourager did not apologize for doing their job.\n3. The peer understood the expectation.\n4. The dynamic remained professional, even if awkward.",
            "red_flags": "1. The Encourager used the 'Feedback Sandwich' so heavily the point was lost.\n2. They blamed the policy on upper management to absolve themselves.\n3. They laughed or joked to break the tension.\n4. They avoided the conversation entirely and just fixed the error themselves.",
            "supervisor_focus": "Watch for the 'apology tour' afterwards. Ensure they sit in the discomfort of the boundary they just set."
        },
        "Program Supervisor": {
            "shift": "**From 'Team Cheerleader' to 'Culture Architect':** As a Program Supervisor, your 'niceness' can become a toxicity if not tempered with courage. You are no longer just boosting morale; you are the immune system of the program culture. This means you must be willing to identify and remove toxic elements, even if they are popular. The shift requires you to stop seeing conflict as a failure of leadership and start seeing it as a tool for clarity. You must transition from being the person who absorbs the team's stress to the person who sets the boundaries that prevent stress. You are not just there to hug the team; you are there to build a house where the team can thrive, which requires firm walls.",
            "why": "Encouragers are great at maintaining morale, but Program Supervisors need to *build* culture, which often involves pruning toxic elements. Encouragers struggle to fire people, put people on performance plans, or make unpopular decisions that are best for the program. They can become 'toxic protectors,' shielding bad staff from accountability to keep the peace, which rots the culture from the inside.",
            "conversation": "**The 'Protect the Hive' Talk:**\n\n'You love this team, and that is your superpower. But right now, by protecting the underperformers, you are hurting your high performers. \n\nYour high performers are tired of carrying the load for the people you won't hold accountable. They are waiting for you to lead. If you value the team, you have to protect the *standard* of the team, not just the feelings of the individual. Leadership is not about making everyone happy today; it's about making the team healthy forever.'",
            "assignment_setup": "This assignment pushes the Encourager to address a systemic issue that requires setting a hard boundary with the entire team, risking their 'approval rating.'",
            "assignment_task": "**The Standard Reset:**\nIdentify a culture issue where the team has become lax (e.g., cell phone use, lateness, sloppy language). You must lead a team meeting where you explicitly reset this expectation.\n\nYou must state the new standard, explain the 'why' (impact on youth), and—crucially—explain the consequence for non-compliance. You must hold the room without backing down or softening the message when they push back.",
            "success_indicators": "1. The standard was defined clearly without ambiguity.\n2. The consequences were stated firmly.\n3. The Encourager did not backpedal when the team complained.\n4. The Encourager focused on the mission, not their popularity.",
            "red_flags": "1. They framed it as 'a suggestion' or 'something we should try'.\n2. They apologized for the new rule.\n3. They let the team debate the rule until it lost all teeth.\n4. They ended the meeting by seeking reassurance ('Is everyone okay with me?')."
        },
        "Manager": {
            "shift": "**From 'Nurturer' to 'Protector of the Agency':** The hardest truth for an Encourager at the Manager level is that you cannot save everyone. You are responsible for the survival of the entire residential program, not just the happiness of the staff. This means making cold, hard decisions—cutting budgets, firing popular but ineffective leaders, or closing programs—to ensure the agency survives. You must move from 'personal care' to 'systemic care.' You have to protect the agency from liability even if it means being the 'bad guy' to the staff.",
            "why": "Encouragers define success by how people feel. Managers often have to make decisions that make people feel bad (for a while) to ensure the agency is safe. They struggle with the 'distance' required at the Manager level. They can't be friends with the Program Supervisors in the same way. They risk burnout by absorbing the emotional weight of the entire agency.",
            "conversation": "**The 'Surgeon' Analogy:**\n\n'A surgeon cannot cry while they are cutting. It doesn't mean they don't care; it means they are focused on saving the life.\n\nAs a Manager, you are the surgeon. If you let a toxic Program Supervisor stay because you like them, the infection spreads to the whole campus. You have to love the mission more than you love being liked. Your compassion must be for the 100 kids we serve, not just the one staff member in your office crying.'",
            "assignment_setup": "This assignment tests their ability to prioritize organizational health over individual relationship.",
            "assignment_task": "**The Performance Intervention:**\nIdentify a Program Supervisor who is underperforming or allowing a toxic culture. You must deliver a formal Performance Improvement Plan (PIP) or a final warning.\n\nFocus on the data and the outcome. You cannot soften the blow to the point where the message is lost. You must prioritize the agency's standard over the relationship.",
            "success_indicators": "1. The message was delivered clearly without excessive apology.\n2. They documented the conversation formally.\n3. They did not take the employee's reaction personally.\n4. They can articulate why this was necessary for the agency.",
            "red_flags": "1. They walked back the consequences when the PS got emotional.\n2. They made it about 'Admin making me do this'.\n3. They lost sleep or spiraled emotionally after the conversation.\n4. They tried to 'fix' the PS's feelings instead of the PS's performance."
        },
        "Director": {
            "shift": "**From 'Chief of Tribe' to 'Architect of Unity':** You oversee 5 different departments (AOBH, TIPS, EPIC, Advocates, TSS). Your natural desire is to be deeply connected to all of them, but you can't. If you try to be the 'emotional glue' for that many people, you will burn out. You must shift from creating connection *personally* to creating *systems* that foster connection. You have to build a 'One Elmcrest' culture where the TIPS staff feels as valued as the Residential staff, without you having to have coffee with every single person. You must lead through culture, not just relationship.",
            "why": "Encouragers scale poorly if they rely on 1:1 connection. At the Director level, they often feel disconnected and guilty because they don't know everyone's name anymore. They might over-focus on the team they like best (the 'in-group') and unintentionally alienate the satellite programs (TIPS/EPIC), creating a fractured culture.",
            "conversation": "**The 'Town Square' Talk:**\n\n'You can't visit every house in the village every day anymore. You have to build the Town Square where everyone comes together.\n\nYour job is to define the culture that binds AOBH to TIPS to EPIC. Why are we all here? I need you to stop trying to be everyone's friend and start being the symbol of our shared mission. If TIPS feels like the step-child of the agency, that is a cultural failure, and only you can fix it.'",
            "assignment_setup": "This assignment forces them to use their superpower (connection) at a systemic level rather than an individual level.",
            "assignment_task": "**The Culture Summit:**\nPlan and lead a joint leadership meeting with the heads of TIPS, EPIC, Advocates, and Residential. \n\nThe goal is not just 'updates'. The goal is to define 3 Shared Values that apply to all departments. You must facilitate this so that the smaller programs feel just as heard as the big ones. Build the bridge.",
            "success_indicators": "1. The satellite programs spoke as much as Residential.\n2. The values created apply to everyone, not just AOBH.\n3. The Director facilitated, rather than dominated with their own feelings.\n4. There is a concrete plan to roll these values out.",
            "red_flags": "1. They let the Residential team dominate the room.\n2. They focused on 'fun' rather than 'alignment'.\n3. They avoided the friction between departments to keep the peace.\n4. They left the meeting feeling exhausted from managing everyone's emotions."
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "**From 'Consensus Builder' to 'Decision Maker':** Your gift for listening and ensuring everyone feels heard is vital for culture, but it can be fatal in a crisis. The shift requires you to abandon the need for 100% agreement. In the Supervisor role, 'good enough and fast' is often better than 'perfect and slow.' You must learn to recognize the moment when discussion ends and command begins. This feels unnatural and perhaps even 'mean' to you, but you must reframe decisiveness as safety. The team feels unsafe when they don't know who is driving the bus. Your new goal is not to make everyone happy with the decision, but to make everyone safe with the direction.",
            "why": "Facilitators are excellent at hearing all sides and ensuring fairness. However, in a crisis or fast-paced shift, this strength becomes a weakness: 'Analysis Paralysis.' They delay making necessary decisions because they are waiting for everyone to agree, or they try to find a 'perfect' solution that upsets no one. On a shift, a good decision *now* is better than a perfect decision *later*. They need to get comfortable with the 51% decision.",
            "conversation": "**The 'Captain of the Ship' Analogy:**\n\n'When the seas are calm, we can vote on where to go for dinner. When the ship is hitting an iceberg, you don't call a meeting; you give an order.\n\nYour team feels unsafe when you hesitate. They aren't looking for a vote; they are looking for a leader. I need you to practice making calls when you only have 60% of the information and 0% of the consensus. If you are wrong, we will fix it together. But you cannot be frozen.'",
            "assignment_setup": "This simulation removes the luxury of time and consensus, forcing the Facilitator to rely on their own judgment.",
            "assignment_task": "**The Crisis Drill (Tabletop):**\nPresent them with a complex, urgent scenario (e.g., two fights breaking out simultaneously while a staff member is injured). Give them 60 seconds to articulate a plan.\n\nThey must assign roles, prioritize safety, and make the call. Do not let them ask 'What do you think?' Stop them if they try to debate the options. Force a commitment: 'What is your order?'",
            "success_indicators": "1. A decision was made within the time limit.\n2. The instructions to the team were clear and direct.\n3. They stood by their decision even when you challenged it.\n4. They prioritized safety over making everyone happy.",
            "red_flags": "1. They froze or went silent.\n2. They tried to ask the group for input.\n3. They gave vague suggestions ('Someone should probably...') instead of orders.\n4. They kept changing their mind.",
            "supervisor_focus": "Validate their *decision-making capability*. They need to know you trust their gut so they can trust it too."
        },
        "Program Supervisor": {
            "shift": "**From 'Mediator' to 'Driver of Change':** You naturally seek equilibrium and stability, acting as the bridge between conflicting parties. However, a Program Supervisor often needs to *disrupt* the equilibrium to force growth. You must shift from being the neutral peacekeeper to the active driver of unpopular but necessary changes. This means you cannot just validate the staff's resistance to new admin policies; you must champion the 'Why' behind the change. You must become comfortable with the team being temporarily unhappy with you for the sake of their long-term development. Leadership is not just about servicing the team's current desires; it is about leading them to a new reality.",
            "why": "Facilitators naturally want to balance the system and keep it stable. As a Program Supervisor, they often need to *disrupt* the system to improve it. They struggle to roll out unpopular changes or enforce new mandates from above because they empathize too deeply with the staff's resistance. They can become 'message carriers' ('Admin said we have to...') rather than leaders who own the mission.",
            "conversation": "**The 'Sales vs. Service' Shift:**\n\n'You are used to servicing the team's needs. Now, I need you to sell them on a new reality. \n\nWe are implementing [New Protocol]. The team is going to hate it at first. Your job is not just to validate their complaints until the protocol dies. Your job is to listen, acknowledge, and then *lead them through the change*. You cannot stay neutral. You have to own this change as if it were your idea. You are the driver, not the passenger.'",
            "assignment_setup": "This assignment tests their ability to champion a directive they didn't create, requiring them to own their authority.",
            "assignment_task": "**The Rollout:**\nAssign them to introduce a new (minor but annoying) policy to the team (e.g., a new paperwork requirement). \n\nThey must present it to the team, explain the 'Why' (connecting it to the mission/safety), and handle the objections *without* blaming upper management or promising to 'see if we can change it.' They must hold the line.",
            "success_indicators": "1. They used 'We' language, not 'They' (admin) language.\n2. They validated feelings ('I know this is extra work') without validating refusal.\n3. They kept the focus on the outcome/mission.\n4. The team left understanding that the change is happening.",
            "red_flags": "1. They said 'I know this sucks, but I have to tell you...'\n2. They promised to try to get the rule cancelled.\n3. They let the meeting devolve into a complaining session.\n4. They stayed neutral/silent when staff attacked the policy."
        },
        "Manager": {
            "shift": "**From 'Voice of the People' to 'Voice of the Mission':** As a PS, you were the advocate for your team against the system. As a Manager, you *are* the system. This is an identity crisis for Facilitators. You have to arbitrate disputes between Program Supervisors without 'splitting the difference.' You have to make decisions that favor the agency's long-term health over a specific program's comfort. You must become comfortable with the fact that in every decision, someone will feel unheard or unhappy. You are no longer the mediator; you are the judge.",
            "why": "Facilitators want everyone to win. In management, resources are finite. Sometimes one program gets the budget and the other doesn't. They struggle to make 'Zero-Sum' decisions. They risk stalling the entire agency by trying to find a solution that pleases everyone.",
            "conversation": "**The 'Judge' Analogy:**\n\n'A mediator tries to get everyone to agree. A judge looks at the law (mission) and makes a ruling.\n\nYou are now the judge. When two Program Supervisors come to you with a conflict over resources, you can't just tell them to work it out. You have to decide who gets the resource based on the strategic needs of the agency. Someone will lose. That is okay. Your job is to make the decision fair, not to make it popular.'",
            "assignment_setup": "This assignment forces them to make a resource allocation decision where compromise is impossible.",
            "assignment_task": "**The Resource War:**\nScenario: We have budget for only one new clinician or one facility upgrade. Program A wants the clinician; Program B wants the upgrade. \n\nDecide which one gets funded. You cannot split the money. You must announce the decision to both PSs and explain the strategic 'Why' without apologizing for the reality of the budget.",
            "success_indicators": "1. A definitive decision was made.\n2. The decision was tied to strategic data, not just who complained loudest.\n3. They communicated the 'No' to the losing party with clarity and firmness.\n4. They did not try to hide from the fallout.",
            "red_flags": "1. They tried to 'split the baby' (giving a little to both, satisfying neither).\n2. They delayed the decision hoping more money would appear.\n3. They apologized excessively for the budget reality.\n4. They let the PSs argue it out indefinitely."
        },
        "Director": {
            "shift": "**From 'Consensus Builder' to 'Executive Decider':** You are overseeing 5 distinct departments (AOBH, TIPS, EPIC, Advocates, TSS). They have competing needs and limited resources. You cannot run this by committee. If you wait for TIPS and AOBH to agree on everything, the agency will stall. You must shift from 'bottom-up' listening to 'top-down' direction setting. You are the only one who sees the whole board. You must be willing to make decisions that benefit the whole agency even if it hurts a specific department. You are not a representative of the parts; you are the leader of the whole.",
            "why": "Facilitators get stuck in the 'Middle'—trying to negotiate between departments. At the Director level, this leads to gridlock. They need to learn that their job isn't to make the departments agree; it's to align them to the mission, even forcibly if necessary.",
            "conversation": "**The 'Hub and Spoke' Talk:**\n\n'Right now, you are acting like the hub of a wheel, trying to keep all the spokes (departments) happy. That is exhausting and slow.\n\nI need you to be the driver of the car. You decide where we are going. If TIPS wants to go left and EPIC wants to go right, you don't negotiate a middle path. You look at the map and decide. Leadership at this level is about disappointment management. Someone will always be unhappy with your resource allocation. That means you are doing it right.'",
            "assignment_setup": "This assignment requires them to resolve a structural conflict between departments without compromise.",
            "assignment_task": "**The Budget Cut:**\nScenario: We have to cut 5% of the operating budget. You have to decide where it comes from. \n\nDo not ask the managers to 'volunteer' cuts (they won't). You must analyze the P&L and make the strategic decision on where to cut to minimize impact on care. Present the decision to the leadership team as a final plan, not a discussion starter.",
            "success_indicators": "1. The decision was strategic, not just 'across the board' cuts (which is lazy fairness).\n2. They owned the decision completely.\n3. They explained the 'Why' clearly.\n4. They did not let the meeting devolve into bargaining.",
            "red_flags": "1. They asked everyone to 'share the pain' equally to avoid conflict.\n2. They delayed the decision to 'get more feedback'.\n3. They blamed the cut on the Board/CEO.\n4. They apologized for leading."
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "**From 'Rule Enforcer' to 'Adaptive Leader':** You find safety in the black-and-white clarity of the rulebook. The shift to Supervisor thrusts you into the gray world of human emotion and crisis management. You must learn that the policy is a map, but the terrain (the actual situation) determines the path. The transition requires you to prioritize the *outcome* (safety/connection) over the *process* (strict compliance). You must learn to ask 'What does this kid need right now?' before asking 'What does page 42 say?' This doesn't mean abandoning rules; it means mastering them so well that you know exactly when to bend them to save a situation.",
            "why": "Trackers find safety in the black-and-white rulebook. As supervisors, they struggle with the 'gray'. They can become rigid 'policy robots' who quote the handbook while the building burns down. They risk losing the team's trust because they prioritize compliance over context. They need to learn that the rule is the map, but the territory (the reality of human behavior) is what matters.",
            "conversation": "**The 'Spirit of the Law' Talk:**\n\n'You know the rules better than anyone. That is your strength. But leadership is about knowing when the rule serves the mission and when it blocks it.\n\nIf you enforce a rule in a way that escalates a kid into a crisis, you have failed the mission of safety, even if you were 'right' on paper. I need you to develop your intuition. I need you to read the room, not just the manual. Compliance is the baseline; safety and connection are the goal.'",
            "assignment_setup": "This scenario forces the Tracker to choose between a rigid rule and a safer, more flexible outcome.",
            "assignment_task": "**The Gray Area Scenario:**\nPresent a scenario where a strict rule needs to be bent for safety (e.g., A dysregulated youth refuses to wear shoes during a transition, but forcing the issue will cause a restraint). \n\nAsk them to manage the transition. The 'correct' answer is to prioritize the relationship/safety (let the kid walk in socks) rather than the rule (shoes are mandatory).",
            "success_indicators": "1. They identified that safety > compliance.\n2. They communicated the *exception* clearly to the team ('We are making an exception for safety').\n3. They did not get into a power struggle with the youth.\n4. They debriefed it as a tactical decision, not a failure.",
            "red_flags": "1. They quoted the rulebook and escalated the youth.\n2. They seemed paralyzed by the choice.\n3. They blamed the youth for 'not following instructions.'\n4. They were unable to explain *why* they would bend the rule.",
            "supervisor_focus": "Praise their flexibility. They need permission to color outside the lines when it serves the mission."
        },
        "Program Supervisor": {
            "shift": "**From 'Guardian' to 'Architect':** You are excellent at maintaining the integrity of existing systems. The Program Supervisor role, however, requires you to *break* systems that no longer work and build better ones. You must shift from a mindset of 'preservation' to 'innovation.' This is difficult because change feels like risk to you. You must learn to see inefficiency as a bigger threat than change. Your job is not just to ensure the forms are filled out correctly; it is to ask if we even need that form at all. You must become the designer of the machine, not just its mechanic.",
            "why": "Trackers are excellent at maintaining existing systems. However, Program Supervisors need to *build* new systems and improve broken ones. Trackers often resist change because change feels like chaos/risk. They can become bottlenecks who stifle innovation because 'we've always done it this way.' They need to shift from protecting the status quo to designing better ways to work.",
            "conversation": "**The 'System Upgrade' Talk:**\n\n'You are great at keeping the train on the tracks. But now I need you to build a better track.\n\nI want you to look at our systems not as sacred laws, but as tools. Some of them are broken. Some are slow. Your job is not just to make people follow the process; it's to fix the process so it's easier to follow. I need you to stop saying 'no' to new ideas and start asking 'how can we make this work safely?''",
            "assignment_setup": "This assignment leverages their love for detail but points it toward innovation rather than compliance.",
            "assignment_task": "**The Workflow Fix:**\nIdentify a process that is currently clunky or inefficient (e.g., shift changeover, incident reporting). Task them with designing a *new*, streamlined version.\n\nThey must map out the current problem, design the new solution, and—most importantly—sell the *efficiency* gain to the team. They cannot just add more rules; they must remove barriers.",
            "success_indicators": "1. The new system is actually simpler/faster, not more complex.\n2. They solicited input from the team on the pain points.\n3. They can explain how the change improves safety/efficiency.\n4. They are excited about the *improvement*, not just the *compliance*.",
            "red_flags": "1. They created a system that is just more paperwork/checklist boxes.\n2. They refused to change the old way because 'it's policy'.\n3. They did not consult the users (staff) about the friction points.\n4. The solution solves a compliance problem but creates an operational nightmare."
        },
        "Manager": {
            "shift": "**From 'Compliance Officer' to 'Risk Manager':** Compliance is black and white—you either followed the rule or you didn't. Risk Management is gray—it is about calculating probabilities and making bets. As a Manager, you have to operate in the gray. You will face situations where every option carries risk (e.g., admitting a high-needs youth to balance the budget vs. denying them to protect staff). You cannot just quote the policy book because the policy book doesn't cover this. You must learn to tolerate the anxiety of not having a perfect answer.",
            "why": "Trackers want certainty. Management is inherently uncertain. They struggle with ambiguity and 'wicked problems' that have no clean solution. They can become paralyzed by the fear of making a mistake that leads to a lawsuit or audit failure.",
            "conversation": "**The 'Poker' Analogy:**\n\n'You are used to playing chess where all the pieces are visible. Management is poker. You have to bet on incomplete information.\n\nI need you to stop looking for the 'perfectly safe' option because it doesn't exist. I need you to tell me: 'Option A has 20% risk, Option B has 40% risk.' Then we choose Option A and live with the anxiety. Your job isn't to eliminate risk; it's to manage it.'",
            "assignment_setup": "This assignment forces them to make a decision where policy offers no clear guidance.",
            "assignment_task": "**The Gray Zone Admission:**\nScenario: We have a referral for a youth who is a marginal fit (risky behaviors) but we desperately need the census/revenue. \n\nAnalyze the referral. You cannot just say 'No' because of risk. You must design a 'Risk Mitigation Plan' that allows us to take the youth safely. Outline the extra staffing/protocols needed to make the 'Yes' possible.",
            "success_indicators": "1. They found a pathway to 'Yes' rather than defaulting to 'No'.\n2. The mitigation plan is realistic and detailed.\n3. They quantified the risk rather than just fearing it.\n4. They accepted that some residual risk remains.",
            "red_flags": "1. They rejected the youth immediately to avoid all risk.\n2. They demanded guarantees of safety that are impossible.\n3. They got stuck in the details of the past history.\n4. They refused to make a recommendation."
        },
        "Director": {
            "shift": "**From 'Risk Manager' to 'Organizational Architect':** You are now responsible for the stability of AOBH, TIPS, EPIC, Advocates, and TSS. The complexity of this system is too high for you to track every detail yourself. If you try to audit every file in 5 departments, you will fail. You must shift from 'inspecting quality' to 'designing systems that ensure quality.' You have to trust the data, not just your eyes. You must build a dashboard that tells you the health of the organization at a glance, and trust your managers to handle the weeds.",
            "why": "Trackers often try to scale by just working harder/longer. At the Director level, the volume of detail is impossible to manage personally. They risk becoming the bottleneck of the entire agency because they won't sign off on things until they have personally checked them. They need to learn to manage by exception (looking at data outliers) rather than inspection.",
            "conversation": "**The 'Air Traffic Controller' Talk:**\n\n'You are no longer the mechanic fixing the plane; you are the air traffic controller watching 50 planes at once. \n\nYou cannot go down to the runway to check the tires on every plane. You have to trust your instruments (data). I need you to build me a dashboard that tells me which department is in trouble. Stop trying to read every incident report and start looking for the patterns in the data.'",
            "assignment_setup": "This assignment forces them to synthesize complex data into a simple, high-level view.",
            "assignment_task": "**The Master Dashboard:**\nCreate a 1-page weekly report that summarizes the health of AOBH, TIPS, EPIC, and TSS. \n\nYou have to pick only 3 metrics per department (e.g., Census, Incidents, Staffing). You cannot include narrative. You must design the system that gathers this info from the managers automatically. The goal is a 'pulse check', not an autopsy.",
            "success_indicators": "1. The dashboard is concise (1 page).\n2. They identified the *critical* metrics, not just *all* metrics.\n3. They created a process for managers to submit data (delegation).\n4. They can explain the 'story' the data is telling.",
            "red_flags": "1. They created a 20-page report.\n2. They are gathering the data themselves instead of making managers do it.\n3. They get stuck on minor inaccuracies.\n4. They cannot see the trend line, only the individual data points."
        }
    }
}

TEAM_CULTURE_GUIDE = {
    "Director": {
        "title": "The Command Center",
        "impact_analysis": "This team moves fast and breaks things. They are highly efficient but likely suffering from low psychological safety. Quiet voices are being steamrolled. The vibe is 'High Performance, Low Patience.'\n\n**The Good:** Crises are handled instantly. Decisions are made fast.\n**The Bad:** Psychological safety is likely low. 'Feelings' are viewed as inefficiencies. Quiet dissenters (Facilitators/Trackers) are likely being steamrolled or silencing themselves to avoid conflict. You are at risk of 'Burn and Turn'—burning out staff and turning over positions.",
        "management_strategy": "**Your Role: The Brake Pedal.**\n\nDirectors view deliberation as weakness. You must reframe it as 'risk management.'\n\n1. **Force the Pause:** Mandate a 10-minute 'Devil's Advocate' session for major decisions. Make them sit in the discomfort of silence.\n2. **Protect Dissent:** Explicitly call on the quietest person in the room first. Protect them from interruption.\n3. **Humanize the Data:** Constantly remind them that 'efficiency' with traumatized youth often looks like 'impatience.'",
        "meeting_protocol": "**The 'No Interruption' Rule:** Directors interrupt to 'speed things up.' Enforce a strict 'one voice at a time' rule to protect slower processors.",
        "team_building": "Vulnerability Exercises (e.g., 'Highs and Lows'). They will hate it, but they need it to humanize each other."
    },
    "Encourager": {
        "title": "The Social Hub",
        "impact_analysis": "This team has high morale but low accountability. They avoid hard conversations and tolerate underperformance to keep the peace. The vibe is 'We Are Family' (which creates toxicity when you have to fire a 'family member').\n\n**The Good:** People feel loved and supported. Retention is high among the core group.\n**The Bad:** Standards slip. Mediocrity is tolerated. High performers burn out carrying the low performers who are 'too nice to fire.'",
        "management_strategy": "**Your Role: The Standard Bearer.**\n\n1. **Redefine Kindness:** Coach them that clear boundaries are kind, and allowing failure is cruel. Frame accountability as 'protecting the team' from toxicity.\n2. **Data-Driven Feedback:** Remove the emotion from performance reviews. Use checklists and audit scores so they can't 'nice' their way out of it.\n3. **The 'Who' vs. The 'What':** They focus on the 'Who' (person). You must constantly pivot back to the 'What' (the mission/youth safety).",
        "meeting_protocol": "**Start with the Failure:** Begin meetings by reviewing an incident or error (blamelessly) to normalize talking about hard things.",
        "team_building": "Debate Club or Competitive Goal-Setting. Force them to compete and disagree safely."
    },
    "Facilitator": {
        "title": "The United Nations",
        "impact_analysis": "This team is fair and inclusive but suffers from analysis paralysis. Decisions take forever because they wait for consensus. The vibe is 'Let's Talk About It.'\n\n**The Good:** Everyone feels heard. Decisions have high buy-in once made.\n**The Bad:** Urgent problems fester. Opportunities are missed. In a crisis, the team may freeze, waiting for a vote when they need a command.",
        "management_strategy": "**Your Role: The Clock.**\n\n1. **The 51% Rule:** Establish a rule that once you have 51% certainty (or 51% consensus), you move. Perfection is the enemy of done.\n2. **Disagree and Commit:** Teach the culture that it is okay to disagree with a decision but still support its execution 100%.\n3. **Assign 'Decision Owners':** Stop making decisions by committee. Assign one person to decide, and the committee only *advises*.",
        "meeting_protocol": "**The '51% Rule':** If we are 51% sure, we move. No revisiting decisions after the meeting ends.",
        "team_building": "Escape Rooms. They force the team to make rapid decisions against a clock to survive."
    },
    "Tracker": {
        "title": "The Audit Team",
        "impact_analysis": "This team is safe and compliant but rigid. They fear change and will quote policy to stop innovation. The vibe is 'By The Book.'\n\n**The Good:** Audits are perfect. Safety risks are low. Documentation is flawless.\n**The Bad:** Innovation is dead. Staff escalate youth behaviors because they prioritize enforcing a minor rule over maintaining the relationship. The culture is fear-based.",
        "management_strategy": "**Your Role: The permission Giver.**\n\n1. **'Safe to Fail' Zones:** Explicitly designate areas where staff are allowed to experiment and fail without consequence.\n2. **The 'Why' Test:** Challenge every rule. If a staff member cannot explain *why* a rule exists (beyond 'it's in the book'), they aren't leading; they are robot-ing.\n3. **Reward Adaptation:** Publicly praise staff who *bent* a rule to save a situation (safely). Show that judgment is valued over blind compliance.",
        "meeting_protocol": "**Ban the phrase:** 'We've always done it this way.' Require a rationale for every old habit.",
        "team_building": "Improv Games. Forcing them to react to the unexpected without a script."
    },
    "Balanced": {
        "title": "The Balanced Team",
        "impact_analysis": "No single style dominates. This reduces blindspots but may increase friction as different 'languages' are spoken.",
        "management_strategy": "**Your Role: The Translator.**\n\nYou must constantly translate intent. 'The Director isn't being mean; they are being efficient.' 'The Tracker isn't being difficult; they are being safe.' Rotate leadership based on the task: let the Director lead the crisis, the Encourager lead the debrief, the Tracker lead the audit.",
        "meeting_protocol": "Round Robin input to ensure the quiet ones speak and the loud ones listen.",
        "team_building": "Role Swapping. Have the Director do the paperwork and the Tracker run the floor."
    }
}

MISSING_VOICE_GUIDE = {
    "Director": {"risk": "**The Drift.** Without a Director, the team lacks a 'spine' of urgency. Decisions linger in 'discussion mode' forever. There is no one to cut through the noise and say 'This is what we are doing.' Problems are admired, not solved.", "fix": "**Be the Bad Guy.** You must artificially inject urgency. Set artificially tight deadlines (e.g., 'Decide by 3 PM'). Use 'Command Language' rather than 'Suggestion Language' during crises."},
    "Encourager": {"risk": "**The Cold Front.** The team is cold and transactional. Burnout is high because no one feels cared for. Staff feel like 'cogs in a machine.' Retention will plummet because people join for the mission but stay for the people.", "fix": "**Artificial Warmth.** You must operationalize care. Start every meeting with a personal check-in. Celebrate birthdays and wins aggressively. Schedule 'no agenda' time just to connect."},
    "Facilitator": {"risk": "**Steamrolling.** The loudest voices win, and quiet dissenters check out. Decisions are made fast but often wrong because key perspectives were ignored. There is 'compliance' but not 'buy-in.'", "fix": "**Forced Input.** Use round-robin speaking. Don't let anyone speak twice until everyone speaks once. Explicitly ask: 'Who haven't we heard from?'"},
    "Tracker": {"risk": "**Chaos.** Details are dropped, and safety issues are missed. The team has great ideas but poor execution. Audits will fail, and safety risks will slip through the cracks.", "fix": "**The Checklist.** You must become the external hard drive. Create checklists for everything. Assign a 'Safety Captain' to review every plan for risks before execution."}
}

MOTIVATION_GAP_GUIDE = {
    "Achievement": {
        "warning": "This team runs on **Winning**. If they cannot see the scoreboard, they will disengage.",
        "coaching": "**Strategy: Gamify the Grind.**\n\n1. **Visual Scoreboards:** Do not just say 'do better.' Put a chart on the wall tracking 'Days Without a Restraint' or 'Paperwork Accuracy %.' They need to see the line go up.\n2. **Micro-Wins:** Youth care is a long game. Break it down. Celebrate 'One smooth transition' or 'One clean file' as a victory.\n3. **Feedback Style:** Be objective. 'You hit 90% accuracy' lands better than 'You did a good job.'\n4. **The Trap:** Watch out for them cutting corners to hit the metric. Audit the *quality*, not just the *quantity*."
    },
    "Connection": {
        "warning": "This team runs on **Belonging**. If the culture feels cold or isolated, they will quit.",
        "coaching": "**Strategy: The Tribe.**\n\n1. **Face Time:** E-mail is the enemy. Walk the floor. Sit in the office and chat. They need to feel your presence to feel safe.\n2. **Rituals:** Establish team rituals (e.g., Friday food, morning huddles). These aren't 'nice to haves'; they are the glue holding the team together.\n3. **Protect the Vibe:** Toxic peers will destroy this team faster than bad management. You must excise toxicity immediately.\n4. **The Trap:** They may form cliques. Ensure the 'connection' includes everyone, not just the favorites."
    },
    "Growth": {
        "warning": "This team runs on **Competence**. If they feel stagnant or bored, they will leave.",
        "coaching": "**Strategy: The Ladder.**\n\n1. **Micro-Promotions:** You can't promote everyone to supervisor, so create 'titles' (e.g., 'Safety Captain', 'Trainer', 'Logistics Lead'). Give them ownership of a domain.\n2. **The 'Why' Behind the Task:** Don't just assign work; explain how this task builds a skill they will need for their next job.\n3. **Mentorship:** Connect them with leaders they admire. They crave access to expertise.\n4. **The Trap:** They may get bored with routine duties. Frame the boring stuff as 'professional discipline' required for advancement."
    },
    "Purpose": {
        "warning": "This team runs on **Mission**. If the work feels meaningless or bureaucratic, they will rebel.",
        "coaching": "**Strategy: The Storyteller.**\n\n1. **Connect Dots:** Constantly draw the line between the boring task (paperwork) and the mission (getting the kid funded/safe). Never assume they see the connection.\n2. **Mission Moments:** Start meetings by sharing a specific story of a youth's success. Remind them why they are tired.\n3. **Validation:** When they vent about the system, validate their moral outrage. 'You are right, it is unfair. That's why we have to fight harder.'\n4. **The Trap:** They can become martyrs, burning themselves out for the cause. You must mandate self-care as a 'mission requirement.'"
    }
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

def get_integrated_hud_data(comm, motiv):
    """
    Returns specific, high-context strings for the Supervisor's HUD
    based on the 16 combinations of Communication + Motivation.
    """
    # Defaults
    s_sig, s_why, s_risk = "N/A", "N/A", "N/A"
    rx_why = "This restores balance."

    # 1. Stress Signature Logic
    if comm == "Director":
        if motiv == "Achievement":
            s_sig = "Micromanaging, taking over tasks, visible irritation with any delay."
            s_why = "They equate speed with competence. When things slow down, they feel the team is failing, so they 'rescue' it to protect the win."
            s_risk = "They will burn out doing everyone else's job, and the team will stop trying because 'The Boss will just fix it anyway.'"
            rx_why = "Removing a barrier proves you value their speed. Giving them a 'win' restores their sense of agency."
        elif motiv == "Growth":
            s_sig = "Become critical of others' intelligence, impatience with training, 'they just don't get it'."
            s_why = "They fear incompetence. Stagnation feels like death to them. They lash out when they feel the team isn't growing fast enough."
            s_risk = "They will alienate learning staff, creating a culture of fear where no one asks questions."
            rx_why = "Feeding their brain with a new challenge distracts them from the team's slowness. Autonomy shows you trust their competence."
        elif motiv == "Purpose":
            s_sig = "Moralizing speed. 'We are failing the kids because we are slow.' Righteous anger."
            s_why = "They view inefficiency as an ethical violation. To them, wasting time = hurting kids."
            s_risk = "They will become a martyr, working 80 hours to 'save' the program, then crash hard."
            rx_why = "Connecting speed to care validates their anger without enabling the burnout. Protective action shows you share their values."
        elif motiv == "Connection":
            s_sig = "Aggressively protective. 'I'll handle it, don't talk to my team.' Us vs. Them."
            s_why = "They fear the team getting hurt or stressed. They use their power to build a fortress around their people."
            s_risk = "They create a silo. The team loves them, but the agency can't work with them."
            rx_why = "Validating their protection lowers their defenses so they can hear feedback. Delegated care builds their trust in you."

    elif comm == "Encourager":
        if motiv == "Achievement":
            s_sig = "Over-promising, saying yes to everything, manic energy followed by a crash."
            s_why = "They fear letting people down means failing. They try to 'win' relationships by doing favors."
            s_risk = "Reliability craters. They drop balls because they are juggling too many 'yeses'."
            rx_why = "A visual scoreboard grounds them in reality. Forced prioritization relieves the pressure of having to please everyone."
        elif motiv == "Growth":
            s_sig = "Chasing shiny objects, bored with routine, starting new initiatives without finishing old ones."
            s_why = "Boredom is painful for them. They seek novelty to keep their energy up."
            s_risk = "Lots of starts, no finishes. The team gets whiplash from constant pivots."
            rx_why = "Project ownership focuses their chaotic energy. Explaining the 'why' of routine reframes boredom as a necessary skill."
        elif motiv == "Purpose":
            s_sig = "Emotional flooding, crying in meetings, taking on client trauma personally."
            s_why = "They have high empathy and low filters. They feel the pain of the work acutely."
            s_risk = "Compassion fatigue. They will burn out from the emotional weight, not the workload."
            rx_why = "Mission stories refill their emotional tank. Boundaries framed as 'ethics' help them protect their heart without guilt."
        elif motiv == "Connection":
            s_sig = "Gossip, venting, wasting time on small talk, avoiding conflict at all costs."
            s_why = "They fear rejection. They prioritize being liked over being effective."
            s_risk = "Toxic harmony. Poor performance is tolerated to keep the peace."
            rx_why = "Face time reassures them they are safe with you. Team rituals channel their social energy into productive culture building."

    elif comm == "Facilitator":
        if motiv == "Achievement":
            s_sig = "Stalling to find the 'perfect' answer that satisfies everyone AND hits the goal."
            s_why = "They fear making the wrong choice that hurts the outcome. They want 100% certainty before moving."
            s_risk = "Missed deadlines. Opportunities die in committee."
            rx_why = "The '51% Rule' gives them permission to move without perfection. Deadlines provide the safety of a container."
        elif motiv == "Growth":
            s_sig = "Endless research, asking 'What about this angle?', analysis paralysis."
            s_why = "They desire mastery and completeness. They don't want to miss a piece of the puzzle."
            s_risk = "Academic debate replaces actual work. Theory over practice."
            rx_why = "Time-boxed research limits the scope. Pilot programs allow them to learn by doing, satisfying their need for growth."
        elif motiv == "Purpose":
            s_sig = "Moral gridlock. 'Neither option feels right.' Refusal to choose the lesser of two evils."
            s_why = "They fear compromising their values. They want a solution where no one gets hurt."
            s_risk = "Ethical stagnation. Urgent decisions are delayed, causing harm."
            rx_why = "Framing the 'Least Bad Option' as the moral choice helps them move. Validating the struggle makes them feel seen."
        elif motiv == "Connection":
            s_sig = "Hiding, refusing to give bad news, mediating instead of leading."
            s_why = "They fear breaking the relationship. They prioritize the group's cohesion over the task."
            s_risk = "Leadership vacuum. The team runs the leader."
            rx_why = "Shared decisions reduce their isolation. Pre-meeting alignment builds their confidence to speak up."

    elif comm == "Tracker":
        if motiv == "Achievement":
            s_sig = "Obsessive formatting, working late on details, refusing to delegate because 'they won't do it right'."
            s_why = "They equate perfection with success. Errors feel like personal failures."
            s_risk = "Burnout on low-value tasks. They miss the forest for the trees."
            rx_why = "Defining 'Done' stops the perfectionism loop. Metrics focus them on output, not just input."
        elif motiv == "Growth":
            s_sig = "Hoarding knowledge, correcting others' grammar/minor errors, acting superior."
            s_why = "They view accuracy as competence. They protect their status by being the expert."
            s_risk = "They alienate peers who feel judged. Collaboration stops."
            rx_why = "Teaching others channels their expertise productively. Giving them an 'Expert Role' validates their status."
        elif motiv == "Purpose":
            s_sig = "Using rules to block action. 'Policy says we can't.' The Bureaucratic Wall."
            s_why = "They believe rules protect the mission. Risk feels like a betrayal of the agency."
            s_risk = "They become a bottleneck that kills innovation and morale."
            rx_why = "Safe exceptions allow flexibility without fear. Explaining the logic behind the policy helps them connect rule to why."
        elif motiv == "Connection":
            s_sig = "Passive aggression, silent resentment, doing 'invisible' work and being mad no one noticed."
            s_why = "They feel used. They show care through tasks, not words, and feel hurt when it's missed."
            s_risk = "Explosive resignation. They quit 'suddenly' after months of silence."
            rx_why = "Public appreciation makes their invisible work visible. Role clarity protects their boundaries."

    return {
        "s_sig": s_sig,
        "s_why": s_why,
        "s_risk": s_risk,
        "rx_why": rx_why
    }

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
    hud_context = get_integrated_hud_data(p_comm, p_mot)

    # 1. Stress Signature
    # Fallback/Base data for display
    stress_base_rx = {
        "Director": ["Remove a barrier they can't move.", "Give them a 'win' to chase.", "Shorten the meeting."],
        "Encourager": ["Schedule face time (no agenda).", "Validate their emotional load.", "Publicly praise a specific contribution."],
        "Facilitator": ["Give a clear deadline.", "Take the blame for a hard decision.", "Ask 'What is the risk of doing nothing?'"],
        "Tracker": ["Give them the 'why' behind the chaos.", "Protect them from last-minute changes.", "Explicitly define 'good enough'."]
    }
    
    with st.container(border=True):
        st.markdown("#### 🚨 Stress Signature (Early Warning System)")
        
        col_sig, col_rx = st.columns([1, 1])
        with col_sig:
            st.error(f"**The Signal (Watch for this):**\n{hud_context['s_sig']}")
            st.markdown(f"**Root Cause Analysis:**\n{hud_context['s_why']}")
            st.markdown(f"**Risk if Ignored:**\n{hud_context['s_risk']}")
            
        with col_rx:
            st.success(f"**The Prescription (Do This):**")
            # We use the generic Rx list but explain WHY it works for this specific combination below
            rx_list = stress_base_rx.get(p_comm, [])
            for r in rx_list:
                st.write(f"• {r}")
            st.info(f"**Why this works for them:**\n{hud_context['rx_why']}")

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
    # (Team DNA logic abbreviated - missing data placeholder below)
    if not df.empty:
        with st.container(border=True):
            teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        if teams:
            tdf = df[df['name'].isin(teams)]
            def calculate_weighted_counts(dframe, p_col, s_col):
                p = dframe[p_col].value_counts() * 1.0
                s = dframe[s_col].value_counts() * 0.5
                return p.add(s, fill_value=0).sort_values(ascending=False)
            
            c1, c2 = st.columns(2)
            with c1:
                comm_counts = calculate_weighted_counts(tdf, 'p_comm', 's_comm')
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, title="Communication Mix"), use_container_width=True)
                
                # Check for Team Culture Guide Data
                if not TEAM_CULTURE_GUIDE:
                    st.info("Detailed team culture guides are currently unavailable.")
                else:
                    # Original logic would go here if data was present
                    pass

            with c2:
                mot_counts = calculate_weighted_counts(tdf, 'p_mot', 's_mot')
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers"), use_container_width=True)

    st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    st.info("Conflict Mediator data is currently offline. Please check back later.")
    st.button("Reset", key="reset_t3", on_click=reset_t3)

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    st.info("Career Pathfinder data is currently offline. Please check back later.")
    st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        total_staff = len(df)
        def calculate_weighted_pct(dframe, p_col, s_col):
            p = dframe[p_col].value_counts() * 1.0
            s = dframe[s_col].value_counts() * 0.5
            total = p.add(s, fill_value=0)
            return (total / total.sum()) * 100

        comm_counts = calculate_weighted_pct(df, 'p_comm', 's_comm').sort_values(ascending=False)
        mot_counts = calculate_weighted_pct(df, 'p_mot', 's_mot').sort_values(ascending=False)
        
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            if not comm_counts.empty:
                dom_comm = comm_counts.idxmax()
                dom_mot = mot_counts.idxmax()
                c1.metric("Dominant Style", f"{dom_comm} ({int(comm_counts.max())}%)")
                c2.metric("Top Driver", f"{dom_mot} ({int(mot_counts.max())}%)") 
                c3.metric("Total Staff Analyzed", total_staff)
            
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: 
            with st.container(border=True):
                st.markdown("##### 🗣️ Communication Mix")
                fig_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']])
                st.plotly_chart(fig_comm, use_container_width=True)
        with c_b: 
            with st.container(border=True):
                st.markdown("##### 🔋 Motivation Drivers")
                fig_mot = px.bar(x=mot_counts.values, y=mot_counts.index, orientation='h', color_discrete_sequence=[BRAND_COLORS['blue']])
                st.plotly_chart(fig_mot, use_container_width=True)
    else: st.warning("No data available.")
