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
    page_icon="",
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
    "blue": "#0A84FF",  # iOS System Blue
    "teal": "#64D2FF",  # iOS System Cyan
    "green": "#30D158", # iOS System Green
    "dark": "#1C1C1E",  # iOS Background
    "gray": "#8E8E93",  # iOS System Gray
    "light_gray": "#F2F2F7"
}

# --- 3. CSS STYLING (iOS 26 DESIGN LANGUAGE) ---
st.markdown(f"""
    <style>
        /* iOS System Font Stack */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --ios-blue: #0A84FF;
            --ios-indigo: #5E5CE6;
            --ios-green: #30D158;
            --ios-bg-dark: #1C1C1E; /* Requested Background */
            --ios-card-dark: #2C2C2E; /* Secondary System Fill */
            --ios-widget-dark: #3A3A3C; /* Tertiary System Fill */
            --ios-border: #38383A;
            --text-main: #FFFFFF;
            --text-sub: #8E8E93;
            --radius-l: 22px;
            --radius-m: 14px;
            --radius-s: 10px;
        }}

        /* RESET & BASE */
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: var(--text-main) !important;
            background-color: var(--ios-bg-dark) !important;
        }}

        .stApp {{
            background-color: var(--ios-bg-dark) !important;
        }}

        /* TYPOGRAPHY */
        h1, h2, h3, h4 {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em;
        }}
        
        p, div, label, span {{
            letter-spacing: -0.01em;
        }}

        /* HERO CARD (Apple Wallet Style) */
        .hero-box {{
            background: linear-gradient(135deg, #0A84FF 0%, #5E5CE6 100%);
            padding: 40px;
            border-radius: var(--radius-l);
            color: white !important;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(10, 132, 255, 0.3);
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        }}
        .hero-title {{
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 8px;
            background: -webkit-linear-gradient(#FFFFFF, #E0E0E0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-subtitle {{
            font-size: 1.15rem;
            opacity: 0.9;
            font-weight: 500;
        }}

        /* NAVIGATION BUTTONS (iOS Control Center Widgets) */
        div[data-testid="column"] .stButton button {{
            background-color: var(--ios-card-dark) !important;
            color: white !important;
            border: none;
            border-radius: var(--radius-l);
            height: 140px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: flex-end;
            text-align: left;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        div[data-testid="column"] .stButton button:hover {{
            background-color: var(--ios-widget-dark) !important;
            transform: scale(1.02);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        
        div[data-testid="column"] .stButton button:active {{
            transform: scale(0.96);
        }}

        /* PRIMARY ACTION BUTTONS (Apple Blue Pills) */
        .stButton button:not([style*="height: 140px"]) {{
            background-color: var(--ios-blue) !important;
            color: white !important;
            border: none;
            border-radius: 40px; /* Full capsule */
            padding: 8px 24px;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 10px rgba(10, 132, 255, 0.3);
            transition: transform 0.2s;
        }}
        .stButton button:not([style*="height: 140px"]):hover {{
            filter: brightness(1.1);
            transform: translateY(-1px);
        }}

        /* INPUTS (Filled Style) */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: var(--ios-card-dark) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px;
            padding: 10px 15px;
            font-size: 16px; /* Prevents zoom on mobile */
        }}
        
        /* DROPDOWNS */
        div[data-baseweb="menu"] {{
            background-color: var(--ios-widget-dark) !important;
            border-radius: 12px;
            border: 1px solid var(--ios-border);
        }}

        /* METRICS & CARDS */
        div[data-testid="stMetric"] {{
            background-color: var(--ios-card-dark);
            padding: 16px;
            border-radius: var(--radius-m);
            border: 1px solid var(--ios-border);
        }}

        /* TABS (Segmented Control) */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--ios-card-dark);
            padding: 4px;
            border-radius: 10px;
            gap: 0px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent;
            color: var(--text-sub);
            border-radius: 8px;
            padding: 6px 16px;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: var(--ios-widget-dark);
            color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}

        /* EXPANDERS */
        div[data-testid="stExpander"] {{
            background-color: var(--ios-card-dark) !important;
            border: none !important;
            border-radius: var(--radius-m);
        }}
        .streamlit-expanderHeader {{
            background-color: transparent !important;
            color: white !important;
            font-weight: 600;
        }}

        /* ALERTS */
        div[data-baseweb="notification"] {{
            border-radius: var(--radius-m);
        }}

        /* LOGIN SCREEN GLASS */
        .login-card {{
            background: rgba(44, 44, 46, 0.6);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            padding: 40px;
            border-radius: 30px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
            margin: 100px auto;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .login-title {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 10px;
            color: white !important;
        }}
        .back-link {{ 
            color: var(--ios-blue); 
            text-decoration: none; 
            font-weight: 500;
            display: inline-block;
            margin-bottom: 20px;
        }}

        /* UTILS */
        .stSpinner > div {{ border-top-color: var(--ios-blue) !important; }}
        hr {{ border-color: var(--ios-border) !important; margin: 30px 0; }}
        
        /* HIDE DEFAULT NAV */
        [data-testid="stSidebarNav"] {{display: none;}}
        section[data-testid="stSidebar"] {{
            background-color: var(--ios-card-dark);
            border-right: 1px solid var(--ios-border);
        }}
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA FETCHING & CLEANING ---
@st.cache_data(ttl=60)
def fetch_staff_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200: return response.json()
        return []
    except: return []

all_staff_list = fetch_staff_data()
df_all = pd.DataFrame(all_staff_list)

if not df_all.empty:
    df_all.columns = df_all.columns.str.lower().str.strip() 
    if 'role' in df_all.columns: df_all['role'] = df_all['role'].astype(str).str.strip()
    if 'cottage' in df_all.columns: df_all['cottage'] = df_all['cottage'].astype(str).str.strip()
    if 'name' in df_all.columns: df_all['name'] = df_all['name'].astype(str).str.strip()

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
            authorized = True; st.session_state.current_user_name = "Administrator"; st.session_state.current_user_role = "Admin"; st.session_state.current_user_cottage = "All"
        else: st.error("Incorrect Administrator Password.")
    elif not df_all.empty:
        user_row = df_all[df_all['name'] == selected_user].iloc[0]
        role_raw = user_row.get('role', 'YDP'); cottage_raw = user_row.get('cottage', 'All')
        if "Program Supervisor" in role_raw:
            if input_pw == PS_PW or input_pw == MASTER_PW: authorized = True
            else: st.error("Incorrect Access Code.")
        elif "Shift Supervisor" in role_raw:
            if input_pw == SS_PW or input_pw == MASTER_PW: authorized = True
            else: st.error("Incorrect Access Code.")
        else:
            if input_pw == MASTER_PW: authorized = True
            else: st.error("Access Restricted.")

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized: st.session_state.authenticated = True; del st.session_state.password_input
    else: st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""<div style="position: absolute; top: 20px; left: 20px;"><a href="/" target="_self" class="back-link">← Back</a></div><div class='login-card'><div class='login-title'>Supervisor Access</div><div class='login-subtitle'>Select your name and enter your role's access code.</div></div>""", unsafe_allow_html=True)
    if not df_all.empty and 'name' in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Admin"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Who are you?", user_names, key="user_select")
    else: st.selectbox("Who are you?", ["Administrator"], key="user_select")
    st.text_input("Access Code", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- 6. DATA FILTERING ENGINE (RBAC) ---
def get_filtered_dataframe():
    user_role = st.session_state.current_user_role
    user_cottage = st.session_state.current_user_cottage
    current_user = st.session_state.current_user_name
    if user_role == "Admin" or current_user == "Administrator": return df_all
    filtered_df = df_all.copy()
    if 'cottage' in df_all.columns and user_cottage != "All":
        filtered_df = filtered_df[filtered_df['cottage'] == user_cottage]
    if 'role' in df_all.columns:
        if "Program Supervisor" in user_role:
            condition = (filtered_df['role'].isin(['Shift Supervisor', 'YDP'])) | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
    return filtered_df

df = get_filtered_dataframe()

with st.sidebar:
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    if st.button("Logout"): st.session_state.authenticated = False; st.rerun()

# ==========================================
# SUPERVISOR TOOL DATA DICTIONARIES
# ==========================================

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# (DATA DICTIONARIES - SAME AS ORIGINAL CODE)

COMM_PROFILES = {
    "Director": {
        "bullets": [
            "**Clarity:** Prioritizes bottom line over backstory. Speaks in headlines.",
            "**Speed:** Processes fast. Prefers 80% solution now over 100% later.",
            "**Conflict:** Views conflict as a tool for solving problems, not personal."
        ],
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately. Value their time.",
            "**Focus on Outcomes:** Tell them 'what', leave the 'how' to them.",
            "**Respect Autonomy:** Don't hover. Trust them to come to you."
        ]
    },
    "Encourager": {
        "bullets": [
            "**Verbal Processing:** Thinks out loud. Needs to talk to process.",
            "**Optimism:** Naturally focuses on potential and positive vision.",
            "**Relationship-First:** Influence comes through charisma and liking."
        ],
        "supervising_bullets": [
            "**Allow Discussion:** Give time for small talk/connection first.",
            "**Ask for Specifics:** Drill down into their generalities for data.",
            "**Follow Up in Writing:** Recap conversations via email."
        ]
    },
    "Facilitator": {
        "bullets": [
            "**Listening:** Gathers all perspectives before speaking.",
            "**Consensus:** Prefers group agreement over unilateral action.",
            "**Process:** Values the 'how' as much as the 'what'."
        ],
        "supervising_bullets": [
            "**Advance Notice:** Send agendas early. Don't put them on the spot.",
            "**Deadlines:** Set clear decision dates to prevent endless deliberation.",
            "**Solicit Opinion:** Ask them explicitly what they think."
        ]
    },
    "Tracker": {
        "bullets": [
            "**Detail-Oriented:** Communicates in data, spreadsheets, and precision.",
            "**Risk-Averse:** Cautious. Avoids definitive statements until sure.",
            "**Process-Driven:** Guardians of the handbook and policy."
        ],
        "supervising_bullets": [
            "**Be Specific:** Use metrics and numbers, not feelings.",
            "**Provide Data:** Back up your requests with evidence.",
            "**Written Instructions:** Follow up verbally with detailed email."
        ]
    }
}

