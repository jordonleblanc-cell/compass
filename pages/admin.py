import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE FOR NAVIGATION ---
if "current_view" not in st.session_state:
    st.session_state.current_view = "Guide Generator"

def set_view(view_name):
    st.session_state.current_view = view_name

# --- SECURITY: PASSWORD CHECK ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    PASSWORD = st.secrets.get("ADMIN_PASSWORD", "elmcrest2025") 
    if st.session_state.password_input == PASSWORD:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Incorrect password")

if not st.session_state.authenticated:
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle at center, #f1f5f9 0%, #cbd5e1 100%); }
        [data-testid="stHeader"] { background: transparent; }
        .login-card {
            background: white; padding: 40px; border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;
            max-width: 400px; margin: 100px auto;
            border: 1px solid #e2e8f0;
        }
        .login-title { color: #015bad; font-size: 1.8rem; font-weight: 800; margin-bottom: 10px; }
        .login-subtitle { color: #64748b; margin-bottom: 20px; }
        </style>
        <div class='login-card'>
            <div class='login-title'>Supervisor Access</div>
            <div class='login-subtitle'>Please enter your credentials to access the leadership dashboard.</div>
        </div>
    """, unsafe_allow_html=True)
    st.text_input("Password", type="password", key="password_input", on_change=check_password)
    st.stop()

# ==========================================
# SUPERVISOR TOOL LOGIC STARTS HERE
# ==========================================

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

BRAND_COLORS = {
    "blue": "#015bad",
    "teal": "#51c3c5",
    "green": "#b9dca4",
    "dark": "#0f172a",
    "gray": "#64748b",
    "light_gray": "#f8fafc"
}

# --- 3. CSS STYLING (Light & Dark Mode Support) ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* DEFINE THEMES */
        :root {{
            --primary: {BRAND_COLORS['blue']};
            --secondary: {BRAND_COLORS['teal']};
            --accent: {BRAND_COLORS['green']};
            
            /* Light Mode Defaults */
            --text-main: #0f172a;
            --text-sub: #475569;
            --bg-start: #f8fafc;
            --bg-end: #e2e8f0;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --shadow: 0 4px 20px rgba(0,0,0,0.05);
            --input-bg: #ffffff;
            --btn-text: #ffffff;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                /* Dark Mode Overrides */
                --text-main: #f1f5f9;
                --text-sub: #cbd5e1;
                --bg-start: #0f172a;
                --bg-end: #020617;
                --card-bg: #1e293b;
                --border-color: #334155;
                --shadow: 0 4px 20px rgba(0,0,0,0.4);
                --input-bg: #0f172a;
            }}
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text-main) !important;
        }}
        
        .stApp {{
            background: radial-gradient(circle at top left, var(--bg-start) 0%, var(--bg-end) 100%);
        }}

        h1, h2, h3, h4 {{
            color: var(--primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}
        
        /* Custom Cards */
        .custom-card {{
            background-color: var(--card-bg);
            padding: 24px;
            border-radius: 16px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
            margin-bottom: 20px;
            color: var(--text-main);
        }}
        
        /* Hero Section */
        .hero-box {{
            background: linear-gradient(135deg, #015bad 0%, #0f172a 100%);
            padding: 40px 30px;
            border-radius: 16px;
            color: white !important;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(1, 91, 173, 0.2);
        }}
        .hero-title {{ color: white !important; font-size: 2.2rem; font-weight: 800; margin-bottom:10px; }}
        .hero-subtitle {{ color: #e2e8f0 !important; font-size: 1.1rem; opacity: 0.9; max-width: 800px; line-height: 1.6; }}

        /* NAVIGATION BUTTONS AS CARDS */
        /* We target the buttons inside the navigation columns specifically */
        div[data-testid="column"] .stButton button {{
            background-color: var(--card-bg);
            background-image: none;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            height: 140px; /* Make them tall like cards */
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            padding: 20px;
            white-space: pre-wrap; /* Allow newlines */
            text-align: left;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }}

        div[data-testid="column"] .stButton button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            border-color: var(--primary);
            color: var(--primary) !important;
        }}
        
        div[data-testid="column"] .stButton button:active {{
            background-color: var(--input-bg);
        }}

        /* Standard Buttons (Generate, Reset, etc.) */
        /* We use a specific selector or just let them be default primary style */
        .stButton button:not([style*="height: 140px"]) {{
             /* Standard button styling fallback or overrides if needed for other buttons */
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px; background-color: var(--card-bg);
            border-radius: 8px 8px 0 0; border: 1px solid var(--border-color);
            border-bottom: none; padding: 0 20px; font-weight: 600;
            color: var(--text-sub);
        }}
        .stTabs [aria-selected="true"] {{
            background-color: var(--bg-start) !important;
            color: var(--primary) !important;
            border-top: 3px solid var(--primary) !important;
        }}

        /* Input Fields & Selectboxes */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: var(--card-bg) !important;
            color: var(--text-main) !important;
            border-color: var(--border-color) !important;
        }}
        div[data-baseweb="popover"] {{ background-color: var(--card-bg) !important; }}
        div[data-baseweb="menu"] {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; }}

        /* Dataframes */
        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--border-color);
            border-radius: 12px; overflow: hidden;
        }}
        
        /* Metric Boxes */
        div[data-testid="stMetric"] {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 10px;
            box-shadow: var(--shadow);
        }}
        div[data-testid="stMetricLabel"] {{ color: var(--text-sub) !important; }}
        div[data-testid="stMetricValue"] {{ color: var(--primary) !important; }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: var(--card-bg) !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
        }}
        div[data-testid="stExpander"] {{
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CONTENT DICTIONARIES (Full Content) ---
# (Included for completeness so the file runs standalone)

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "The 'Bulldozer vs. Doormat' Dynamic.",
            "root_cause": "Value Mismatch: Utility vs. Affirmation.",
            "watch_fors": ["Encourager silent in meetings", "Director interrupting", "Encourager complaining of 'meanness'"],
            "intervention_steps": ["**Pre-Frame:** 'Efficiency without Empathy is Inefficiency.'", "**Translate:** Feelings are data about team health.", "**The Deal:** Listen for 5 mins before solving."],
            "scripts": {"To Director": "You are trying to fix the problem, but right now, the *relationship* is the problem.", "To Encourager": "My brevity is not anger; it is urgency. I need you to tell me: 'I can help you win, but I need you to lower your volume.'", "Joint": "We are speaking two different languages. I will validate your concern before we move to the next step."}
        },
        "Facilitator": {"tension": "Gas vs. Brake", "root_cause": "Stagnation vs. Error", "watch_fors": ["Email commands", "Indecision"], "intervention_steps": ["Define Clock", "Define Veto", "Debrief"], "scripts": {"To Director": "Force = Compliance, not Buy-in.", "To Facilitator": "Silence = Agreement.", "Joint": "Set a timer."}},
        "Tracker": {"tension": "Vision vs. Obstacle", "root_cause": "Intuition vs. Handbook", "watch_fors": ["Quoting policy", "Bypassing"], "intervention_steps": ["Clarify Roles", "Yes If", "Risk Acceptance"], "scripts": {"To Director": "They are protecting you.", "To Tracker": "Start with solution.", "Joint": "Destination vs. Brakes."}},
        "Director": {"tension": "King vs. King", "root_cause": "Dominance/Control", "watch_fors": ["Interruptions", "Debates"], "intervention_steps": ["Separate Lanes", "Truce", "Commit"], "scripts": {"To Director": "Fighting to be right vs effective.", "To Other": "Strip the tone.", "Joint": "Stop fighting for the wheel."}}
    },
    "Encourager": {
        "Director": {"tension": "Sensitivity Gap", "root_cause": "External vs Internal Validation", "watch_fors": ["Apologizing", "Venting"], "intervention_steps": ["Headline First", "Explain Why", "Scheduled Venting"], "scripts": {"To Encourager": "Translate feelings to business risk.", "To Director": "Please/Thank you buys speed.", "Joint": "Timeline vs Communication Plan."}},
        "Facilitator": {"tension": "Polite Stagnation", "root_cause": "Rejection vs Unfairness", "watch_fors": ["Endless meetings", "Passive language"], "intervention_steps": ["Name Fear", "Assign Bad Guy", "Script It"], "scripts": {"To Encourager": "Protecting feelings hurts program.", "To Facilitator": "Consensus search is procrastination.", "Joint": "Who delivers the news?"}},
        "Tracker": {"tension": "Rigidity vs Flow", "root_cause": "Connection vs Consistency", "watch_fors": ["Secret deals", "Public policing"], "intervention_steps": ["Why of Rules", "Why of Exceptions", "Hybrid"], "scripts": {"To Encourager": "Bending rules makes Tracker the bad guy.", "To Tracker": "Right policy, cold delivery."}},
        "Encourager": {"tension": "Echo Chamber", "root_cause": "Emotional Contagion", "watch_fors": ["Venting only", "Us vs Them"], "intervention_steps": ["5 Min Rule", "Pivot", "Data"], "scripts": {"To Encourager": "We are spinning.", "Joint": "Challenge each other."}}
    },
    "Facilitator": {
        "Director": {"tension": "Steamroll", "root_cause": "External vs Internal Processing", "watch_fors": ["Silence", "Assumed Agreement"], "intervention_steps": ["Interrupt", "Pre-Meeting", "Frame Risk"], "scripts": {"To Director": "Moving too fast.", "To Facilitator": "Speak up."}},
        "Tracker": {"tension": "Details Loop", "root_cause": "Horizontal vs Vertical Scope", "watch_fors": ["Email chains", "Overtime meetings"], "intervention_steps": ["Concept First", "Detail Second", "Parking Lot"], "scripts": {"To Tracker": "30,000 ft view.", "To Facilitator": "Testing the idea."}},
        "Encourager": {"tension": "Fairness vs Feelings", "root_cause": "System vs Person", "watch_fors": ["Exceptions", "Inequity"], "intervention_steps": ["Validate Intent", "Explain Inequity", "Standard"], "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart first."}}
    },
    "Tracker": {
        "Director": {"tension": "Micromanagement Trap", "root_cause": "Verification vs Competence", "watch_fors": ["Corrections", "Avoidance"], "intervention_steps": ["Pick Battles", "Sandbox", "Solution First"], "scripts": {"To Director": "Compliance safety.", "To Tracker": "Stop correcting spelling."}},
        "Encourager": {"tension": "Rules vs Relationship", "root_cause": "Safety source mismatch", "watch_fors": ["Public correction", "Resentment"], "intervention_steps": ["Explain Why", "Connect First", "Hybrid"], "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect safety."}},
        "Facilitator": {"tension": "Details vs Concepts", "root_cause": "Checklist vs Conversation", "watch_fors": ["Frustration", "Confusion"], "intervention_steps": ["Deliverable check", "Operationalize", "Collaborate"], "scripts": {"To Tracker": "Alignment is the deliverable.", "To Facilitator": "Define the to-do."}}
    }
}
# Fallback
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {
                "tension": "Differing perspectives.", "root_cause": "Priorities.", "watch_fors": [], "intervention_steps": ["Listen", "Align"], "scripts": {"To Supervisor": "Align.", "To Staff": "Align.", "Joint": "Align."}
            }

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {"shift": "Doing -> Enabling", "why": "If you fix everything, team learns nothing.", "conversation": "Sit on your hands. Success is team confidence, not your speed.", "assignment_setup": "Lead shift from office.", "assignment_task": "Verbal direction only.", "success_indicators": "Clear verbal commands.", "red_flags": "Running out to fix it.", "supervisor_focus": "Hero Mode"},
        "Program Supervisor": {"shift": "Command -> Influence", "why": "Can't order peers.", "conversation": "Slow down to build relationships.", "assignment_setup": "Peer project.", "assignment_task": "Cross-dept interview.", "success_indicators": "Incorporated feedback.", "red_flags": "100% own idea.", "supervisor_focus": "Patience"},
        "Manager": {"shift": "Tactical -> Strategic", "why": "Prevent fires.", "conversation": "Reliance on systems vs will.", "assignment_setup": "Strategic plan.", "assignment_task": "Data/Budget projection.", "success_indicators": "Systems thinking.", "red_flags": "Last minute planning.", "supervisor_focus": "Horizon check"}
    },
    "Encourager": {
        "Shift Supervisor": {"shift": "Friend -> Guardian", "why": "Accountability is kindness.", "conversation": "Be a guardian of the standard.", "assignment_setup": "Policy reset.", "assignment_task": "Lead accountability meeting.", "success_indicators": "No apologies.", "red_flags": "Joking/Apologizing.", "supervisor_focus": "Apology Language"},
        "Program Supervisor": {"shift": "Vibe -> Structure", "why": "Structure protects team.", "conversation": "Master the boring parts.", "assignment_setup": "Audit.", "assignment_task": "Present data/rationale.", "success_indicators": "Accurate/Factual.", "red_flags": "Delegating/Procrastinating.", "supervisor_focus": "Organization"},
        "Manager": {"shift": "Caregiver -> Director", "why": "Weight is too heavy.", "conversation": "Set emotional boundaries.", "assignment_setup": "Resource conflict.", "assignment_task": "Deliver a No.", "success_indicators": "Holding the line.", "red_flags": "Caving.", "supervisor_focus": "Burnout"}
    },
    "Facilitator": {
        "Shift Supervisor": {"shift": "Peer -> Decider", "why": "Consensus isn't always safe.", "conversation": "Make the 51% decision.", "assignment_setup": "Crisis drill.", "assignment_task": "Immediate calls.", "success_indicators": "Direct commands.", "red_flags": "Seeking consensus.", "supervisor_focus": "Speed"},
        "Program Supervisor": {"shift": "Mediator -> Visionary", "why": "Lead from front.", "conversation": "Inject your vision.", "assignment_setup": "Culture initiative.", "assignment_task": "Present as direction.", "success_indicators": "Declarative statements.", "red_flags": "Asking for permission.", "supervisor_focus": "The Buffer"},
        "Manager": {"shift": "Process -> Outcome", "why": "Fairness can stall results.", "conversation": "Prioritize outcome over comfort.", "assignment_setup": "Unpopular policy.", "assignment_task": "Implement without changing.", "success_indicators": "On time implementation.", "red_flags": "Delays/Watering down.", "supervisor_focus": "Conflict Tolerance"}
    },
    "Tracker": {
        "Shift Supervisor": {"shift": "Executor -> Overseer", "why": "Micromanagement burns out.", "conversation": "Trust the team.", "assignment_setup": "Hands-off day.", "assignment_task": "Supervise complex task verbally.", "success_indicators": "Hands in pockets.", "red_flags": "Grabbing pen.", "supervisor_focus": "Micromanagement"},
        "Program Supervisor": {"shift": "Black/White -> Gray", "why": "Rules don't cover everything.", "conversation": "Develop intuition.", "assignment_setup": "Complex complaint.", "assignment_task": "Principle-based decision.", "success_indicators": "Sensible exception.", "red_flags": "Freezing.", "supervisor_focus": "Rigidity"},
        "Manager": {"shift": "Compliance -> Culture", "why": "Efficiency over people breaks culture.", "conversation": "Invest in feelings.", "assignment_setup": "Retention initiative.", "assignment_task": "Focus on relationships.", "success_indicators": "Non-work chats.", "red_flags": "Checklist morale.", "supervisor_focus": "Human Element"}
    }
}

COMM_PROFILES = {
    "Director": {"overview": "Leads with clarity, structure, and urgency.", "supervising": "Be direct, concise. Don't micromanage.", "struggle_bullets": ["Impatience", "Over-assertiveness", "Steamrolling"], "coaching": ["What are the risks of speed?", "Who haven't we heard from?"], "advancement": "Shift from Command to Influence."},
    "Encourager": {"overview": "Leads with warmth, optimism, and EQ.", "supervising": "Connect relationally first.", "struggle_bullets": ["Conflict avoidance", "Disorganization"], "coaching": ["Prioritizing popularity?", "Hard truths?"], "advancement": "Master operations/structure."},
    "Facilitator": {"overview": "Leads by listening and consensus.", "supervising": "Give time to process.", "struggle_bullets": ["Analysis paralysis", "Indecision"], "coaching": ["Cost of waiting?", "Your opinion?"], "advancement": "Develop executive presence."},
    "Tracker": {"overview": "Leads with data, details, systems.", "supervising": "Provide clear expectations.", "struggle_bullets": ["Rigidity", "Micromanagement"], "coaching": ["Safety vs Preference?", "Big picture?"], "advancement": "Delegate details."}
}
MOTIVATION_PROFILES = {
    "Growth": {"name": "Growth", "tagline": "The Learner", "summary": "Thrives on progress and challenge.", "boosters": ["Stretch goals", "Training"], "killers": ["Repetition", "Stagnation"], "roleSupport": {"Program Supervisor": "Career pathing", "Shift Supervisor": "Skill practice", "YDP": "Realistic goals"}, "motivating": "Give problems to solve.", "support": "Sponsor training.", "thriving_bullets": ["Proactive", "Mentoring"], "intervention": "Add learning challenge.", "celebrate": "Skill acquisition."},
    "Purpose": {"name": "Purpose", "tagline": "The Missionary", "summary": "Thrives on meaning and alignment.", "boosters": ["Mission connection", "Ethics"], "killers": ["Bureaucracy", "Injustice"], "roleSupport": {"Program Supervisor": "Policy collab", "Shift Supervisor": "Explain why", "YDP": "Values check"}, "motivating": "Connect to mission.", "support": "Validate passion.", "thriving_bullets": ["Advocacy", "Integrity"], "intervention": "Reconnect to 'Why'.", "celebrate": "Impact stories."},
    "Connection": {"name": "Connection", "tagline": "The Builder", "summary": "Thrives on belonging and team.", "boosters": ["Team bonding", "Recognition"], "killers": ["Isolation", "Conflict"], "roleSupport": {"Program Supervisor": "Peer networks", "Shift Supervisor": "Rituals", "YDP": "Inclusion"}, "motivating": "Prioritize team.", "support": "Ensure no isolation.", "thriving_bullets": ["Collaboration", "Morale"], "intervention": "Repair relationships.", "celebrate": "Culture contribution."},
    "Achievement": {"name": "Achievement", "tagline": "The Architect", "summary": "Thrives on goals and completion.", "boosters": ["Metrics", "Checklists"], "killers": ["Vague goals", "No credit"], "roleSupport": {"Program Supervisor": "Metrics design", "Shift Supervisor": "Unit goals", "YDP": "Clear wins"}, "motivating": "Set clear goals.", "support": "Remove blockers.", "thriving_bullets": ["Efficiency", "Output"], "intervention": "Clarify success.", "celebrate": "Reliability."}
}

# --- 5. HELPER FUNCTIONS ---
def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

@st.cache_data(ttl=60)
def fetch_staff_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200: return response.json()
        return []
    except: return []

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (1, 91, 173); black = (0, 0, 0)
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(8)
    
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*blue)
        pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(2)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        pdf.multi_cell(0, 5, clean_text(body))
        if bullets:
            for b in bullets:
                pdf.cell(5, 5, "-", 0, 0)
                pdf.multi_cell(0, 5, clean_text(b))
        pdf.ln(4)

    add_section(f"1. Communication: {p_comm}", c['overview'])
    add_section("2. Supervising Their Communication", c['supervising'])
    add_section(f"3. Motivation: {p_mot}", m['overview'])
    add_section("4. Motivating Them", m['motivating'])
    
    integrated = f"Leads with {p_comm} traits to achieve {p_mot} goals. When aligned, they are unstoppable. Conflict between speed ({p_comm}) and needs ({p_mot}) causes stress."
    add_section("5. Integrated Leadership Profile", integrated)
    
    add_section("6. Best Support", m['support'])
    add_section("7. Thriving Signs", "Look for:", m['thriving_bullets'])
    add_section("8. Struggling Signs", "Look for:", c['struggle_bullets'])
    add_section("9. Interventions", m['intervention'])
    add_section("10. Celebrate", m['celebrate'])
    add_section("11. Coaching Questions", "Ask these:", c['coaching'])
    add_section("12. Advancement", c['advancement'])
    
    return pdf.output(dest='S').encode('latin-1')

# --- 6. MAIN APP LOGIC ---
staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# Reset Helpers
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- HERO SECTION (LANDING PAGE) ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Elmcrest Leadership Intelligence</div>
    <div class="hero-subtitle">
        Your command center for staff development. Select a tool below to begin.
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION MENU ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("📝 Guide Generator\n\nCreate 12-point coaching manuals.", use_container_width=True):
        set_view("Guide Generator")

with nav_col2:
    if st.button("🧬 Team DNA\n\nAnalyze unit culture & blindspots.", use_container_width=True):
        set_view("Team DNA")

with nav_col3:
    if st.button("⚖️ Conflict Mediator\n\nScripts for tough conversations.", use_container_width=True):
        set_view("Conflict Mediator")

with nav_col4:
    if st.button("🚀 Career Pathfinder\n\nPromotion readiness tests.", use_container_width=True):
        set_view("Career Pathfinder")

# Org Pulse Button
st.markdown("###")
if st.button("📈 Organization Pulse (See All Data)", use_container_width=True):
    set_view("Org Pulse")

st.markdown("---")

# --- VIEW CONTROLLER ---

# 1. GUIDE GENERATOR
if st.session_state.current_view == "Guide Generator":
    st.subheader("📝 Guide Generator")
    sub1, sub2 = st.tabs(["Database", "Manual"])
    with sub1:
        if not df.empty:
            options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            sel = st.selectbox("Select Staff", options.keys(), index=None, key="t1_staff_select")
            if sel:
                d = options[sel]
                c1,c2,c3 = st.columns(3)
                c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                if st.button("Generate Guide", type="primary"):
                    pdf = create_supervisor_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                    st.download_button("Download PDF", pdf, f"Guide_{d['name']}.pdf", "application/pdf")
                    
                    # Instant View
                    st.divider()
                    st.markdown("### Quick Preview")
                    c = COMM_PROFILES[d['p_comm']]; m = MOTIVATION_PROFILES[d['p_mot']]
                    st.info(f"**Supervising:** {c['supervising']}")
                    st.success(f"**Motivating:** {m['motivating']}")
                st.button("Reset", on_click=reset_t1)
    with sub2:
        with st.form("manual"):
            c1,c2 = st.columns(2)
            mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
            mpc = c1.selectbox("Comm", COMM_TRAITS.keys()); mpm = c2.selectbox("Motiv", ["Growth", "Purpose", "Connection", "Achievement"])
            if st.form_submit_button("Generate") and mn:
                pdf = create_supervisor_guide(mn, mr, mpc, None, mpm, None)
                st.download_button("Download PDF", pdf, "guide.pdf", "application/pdf")

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
                present = set(tdf['p_comm'].unique()); missing = set(COMM_TRAITS.keys()) - present
                if missing: st.error(f"🚫 **Blindspot Alert:** This team lacks **{', '.join(missing)}** energy.")
            with c2:
                mot_counts = tdf['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
            st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    if not df.empty:
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Supervisor", df['name'].unique(), index=None, key="p1")
        p2 = c2.selectbox("Staff", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            s1, s2 = d1['p_comm'], d2['p_comm']
            
            st.divider()
            st.subheader(f"{s1} (Sup) vs. {s2} (Staff)")
            
            if s1 in SUPERVISOR_CLASH_MATRIX and s2 in SUPERVISOR_CLASH_MATRIX[s1]:
                clash = SUPERVISOR_CLASH_MATRIX[s1][s2]
                with st.expander("🔍 Root Cause Analysis", expanded=True):
                    st.markdown(f"**The Dynamic:** {clash['tension']}")
                    st.markdown(f"**Root Cause:** {clash['root_cause']}")
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("##### 🚩 Watch For")
                    for w in clash['watch_fors']: st.write(f"• {w}")
                    st.markdown("##### 🛠️ Intervention Steps")
                    for i in clash['intervention_steps']: st.info(i)
                with c_b:
                    st.markdown("##### 🗣️ Coaching Scripts")
                    st.success(f"**You Say:** \"{clash['scripts'].get('To '+s1, '...')}\"")
                    st.warning(f"**They Hear:** \"{clash['scripts'].get('To '+s2, '...')}\"")
                    st.info(f"**Joint Goal:** \"{clash['scripts'].get('Joint', '...')}\"")
            else: st.info("Same-style match. Focus on not amplifying weaknesses.")
            st.button("Reset", key="reset_t3", on_click=reset_t3)

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    if not df.empty:
        c1, c2 = st.columns(2)
        cand = c1.selectbox("Candidate", df['name'].unique(), index=None, key="career")
        role = c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target")
        
        if cand and role:
            d = df[df['name']==cand].iloc[0]
            style = d['p_comm']
            path = CAREER_PATHWAYS.get(style, {}).get(role)
            if path:
                st.info(f"**Shift:** {path['shift']}")
                c_a, c_b = st.columns(2)
                with c_a:
                    with st.container(border=True):
                        st.markdown("##### 🗣️ The Conversation")
                        st.write(path['conversation'])
                        st.warning(f"**Supervisor Watch Item:** {path.get('supervisor_focus')}")
                with c_b:
                    with st.container(border=True):
                        st.markdown("##### ✅ Assignment")
                        st.write(f"**Task:** {path['assignment_task']}")
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flag:** {path['red_flags']}")
            st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        top_comm = df['p_comm'].mode()[0]
        top_mot = df['p_mot'].mode()[0]
        c1.metric("Dominant Style", top_comm)
        c2.metric("Top Driver", top_mot)
        c3.metric("Total Staff", len(df))
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
        with c_b: 
            if 'role' in df.columns: st.plotly_chart(px.histogram(df, x="role", color="p_comm", title="Leadership Pipeline (Comm Style by Role)", color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
    else: st.warning("No data available.")
