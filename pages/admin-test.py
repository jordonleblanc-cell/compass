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
    "Director-Achievement": {
        "title": "The Executive General",
        "synergy": "Operational Velocity. They don't just want to lead; they want to win. They cut through noise to identify the most efficient path to success. They are excellent at turnarounds or crisis management where decisive action is required immediately.",
        "support": "**Operational Risk:** Name the operational risk of moving fast. Say, 'We can do this quickly if we build in these guardrails.' This validates their speed while protecting the agency from errors. Help them see that slowing down slightly to check safety is actually an efficiency measure in the long run.\n\n**Burnout Watch:** They are the best person to identify when the 'ask' exceeds capacity, but they need permission to say it. They often view endurance as a badge of honor and will work until they collapse. Proactively ask them about their fuel tank before they run dry. They often do not realize they are exhausted until they are already sick.",
        "thriving": "**Rapid Decision Architecture:** They make calls with partial information, preventing the team from freezing in analysis paralysis. They create a sense of momentum that energizes the entire unit. Their confidence stabilizes the team during chaotic shifts.\n\n**Objective Focus:** They separate story from fact, focusing on behaviors and outcomes. This helps de-escalate emotional situations by grounding them in reality. They are excellent at conducting after-action reviews that are blameless but rigorous.\n\n**High-Bar Accountability:** They refuse to walk past a mistake, raising the standard of care. They hold peers accountable naturally, often elevating the performance of the whole group. They expect excellence and usually model it themselves.",
        "struggling": "**The Steamroller Effect:** They announce decisions without checking if the team is emotionally ready. This can alienate staff who feel unheard or bulldozed. They may view team building as 'fluff' and skip essential relationship steps.\n\n**Burnout by Intensity:** They assume everyone has their stamina and push until the team breaks. They struggle to understand why others can't just 'power through.' This can create a culture of exhaustion if left unchecked.\n\n**Dismissing 'Soft' Data:** They ignore 'bad feelings' or intuition because there is no proof. This leads to missing early warning signs of cultural toxicity or client unrest. They may view emotional concerns as irrelevant to the mission.",
        "interventions": [
            "**Phase 1: The Pause Button (0-6 Months):** You must force a deliberate delay between their initial thought and their resulting action. The goal is to break the reflex of immediate command. Require them to ask three distinct questions of their team before they are allowed to issue a final decision. This artificial constraint effectively trains the muscle of consultation and prevents them from leaving their team behind. By slowing down the initial step, you ensure the eventual action has better buy-in and fewer blind spots.",
            "**Phase 2: Narrative Leadership (6-12 Months):** Coach them to meticulously script the 'Why' behind their directives before they speak. A Director naturally assumes the logic is obvious to everyone, but the team often needs the backstory to understand the vision. They need to learn that explaining their logic is not a waste of time, but a critical investment in trust and buy-in. Require them to spend the first 5 minutes of any rollout meeting explaining the context before delegating the tasks. The story they tell is just as important as the strategy they designed.",
            "**Phase 3: Multiplier Effect (12-18 Months):** Identify two deputies and train the supervisor to literally sit on their hands while the deputies lead the meeting. This shifts their focus from 'doing it all' themselves to 'developing leaders' who can do it for them. The Executive General loves to be the hero, so this phase forces them to become the mentor who empowers others. Their metric for success must shift from 'what I achieved' to 'what my team achieved without me.' You are moving them from adding value personally to multiplying it organizationally."
        ],
        "questions": [
            "How are you defining success today beyond just metrics? (This encourages them to value human elements like morale and trust, ensuring they don't treat people like machines. It expands their scorecard to include qualitative wins.)",
            "What is one win you can celebrate right now? (Achievement types often focus entirely on the gap between current reality and the goal, leading to chronic dissatisfaction. This forces them to stop and recognize the progress they have already made.)",
            "Are you driving the team too hard? (This brings critical self-awareness to their pace, which is likely faster than the group's capacity. It invites them to check the rearview mirror to see if they have lost their followers.)",
            "What is the cost of speed right now? (This highlights the hidden trade-offs like errors, burnout, and missed details that come with moving too fast. It frames 'slow' not as laziness, but as a strategic choice to ensure quality.)",
            "Where are you moving too fast for the team? (This helps them calibrate their velocity to the team's actual capacity, rather than their ideal capacity. It prevents the 'leader without followers' scenario by forcing a reality check.)",
            "Who haven't you heard from on this issue? (This reminds them to check for blind spots and quiet voices they may have steamrolled in their rush to decide. It forces them to pause and widen their aperture.)",
            "How does your tone land when you are stressed? (This invites them to audit their non-verbal communication during high-pressure moments, which is often more aggressive than they intend.)",
            "Are you celebrating the small wins? (This reinforces the habit of positive reinforcement, which they often skip in favor of focusing on the next problem. It helps build a culture of encouragement.)",
            "Who helped you win this week? (This shifts the focus from individual heroism to team contribution, encouraging them to share the credit. It fights their tendency to be the 'lone wolf.')",
            "What is 'good enough' for right now? (This challenges perfectionism and helps them accept sufficient outcomes rather than wasting resources on diminishing returns. It teaches them the law of diminishing returns.)"
        ],
        "advancement": "**Delegate Effectively:** Give away tasks they are good at to prove they can build a team. They must learn that their value comes from their team's output, not just their own. If they hoard tasks, they are not promotable because they are too busy. They need to make themselves replaceable to move up.\n\n**Allow Safe Failure:** Let the team struggle so they can learn, rather than rescuing them. Rescuing robs the team of the learning opportunity and creates dependency. They need to learn to tolerate the discomfort of watching someone else do it slower than they would. This builds a resilient bench of talent.\n\n**Focus on Strategy:** Move from the 'how' (tactics) to the 'why' (organizational strategy). Advancement requires thinking about the next year, not just the next shift. They must prove they can think systemically, not just operationally. They need to transition from playing the game to designing the league."
    },
    "Director-Growth": {
        "title": "The Restless Improver",
        "synergy": "Transformational Leadership. They don't just manage the shift; they want to upgrade it. They see potential in every staff member and are willing to push hard to unlock it. They are natural disruptors who prevent the agency from stagnating.",
        "support": "**Connect Goals:** Link their personal growth goals to youth outcomes and the mission. Help them see that 'getting better' isn't just about their resume, but about serving the client better. This grounds their ambition in service.\n\n**Pacing:** Remind them that not everyone learns at their speed. They need help understanding that organizational change is a marathon, not a sprint. Coach them to wait for the team to catch up before introducing the next change.",
        "thriving": "**Diagnostic Speed:** They quickly identify the root causes of failures rather than treating symptoms. They are excellent at analyzing a crisis to prevent it from recurring. They turn every incident into a case study for improvement.\n\n**Fearless Innovation:** They are willing to break the status quo to find a better way. They are not afraid of administrative pushback if they believe their idea improves care. They constantly ask, 'Is there a better way to do this?'\n\n**High-Impact Coaching:** They give direct, developmental feedback that accelerates the growth of their peers. They are often the 'tough love' mentor on the unit. People grow faster under their leadership than anywhere else.",
        "struggling": "**The Pace Mismatch:** They get visibly frustrated with slow learners or bureaucracy. This impatience can leak out as arrogance or disdain. They may make others feel stupid or slow without realizing it.\n\n**'Fix-It' Fatigue:** They are constantly pointing out flaws and forgetting to validate what is working. The team may feel that nothing is ever good enough for them. They risk demoralizing the team by only focusing on the gap.\n\n**Leaving People Behind:** They focus on the idea of change rather than the adoption of change. They implement new systems without getting buy-in, leading to failure. They assume because an idea is logical, everyone will just do it.",
        "interventions": [
            "**Phase 1: Validation (0-6 Months):** Mandate that they validate the current effort before suggesting improvements. They must prove they understand why the current system exists before they are allowed to tear it down. Require them to catch people doing things right to build trust. If they only criticize, the team will stop listening to their good ideas. You are teaching them that relationship precedes influence.",
            "**Phase 2: Change Management (6-12 Months):** Require a 'stakeholder analysis' for their next idea (who will resist and why?). This forces them to consider the human element of change, which they often overlook. They must present a plan for how to get buy-in, not just a plan for the change itself. This turns them from a critic into a leader. It forces them to think politically and relationally.",
            "**Phase 3: Capacity Building (12-18 Months):** Shift them from being the idea generator to the facilitator of others' ideas. Challenge them to help a peer implement a change project. This moves them from 'Individual Contributor' to 'Leader' by proving they can get results through others. They learn that the ultimate growth is reproducing their skills in someone else."
        ],
        "questions": [
            "Where are you moving too fast for the team? (This checks the gap between leader and team, preventing them from running a race alone. It forces them to look back and see if anyone is following.)",
            "Who haven't you heard from on this issue? (This ensures they aren't ignoring strugglers or dissenters who might have valuable feedback. It broadens their data set before making a decision.)",
            "How does your tone land when you are stressed? (This monitors aggression vs. passion, helping them see how their intensity affects others. It builds self-regulation skills.)",
            "What are you learning from this struggle? (This reframes problems as learning opportunities, which fuels their motivation rather than draining it. It leverages their core motivation (growth) to handle adversity.)",
            "Are you expecting too much too soon from others? (This calibrates their expectations to reality, preventing frustration with slower teammates. It helps them accept that not everyone is a 'high potential' employee.)",
            "How are you feeding your own curiosity? (This ensures they are intellectually stimulated and not stagnating in routine. It prevents boredom, which is a major retention risk for this profile.)",
            "What is one way you can slow down for others? (This creates actionable patience, forcing them to modify their behavior for the good of the group. It turns patience from a feeling into a tactic.)",
            "How are you measuring your own growth beyond just speed? (This broadens their definition of success to include depth, wisdom, and emotional intelligence. It encourages them to grow vertically, not just horizontally.)",
            "Are you leaving the team behind? (A direct check on buy-in; if the team isn't with them, they aren't leading, they are just walking. It emphasizes the collective nature of leadership.)",
            "Is this change necessary right now? (This forces them to prioritize stability over tinkering, learning the value of leaving things alone. It teaches them that sometimes the best move is no move.)"
        ],
        "advancement": "**Delegate Effectively:** Stop being the 'fixer', become the 'developer.' They must learn to guide others to the answer rather than providing it. If they answer every question, their team never learns to think. They need to facilitate growth, not just provide solutions.\n\n**Allow Safe Failure:** Resist the urge to jump in and correct every mistake. They need to learn that struggle is a necessary part of the learning process for their staff. By intervening too soon, they stunt the growth of their team. They must learn to sit on their hands.\n\n**Focus on Strategy:** Design tomorrow's solutions rather than solving today's problems. Shift their gaze from 'immediate fix' to 'systemic prevention.' They need to prove they can build systems that run without them. This requires a shift from tactical to strategic thinking."
    },
    "Director-Purpose": {
        "title": "The Mission Defender",
        "synergy": "Ethical Courage. They provide the moral backbone for the team, ensuring expediency never trumps integrity. They are the conscience of the unit and will speak truth to power without hesitation.",
        "support": "**Share Values:** Share your own core values so they trust your leadership. They need to know you are 'one of the good guys.' If they trust your heart, they will follow your orders.\n\n**Operational Risk:** Frame slowing down as 'protecting the mission.' Help them see that rushing can lead to mistakes that hurt the client. This aligns their need for speed with their need for care.",
        "thriving": "**Unshakeable Advocacy:** They act immediately against injustice. They do not wait for permission to stop something unsafe or unethical. They are the first to report abuse or neglect.\n\n**Clarity of 'Why':** They contextualize the grind for the staff. When the team is tired, they remind everyone why the work matters. They turn mundane tasks into holy work.\n\n**Crisis Ethics:** They keep their moral compass even in chaos. When everyone else is panicking, they are asking 'What is the right thing to do?' They provide a steady hand based on principles.",
        "struggling": "**Righteous Rigidity:** They struggle to see the gray areas, viewing everything as black and white. This can make them inflexible and difficult to negotiate with. They may view compromise as a sin.\n\n**The Martyr Complex:** They overwork because they don't trust others to care enough. They believe that if they stop, the clients will suffer. This leads to rapid burnout and resentment.\n\n**Judgmental Tone:** They come across as 'preachy' or morally superior. They may unintentionally shame staff who are just trying to get through the day. They alienate allies by demanding ideological purity.",
        "interventions": [
            "**Phase 1: The Gray Zone (0-6 Months):** Practice identifying validity in opposing viewpoints. Require them to argue the 'other side' of an ethical debate to build cognitive flexibility. They must learn that not everyone who disagrees with them is evil. This reduces their judgmental tendencies. You are teaching them complexity.",
            "**Phase 2: Sustainable Advocacy (6-12 Months):** Coach them to use a 'Tier System' for battles (Tier 1: Fight, Tier 2: Debate, Tier 3: Let go). They cannot die on every hill; they must learn to prioritize their moral outrage. This prevents compassion fatigue and keeps them effective for the big issues. You are teaching them strategy.",
            "**Phase 3: Cultural Architecture (12-18 Months):** Move from fighting battles to building systems that prevent injustice. Challenge them to write the policy rather than just complaining about the lack of one. This shifts them from a 'warrior' mindset to a 'builder' mindset. You are teaching them legacy."
        ],
        "questions": [
            "Where do you feel the system is failing your values? (Validates feelings and opens constructive problem solving.)",
            "How can you advocate without burning bridges? (Challenges them to be diplomatic without compromising.)",
            "Is this a hill worth dying on? (Helps prioritize battles to avoid compassion fatigue.)",
            "How does flexibility serve the mission here? (Reframes rigidity as a potential obstacle to the mission.)",
            "What do you need right now? (Checks on their emotional depletion.)",
            "Where are you stuck? (Identifies where their moral compass might be locking them.)",
            "How can I help? (Reinforces that they are not alone in the fight.)",
            "What is the goal? (Refocuses on the outcome rather than the principle.)",
            "Where are you moving too fast for the team? (Brings them back to the group.)",
            "How does your tone land when you are stressed? (Checks if passion is perceived as aggression.)"
        ],
        "advancement": "**Delegate Effectively:** Build a team that protects children. They must learn that can multiply their impact by teaching others to care, rather than doing all the caring themselves. Trusting others' hearts is a key step.\n\n**Allow Safe Failure:** Trust that others also care. They need to learn that a mistake by a staff member doesn't mean that staff member is 'bad.' They must separate competence from character.\n\n**Focus on Strategy:** Build systems that prevent injustice. They need to move from reacting to individual crises to preventing them through policy and culture. This is the shift from tactical advocacy to strategic advocacy."
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to. They are the 'Mama Bear' or 'Papa Bear' of the unit.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial. You don't need a one-hour meeting; you need five minutes of real connection. Consistency matters more than duration.\n\n**Backing:** Be candid about where you can back them up (air cover). They need to know you are in their corner. If they feel exposed or unsupported, they will withdraw their loyalty.",
        "thriving": "**Decisive Care:** They fix problems for people immediately. They don't just sympathize; they solve. They use their Director power to remove obstacles for their people.\n\n**Crisis Stabilization:** They become the calm human shield during a crisis. Staff look to them for physical and emotional safety. Their presence alone can de-escalate a room.\n\n**Team Loyalty:** They build a strong 'Us.' The team has a distinct identity and high morale. People protect each other and cover for each other because the Captain has set the standard.",
        "struggling": "**Us vs. Them:** They become hostile toward outsiders (admin, other units). They circle the wagons and view any critique of their team as an attack. They can create a silo that is hard to penetrate.\n\n**Over-Functioning:** They do everyone's job to protect them. They burn themselves out trying to carry the load for 'weaker' team members. They enable underperformance in the name of loyalty.\n\n**Taking Conflict Personally:** They conflate professional disagreement with personal betrayal. If you correct them, they feel unloved. This makes supervision very tricky and emotional.",
        "interventions": [
            "**Phase 1: Delegation of Care (0-6 Months):** Stop being the only fixer; assign care tasks to others. Require them to let someone handle a crisis or plan a party. They must learn that the team can survive without their constant intervention. You are breaking the dependency cycle.",
            "**Phase 2: Organizational Citizenship (6-12 Months):** Expand the circle of loyalty to the whole agency. Challenge them to partner with another unit or department. They need to see that 'Us' includes the whole organization, not just their shift. You are breaking down silos.",
            "**Phase 3: Mentorship (12-18 Months):** Transition from Captain to Admiral (teaching others to build loyalty). Task them with training a new supervisor on how to build culture. This moves them from doing the leading to teaching the leading."
        ],
        "questions": [
            "Are you avoiding this conversation to be kind, or to be safe? (Challenges them to distinguish between genuine care and conflict avoidance.)",
            "How can you be direct and caring at the same time? (Helps integrate their Director style with their Connection motivation.)",
            "Are you protecting them from growth? (Reframes 'rescuing' the team as actually hurting their development.)",
            "How is the team reacting to your directness? (Checks on the impact of their communication style.)",
            "What do you need right now? (A check-in on their own emotional tank.)",
            "Where are you stuck? (Identifies where loyalty might be preventing a necessary decision.)",
            "How can I help? (Reinforces that they have support too.)",
            "What is the goal? (Refocuses on the objective outcome.)",
            "Where are you moving too fast for the team? (Checks if they are making decisions without bringing the 'family' along.)",
            "Who do you need to check in with today? (Leverages their natural strength for connection.)"
        ],
        "advancement": "**Delegate Effectively:** Stop being 'camp parent.' They must prove they can manage managers, not just staff. This means letting go of the daily emotional caretaking.\n\n**Allow Safe Failure:** Learn the team is resilient. They need to see that the team won't break if they step back. This builds their confidence in the system.\n\n**Focus on Strategy:** Expand loyalty to the whole agency. They need to advocate for the organization, not just their unit. This is the shift to executive thinking."
    },
    "Encourager-Achievement": {
        "title": "The Coach",
        "synergy": "Inspirational Performance. They make hard work feel like a game. They believe the team can win and their energy is contagious. They drive results not by demanding them, but by pumping the team up to chase them.",
        "support": "**Reality Checks:** Be the ground to their sky. Validate their enthusiasm but ask 'What is the plan if this goes wrong?' You provide the tether that keeps them from floating away.\n\n**Focus:** Help them pick one lane. They want to achieve everything at once; force them to prioritize. You are the editor of their ambition.",
        "thriving": "**Team Morale:** The unit has high energy and believes they are the best unit in the building. There is a 'swag' to the team. They create a winning culture.\n\n**Rallying:** They can turn a bad shift around with a pep talk. They refuse to let the team wallow in defeat. They are resilient optimists.\n\n**Goal-Smashing:** When locked in, they hit metrics with flair and celebrate loudly. They make success look fun. They normalize high performance.",
        "struggling": "**Overselling:** They promise things they can't deliver to get buy-in. This leads to disappointment and loss of trust later. They write checks their reality can't cash.\n\n**Disorganization:** They are moving so fast and talking so much they lose paperwork or forget details. They leave a wake of administrative chaos. They miss the trees for the forest.\n\n**Impatience:** They get frustrated when the team doesn't share their burning desire to win immediately. They can't understand low energy. They judge the 'plodders.'",
        "interventions": [
            "**Phase 1: Follow-Through (0-6 Months):** Focus on finishing. Require them to complete one project fully before starting the next exciting one. Inspect their work for completion, not just quality. You are teaching discipline.",
            "**Phase 2: Data Discipline (6-12 Months):** Move from 'feeling' to 'fact.' Require them to bring data to supervision, not just stories. 'Show me, don't just tell me.' You are teaching objectivity.",
            "**Phase 3: Grooming Talent (12-18 Months):** Challenge them to let others shine. The 'Coach' needs to get off the field and let the players score. They must learn to win through others. You are teaching delegation."
        ],
        "questions": [
            "How do we keep this energy up when things get boring? (Plans for the inevitable dip in excitement.)",
            "What are the specific steps to get to that vision? (Grounds big ideas in executable tactics.)",
            "Who is doing the work: you or the team? (Checks if they are carrying the ball or coaching.)",
            "How will you track this? (Appeals to Achievement drive while solving disorganization.)",
            "What is the one thing we must finish this week? (Focuses scattered energy on a single priority.)",
            "Who needs the spotlight more than you right now? (Challenges their natural desire to be the star.)",
            "Are you listening or just waiting to speak? (Trains active listening.)",
            "What happens if we miss this goal? (Forces them to consider risks.)",
            "How are you celebrating the team's grind, not just the win? (Ensures they value the work, not just the result.)",
            "Is your enthusiasm masking a problem? (Checks if they are 'spinning' a negative situation.)"
        ],
        "advancement": "**Detail Management:** They must prove they can handle the boring stuff (admin, budgets). If they can't do the paperwork, they can't run the department. They need to show administrative competence.\n\n**Listening:** They need to learn to sit back and let others speak. They must prove they can intake information, not just output it. They need to master the pause.\n\n**Consistency:** Prove they can maintain performance when the excitement fades. They need to show they can grind. They need to be reliable, not just flashy."
    },
    "Encourager-Growth": {
        "title": "The Mentor",
        "synergy": "Developmental Charisma. They see the gold in people and talk it out of them. They make people feel smarter and more capable just by being around them. They lead by selling the team on their own potential.",
        "support": "**Structure:** They have a million ideas; provide the structure to execute one at a time. You are the trellis for their vine. Help them focus their creative energy on the most impactful goals. Prevent them from drowning in their own possibilities.\n\n**Patience:** Remind them that growth is messy and non-linear. They can get discouraged when people slide back or don't grow fast enough. Be the steady hand that reminds them change takes time.",
        "thriving": "**Talent Magnet:** People want to work for them because they feel grown and seen. They attract high-potential staff who want to develop. They build a deep bench of future leaders.\n\n**Culture of Learning:** Mistakes are celebrated as learning opportunities, reducing fear in the unit. They create a safe laboratory for growth where experimentation is encouraged. They normalize failure as part of the process.\n\n**Innovation:** They are constantly bringing in new ideas from books, podcasts, or other units. They keep the agency fresh and relevant. They prevent stagnation by constantly injecting new thought.",
        "struggling": "**Shiny Object Syndrome:** They chase a new initiative every week, confusing the team. The staff gets whiplash from the constant pivots and lack of follow-through. They start many fires but tend few.\n\n**Avoidance of Hard Conversations:** They want to inspire, not correct. They struggle to give negative feedback that might 'hurt' the relationship. They sugarcoat the poison to avoid being the 'bad guy.'\n\n**All Talk:** They talk a great game about development but lack the follow-through to document it. Great visions, poor execution. They can be dreamers who don't do the hard work of implementation.",
        "interventions": [
            "**Phase 1: Closing the Loop (0-6 Months):** Force them to finish what they start. No new ideas until the last one is fully implemented and evaluated. Make them live with their creations long enough to see the flaws. You are teaching them endurance and the value of completion.",
            "**Phase 2: Difficult Feedback (6-12 Months):** Role-play giving 'hard' feedback without the fluff. Teach them that clarity is kind and ambiguity is cruel. They must learn to break the news without breaking the bond. You are teaching assertiveness and professional courage.",
            "**Phase 3: Systems of Growth (12-18 Months):** Turn their informal mentoring into a formal training manual or curriculum. Capture their genius in a document that can survive without them. Move them from individual heroics to systemic impact. You are teaching sustainability."
        ],
        "questions": [
            "Who are you investing in, and who are you ignoring? (Ensures they aren't just mentoring the 'stars' but are also developing the strugglers.)",
            "How do we turn this idea into a habit? (Moves them from inspiration to execution and sustainable practice.)",
            "Are you avoiding the hard truth to be nice? (Challenges the tendency to sugarcoat negative feedback to preserve feelings.)",
            "What is the one skill the team needs right now? (Focuses their broad desire for growth onto a specific, actionable need.)",
            "How are you measuring that improvement? (Adds necessary accountability and data to their development plans.)",
            "Are you talking more than they are? (Reminds them that true mentoring involves deep listening, not just lecturing.)",
            "What did you finish this week? (A hard check on their follow-through and project completion.)",
            "Is this practical, or just interesting? (Filters abstract ideas through the lens of immediate utility for the team.)",
            "How does this help the client today? (Connects their high-level growth goals to immediate client impact.)",
            "What are you reading/learning? (Feeds their motivation by showing genuine interest in their intellect.)"
        ],
        "advancement": "**Execution:** Prove they can implement, not just ideate. They need to show they can land the plane, not just fly it. They need to show tangible results from their visions.\n\n**Toughness:** Prove they can make the hard personnel calls. They need to show they can fire someone if necessary for the good of the team. They need to have a spine, not just a heart.\n\n**Focus:** Prove they can stick to a boring plan for the long haul. They need to show they can survive the mundane aspects of leadership. They need grit to match their vision."
    },
    "Encourager-Purpose": {
        "title": "The Heart of the Mission",
        "synergy": "Passionate Advocacy. They are the soul of the unit. They keep the emotional flame alive. When everyone else is cynical, they are the ones reminding the team why this work matters. They lead with raw emotion and belief.",
        "support": "**Emotional Boundaries:** Help them distinguish between caring and carrying. They will burn out by taking home the trauma of the clients. You must be the wall that keeps the flood out. Teach them the art of detached concern.\n\n**Validation:** Frequently affirm that their heart is a strength, not a weakness. They often feel 'too soft' for the work; remind them that softness is a tool. Validate their empathy as a professional asset.",
        "thriving": "**Cultural Carrier:** They set the emotional tone for the entire workspace. If they are up, the unit is up. They are the thermostat of the team, regulating the emotional temperature. They create warmth and acceptance.\n\n**Advocate:** They are fearless in speaking up for kids, using their persuasion to get resources. They can charm the resources out of administration by making them feel the need. They fight for their people with tenacity.\n\n**Inspiration:** They can make a tired team feel like heroes again. They bring the magic back to the work when it feels like a grind. They renew the spirit of the group.",
        "struggling": "**Emotional Flooding:** They get so wrapped up in the 'story' that they lose objectivity. They might cry in meetings or get irrationally angry at perceived slights. They lose perspective and cannot see the other side.\n\n**Us vs. The System:** They can whip the team into a frenzy against 'cold' administration. They become the ringleader of the rebellion, viewing policy as the enemy of care. They vilify leadership to protect the team.\n\n**Burnout:** They give everything and have nothing left. They crash hard and often abruptly because they have no reserves. They function on adrenaline and emotion until they break.",
        "interventions": [
            "**Phase 1: Boundaries (0-6 Months):** Teach them to leave work at work. 'The badge stays at the door.' Create specific rituals for disconnecting from the emotional weight of the job. You are teaching self-preservation.",
            "**Phase 2: Fact-Checking (6-12 Months):** When they tell a passionate story, ask 'Is that true, or is that how it felt?' Force them to separate emotion from data without invalidating the emotion. You are teaching objectivity.",
            "**Phase 3: Channeling Passion (12-18 Months):** Give them a platform (e.g., orientation training) where their passion is an asset, not a distraction. Let them light fires in appropriate places where energy is needed. You are teaching deployment."
        ],
        "questions": [
            "Is this feeling a fact? (Helps them separate their strong emotions from objective reality to prevent spiraling.)",
            "How can you care without carrying? (A mantra for preventing emotional burnout and establishing professional distance.)",
            "Are you whipping the team up or calming them down? (Checks how they are using their influence and asks them to be responsible for the room's energy.)",
            "What is the most ethical choice, even if it feels bad? (Challenges them to do the hard right thing over the emotional thing.)",
            "Who is supporting you? (Checks on their support network to ensure they aren't isolated in their caring.)",
            "Is this your battle to fight? (Helps them prioritize their advocacy to prevent exhaustion and compassion fatigue.)",
            "How does the policy actually help the child? (Reframes 'cold' rules as tools for care to help them make peace with the system.)",
            "Are you listening to the logic, or just the tone? (Encourages them to hear the substance of a directive, bypassing their emotional filter.)",
            "What do you need to let go of today? (A ritual for release that helps them decompress and leave work at work.)",
            "How can we use your voice for good? (Validates their desire to speak up and empowers them to be a positive changemaker.)"
        ],
        "advancement": "**Objectivity:** Prove they can make dispassionate decisions. They need to show they can look at a spreadsheet without crying. They need to be cool-headed in a crisis.\n\n**Policy:** Understand the legal/fiscal reasons behind rules. They need to learn the language of administration and risk management. They need to see the big picture beyond the immediate emotion.\n\n**Resilience:** Bounce back without drama. They need to show they can take a hit and keep moving without needing constant reassurance. They need emotional toughness."
    },
    "Encourager-Connection": {
        "title": "The Team Builder",
        "synergy": "Social Cohesion. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy. They lead by making the workplace feel like a community.",
        "support": "**Hard Decisions:** Step in to be the 'bad guy' so they don't have to burn social capital. They struggle to be the enforcer, so lend them your spine until they grow their own. eventually, you must train them to make the call themselves.\n\n**Focus:** Remind them that work is the goal, fun is the method. Don't let the party overtake the mission. Keep the main thing the main thing. Ensure that the social cohesiveness results in productivity, not just distraction.",
        "thriving": "**Zero Turnover:** People stay because they love the team. They create a sticky culture that is hard to leave. Staff feel at home and supported. They save the agency money by retaining talent.\n\n**Conflict Resolution:** They talk things out and smooth over rough edges. They keep the social machinery oiled. They heal rifts before they become canyons. They mediate disputes naturally.\n\n**Joy:** There is laughter on the unit, which is therapeutic. They make the heavy work lighter. They bring the fun to the grind. They prevent the atmosphere from becoming toxic.",
        "struggling": "**The Country Club:** Too much socializing, not enough work. The unit becomes a hangout spot where standards slip. Productivity drops because everyone is having too much fun.\n\n**Gossip:** Their need to be 'in the know' and close to everyone can spiral into drama. They trade secrets for connection. They become the center of the rumor mill.\n\n**Favoritism:** They struggle to lead people they don't personally like. They create an 'in-crowd' and an 'out-crowd.' They alienate the outliers who don't fit their vibe.",
        "interventions": [
            "**Phase 1: Professionalism (0-6 Months):** Define the line between 'friend' and 'colleague' explicitly. They often blur these lines, leading to confusion when authority is needed. Create clear rules about socializing on the clock versus off the clock. Explain that leadership requires a degree of separation to remain objective. You are teaching them boundaries, which protects them from accusations of favoritism later. This foundational step is crucial before they can lead effectively.",
            "**Phase 2: Inclusive Leadership (6-12 Months):** Challenge them to connect with the staff member they like the least. Their natural tendency is to surround themselves with people who reflect their energy. Force them to build a bridge to the outlier or the quietest person in the room. This breaks up their clique and demonstrates that they can lead everyone, not just their friends. You are teaching equity and expanding their influence beyond their comfort zone.",
            "**Phase 3: Task Focus (12-18 Months):** Assign them a project that requires solitude or deep focus to build that muscle. They rely heavily on collaboration and social energy to get through the day. Make them work without the audience to prove they can self-regulate and deliver results independently. This prevents them from using 'collaboration' as a cover for socializing. You are teaching independence and task discipline."
        ],
        "questions": [
            "Are we having fun, or are we working? (A gentle reminder of the primary task to re-center them.)",
            "Who is on the outside of the circle? (Challenges them to expand their clique and practice inclusion.)",
            "Are you avoiding the conflict to keep the peace? (Identifies false harmony and the cost of niceness.)",
            "How can you deliver that news directly? (Coaches assertiveness and provides a script for hard talks.)",
            "Are you gossiping or venting? (Distinguishes between toxic and healthy speech to check integrity.)",
            "Can you be friendly without being their best friend? (Sets a professional boundary and defines the role.)",
            "How does the work get done if we talk all day? (An operational reality check that points to productivity.)",
            "What is the cost of not holding them accountable? (Reframes accountability as care to show that 'nice' can be harmful.)",
            "Who needs to hear from you today? (Leverages their strength and directs their social energy.)",
            "How are you protecting your own energy? (Checks for fatigue, as constant connection is exhausting.)"
        ],
        "advancement": "**Separation:** Prove they can lead without needing to be liked. They need to be respected first, liked second. This is the hardest hurdle for them, as they fear rejection. They must learn to stand alone on a decision if it is right for the business.\n\n**Confidentiality:** Prove they can keep secrets. They need to show they aren't a sieve for information. Their desire to connect often leads to oversharing, which destroys executive trust. They must learn that information is not currency for friendship.\n\n**Productivity:** Prove they can drive results, not just vibes. They need to show they can hit the numbers and hold others to them. A happy team that misses every deadline is a failure. They need to balance morale with output."
    },
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "synergy": "Methodical Progress. They don't sprint; they march with purpose and precision. They get the team to the finish line by ensuring everyone knows their role and the process is solid. They are the engine that keeps the unit moving forward without chaos or drama.",
        "support": "**Decision Speed:** Push them to decide even when they don't have 100% consensus. Appeal to their need to 'finish' the task to overcome their hesitation. Frame indecision as a failure to achieve the goal. Remind them that a good decision today is better than a perfect decision next week.\n\n**Validation:** Praise the quiet work of organization that often goes unseen. Notice the spreadsheets, the schedules, and the well-run meetings. Acknowledge that their structure allows the rest of the team to function. Validate their role as the stabilizer of the group.",
        "thriving": "**Consistent Wins:** They hit the metrics every month without drama or panic. They are boringly successful in the best way possible. They are the metronome of the department, keeping the beat steady. You can set your watch by their performance.\n\n**Efficient Meetings:** They run meetings where everyone feels heard, but action items are clearly assigned. They master the follow-up to ensure accountability. They respect everyone's time by keeping things on track. They balance voice with velocity.\n\n**Project Management:** They are excellent at long-term implementation of complex initiatives. They don't drop the ball on details or deadlines. They keep the trains running on time regardless of the weather. They turn strategy into reality through execution.",
        "struggling": "**Analysis Paralysis:** They want to achieve the goal (Achievement) but want everyone to agree on how (Facilitator), leading to stalls. They get stuck in the 'how' and lose sight of the 'what.' They freeze at the intersection of speed and agreement. They delay action to avoid friction.\n\n**Frustration with Chaos:** They hate last-minute changes that disrupt the plan they worked hard to create. They can be rigid when the plan changes unexpectedly. They struggle to pivot quickly without a new plan in place. They view spontaneity as a threat to efficiency.\n\n**Silent Resentment:** They work hard and resent those who don't, but won't say it aloud to avoid conflict. They steam internally while picking up the slack. They become passive-aggressive instead of direct. They let resentment build until it affects their morale.",
        "interventions": [
            "**Phase 1: Speaking Up (0-6 Months):** Call on them first in meetings to break the habit of waiting. Force them to voice their messy thoughts before they are fully formed. You are teaching courage and the value of imperfect contribution. This builds their confidence to speak without a script.",
            "**Phase 2: Imperfect Action (6-12 Months):** Assign a task with an impossible deadline to force a 'good enough' decision. Make them move before they are fully ready to test their agility. You are teaching them that speed is a quality of its own. This breaks their addiction to total preparation.",
            "**Phase 3: Direct Delegation (12-18 Months):** Challenge them to assign tasks without asking for volunteers or consensus. They must learn to command the room, not just coordinate it. You are teaching authority and the necessity of hierarchy in crisis. This shifts them from facilitator to leader."
        ],
        "questions": [
            "What is the 'good enough' decision right now? (Combats analysis paralysis and perfectionism.)",
            "Are you waiting for everyone to agree? (Identifies the bottleneck in the decision process.)",
            "How can we move forward even if it's messy? (Prioritizes progress over process and comfort.)",
            "Who is holding up the project? (Identifies blockers and asks for accountability.)",
            "What have you achieved this week? (Feeds the achievement drive and tracks progress.)",
            "Is the process helping or hurting the goal? (Checks for bureaucracy and over-engineering.)",
            "How can you say 'no' to protect the timeline? (Empowers boundaries and prioritization.)",
            "Who needs to be cut out of the decision loop? (Streamlines communication and reduces noise.)",
            "Are you doing the work to avoid asking others? (Checks for conflict avoidance and martyrdom.)",
            "What is the next step? (Focuses on immediate action to break inertia.)"
        ],
        "advancement": "**Speed:** Make faster decisions with less data. They need to prove they can move at the speed of the crisis. They need to show agility in a changing environment. They must learn to trust their gut.\n\n**Conflict:** Call out underperformance directly and verbally. They need to show they can have the hard talk without crumbling. They need to stop being so nice and start being effective. They must prioritize the standard over the feeling.\n\n**Vision:** Look beyond the checklist to the strategy. They need to lift their eyes to the horizon and see what's coming. They need to see the 'why' behind the 'what.' They must transition from operator to architect."
    },
    "Facilitator-Growth": {
        "title": "The Patient Gardener",
        "synergy": "Organic Development. They don't force growth; they create the conditions for it. They are incredibly patient with difficult staff or youth, believing that everyone can change if given enough time and support. They nurture rather than drive.",
        "support": "**Urgency:** You must provide the urgency, or they will let things grow forever. Remind them that sometimes we need to prune (fire/discipline) for the health of the whole. Be the winter to their summer to create balance. Help them see that time is a limited resource.\n\n**Outcome Focus:** Remind them that growth must eventually result in performance. Potential is not enough; we need kinetic energy and results. Help them connect development to deliverables and metrics. Ensure that the learning leads to doing.",
        "thriving": "**Turnaround Specialist:** They can take a failing staff member and slowly rehabilitate them. They save people others would fire by finding their hidden strengths. They have the magic touch for restoration and second chances. They see gold where others see dirt.\n\n**Deep Listening:** They understand the nuance of the unit better than anyone. They know the root system of the culture and the hidden dynamics. They see what others miss because they are paying attention. They diagnose the disease, not just the symptom.\n\n**Sustainable Pace:** They model a healthy work-life balance that prevents burnout. They run a marathon pace, not a sprint, ensuring longevity. They are in it for the long haul and help others do the same. They create a calm in the storm.",
        "struggling": "**Tolerance of Mediocrity:** They give people too many chances in the name of 'growth.' They enable bad behavior by refusing to set hard limits. They can't let go of the hope that someone will change, even when evidence says otherwise. They confuse kindness with weakness.\n\n**Slow to Launch:** They study the problem forever without fixing it. They get stuck in diagnosis and analysis paralysis. They over-analyze and under-act, waiting for perfect conditions. They value the theory over the practice.\n\n**Fear of Judgment:** They struggle to evaluate people because they know how hard growth is. They don't want to play judge or executioner. They avoid the hard call to protect the relationship and the person's feelings. They struggle to give a failing grade.",
        "interventions": [
            "**Phase 1: Timelines (0-6 Months):** Put a date on development goals. 'They have 3 months to improve, not forever.' Create a kill switch for their patience to prevent endless enabling. You are teaching them limits and the value of time as a resource. This forces them to prioritize.",
            "**Phase 2: Judgment (6-12 Months):** Practice evaluating performance objectively based on data. 'Is this good or bad?' Force them to use binary labels to sharpen their discernment. You are teaching clarity and standards over potential. This helps them separate the person from the performance.",
            "**Phase 3: Pruning (12-18 Months):** They must terminate or discipline a staff member to learn that protection isn't always love. They must experience the necessity of the cut for the greater good of the team. You are teaching stewardship and the hard side of leadership. This proves they can protect the garden."
        ],
        "questions": [
            "How long is too long to wait for improvement? (Setting a necessary boundary on patience.)",
            "Is this person actually growing, or are we just hoping? (Demanding evidence over optimism.)",
            "What is the cost to the team of keeping this person? (Highlighting the impact on others.)",
            "Are you learning, or just stalling? (Differentiating study from procrastination.)",
            "What is the lesson here? (Leveraging their growth mindset.)",
            "How can you speed up this process? (Injecting urgency.)",
            "Who are you neglecting by focusing on the struggler? (Reallocating attention.)",
            "What does 'accountability' look like to you? (Defining a hard term for a soft leader.)",
            "Are you afraid to judge? (Naming the fear.)",
            "What is the next step today? (Forcing action.)"
        ],
        "advancement": "**Decisiveness:** Act on the data, not just the hope. They must show they can call the game based on facts. They need to be firm when necessary to protect the standard. They cannot lead if they cannot decide.\n\n**Speed:** Move faster than feels comfortable. They must match the market's pace and urgency. They need to accelerate their decision-making to keep up with the organization. They need to learn to sprint when needed.\n\n**Standards:** Hold the line on quality without apology. They must show they have a floor for performance that cannot be crossed. They need to demand excellence, not just effort, from their team. They must learn that standards protect the mission."
    },
    "Facilitator-Purpose": {
        "title": "The Moral Compass",
        "synergy": "Principled Consensus. They are the quiet conscience of the team. They ensure that the team doesn't just get things done, but gets them done right. They build unity around shared values and mission, creating a deeply ethical culture.",
        "support": "**Validation of Values:** Regularly affirm their role as the ethical standard-bearer. Tell them, 'I appreciate that you always keep the client's needs in focus.' Reinforce that their conscience is an asset, not a liability. Make them feel seen for their integrity.\n\n**Decision Frameworks:** Give them a framework for making 'imperfect' decisions (e.g., 'We are choosing the least bad option'). Help them navigate the gray areas where values conflict. Provide tools for ethical triage. Help them accept trade-offs.",
        "thriving": "**Ethical Anchor:** When the team is confused, they bring everyone back to the mission statement. They center the boat in the storm. They provide true north when the map is lost. They remind everyone who we serve.\n\n**Unified Team:** They create a team culture where everyone feels respected and heard. They build a moral community based on trust. They foster deep connections among staff. They create a safe harbor for the team.\n\n**Trust:** Staff trust them implicitly because they know they are not self-interested. They have high credibility because their motives are pure. They walk the talk and model the values. They are seen as the 'good' leader.",
        "struggling": "**Moral Paralysis:** They refuse to make a decision because no option is perfectly ethical. They freeze in the face of ambiguity. They get stuck in the dilemma and stall the team. They let the perfect be the enemy of the good.\n\n**Passive Resistance:** Instead of arguing openly, they simply don't do the things they disagree with. They silently rebel against policies they dislike. They become a bottleneck for implementation. They vote with their feet (or their inaction).\n\n**Judgment:** They may silently judge others who are more pragmatic or business-minded. They can become self-righteous and isolated. They separate themselves from the 'impure' parts of the organization. They create an 'us vs. them' dynamic based on morals.",
        "interventions": [
            "**Phase 1: The '51% Decision' (0-6 Months):** Teach them that in leadership, you often have to move with only 51% certainty. Require them to make calls even when they are uncomfortable and the path isn't perfectly clear. You are teaching pragmatism and the necessity of action. Inaction is also a choice with moral consequences.",
            "**Phase 2: Voice Training (6-12 Months):** Challenge them to speak their dissent in the meeting, not after it in the hallway. They need to learn to be a 'vocal conscience' rather than a silent judge. You are teaching courage and direct communication. Their voice is needed to shape the decision, not just critique it.",
            "**Phase 3: Operational Ethics (12-18 Months):** Task them with creating a system or policy that institutionalizes their values. Move them from complaining about the system to building a better one. You are teaching structural change and legacy. Give them the power to fix what they think is broken."
        ],
        "questions": [
            "What moral tension are you holding right now? (Acknowledges ethical weight.)",
            "How can you speak up for your values effectively? (Moves them to active influence.)",
            "Are you staying neutral when you should take a stand? (Challenges passivity.)",
            "How does your silence impact the team? (Shows the cost of inaction.)",
            "What do you need right now? (Check-in on depletion.)",
            "Where are you stuck? (Identifies the ethical dilemma.)",
            "How can I help? (Offers partnership.)",
            "What is the goal? (Refocuses on the outcome.)",
            "Where do you need to make a 51% decision? (Prompts action.)",
            "Are you waiting for consensus that isn't coming? (Reality check.)"
        ],
        "advancement": "**Decisiveness:** They must prove they can make hard calls when it is necessary, even if it hurts feelings. They need to show they can act in the face of ambiguity. They cannot wait for a perfect world to lead.\n\n**Public Speaking:** They need to get comfortable projecting their voice and values to a larger audience. They need to lead out loud and inspire others. They must become an evangelist for the mission, not just a guardian.\n\n**Pragmatism:** They need to demonstrate they understand the business realities alongside the ethical ones. They need balance between money and mission. They must learn that no margin means no mission."
    },
    "Facilitator-Connection": {
        "title": "The Peacemaker",
        "synergy": "Harmonious Inclusion. They create a psychological safety net for the team. They lead by relationship, ensuring that staff feel loved, supported, and heard so they can do the hard work of care.",
        "support": "**Conflict Coaching:** They are likely terrified of conflict and will avoid it. Role-play hard conversations with them to build muscle memory. Be their sparring partner in a safe space. Build their confidence to say hard things.\n\n**Permission to Disappoint:** Explicitly tell them, 'It is okay if they are mad at you.' Absolve them of the need to please everyone all the time. Free them from the guilt of making a tough call. Remind them that leadership requires making people unhappy sometimes.",
        "thriving": "**High Retention:** People rarely leave their team because it feels good to work there. They build deep loyalty and connection. Staff feel loved and seen. They stay for the leader, not the paycheck.\n\n**Psychological Safety:** Staff admit mistakes freely because they aren't afraid of shame. The environment is low-fear and high-trust. People feel safe to fail and grow. They create a learning organization.\n\n**De-escalation:** They can calm a room just by walking in. They are a sedative for chaos and stress. They bring the peace to high-stress situations. Their presence lowers the blood pressure of the unit.",
        "struggling": "**The Doormat:** They let staff walk all over them to avoid a fight. They lose respect and authority. They become a pushover who cannot enforce rules. They get used by stronger personalities.\n\n**Exhaustion:** They carry everyone's emotional baggage and trauma. They develop compassion fatigue from over-caring. They burn out because they have no boundaries. They deplete themselves to feed others.\n\n**Triangulation:** Instead of addressing an issue directly, they complain to others to vent. They create side conversations to avoid the main conflict. They avoid the source of the pain. They create drama by trying to avoid it.",
        "interventions": [
            "**Phase 1: Direct Address (0-6 Months):** Require them to have one direct, hard conversation per week. Inspect the result and ask how it felt. You are building calluses on their empathy. This proves they can survive conflict.",
            "**Phase 2: Disappointing Others (6-12 Months):** Challenge them to make a decision they know will be unpopular with the team. Support them through the backlash but make them stand firm. You are teaching resilience and the difference between being liked and being respected.",
            "**Phase 3: Self-Protection (12-18 Months):** Teach them to set boundaries on their time and empathy. They must learn to say 'no' to protect their own health. You are teaching sustainability and self-preservation. They cannot pour from an empty cup."
        ],
        "questions": [
            "What boundaries do you need to set to protect your energy? (Crucial for preventing empathy fatigue.)",
            "Are you listening too much and leading too little? (Highlights the imbalance.)",
            "Who is taking care of you? (Reminds them they have needs too.)",
            "Is your silence creating confusion? (Reframes silence as withholding leadership.)",
            "What do you need right now? (Self-care check.)",
            "Where are you stuck? (Identifies conflict avoidance.)",
            "How can I help? (Offers support.)",
            "What is the goal? (Refocuses on the task.)",
            "Where do you need to make a 51% decision? (Pushes for action.)",
            "Are you waiting for consensus that isn't coming? (Reality check.)"
        ],
        "advancement": "**Conflict:** Prove they can handle a fight without crumbling. They need to show toughness and the ability to hold a line. They must be able to deliver bad news.\n\n**Separation:** Prove they can lead friends and former peers. They need to show authority and professional distance. They must prioritize the organization over the relationship.\n\n**Results:** Prove they value outcomes as much as feelings. They need to show performance metrics, not just morale scores. They must demonstrate that a happy team is also a productive team."
    },
    "Tracker-Achievement": {
        "title": "The Architect",
        "synergy": "Systematic Perfection. They build the systems that allow the team to succeed. They are the engineers of the unit. They ensure that nothing falls through the cracks and that every procedure is followed to the letter.",
        "support": "**Clarity:** Be hyper-clear about expectations and deliverables. Ambiguity is torture for them and leads to anxiety. If the instructions are vague, they will freeze or ask a million questions. Provide the map and the compass.\n\n**Time:** Give them the time to do it right. If you rush them, they will panic because they cannot ensure quality. Respect their need for precision and thoroughness. Don't force speed over quality unless necessary.",
        "thriving": "**Flawless Execution:** Their paperwork is perfect and their data is clean. Their audits are 100% compliant. You never have to check their work twice because they already checked it three times. They are meticulous and reliable.\n\n**System Builder:** They create new trackers or logs that save everyone time. They solve problems permanently by fixing the system, not just the symptom. They build infrastructure that outlasts them.\n\n**Reliability:** If they say it is done, it is done right. They are the most dependable person on the staff for technical tasks. They keep their word and their deadlines. They are a safe pair of hands.",
        "struggling": "**Rigidity:** They refuse to bend the rules even when it makes sense for the client. They value the policy over the person. They become the 'bureaucrat' who blocks progress. They lack flexibility and empathy in the moment.\n\n**Micromanagement:** If they lead others, they hover to ensure it is done 'perfectly.' They drive their staff crazy with minor corrections. They can't let go of control because they don't trust others' standards.\n\n**Critique:** They constantly point out others' errors and flaws. They become the 'compliance police,' alienating their peers. They focus on the negative and the gap, rather than the progress.",
        "interventions": [
            "**Phase 1: Flexibility (0-6 Months):** Challenge them to identify one rule that can be bent for the greater good. Force them to operate in the gray and make a judgment call. You are teaching nuance and the spirit of the law vs. the letter. This softens their rigidity.",
            "**Phase 2: People over Process (6-12 Months):** Require them to mentor a disorganized staff member without doing the work for them. They must learn to tolerate imperfection in others and coach rather than correct. You are teaching patience and people management.",
            "**Phase 3: Big Picture (12-18 Months):** Ask them to explain why the system exists, not just how it works. Move them from the weeds to the sky to see the strategic vision. You are teaching strategy and organizational thinking. This expands their scope."
        ],
        "questions": [
            "How can you measure effort, not just outcome? (Humanizes their leadership.)",
            "Are you valuing the data more than the person? (Direct check on priorities.)",
            "Where is flexibility needed right now? (Challenges rigidity.)",
            "How can you support the person, not just the process? (Coaches support.)",
            "What do you need right now? (Self-check.)",
            "Where are you stuck? (Identifies the block.)",
            "How can I help? (Reduces isolation.)",
            "What is the goal? (Re-centers on the objective.)",
            "Are you focusing on the rule or the relationship? (Forces a choice.)",
            "What is 'good enough' for right now? (Combats perfectionism.)"
        ],
        "advancement": "**Flexibility:** Prove they can handle chaos without breaking. They need to show adaptability when the plan fails. They must be able to pivot without panic.\n\n**Delegation:** Prove they can trust others to do the work, even imperfectly. They need to let go of the control to scale their impact. They must learn to manage outcomes, not just methods.\n\n**Warmth:** Prove they can connect with people, not just papers. They need to build relationships to influence the team. They must learn that leadership is a social activity."
    },
    "Tracker-Growth": {
        "title": "The Technical Expert",
        "synergy": "Knowledge Mastery. They are the walking encyclopedia of the agency. They know every rule, every regulation, and every loophole. They lead by being the authority that everyone turns to for the answer.",
        "support": "**Resources:** Give them access to the information they crave. Do not gatekeep the data or the policy. Open the books and let them read. Feed their mind with the details they need to feel secure.\n\n**Challenge:** Give them a problem that no one else can solve. They love a puzzle that tests their limits. Test their skills with a high-level project. Let them prove their worth through intellectual combat.",
        "thriving": "**Problem Solver:** They fix the technical issues that stump everyone else. They are the 'IT support' for the program logic. They find the solution where others see a dead end. They are invaluable in a crisis.\n\n**Teacher:** They patiently explain complex systems to others. They raise the unit's IQ by sharing what they know. They share the knowledge freely. They empower the team through education.\n\n**Innovator:** They find new tools or methods to make the work better. They upgrade the operating system of the team. They modernize the work. They are constantly tweaking the machine for better performance.",
        "struggling": "**Arrogance:** They can make others feel stupid for not knowing the rules. They weaponize their knowledge to dominate. They talk down to people who are less technical. They value IQ over EQ.\n\n**Over-Complication:** They design systems that are too complex for anyone else to use. They engineer for experts, not users. They lose the audience with jargon. They create barriers to entry.\n\n**Disengagement:** If they stop learning, they check out completely. They cannot tolerate stagnation or boredom. They get bored easily if the work becomes routine. They need constant stimulation.",
        "interventions": [
            "**Phase 1: Simplification (0-6 Months):** Challenge them to explain a complex idea to a layperson without using jargon. You are teaching communication and accessibility. This forces them to distill their knowledge into utility.",
            "**Phase 2: Emotional Intelligence (6-12 Months):** Require them to mentor someone based on their potential, not their current knowledge. Focus on the relationship, not the data. You are teaching empathy and patience with learners. This builds their soft skills.",
            "**Phase 3: Strategic Vision (12-18 Months):** Ask them to solve a problem where there is no 'right' answer, only trade-offs. Move them away from black-and-white thinking. You are teaching executive judgment and ambiguity. This prepares them for higher leadership."
        ],
        "questions": [
            "Are you focusing on the system or the person? (Re-centers humanity.)",
            "What is 'good enough' for today? (Sets limits on perfection.)",
            "Are you correcting or coaching? (Distinguishes fixing errors vs people.)",
            "How can you make it safe to make mistakes? (Reduces fear.)",
            "What do you need right now? (Self-check.)",
            "Where are you stuck? (Identifies paralysis.)",
            "How can I help? (Support offer.)",
            "What is the goal? (Focuses on outcome.)",
            "Are you focusing on the rule or the relationship? (Asks for balance.)",
            "What is 'good enough' for right now? (Anti-perfectionism.)"
        ],
        "advancement": "**Communication:** Prove they can speak simply and clearly. They need to translate the technical to the practical for leadership. They must be understood by everyone, not just experts.\n\n**Empathy:** Prove they can care about people who aren't experts. They need to show patience with learners and strugglers. They must value the person, not just the brain.\n\n**Strategy:** Prove they can think about the 'why,' not just the 'how.' They need to see the business case and the mission impact. They must connect their expertise to the organizational goals."
    },
    "Tracker-Purpose": {
        "title": "The Guardian",
        "synergy": "Protective Compliance. They believe that following the rules is the highest form of caring. They protect the mission by ensuring that the agency never gets in trouble. They are the shield that keeps the organization safe from external threat.",
        "support": "**Explanation:** Explain the 'why' behind every change in policy. If they think a change endangers the mission, they will block it. Give them the rationale so they can get on board.\n\n**Validation:** Validate their fears and concerns. Don't dismiss their anxiety; thank them for spotting the risk, then explain how you will mitigate it. Honor their watchfulness as a skill.",
        "thriving": "**Safety Net:** They catch the errors that would cause a lawsuit or a licensing violation. They save the agency's life by finding the needle in the haystack. They are the backstop that prevents failure.\n\n**Moral Consistency:** They ensure that we do what we say we do. They close the gap between values and behavior. They keep us honest and aligned with our mission.\n\n**Reliability:** You can trust them with the most sensitive tasks. They are a vault for secrets and safety. They are dependable and consistent.",
        "struggling": "**Bureaucracy:** They use rules to block necessary action. They value the form over the child. They get stuck in red tape and slow everything down. They lose the spirit of the law.\n\n**Fear-Mongering:** They constantly predict disaster and doom. They are the 'Chicken Little' of the unit. They spread anxiety to the rest of the team. They see risk everywhere.\n\n**Judgment:** They view errors as moral failings. If you mess up the paperwork, you don't care about the kids. They judge harshly and lack grace. They alienate teammates with their rigidity.",
        "interventions": [
            "**Phase 1: Risk Assessment (0-6 Months):** When they flag a risk, ask them to rate it 1-10. Teach them that not all risks are fatal. You are teaching perspective and triage. This helps them calm down.",
            "**Phase 2: The 'Why' of Flexibility (6-12 Months):** Show them a case where breaking a rule saved a kid. Challenge their black-and-white thinking with real-world complexity. You are teaching nuance and judgment. This softens their approach.",
            "**Phase 3: Solution Focus (12-18 Months):** Don't let them bring a problem without a solution. Move them from 'Stop' to 'How.' You are teaching leadership and agency. This turns them into problem solvers."
        ],
        "questions": [
            "How can you protect the mission without being rigid? (Asks for balance.)",
            "Are you using rules to manage your anxiety? (Exposes the root.)",
            "Is this rule serving the child right now? (Re-centers the mission.)",
            "How can you explain the 'why' behind the rule? (Coaches communication.)",
            "What do you need right now? (Self-check.)",
            "Where are you stuck? (Identifies fear-based stalling.)",
            "How can I help? (Support offer.)",
            "What is the goal? (Refocuses on mission.)",
            "Are you focusing on the rule or the relationship? (Forces a choice.)",
            "What is 'good enough' for right now? (Risk tolerance check.)"
        ],
        "advancement": "**Risk Tolerance:** Prove they can take a calculated risk. They need to show courage to act when the outcome isn't guaranteed. They must learn that growth requires risk.\n\n**Flexibility:** Prove they can adapt to change without panic. They need to show agility in a shifting landscape. They must learn to bend without breaking.\n\n**Vision:** Prove they can see the forest, not just the trees. They need to see the big picture and the long-term goal. They must rise above the daily compliance to see the strategy."
    },
    "Tracker-Connection": {
        "title": "The Reliable Rock",
        "synergy": "Servant Consistency. They show their love for the team by doing the work perfectly. They are the backbone of the unit. They don't want the spotlight; they just want to be useful and safe within the group.",
        "support": "**Notice the Details:** Notice when they refill the copier or clean the breakroom. Small praises mean the world to them. Validate the invisible labor that keeps the office running. Show them you see them.\n\n**Change Management:** Hold their hand through change. Explain how the new way will help the people they love. Ease their anxiety about the unknown. Be their anchor during transitions.",
        "thriving": "**Steady Presence:** They are always there, always on time, always prepared. They are the anchor in the storm for the team. They are consistent and dependable. They provide stability.\n\n**Helper:** They use their skills to help others succeed. They are the best assistant manager you could ask for. They support the lead without ego. They make everyone else look good.\n\n**Culture Keeper:** They maintain the traditions and the history of the unit. They remember the birthdays and the anniversaries. They keep the family together through ritual. They nurture the bond.",
        "struggling": "**Overwhelmed:** They say 'yes' to everything to please people and then drown in the details. They cannot set boundaries. They burn out quietly without complaining. They suffer in silence.\n\n**Passive Aggressive:** If they feel unappreciated, they will slow down or withdraw. They punish you with silence and minimum effort. They resent the lack of thanks. They become stubborn.\n\n**Resistance to Change:** They dig their heels in when you try to change a routine. They love the rut because it is safe. They fear the new and the unknown. They block innovation.",
        "interventions": [
            "**Phase 1: Saying No (0-6 Months):** Practice saying 'no' to a request. Teach them that boundaries are healthy and necessary. You are teaching self-respect and capacity management. This prevents burnout.",
            "**Phase 2: Vocalizing Needs (6-12 Months):** Ask them what they need in every meeting. Force them to take up space and voice their desires. You are teaching assertiveness. This helps them become a partner, not just a helper.",
            "**Phase 3: Leading Change (12-18 Months):** Ask them to help a new person adapt to the unit. Use their connection drive to overcome their fear of the new. You are teaching mentorship and adaptability. This expands their role."
        ],
        "questions": [
            "How can you show care in a way they understand? (Challenges them to use words, not just tasks.)",
            "Are you doing too much for others? (Checks for over-functioning.)",
            "Do they know you care? (Reality check on communication.)",
            "Where do you need help carrying the load? (Encourages delegation.)",
            "What do you need right now? (Validates their needs.)",
            "Where are you stuck? (Identifies routine rigidity.)",
            "How can I help? (Support offer.)",
            "What is the goal? (Re-centers on outcome.)",
            "Are you focusing on the rule or the relationship? (Asks for balance.)",
            "What is 'good enough' for right now? (Lowers the bar.)"
        ],
        "advancement": "**Voice:** Prove they can speak up in a meeting. They need to be heard to lead. They must learn to advocate for themselves and others verbally.\n\n**Boundaries:** Prove they can stop over-functioning. They need to sustain themselves to lead others. They must learn to protect their time.\n\n**Flexibility:** Prove they can handle a new way of doing things. They need to adapt to grow. They must show they can navigate change without freezing."
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
        "cheat_fuel": m_data.get('strategies_bullets')
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
    
    # --- SECTION 6: THE SUPERVISOR'S HUD (REWORKED) ---
    st.subheader("6. The Supervisor's HUD (Heads-Up Display)")
    st.info("This dashboard is your monthly maintenance checklist. Use it to diagnose burnout risks before they become resignations.")

    # 1. Stress Signature
    stress_data = {
        "Director": {
            "signal": "Becomes aggressive, micromanages, and stops listening.",
            "root_cause": "They feel a loss of control or forward momentum. They are compensating by trying to force speed.",
            "strategy": "Stop talking and start doing. Give them a specific, solvable problem to own immediately to restore their sense of agency.",
            "rx": ["Remove a barrier they can't move.", "Give them a 'win' to chase.", "Shorten the meeting."]
        },
        "Encourager": {
            "signal": "Becomes silent, withdrawn, or agrees to everything (martyrdom) while resentful.",
            "root_cause": "They feel disconnected, unappreciated, or unsafe. They are 'checking out' to protect their emotions.",
            "strategy": "Re-establish relational safety before addressing tasks. They cannot perform if they feel isolated.",
            "rx": ["Schedule face time (no agenda).", "Validate their emotional load.", "Publicly praise a specific contribution."]
        },
        "Facilitator": {
            "signal": "Becomes paralyzed, asks for endless data, and refuses to make a decision.",
            "root_cause": "They fear making an unfair decision or upsetting the harmony. They are stalling to avoid conflict.",
            "strategy": "Remove the burden of the final call. Step in and take responsibility for the decision so they feel safe.",
            "rx": ["Give a clear deadline.", "Take the blame for a hard decision.", "Ask 'What is the risk of doing nothing?'"]
        },
        "Tracker": {
            "signal": "Becomes rigid, quotes policy excessively, and focuses on minor errors.",
            "root_cause": "They fear chaos, error, or liability. They are grasping for certainty in a chaotic environment.",
            "strategy": "Restore order. Provide clarity, written instructions, and protection from last-minute changes.",
            "rx": ["Give them the 'why' behind the chaos.", "Protect them from last-minute changes.", "Explicitly define 'good enough'."]
        }
    }
    
    s_dat = stress_data.get(p_comm, {})
    
    with st.container(border=True):
        st.markdown("#### 🚨 Stress Signature (Early Warning System)")
        with st.expander("🎓 **Training: How to read behavior as language**"):
             st.markdown("""
             **What this is:** High performers rarely admit they are drowning until they quit. Instead, they "act out" their stress profile.
             **Why it matters:** Behavior change is a lagging indicator of burnout. If you see these signals, their "emotional battery" is already red.
             **How to use:** Do not discipline the behavior immediately. Treat it as a symptom. Ask: "I see [Signal], which usually means you are feeling [Root Cause]. How can I help?"
             """)
        
        col_sig, col_rx = st.columns([1, 1])
        with col_sig:
            st.error(f"**The Signal (Watch for this):**\n{s_dat.get('signal')}")
            st.caption(f"**Psychological Root Cause:** {s_dat.get('root_cause')}")
        with col_rx:
            st.success(f"**The Antidote (Do This):**\n{s_dat.get('strategy')}")
            st.write("**Specific Actions:**")
            for r in s_dat.get('rx', []):
                st.write(f"• {r}")

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
        with st.expander("🎓 **Training: Friction vs. Fuel**"):
             st.markdown("""
             **The Equation:** *Retention = (Fuel - Friction) x Connection*
             **Friction:** The daily annoyances that drain energy. For a Director, waiting is friction. For a Tracker, chaos is friction.
             **Fuel:** The specific psychological reward they crave. Money is temporary fuel; this is sustainable fuel.
             **How to use:** Ask them monthly: "What is the biggest friction point in your day right now?" and fix it.
             """)
        
        ac1, ac2 = st.columns(2)
        with ac1:
            st.metric("Top Friction (The Kryptonite)", fric.get('friction'))
            st.write(f"**The Cost:** If this persists, they will quit emotionally before they quit physically.")
            st.error(f"**Fix:** {fric.get('fix')}")
        with ac2:
            st.metric("Top Fuel (The Superpower)", fuel.get('fuel'))
            st.write(f"**The ROI:** This is the cheapest way to buy their engagement.")
            st.success(f"**Inject:** {fuel.get('fix')}")

    # 3. Crisis Protocol
    crisis_data = {
        "Director": {
            "script": "I am giving you the ball. Run with it. I will block for you.",
            "why": "Restores their sense of control and action (Agency)."
        },
        "Encourager": {
            "script": "We are in this together. I have your back. Let's do this.",
            "why": "Restores their sense of safety and connection (Belonging)."
        },
        "Facilitator": {
            "script": "I need you to trust my call on this one. We will debrief later.",
            "why": "Relieves them of the pressure to find consensus in an emergency (Absolution)."
        },
        "Tracker": {
            "script": "Follow the protocol. I am responsible for the outcome.",
            "why": "Relieves them of the fear of liability or error (Protection)."
        }
    }
    
    c_dat = crisis_data.get(p_comm, {})

    with st.container(border=True):
        st.markdown("#### 🆘 Crisis Protocol (Break Glass in Emergency)")
        with st.expander("🎓 **Training: Cognitive Tunneling**"):
             st.markdown("""
             **The Science:** In high-stress moments (crisis, restraint, deadline), the prefrontal cortex (logic brain) shuts down. Staff cannot process complex sentences or nuance.
             **The Fix:** You need a "Short-Code" sentence that bypasses the panic and speaks directly to their core safety need.
             **How to use:** Memorize the script below. Say it calmly, firmly, and exactly as written when they are melting down.
             """)
        st.info(f"**Say exactly this:** \"{c_dat.get('script')}\"")
        st.caption(f"**Why it works:** {c_dat.get('why')}")


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
    
    # 1. Helper to generate DYNAMIC moves based on integrated profile
    def get_dynamic_coaching_moves(comm, motiv, phase):
        # Comm Moves (How they receive coaching)
        c_moves = {
            "Director": ["The 'Bottom Line' Opener: Start with the goal, not the background.", "The Autonomy Check: Ask 'What do you need to own this?'"],
            "Encourager": ["The Relational Buffer: Spend 2 mins on 'us' before 'the work'.", "The Vision Connect: Link the boring task to the team vibe."],
            "Facilitator": ["The Advance Warning: Send the agenda 24hrs early.", "The Process Map: Ask them to design the 'how'."],
            "Tracker": ["The Data Dive: Bring specific examples/numbers.", "The Risk Assessment: Ask 'What risks do you see?'"]
        }
        # Motiv Moves (How they stay engaged)
        m_moves = {
            "Achievement": ["The Scoreboard: Define what 'winning' looks like.", "The Sprint: Set a short-term, high-intensity goal."],
            "Growth": ["The Stretch: Give a task slightly above their pay grade.", "The Debrief: Ask 'What did you learn?' not just 'Did you do it?'"],
            "Purpose": ["The Impact Story: Share a specific youth success story.", "The Why: Explain the mission value of the task."],
            "Connection": ["The Peer Mentor: Have them teach a peer.", "The Team Check: Ask 'How is the team feeling?'"]
        }
        # Phase Moves (Developmental Stage)
        p_moves = {
            1: ["The Safety Net: 'Call me if you get stuck.'", "The Binary Feedback: 'This was right/wrong.'"],
            2: ["The Scenario Drill: 'What would you do if...?'", "The Pattern Spot: 'I see you doing X often.'"],
            3: ["The Delegation: 'You run the meeting today.'", "The Systems Think: 'How do we fix this process?'"]
        }
        
        return c_moves.get(comm, []) + m_moves.get(motiv, []) + p_moves.get(phase, [])

    # Phase Selector
    phase_state_key = f"ipdp_phase__{name}".replace(" ", "_")
    if phase_state_key not in st.session_state: st.session_state[phase_state_key] = 1
    
    sel_num = st.radio("Select Phase:", [1, 2, 3], format_func=lambda x: f"Phase {x}", horizontal=True, key=phase_state_key)

    # Generate Dynamic Moves
    my_moves = get_dynamic_coaching_moves(p_comm, p_mot, sel_num)
    
    # Display Matrix
    st.markdown("#### 🧭 Coaching Matrix: 6 High-Impact Moves (Tailored)")
    
    colA, colB, colC = st.columns(3)
    
    # Move 1 & 2 (Comm)
    with colA:
        with st.container(border=True):
            st.markdown("**1. The Opener**")
            st.caption(my_moves[0])
            st.markdown("---")
            st.markdown("**2. The Assignment**")
            st.caption(my_moves[1])
            
    # Move 3 & 4 (Motiv)
    with colB:
        with st.container(border=True):
            st.markdown("**3. The Fuel**")
            st.caption(my_moves[2])
            st.markdown("---")
            st.markdown("**4. The Hook**")
            st.caption(my_moves[3])
            
    # Move 5 & 6 (Phase)
    with colC:
        with st.container(border=True):
            st.markdown("**5. The Safety Valve**")
            st.caption(my_moves[4])
            st.markdown("---")
            st.markdown("**6. The Growth Edge**")
            st.caption(my_moves[5])

    st.markdown("#### 🎓 Pedagogical Deep Dive")
    st.info(PEDAGOGY_GUIDE.get(sel_num, "Guide and support consistent growth."))
    
    # Original PDF Download Button (Logic preserved)
    # ... (PDF logic remains, referencing generic data for stability, but matrix on screen is new/dynamic) ...
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