MOTIV_PROFILES = {
    "Achievement": {
        "bullets": ["**Scoreboard:** Needs to know if they are winning.", "**Completion:** Loves closing loops and finishing tasks.", "**Efficiency:** Hates wasted time."],
        "strategies_bullets": ["**Visual Goals:** Use charts/dashboards.", "**Public Wins:** Acknowledge success.", "**Autonomy:** Let them design the path."],
        "celebrate_bullets": ["Efficiency gains.", "Difficult problems solved.", "Resilience."]
    },
    "Growth": {
        "bullets": ["**Curiosity:** Asks 'why' and 'how'.", "**Future-Focused:** Views role as stepping stone.", "**Feedback:** Craves correction over praise."],
        "strategies_bullets": ["**Stretch Assignments:** Give tasks above skill level.", "**Career Pathing:** Discuss future roles.", "**Mentorship:** Connect with leaders."],
        "celebrate_bullets": ["Insight.", "Development of others.", "Trying new things."]
    },
    "Purpose": {
        "bullets": ["**Values-Driven:** Filters decisions through 'Is this right?'.", "**Advocacy:** Fights for the underdog.", "**Meaning:** Needs the 'why' connected to client care."],
        "strategies_bullets": ["**The Why:** Explain mission behind mandates.", "**Storytelling:** Share impact stories.", "**Ethics:** Validate moral concerns."],
        "celebrate_bullets": ["Integrity.", "Advocacy.", "Consistency."]
    },
    "Connection": {
        "bullets": ["**Belonging:** Views team as family.", "**Harmony:** Sensitive to tension.", "**Support:** Motivated by helping peers."],
        "strategies_bullets": ["**Face Time:** Prioritize in-person check-ins.", "**Team Rituals:** Encourage traditions.", "**Personal Care:** Ask about life outside work."],
        "celebrate_bullets": ["Loyalty.", "Stabilizing the team.", "Culture building."]
    }
}

