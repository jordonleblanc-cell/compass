import streamlit as st
import requests
import pandas as pd
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
        
        if input_pw == MASTER_PW:
            authorized = True
            
        else:
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except:
                individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip():
                authorized = True
            
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
        "support": "**Operational Risk:** Name the operational risk of moving fast. Say, 'We can do this quickly if we build in these guardrails.' This validates their speed while protecting the agency from errors.\n\n**Burnout Watch:** They are the best person to identify when the 'ask' exceeds capacity, but they need permission to say it. They often view endurance as a badge of honor.",
        "thriving": "**Rapid Decision Architecture:** They make calls with partial information, preventing the team from freezing in analysis paralysis.\n**Objective Focus:** They separate story from fact, focusing on behaviors and outcomes.\n**High-Bar Accountability:** They refuse to walk past a mistake, raising the standard of care.",
        "struggling": "**The Steamroller Effect:** They announce decisions without checking if the team is emotionally ready.\n**Burnout by Intensity:** They assume everyone has their stamina and push until the team breaks.\n**Dismissing 'Soft' Data:** They ignore 'bad feelings' or intuition because there is no proof.",
        "interventions": [
            "**Phase 1: The Pause Button (0-6 Months):** Force a deliberate delay between their initial thought and their resulting action. Require them to ask three distinct questions of their team before issuing a final decision.",
            "**Phase 2: Narrative Leadership (6-12 Months):** Coach them to script the 'Why' behind their directives. Require them to spend the first 5 minutes of any rollout explaining the context.",
            "**Phase 3: Multiplier Effect (12-18 Months):** Identify two deputies and train the supervisor to sit on their hands while the deputies lead. Their metric for success must shift to 'what my team achieved without me.'"
        ],
        "questions": [
            "How are you defining success today beyond just metrics?",
            "What is one win you can celebrate right now?",
            "Are you driving the team too hard?",
            "What is the cost of speed right now?",
            "Where are you moving too fast for the team?",
            "Who haven't you heard from on this issue?",
            "How does your tone land when you are stressed?",
            "Are you celebrating the small wins?",
            "Who helped you win this week?",
            "What is 'good enough' for right now?"
        ],
        "advancement": "**Delegate Effectively:** Give away tasks they are good at to prove they can build a team.\n**Allow Safe Failure:** Let the team struggle so they can learn, rather than rescuing them.\n**Focus on Strategy:** Move from the 'how' (tactics) to the 'why' (organizational strategy)."
    },
    "Director-Growth": {
        "title": "The Restless Improver",
        "synergy": "Transformational Leadership. They don't just manage the shift; they want to upgrade it. They see potential in every staff member and are willing to push hard to unlock it.",
        "support": "**Connect Goals:** Link their personal growth goals to youth outcomes and the mission.\n**Pacing:** Remind them that not everyone learns at their speed. Coach them to wait for the team to catch up before introducing the next change.",
        "thriving": "**Diagnostic Speed:** They quickly identify root causes rather than treating symptoms.\n**Fearless Innovation:** They are willing to break the status quo to find a better way.\n**High-Impact Coaching:** They give direct, developmental feedback that accelerates growth.",
        "struggling": "**The Pace Mismatch:** They get visibly frustrated with slow learners or bureaucracy.\n**'Fix-It' Fatigue:** They constantly point out flaws and forget to validate what is working.\n**Leaving People Behind:** They focus on the idea of change rather than the adoption of change.",
        "interventions": [
            "**Phase 1: Validation (0-6 Months):** Mandate that they validate the current effort before suggesting improvements. Require them to catch people doing things right to build trust.",
            "**Phase 2: Change Management (6-12 Months):** Require a 'stakeholder analysis' for their next idea (who will resist and why?). They must present a plan for buy-in, not just the change itself.",
            "**Phase 3: Capacity Building (12-18 Months):** Shift them from idea generator to facilitator. Challenge them to help a peer implement a change project."
        ],
        "questions": [
            "Where are you moving too fast for the team?",
            "Who haven't you heard from on this issue?",
            "How does your tone land when you are stressed?",
            "What are you learning from this struggle?",
            "Are you expecting too much too soon from others?",
            "How are you feeding your own curiosity?",
            "What is one way you can slow down for others?",
            "How are you measuring your own growth beyond just speed?",
            "Are you leaving the team behind?",
            "Is this change necessary right now?"
        ],
        "advancement": "**Delegate Effectively:** Stop being the 'fixer', become the 'developer.'\n**Allow Safe Failure:** Resist the urge to jump in and correct every mistake.\n**Focus on Strategy:** Design tomorrow's solutions rather than solving today's problems."
    },
    "Director-Purpose": {
        "title": "The Mission Defender",
        "synergy": "Ethical Courage. They provide the moral backbone for the team, ensuring expediency never trumps integrity. They are the conscience of the unit.",
        "support": "**Share Values:** Share your own core values so they trust your leadership.\n**Operational Risk:** Frame slowing down as 'protecting the mission.' Help them see that rushing can lead to mistakes that hurt the client.",
        "thriving": "**Unshakeable Advocacy:** They act immediately against injustice.\n**Clarity of 'Why':** They contextualize the grind for the staff, reminding everyone why the work matters.\n**Crisis Ethics:** They keep their moral compass even in chaos.",
        "struggling": "**Righteous Rigidity:** They struggle to see gray areas, viewing everything as black and white.\n**The Martyr Complex:** They overwork because they don't trust others to care enough.\n**Judgmental Tone:** They come across as 'preachy' or morally superior.",
        "interventions": [
            "**Phase 1: The Gray Zone (0-6 Months):** Require them to argue the 'other side' of an ethical debate to build cognitive flexibility.",
            "**Phase 2: Sustainable Advocacy (6-12 Months):** Coach them to use a 'Tier System' for battles (Tier 1: Fight, Tier 2: Debate, Tier 3: Let go).",
            "**Phase 3: Cultural Architecture (12-18 Months):** Move from fighting battles to building systems that prevent injustice. Challenge them to write the policy rather than just complaining."
        ],
        "questions": [
            "Where do you feel the system is failing your values?",
            "How can you advocate without burning bridges?",
            "Is this a hill worth dying on?",
            "How does flexibility serve the mission here?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Where are you moving too fast for the team?",
            "How does your tone land when you are stressed?"
        ],
        "advancement": "**Delegate Effectively:** Build a team that protects children. Multiply impact by teaching others to care.\n**Allow Safe Failure:** Trust that others also care; separate competence from character.\n**Focus on Strategy:** Build systems that prevent injustice."
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial.\n**Backing:** Be candid about where you can back them up (air cover). They need to know you are in their corner.",
        "thriving": "**Decisive Care:** They fix problems for people immediately.\n**Crisis Stabilization:** They become the calm human shield during a crisis.\n**Team Loyalty:** They build a strong 'Us.' The team has a distinct identity.",
        "struggling": "**Us vs. Them:** They become hostile toward outsiders (admin, other units).\n**Over-Functioning:** They do everyone's job to protect them, burning out.\n**Taking Conflict Personally:** They conflate professional disagreement with personal betrayal.",
        "interventions": [
            "**Phase 1: Delegation of Care (0-6 Months):** Stop being the only fixer. Require them to let someone else handle a crisis or plan a party.",
            "**Phase 2: Organizational Citizenship (6-12 Months):** Expand the circle of loyalty. Challenge them to partner with another unit.",
            "**Phase 3: Mentorship (12-18 Months):** Transition from Captain to Admiral. Task them with training a new supervisor on building culture."
        ],
        "questions": [
            "Are you avoiding this conversation to be kind, or to be safe?",
            "How can you be direct and caring at the same time?",
            "Are you protecting them from growth?",
            "How is the team reacting to your directness?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Where are you moving too fast for the team?",
            "Who do you need to check in with today?"
        ],
        "advancement": "**Delegate Effectively:** Stop being 'camp parent.' Prove they can manage managers.\n**Allow Safe Failure:** Learn the team is resilient and won't break if they step back.\n**Focus on Strategy:** Expand loyalty to the whole agency."
    },
    "Encourager-Achievement": {
        "title": "The Coach",
        "synergy": "Inspirational Performance. They make hard work feel like a game. They believe the team can win and their energy is contagious.",
        "support": "**Reality Checks:** Be the ground to their sky. Validate enthusiasm but ask 'What is the plan if this goes wrong?'\n**Focus:** Help them pick one lane. They want to achieve everything at once; force them to prioritize.",
        "thriving": "**Team Morale:** The unit has high energy and believes they are the best.\n**Rallying:** They can turn a bad shift around with a pep talk.\n**Goal-Smashing:** They hit metrics with flair and celebrate loudly.",
        "struggling": "**Overselling:** They promise things they can't deliver to get buy-in.\n**Disorganization:** They leave a wake of administrative chaos.\n**Impatience:** They get frustrated when the team doesn't share their burning desire to win immediately.",
        "interventions": [
            "**Phase 1: Follow-Through (0-6 Months):** Focus on finishing. Require them to complete one project fully before starting the next.",
            "**Phase 2: Data Discipline (6-12 Months):** Require them to bring data to supervision, not just stories.",
            "**Phase 3: Grooming Talent (12-18 Months):** Challenge them to let others shine. The 'Coach' needs to get off the field."
        ],
        "questions": [
            "How do we keep this energy up when things get boring?",
            "What are the specific steps to get to that vision?",
            "Who is doing the work: you or the team?",
            "How will you track this?",
            "What is the one thing we must finish this week?",
            "Who needs the spotlight more than you right now?",
            "Are you listening or just waiting to speak?",
            "What happens if we miss this goal?",
            "How are you celebrating the team's grind, not just the win?",
            "Is your enthusiasm masking a problem?"
        ],
        "advancement": "**Detail Management:** Prove they can handle admin/budgets.\n**Listening:** Learn to sit back and let others speak.\n**Consistency:** Prove they can maintain performance when excitement fades."
    },
    "Encourager-Growth": {
        "title": "The Mentor",
        "synergy": "Developmental Charisma. They see the gold in people and talk it out of them. They make people feel smarter and more capable just by being around them.",
        "support": "**Structure:** Provide the structure to execute one idea at a time. Help them focus creative energy.\n**Patience:** Remind them that growth is messy and non-linear.",
        "thriving": "**Talent Magnet:** People want to work for them because they feel grown and seen.\n**Culture of Learning:** Mistakes are celebrated as learning opportunities.\n**Innovation:** They keep the agency fresh and relevant by injecting new thought.",
        "struggling": "**Shiny Object Syndrome:** They chase a new initiative every week, confusing the team.\n**Avoidance of Hard Conversations:** They struggle to give negative feedback.\n**All Talk:** Great visions, poor execution.",
        "interventions": [
            "**Phase 1: Closing the Loop (0-6 Months):** Force them to finish what they start. No new ideas until the last one is implemented.",
            "**Phase 2: Difficult Feedback (6-12 Months):** Role-play giving 'hard' feedback. Teach them that clarity is kind.",
            "**Phase 3: Systems of Growth (12-18 Months):** Turn informal mentoring into a formal training document."
        ],
        "questions": [
            "Who are you investing in, and who are you ignoring?",
            "How do we turn this idea into a habit?",
            "Are you avoiding the hard truth to be nice?",
            "What is the one skill the team needs right now?",
            "How are you measuring that improvement?",
            "Are you talking more than they are?",
            "What did you finish this week?",
            "Is this practical, or just interesting?",
            "How does this help the client today?",
            "What are you reading/learning?"
        ],
        "advancement": "**Execution:** Prove they can implement, not just ideate.\n**Toughness:** Prove they can make hard personnel calls.\n**Focus:** Prove they can stick to a boring plan for the long haul."
    },
    "Encourager-Purpose": {
        "title": "The Heart of the Mission",
        "synergy": "Passionate Advocacy. They are the soul of the unit. They keep the emotional flame alive and lead with raw emotion and belief.",
        "support": "**Emotional Boundaries:** Help them distinguish between caring and carrying. Teach detached concern.\n**Validation:** Affirm that their heart is a strength, not a weakness.",
        "thriving": "**Cultural Carrier:** They set the emotional tone for the workspace.\n**Advocate:** They are fearless in speaking up for kids.\n**Inspiration:** They can make a tired team feel like heroes again.",
        "struggling": "**Emotional Flooding:** They lose objectivity and get wrapped up in the 'story.'\n**Us vs. The System:** They vilify leadership/policy to protect the team.\n**Burnout:** They crash hard because they have no reserves.",
        "interventions": [
            "**Phase 1: Boundaries (0-6 Months):** Teach them to leave work at work. Create rituals for disconnecting.",
            "**Phase 2: Fact-Checking (6-12 Months):** Ask 'Is that true, or is that how it felt?' Force separation of emotion from data.",
            "**Phase 3: Channeling Passion (12-18 Months):** Give them a platform where passion is an asset (e.g., orientation)."
        ],
        "questions": [
            "Is this feeling a fact?",
            "How can you care without carrying?",
            "Are you whipping the team up or calming them down?",
            "What is the most ethical choice, even if it feels bad?",
            "Who is supporting you?",
            "Is this your battle to fight?",
            "How does the policy actually help the child?",
            "Are you listening to the logic, or just the tone?",
            "What do you need to let go of today?",
            "How can we use your voice for good?"
        ],
        "advancement": "**Objectivity:** Prove they can make dispassionate decisions.\n**Policy:** Understand the legal/fiscal reasons behind rules.\n**Resilience:** Bounce back without drama."
    },
    "Encourager-Connection": {
        "title": "The Team Builder",
        "synergy": "Social Cohesion. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy.",
        "support": "**Hard Decisions:** Step in to be the 'bad guy' occasionally so they don't burn social capital.\n**Focus:** Remind them that work is the goal, fun is the method.",
        "thriving": "**Zero Turnover:** People stay because they love the team.\n**Conflict Resolution:** They heal rifts before they become canyons.\n**Joy:** They bring fun to the grind, preventing toxicity.",
        "struggling": "**The Country Club:** Too much socializing, not enough work.\n**Gossip:** Their need to be 'in the know' can spiral into drama.\n**Favoritism:** They create an 'in-crowd' and alienate outliers.",
        "interventions": [
            "**Phase 1: Professionalism (0-6 Months):** Define the line between 'friend' and 'colleague.' Create clear rules about socializing.",
            "**Phase 2: Inclusive Leadership (6-12 Months):** Challenge them to connect with the staff member they like the least.",
            "**Phase 3: Task Focus (12-18 Months):** Assign them a project requiring solitude or deep focus."
        ],
        "questions": [
            "Are we having fun, or are we working?",
            "Who is on the outside of the circle?",
            "Are you avoiding the conflict to keep the peace?",
            "How can you deliver that news directly?",
            "Are you gossiping or venting?",
            "Can you be friendly without being their best friend?",
            "How does the work get done if we talk all day?",
            "What is the cost of not holding them accountable?",
            "Who needs to hear from you today?",
            "How are you protecting your own energy?"
        ],
        "advancement": "**Separation:** Prove they can lead without needing to be liked.\n**Confidentiality:** Prove they can keep secrets and not overshare.\n**Productivity:** Prove they can drive results, not just vibes."
    },
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "synergy": "Methodical Progress. They don't sprint; they march with purpose. They get the team to the finish line by ensuring everyone knows their role.",
        "support": "**Decision Speed:** Push them to decide with 80% consensus. Frame indecision as failure.\n**Validation:** Praise the quiet work of organization and structure.",
        "thriving": "**Consistent Wins:** They hit metrics without drama. They are the metronome of the department.\n**Efficient Meetings:** Everyone feels heard, but action items are clear.\n**Project Management:** They are excellent at long-term implementation.",
        "struggling": "**Analysis Paralysis:** They freeze at the intersection of speed and agreement.\n**Frustration with Chaos:** They struggle to pivot quickly without a new plan.\n**Silent Resentment:** They work hard and resent those who don't, but won't say it aloud.",
        "interventions": [
            "**Phase 1: Speaking Up (0-6 Months):** Call on them first to break the habit of waiting. Force them to voice messy thoughts.",
            "**Phase 2: Imperfect Action (6-12 Months):** Assign a task with an impossible deadline to force 'good enough' decisions.",
            "**Phase 3: Direct Delegation (12-18 Months):** Challenge them to assign tasks without asking for volunteers."
        ],
        "questions": [
            "What is the 'good enough' decision right now?",
            "Are you waiting for everyone to agree?",
            "How can we move forward even if it's messy?",
            "Who is holding up the project?",
            "What have you achieved this week?",
            "Is the process helping or hurting the goal?",
            "How can you say 'no' to protect the timeline?",
            "Who needs to be cut out of the decision loop?",
            "Are you doing the work to avoid asking others?",
            "What is the next step?"
        ],
        "advancement": "**Speed:** Make faster decisions with less data.\n**Conflict:** Call out underperformance directly and verbally.\n**Vision:** Look beyond the checklist to the strategy."
    },
    "Facilitator-Growth": {
        "title": "The Patient Gardener",
        "synergy": "Organic Development. They don't force growth; they create conditions for it. They are incredibly patient with difficult staff.",
        "support": "**Urgency:** Provide urgency or they will let things grow forever. Be the winter to their summer.\n**Outcome Focus:** Remind them that growth must result in performance.",
        "thriving": "**Turnaround Specialist:** They save people others would fire by finding hidden strengths.\n**Deep Listening:** They know the root system of the culture.\n**Sustainable Pace:** They model a healthy work-life balance.",
        "struggling": "**Tolerance of Mediocrity:** They give too many chances in the name of 'growth.'\n**Slow to Launch:** They study the problem forever without fixing it.\n**Fear of Judgment:** They struggle to evaluate people or play judge.",
        "interventions": [
            "**Phase 1: Timelines (0-6 Months):** Put a date on development goals. Create a kill switch for their patience.",
            "**Phase 2: Judgment (6-12 Months):** Practice evaluating performance objectively ('Is this good or bad?').",
            "**Phase 3: Pruning (12-18 Months):** They must terminate or discipline a staff member to learn that protection isn't always love."
        ],
        "questions": [
            "How long is too long to wait for improvement?",
            "Is this person actually growing, or are we just hoping?",
            "What is the cost to the team of keeping this person?",
            "Are you learning, or just stalling?",
            "What is the lesson here?",
            "How can you speed up this process?",
            "Who are you neglecting by focusing on the struggler?",
            "What does 'accountability' look like to you?",
            "Are you afraid to judge?",
            "What is the next step today?"
        ],
        "advancement": "**Decisiveness:** Act on data, not just hope.\n**Speed:** Move faster than feels comfortable.\n**Standards:** Hold the line on quality without apology."
    },
    "Facilitator-Purpose": {
        "title": "The Moral Compass",
        "synergy": "Principled Consensus. They are the quiet conscience of the team. They ensure the team gets things done right, building unity around values.",
        "support": "**Validation of Values:** Affirm their role as ethical standard-bearer.\n**Decision Frameworks:** Give them a framework for making 'imperfect' decisions and navigating gray areas.",
        "thriving": "**Ethical Anchor:** They center the boat in the storm using the mission statement.\n**Unified Team:** They create a moral community based on trust.\n**Trust:** Staff trust them implicitly because their motives are pure.",
        "struggling": "**Moral Paralysis:** They freeze when no option is perfectly ethical.\n**Passive Resistance:** They silently rebel against policies they dislike.\n**Judgment:** They may silently judge pragmatists and become self-righteous.",
        "interventions": [
            "**Phase 1: The '51% Decision' (0-6 Months):** Teach them to move with only 51% certainty or consensus.",
            "**Phase 2: Voice Training (6-12 Months):** Challenge them to speak dissent in meetings, not hallways.",
            "**Phase 3: Operational Ethics (12-18 Months):** Task them with creating a system that institutionalizes their values."
        ],
        "questions": [
            "What moral tension are you holding right now?",
            "How can you speak up for your values effectively?",
            "Are you staying neutral when you should take a stand?",
            "How does your silence impact the team?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Where do you need to make a 51% decision?",
            "Are you waiting for consensus that isn't coming?"
        ],
        "advancement": "**Decisiveness:** Prove they can make hard calls despite ambiguity.\n**Public Speaking:** Get comfortable projecting voice and values.\n**Pragmatism:** Balance money and mission."
    },
    "Facilitator-Connection": {
        "title": "The Peacemaker",
        "synergy": "Harmonious Inclusion. They create a psychological safety net. They lead by relationship, ensuring staff feel loved and heard.",
        "support": "**Conflict Coaching:** Role-play hard conversations to build muscle memory.\n**Permission to Disappoint:** Explicitly tell them 'It is okay if they are mad at you.'",
        "thriving": "**High Retention:** People stay for the leader, not the paycheck.\n**Psychological Safety:** The environment is low-fear and high-trust.\n**De-escalation:** They calm a room just by walking in.",
        "struggling": "**The Doormat:** They let staff walk all over them to avoid fights.\n**Exhaustion:** They carry everyone's emotional baggage.\n**Triangulation:** They complain to others to vent instead of addressing issues directly.",
        "interventions": [
            "**Phase 1: Direct Address (0-6 Months):** Require one direct, hard conversation per week.",
            "**Phase 2: Disappointing Others (6-12 Months):** Challenge them to make an unpopular decision and stand firm.",
            "**Phase 3: Self-Protection (12-18 Months):** Teach them to set boundaries on their time and empathy."
        ],
        "questions": [
            "What boundaries do you need to set to protect your energy?",
            "Are you listening too much and leading too little?",
            "Who is taking care of you?",
            "Is your silence creating confusion?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Where do you need to make a 51% decision?",
            "Are you waiting for consensus that isn't coming?"
        ],
        "advancement": "**Conflict:** Prove they can handle a fight without crumbling.\n**Separation:** Prove they can lead friends and former peers.\n**Results:** Prove they value outcomes as much as feelings."
    },
    "Tracker-Achievement": {
        "title": "The Architect",
        "synergy": "Systematic Perfection. They build the systems that allow the team to succeed. They ensure nothing falls through the cracks.",
        "support": "**Clarity:** Be hyper-clear about expectations. Ambiguity is torture for them.\n**Time:** Give them time to do it right. Respect their need for precision.",
        "thriving": "**Flawless Execution:** Paperwork and data are clean. Audits are 100% compliant.\n**System Builder:** They create trackers that save everyone time.\n**Reliability:** They are the most dependable person on staff.",
        "struggling": "**Rigidity:** They refuse to bend rules even when it makes sense.\n**Micromanagement:** They hover to ensure things are done 'perfectly.'\n**Critique:** They constantly point out errors, becoming 'compliance police.'",
        "interventions": [
            "**Phase 1: Flexibility (0-6 Months):** Challenge them to identify one rule to bend for the greater good.",
            "**Phase 2: People over Process (6-12 Months):** Require them to mentor a disorganized staff member without doing the work.",
            "**Phase 3: Big Picture (12-18 Months):** Ask them to explain why the system exists, not just how it works."
        ],
        "questions": [
            "How can you measure effort, not just outcome?",
            "Are you valuing the data more than the person?",
            "Where is flexibility needed right now?",
            "How can you support the person, not just the process?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Are you focusing on the rule or the relationship?",
            "What is 'good enough' for right now?"
        ],
        "advancement": "**Flexibility:** Prove they can handle chaos without breaking.\n**Delegation:** Prove they can trust others to do the work, even imperfectly.\n**Warmth:** Prove they can connect with people, not just papers."
    },
    "Tracker-Growth": {
        "title": "The Technical Expert",
        "synergy": "Knowledge Mastery. They are the walking encyclopedia of the agency. They lead by being the authority everyone turns to.",
        "support": "**Resources:** Give them access to data and policy. Do not gatekeep information.\n**Challenge:** Give them a problem no one else can solve.",
        "thriving": "**Problem Solver:** They fix technical issues that stump others.\n**Teacher:** They patiently explain complex systems.\n**Innovator:** They find new tools to make work better.",
        "struggling": "**Arrogance:** They make others feel stupid for not knowing rules.\n**Over-Complication:** They design systems too complex for users.\n**Disengagement:** If they stop learning, they check out.",
        "interventions": [
            "**Phase 1: Simplification (0-6 Months):** Challenge them to explain complex ideas without jargon.",
            "**Phase 2: Emotional Intelligence (6-12 Months):** Require mentoring based on potential, not knowledge.",
            "**Phase 3: Strategic Vision (12-18 Months):** Ask them to solve a problem with no 'right' answer."
        ],
        "questions": [
            "Are you focusing on the system or the person?",
            "What is 'good enough' for today?",
            "Are you correcting or coaching?",
            "How can you make it safe to make mistakes?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Are you focusing on the rule or the relationship?",
            "What is 'good enough' for right now?"
        ],
        "advancement": "**Communication:** Prove they can speak simply and clearly.\n**Empathy:** Prove they can care about non-experts.\n**Strategy:** Prove they can think about the 'why,' not just the 'how.'"
    },
    "Tracker-Purpose": {
        "title": "The Guardian",
        "synergy": "Protective Compliance. They believe following rules is the highest form of caring. They protect the mission by ensuring the agency never gets in trouble.",
        "support": "**Explanation:** Explain the 'why' behind policy changes.\n**Validation:** Validate their fears and concerns. Honor watchfulness as a skill.",
        "thriving": "**Safety Net:** They catch errors that would cause violations.\n**Moral Consistency:** They ensure we do what we say we do.\n**Reliability:** A vault for secrets and safety.",
        "struggling": "**Bureaucracy:** They use rules to block action.\n**Fear-Mongering:** They spread anxiety and see risk everywhere.\n**Judgment:** They view errors as moral failings.",
        "interventions": [
            "**Phase 1: Risk Assessment (0-6 Months):** Ask them to rate risks 1-10. Teach triage.",
            "**Phase 2: The 'Why' of Flexibility (6-12 Months):** Show cases where breaking a rule saved a kid.",
            "**Phase 3: Solution Focus (12-18 Months):** Don't let them bring a problem without a solution."
        ],
        "questions": [
            "How can you protect the mission without being rigid?",
            "Are you using rules to manage your anxiety?",
            "Is this rule serving the child right now?",
            "How can you explain the 'why' behind the rule?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Are you focusing on the rule or the relationship?",
            "What is 'good enough' for right now?"
        ],
        "advancement": "**Risk Tolerance:** Prove they can take calculated risks.\n**Flexibility:** Prove they can adapt to change without panic.\n**Vision:** Prove they can see the big picture."
    },
    "Tracker-Connection": {
        "title": "The Reliable Rock",
        "synergy": "Servant Consistency. They show love for the team by doing work perfectly. They are the backbone of the unit.",
        "support": "**Notice the Details:** Validate invisible labor.\n**Change Management:** Hold their hand through change and ease anxiety.",
        "thriving": "**Steady Presence:** Always there, prepared, and consistent.\n**Helper:** They use skills to help others succeed.\n**Culture Keeper:** They maintain traditions and history.",
        "struggling": "**Overwhelmed:** They say 'yes' to everything and burn out.\n**Passive Aggressive:** They withdraw if unappreciated.\n**Resistance to Change:** They dig in their heels to protect routine.",
        "interventions": [
            "**Phase 1: Saying No (0-6 Months):** Practice saying 'no' to requests.",
            "**Phase 2: Vocalizing Needs (6-12 Months):** Force them to voice desires in meetings.",
            "**Phase 3: Leading Change (12-18 Months):** Ask them to help a new person adapt."
        ],
        "questions": [
            "How can you show care in a way they understand?",
            "Are you doing too much for others?",
            "Do they know you care?",
            "Where do you need help carrying the load?",
            "What do you need right now?",
            "Where are you stuck?",
            "How can I help?",
            "What is the goal?",
            "Are you focusing on the rule or the relationship?",
            "What is 'good enough' for right now?"
        ],
        "advancement": "**Voice:** Prove they can speak up in meetings.\n**Boundaries:** Prove they can stop over-functioning.\n**Flexibility:** Prove they can handle new ways of working."
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
            "success_indicators": "1. The new system is actually simpler/faster, not more complex.\n2. They solicited input from the team on the pain points.\n3. They can explain the change improves safety/efficiency.\n4. They are excited about the *improvement*, not just the *compliance*.",
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

# 5c. INTEGRATED PROFILES (Expanded & 10 Coaching Questions Logic)
def generate_profile_content(comm, motiv):
    
    # This dictionary holds the specific text for the 16 combinations
    combo_key = f"{comm}-{motiv}"
    
    # Lookup individual profiles
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
        "s5": f"**Profile:** {i_data.get('title')}\n\n{i_data.get('synergy')}",
        "s6": i_data.get('support', ''),
        "s7": i_data.get('thriving', ''), # Thriving paragraphs
        "s8": i_data.get('struggling', ''), # Struggling paragraphs
        "s9": "Strategies for Course Correction:", # Intervention Header
        "s9_b": i_data.get('interventions', []),
        "s10_b": m_data.get('celebrate_bullets'),
        "coaching": i_data.get('questions', []),
        "advancement": i_data.get('advancement', ''),
        
        # New keys for cheat sheet consistency
        "cheat_do": c_data.get('supervising_bullets'),
        "cheat_avoid": avoid_map.get(comm, []),
        "cheat_fuel": m_data.get('strategies_bullets')
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def send_pdf_via_email(to_email, subject, body, pdf_bytes, filename="Guide.pdf"):
    try:
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
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
    
    # Colors
    blue = (26, 115, 232)
    green = (52, 168, 83)
    red = (234, 67, 53)
    black = (0, 0, 0)
    gray = (128, 128, 128)
    
    # Header
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(5)
    
    # Generate Data
    data = generate_profile_content(p_comm, p_mot)

    # --- CHEAT SHEET SECTION (NEW) ---
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
            # Clean up bold markdown for PDF
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
    add_section("5. Integrated Leadership Profile", data['s5']) 
    add_section("6. How You Can Best Support Them", data['s6'])
    add_section("7. What They Look Like When Thriving", data['s7'])
    add_section("8. What They Look Like When Struggling", data['s8'])
    add_section("9. Supervisory Interventions (Roadmap)", None, data['s9_b'])
    add_section("10. What You Should Celebrate", None, data['s10_b'])

    # 11. Coaching Questions (10 questions)
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
    # Pass 'generate_profile_content' helper logic if not already present
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---")
    
    # --- DASHBOARD HEADER ---
    st.markdown(f"### 📘 Supervisory Guide: {name}")
    st.caption(f"Role: {role} | Profile: {p_comm}/{s_comm} • {p_mot}/{s_mot}")
    
    # --- VISUALIZATION SECTION ---
    with st.container(border=True):
        st.subheader("📊 Profile At-A-Glance")
        vc1, vc2 = st.columns(2)
        
        with vc1:
            # 1. COMMUNICATION RADAR
            comm_scores = {"Director": 2, "Encourager": 2, "Facilitator": 2, "Tracker": 2}
            if p_comm in comm_scores: comm_scores[p_comm] = 10
            if s_comm in comm_scores: comm_scores[s_comm] = 7
            
            radar_df = pd.DataFrame(dict(r=list(comm_scores.values()), theta=list(comm_scores.keys())))
            fig_comm = px.line_polar(radar_df, r='r', theta='theta', line_close=True, title="Communication Footprint", range_r=[0,10])
            fig_comm.update_traces(fill='toself', line_color=BRAND_COLORS['blue'])
            fig_comm.update_layout(height=300, margin=dict(t=30, b=30, l=30, r=30))
            st.plotly_chart(fig_comm, use_container_width=True)
            
        with vc2:
            # 2. MOTIVATION BATTERY
            mot_scores = {"Achievement": 2, "Growth": 2, "Purpose": 2, "Connection": 2}
            if p_mot in mot_scores: mot_scores[p_mot] = 10
            if s_mot in mot_scores: mot_scores[s_mot] = 7
            
            sorted_mot = dict(sorted(mot_scores.items(), key=lambda item: item[1], reverse=True))
            mot_df = pd.DataFrame(dict(Driver=list(sorted_mot.keys()), Intensity=list(sorted_mot.values())))
            
            fig_mot = px.bar(mot_df, x="Intensity", y="Driver", orientation='h', title="Motivation Drivers", color="Intensity", color_continuous_scale=[BRAND_COLORS['gray'], BRAND_COLORS['blue']])
            fig_mot.update_layout(height=300, showlegend=False, margin=dict(t=30, b=30, l=30, r=30))
            fig_mot.update_xaxes(visible=False)
            st.plotly_chart(fig_mot, use_container_width=True)

    # --- CHEAT SHEET SECTION ---
    with st.expander("⚡ Rapid Interaction Cheat Sheet", expanded=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown("##### ✅ Do This")
            for b in data['cheat_do']: st.success(b)
        with cc2:
            st.markdown("##### ⛔ Avoid This")
            for avoid in data['cheat_avoid']: st.error(avoid)
        with cc3:
            st.markdown("##### 🔋 Fuel")
            for b in data['cheat_fuel']: st.info(b)

    st.divider()
    
    def show_section(title, text, bullets=None):
        with st.expander(title, expanded=False):
            if text: st.write(text)
            if bullets:
                for b in bullets:
                    st.markdown(f"- {b}")

    # Sections 1-4
    show_section(f"1. Communication Profile: {p_comm}", None, data['s1_b'])
    show_section("2. Supervising Their Communication", None, data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    show_section("4. Motivating This Staff Member", None, data['s4_b'])

    # --- SECTION 5: INTEGRATED PROFILE (UPDATED WITH TABS) ---
    st.markdown("### 5. Integrated Leadership Profile")
    with st.container(border=True):
        st.markdown(f"#### {data['s5'].splitlines()[0]}") # Title
        st.markdown(f"*{data['s5'].splitlines()[-1]}*") # Synergy description
        
        # Tabs for detailed breakdown
        tab_mgmt, tab_diag, tab_fix, tab_coach, tab_adv = st.tabs([
            "🛡️ Support Strategy", 
            "🩺 Thriving vs. Struggling", 
            "🔧 Intervention Plan", 
            "❓ Coaching Questions",
            "🚀 Advancement"
        ])
        
        with tab_mgmt:
            st.info(data['s6']) # Support text
            
        with tab_diag:
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**When Thriving:**\n\n{data['s7']}")
            with c2:
                st.error(f"**When Struggling:**\n\n{data['s8']}")
                
        with tab_fix:
            st.write("**Phased Correction Plan:**")
            for i, step in enumerate(data['s9_b']):
                st.info(f"{i+1}. {step}")
                
        with tab_coach:
            st.write("**Top 10 Questions to Ask:**")
            for i, q in enumerate(data['coaching']):
                st.markdown(f"**{i+1}.** {q}")

        with tab_adv:
            st.warning(f"**Promotion Readiness:**\n\n{data['advancement']}")

    # Remaining Sections
    show_section("6. Other Support Strategies", data['s6']) # Kept for PDF consistency, but shown in tab above
    show_section("10. What You Should Celebrate", None, data['s10_b'])

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
            
            # --- FIX: Calculate Index for Persistence ---
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

    # --- [NEW] INPUT OFFLINE DATA TAB ---
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
                                "name": off_name,
                                "email": off_email,
                                "role": off_role,
                                "cottage": off_cottage,
                                "p_comm": off_p_comm,
                                "s_comm": off_s_comm,
                                "p_mot": off_p_mot,
                                "s_mot": off_s_mot
                            }
                            
                            success = submit_data_to_google(payload)
                            
                            if success:
                                st.success(f"Successfully saved {off_name}!")
                                
                                # Manually update local session state so we don't have to reload to see them
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
