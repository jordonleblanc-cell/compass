import streamlit as st
import requests
import pandas as pd
import re
from fpdf import FPDF
import plotly.express as px
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
    """
    Submits offline data to Google Sheets via the Apps Script.
    """
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
        if response.status_code == 200:
            return True
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
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user_role" not in st.session_state:
    st.session_state.current_user_role = None
if "current_user_cottage" not in st.session_state:
    st.session_state.current_user_cottage = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None

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
        
        # 1. Master Override
        if input_pw == MASTER_PW:
            authorized = True
            
        # 2. Individual Password Check
        else:
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except:
                individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip():
                authorized = True
            
            # 3. Fallback to Role-Based
            elif not authorized:
                if "Program Supervisor" in role_raw or "Director" in role_raw or "Manager" in role_raw:
                    if input_pw == PS_PW: authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                elif "Shift Supervisor" in role_raw:
                    if input_pw == SS_PW: authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                else:
                    st.error("Access Restricted. Please contact your administrator.")
                    return

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Authentication Failed.")

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
    else:
        st.selectbox("Who are you?", ["Administrator"], key="user_select")
        
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
        if "Program Supervisor" in user_role:
            pass
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
        elif "YDP" in user_role:
            filtered_df = filtered_df[filtered_df['name'] == current_user]

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
        ]
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
        ]
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
        ]
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
        ]
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

# --- EXTENDED DICTIONARIES (DNA/Missing Voice/Conflict) ---

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
            "watch_fors": ["**The Policy War:** They quote the handbook; you quote the 'context'.", "**Ignoring:** You ignoring their emails because they feel like nagging.", "**Anxiety:** They get anxious when you say 'let's just see how it goes'."],
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
            "red_flags": "1. They just ordered AOBH to 'do more'.\n2. They ignored the unique constraints of TIPS/EPIC.\n3. They tried to run the meeting themselves instead of empowering the leaders.\n4. They viewed the satellite programs