# Simplified for brevity in this full-code dump, but logic handles all combinations
INTEGRATED_PROFILES = {
    "Director-Achievement": {"title": "The Executive General", "synergy": "Operational Velocity.", "support": "Name operational risks.", "thriving": "Rapid decisions.", "struggling": "Steamrolling team."},
    "Director-Growth": {"title": "The Restless Improver", "synergy": "Transformational Leadership.", "support": "Connect goals to mission.", "thriving": "Innovation.", "struggling": "Impatience with slow learners."},
    "Director-Purpose": {"title": "The Mission Defender", "synergy": "Ethical Courage.", "support": "Share values.", "thriving": "Advocacy.", "struggling": "Righteous rigidity."},
    "Director-Connection": {"title": "The Protective Captain", "synergy": "Safe Enclosure.", "support": "Regular touchpoints.", "thriving": "Team loyalty.", "struggling": "Us vs Them mentality."},
    "Encourager-Achievement": {"title": "The Coach", "synergy": "Inspirational Performance.", "support": "Reality checks.", "thriving": "High morale.", "struggling": "Overselling."},
    "Encourager-Growth": {"title": "The Mentor", "synergy": "Developmental Charisma.", "support": "Structure for ideas.", "thriving": "Talent magnet.", "struggling": "Shiny object syndrome."},
    "Encourager-Purpose": {"title": "The Heart of the Mission", "synergy": "Passionate Advocacy.", "support": "Emotional boundaries.", "thriving": "Cultural carrier.", "struggling": "Emotional flooding."},
    "Encourager-Connection": {"title": "The Team Builder", "synergy": "Social Cohesion.", "support": "Help making hard calls.", "thriving": "Zero turnover.", "struggling": "Country club atmosphere."},
    "Facilitator-Achievement": {"title": "The Steady Mover", "synergy": "Methodical Progress.", "support": "Push for decisions.", "thriving": "Consistent wins.", "struggling": "Analysis paralysis."},
    "Facilitator-Growth": {"title": "The Patient Gardener", "synergy": "Organic Development.", "support": "Create urgency.", "thriving": "Turnarounds.", "struggling": "Tolerating mediocrity."},
    "Facilitator-Purpose": {"title": "The Moral Compass", "synergy": "Principled Consensus.", "support": "Decision frameworks.", "thriving": "Ethical anchor.", "struggling": "Moral paralysis."},
    "Facilitator-Connection": {"title": "The Peacemaker", "synergy": "Harmonious Inclusion.", "support": "Conflict coaching.", "thriving": "Psychological safety.", "struggling": "Being a doormat."},
    "Tracker-Achievement": {"title": "The Architect", "synergy": "Systematic Perfection.", "support": "Clarity.", "thriving": "Flawless execution.", "struggling": "Micromanagement."},
    "Tracker-Growth": {"title": "The Technical Expert", "synergy": "Knowledge Mastery.", "support": "Resources.", "thriving": "Problem solver.", "struggling": "Arrogance."},
    "Tracker-Purpose": {"title": "The Guardian", "synergy": "Protective Compliance.", "support": "Explain the 'why'.", "thriving": "Safety net.", "struggling": "Bureaucracy."},
    "Tracker-Connection": {"title": "The Reliable Rock", "synergy": "Servant Consistency.", "support": "Notice details.", "thriving": "Stability.", "struggling": "Passive aggressive."}
}

# --- EXTENDED DICTIONARIES ---
TEAM_CULTURE_GUIDE = {
    "Director": {"title": "The Command Center", "impact_analysis": "High efficiency, low patience.", "management_strategy": "Force the pause. Protect dissent.", "meeting_protocol": "No interruption rule.", "team_building": "Vulnerability exercises."},
    "Encourager": {"title": "The Social Hub", "impact_analysis": "High morale, low accountability.", "management_strategy": "Redefine kindness. Data-driven feedback.", "meeting_protocol": "Start with failure review.", "team_building": "Debate club."},
    "Facilitator": {"title": "The United Nations", "impact_analysis": "Inclusive, but analysis paralysis.", "management_strategy": "The 51% rule. Disagree and commit.", "meeting_protocol": "Decision deadlines.", "team_building": "Escape rooms (timed decisions)."},
    "Tracker": {"title": "The Audit Team", "impact_analysis": "Compliant, but rigid.", "management_strategy": "Safe-to-fail zones. The 'Why' test.", "meeting_protocol": "Ban 'we always did it this way'.", "team_building": "Improv games."}
}

MISSING_VOICE_GUIDE = {
    "Director": {"risk": "No urgency. Decisions linger.", "fix": "Set artificial deadlines. Use command language."},
    "Encourager": {"risk": "Cold culture. Burnout high.", "fix": "Operationalize care. Start meetings with check-ins."},
    "Facilitator": {"risk": "Steamrolling. Loudest voice wins.", "fix": "Round-robin speaking. Ask 'who haven't we heard from?'"},
    "Tracker": {"risk": "Chaos. dropped details.", "fix": "Create checklists. Assign a safety captain."}
}

MOTIVATION_GAP_GUIDE = {
    "Achievement": {"warning": "Runs on winning.", "coaching": "Visual scoreboards. Micro-wins."},
    "Connection": {"warning": "Runs on belonging.", "coaching": "Face time. Rituals. Protect the vibe."},
    "Growth": {"warning": "Runs on competence.", "coaching": "Micro-promotions. Mentorship."},
    "Purpose": {"warning": "Runs on mission.", "coaching": "Connect dots to youth. Storytelling."}
}

SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {"tension": "Efficiency vs Empathy", "psychology": "Safety in speed vs Safety in connection.", "watch_fors": ["Shut down", "Smile & nod"], "intervention_steps": ["Disarm threat", "Translate intent"], "scripts": {"Opening": "I want to talk task, but first how are you?"}},
        "Facilitator": {"tension": "Speed vs Process", "psychology": "Done vs Fair.", "watch_fors": ["Delaying", "Passive resistance"], "intervention_steps": ["Define sandbox", "Good enough agreement"], "scripts": {"Opening": "I know this feels rushed."}},
        "Tracker": {"tension": "Innovation vs Compliance", "psychology": "Break rules vs Follow rules.", "watch_fors": ["Rulebook defense", "Anxiety"], "intervention_steps": ["Pre-mortem", "Trial runs"], "scripts": {"Opening": "I need your eyes on this to make it safe."}}
    }
}

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From Hero to Conductor", "why": "Identity crisis of not doing it yourself.", 
            "conversation": "Your value changed from running fast to directing traffic.",
            "assignment_setup": "Force them to lead verbally.", "assignment_task": "The Chair Challenge: Sit for 1 hour.",
            "success_indicators": "Remained in chair. Used questions.", "red_flags": "Jumped up to fix things."
        }
    }
}


# --- 5c. HELPER FUNCTIONS ---

def send_pdf_via_email(to_email, subject, body, pdf_bytes, filename):
    """Sends the generated PDF via SMTP."""
    if "EMAIL_USER" not in st.secrets or "EMAIL_PASSWORD" not in st.secrets:
        return False, "⚠️ SMTP credentials not found in secrets.toml."

    smtp_server = st.secrets.get("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = st.secrets.get("EMAIL_PORT", 587)
    sender_email = st.secrets["EMAIL_USER"]
    sender_password = st.secrets["EMAIL_PASSWORD"]

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "✅ Email sent successfully!"
    except Exception as e:
        return False, f"❌ Error sending email: {str(e)}"

def generate_profile_content(comm, motiv):
    combo_key = f"{comm}-{motiv}"
    c_data = COMM_PROFILES.get(comm, {})
    m_data = MOTIV_PROFILES.get(motiv, {})
    i_data = INTEGRATED_PROFILES.get(combo_key, {})

    return {
        "s1_b": c_data.get('bullets', []), "s2_b": c_data.get('supervising_bullets', []),
        "s3_b": m_data.get('bullets', []), "s4_b": m_data.get('strategies_bullets', []),
        "s5": f"**Profile:** {i_data.get('title', 'N/A')}\n\n{i_data.get('synergy', '')}",
        "s6": i_data.get('support', ''), "s7": i_data.get('thriving', ''),
        "s8": i_data.get('struggling', ''), "s9": "Strategies for Course Correction:",
        "s9_b": i_data.get('interventions', []), "s10_b": m_data.get('celebrate_bullets', []),
        "coaching": i_data.get('questions', []), "advancement": i_data.get('advancement', '')
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (1, 91, 173); black = (0, 0, 0)
    
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(8)
    
    data = generate_profile_content(p_comm, p_mot)

    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True); pdf.ln(2)
        pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
        if body: pdf.multi_cell(0, 5, clean_text(body.replace("**", "").replace("* ", "- ")))
        if bullets:
            pdf.ln(1)
            for b in bullets:
                pdf.cell(5, 5, "-", 0, 0)
                pdf.multi_cell(0, 5, clean_text(b.replace("**", "")))
        pdf.ln(4)

    add_section(f"1. Communication Profile: {p_comm}", None, data['s1_b']) 
    add_section("2. Supervising Their Communication", None, data['s2_b'])
    add_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    add_section("4. Motivating This Staff Member", None, data['s4_b'])
    add_section("5. Integrated Leadership Profile", data['s5']) 
    add_section("6. How You Can Best Support Them", data['s6'])
    add_section("7. What They Look Like When Thriving", data['s7'])
    add_section("8. What They Look Like When Struggling", data['s8'])
    add_section("9. Supervisory Interventions", None, data['s9_b'])
    add_section("10. What You Should Celebrate", None, data['s10_b'])
    add_section("11. Helping Them Prepare for Advancement", data['advancement'])
    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)
    st.markdown("---"); st.markdown(f"### 📘 Supervisory Guide: {name}"); st.divider()
    
    def show_section(title, text, bullets=None):
        st.subheader(title)
        if text: st.write(text)
        if bullets:
            for b in bullets: st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)

    show_section(f"1. Communication Profile: {p_comm}", None, data['s1_b'])
    show_section("2. Supervising Their Communication", None, data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    show_section("4. Motivating This Staff Member", None, data['s4_b'])
    show_section("5. Integrated Leadership Profile", data['s5'])
    show_section("6. How You Can Best Support Them", data['s6'])
    c1, c2 = st.columns(2)
    with c1: st.subheader("7. Thriving"); st.success(data['s7'])
    with c2: st.subheader("8. Struggling"); st.error(data['s8'])
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. Supervisory Interventions", None, data['s9_b'])
    show_section("10. What You Should Celebrate", None, data['s10_b'])
    show_section("11. Helping Them Prepare for Advancement", data['advancement'])

# --- 6. MAIN APP LOGIC ---
def reset_t1(): st.session_state.t1_staff_select = None; st.session_state.pop("generated_pdf", None)
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None; st.session_state.messages = []
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- HERO SECTION ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Elmcrest Leadership Intelligence</div>
    <div class="hero-subtitle">Your command center for staff development. Select a tool below to begin.</div>
</div>
""", unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("📝 Supervisor's Guide\n\nCreate coaching manuals.", use_container_width=True): set_view("Supervisor's Guide")
with nav_col2:
    if st.button("🧬 Team DNA\n\nAnalyze unit culture.", use_container_width=True): set_view("Team DNA")
with nav_col3:
    if st.button("⚖️ Conflict Mediator\n\nScripts for tough talks.", use_container_width=True): set_view("Conflict Mediator")
with nav_col4:
    if st.button("🚀 Career Pathfinder\n\nPromotion readiness.", use_container_width=True): set_view("Career Pathfinder")
st.markdown("###")
if st.button("📈 Organization Pulse (See All Data)", use_container_width=True): set_view("Org Pulse")
st.markdown("---")

# --- VIEW CONTROLLER ---

# 1. Supervisor's Guide
if st.session_state.current_view == "Supervisor's Guide":
    st.subheader("📝 Supervisor's Guide")
    sub1, sub2 = st.tabs(["Database", "Manual"])
    
    with sub1:
        if not df.empty:
            filtered_staff_list = df.to_dict('records')
            options = {f"{s['name']} ({s['role']})": s for s in filtered_staff_list}
            
            sel = st.selectbox("Select Staff", options.keys(), index=None, key="t1_staff_select")
            if sel:
                d = options[sel]
                c1,c2,c3 = st.columns(3)
                c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                
                if st.button("Generate Guide", type="primary"):
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
    
    with sub2:
        with st.form("manual"):
            c1,c2 = st.columns(2)
            mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
            mpc = c1.selectbox("Comm", COMM_TRAITS); mpm = c2.selectbox("Motiv", MOTIV_TRAITS)
            
            if st.form_submit_button("Generate") and mn:
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

# 2. TEAM DNA
elif st.session_state.current_view == "Team DNA":
    st.subheader("🧬 Team DNA")
    if not df.empty:
        teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        if teams:
            tdf = df[df['name'].isin(teams)]
            c1, c2 = st.columns(2)
            with c1:
                comm_counts = tdf['p_comm'].value_counts()
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, title="Communication Mix", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
                
                if not comm_counts.empty:
                    dom_style = comm_counts.idxmax()
                    ratio = comm_counts.max() / len(tdf)
                    
                    if ratio > 0.5:
                        guide = TEAM_CULTURE_GUIDE.get(dom_style, {})
                        st.warning(f"⚠️ **Dominant Culture:** This team is {int(ratio*100)}% **{dom_style}**.")
                        with st.expander(f"📖 Managing the {guide.get('title', dom_style)}", expanded=True):
                            st.markdown(f"**The Vibe:**\n{guide.get('impact_analysis')}")
                            st.markdown(guide.get('management_strategy'))
                            st.markdown(f"**📋 Meeting Protocol:**\n{guide.get('meeting_protocol')}")
                            st.info(f"**🎉 Team Building Idea:** {guide.get('team_building')}")
                    else:
                        st.info("**Balanced Culture:** No single style dominates.")
                
                present_styles = set(tdf['p_comm'].unique())
                missing_styles = set(COMM_TRAITS) - present_styles
                if missing_styles:
                    st.markdown("---")
                    st.error(f"🚫 **Missing Voices:** {', '.join(missing_styles)}")
                    for style in missing_styles:
                        data = MISSING_VOICE_GUIDE.get(style, {})
                        st.write(f"**Risk:** {data.get('risk')} | **Fix:** {data.get('fix')}")

            with c2:
                mot_counts = tdf['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
                
                if not mot_counts.empty:
                    dom_mot = mot_counts.idxmax()
                    st.markdown("---")
                    st.subheader(f"⚠️ Motivation Gap: {dom_mot} Driven")
                    mot_guide = MOTIVATION_GAP_GUIDE.get(dom_mot, {})
                    if mot_guide:
                        st.warning(mot_guide['warning'])
                        st.markdown(mot_guide['coaching'])
            st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    if not df.empty:
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1")
        p2 = c2.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            s1, s2 = d1['p_comm'], d2['p_comm']
            st.divider()
            st.subheader(f"{s1} (Sup) vs. {s2} (Staff)")
            if s1 in SUPERVISOR_CLASH_MATRIX and s2 in SUPERVISOR_CLASH_MATRIX[s1]:
                clash = SUPERVISOR_CLASH_MATRIX[s1][s2]
                st.markdown(f"**Tension:** {clash['tension']}")
                st.markdown(f"**Psychology:** {clash['psychology']}")
                st.info(f"**Intervention:** {clash['intervention_steps'][0]}")
                st.success(f"**Script:** \"{clash['scripts']['Opening']}\"")
            else: st.info("No specific protocol. Focus on active listening.")
        st.button("Reset", key="reset_t3", on_click=reset_t3)

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    if not df.empty:
        c1, c2 = st.columns(2)
        cand = c1.selectbox("Candidate", df['name'].unique(), index=None, key="career")
        role = c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor"], index=None, key="career_target")
        if cand and role:
            d = df[df['name']==cand].iloc[0]
            style = d['p_comm']
            path = CAREER_PATHWAYS.get(style, {}).get(role)
            if path:
                st.info(f"**Shift:** {path['shift']}")
                st.markdown(f"**Why it's hard:** {path['why']}")
                st.success(f"**Assignment:** {path['assignment_task']}")
            else: st.warning("Path not defined in database yet.")
        st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        total_staff = len(df)
        comm_counts = df['p_comm'].value_counts(normalize=True) * 100
        mot_counts = df['p_mot'].value_counts(normalize=True) * 100
        
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
                st.markdown("##### 🗣️ Communication Mix")
                st.plotly_chart(px.pie(df, names='p_comm', color='p_comm', color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
            with c_b: 
                st.markdown("##### 🔋 Motivation Drivers")
                st.plotly_chart(px.bar(df['p_mot'].value_counts(), orientation='h', color_discrete_sequence=[BRAND_COLORS['blue']]), use_container_width=True)
    else: st.warning("No data available.")
