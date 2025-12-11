import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px
import time
import json

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NAVIGATION HELPER ---
if "current_view" not in st.session_state:
    st.session_state.current_view = "Guide Generator"

def set_view(view_name):
    st.session_state.current_view = view_name

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

# --- 3. CSS STYLING ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --primary: {BRAND_COLORS['blue']};
            --secondary: {BRAND_COLORS['teal']};
            --accent: {BRAND_COLORS['green']};
            --text-main: #0f172a;
            --text-sub: #475569;
            --bg-start: #f8fafc;
            --bg-end: #e2e8f0;
            --card-bg: rgba(255, 255, 255, 0.9);
            --border-color: #e2e8f0;
            --shadow: 0 4px 20px rgba(0,0,0,0.05);
            --input-bg: #ffffff;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --text-main: #f1f5f9;
                --text-sub: #cbd5e1;
                --bg-start: #0f172a;
                --bg-end: #020617;
                --card-bg: rgba(30, 41, 59, 0.9);
                --border-color: #334155;
                --shadow: 0 4px 20px rgba(0,0,0,0.4);
                --input-bg: #0f172a;
            }}
        }}

        /* HIDE SIDEBAR NAVIGATION */
        [data-testid="stSidebarNav"] {{display: none;}}
        section[data-testid="stSidebar"] {{display: none;}}

        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: var(--text-main) !important; }}
        .stApp {{ background: radial-gradient(circle at top left, var(--bg-start) 0%, var(--bg-end) 100%); }}
        h1, h2, h3, h4 {{ color: var(--primary) !important; font-weight: 700 !important; letter-spacing: -0.02em; }}
        
        .custom-card {{ background-color: var(--card-bg); padding: 24px; border-radius: 16px; box-shadow: var(--shadow); border: 1px solid var(--border-color); margin-bottom: 20px; color: var(--text-main); backdrop-filter: blur(10px); }}
        
        .hero-box {{ background: linear-gradient(135deg, #015bad 0%, #0f172a 100%); padding: 40px; border-radius: 16px; color: white !important; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(1, 91, 173, 0.2); }}
        .hero-title {{ color: white !important; font-size: 2.2rem; font-weight: 800; margin-bottom:10px; }}
        .hero-subtitle {{ color: #e2e8f0 !important; font-size: 1.1rem; opacity: 0.9; max-width: 800px; line-height: 1.6; }}

        /* Navigation Buttons */
        div[data-testid="column"] .stButton button {{
            background-color: var(--card-bg); color: var(--text-main) !important; border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 140px; display: flex; flex-direction: column;
            align-items: flex-start; justify-content: center; padding: 20px; white-space: pre-wrap; text-align: left; transition: all 0.2s;
        }}
        div[data-testid="column"] .stButton button:hover {{
            transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); border-color: var(--primary); color: var(--primary) !important;
        }}
        
        /* Action Buttons */
        .stButton button:not([style*="height: 140px"]) {{
            background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white !important; border: none; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 10px rgba(1, 91, 173, 0.2);
        }}

        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: var(--input-bg) !important; color: var(--text-main) !important; border-color: var(--border-color) !important; border-radius: 8px; }}
        div[data-baseweb="popover"] {{ background-color: var(--card-bg) !important; }}
        div[data-baseweb="menu"] {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; }}
        div[data-testid="stDataFrame"] {{ border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }}
        .streamlit-expanderHeader {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; border: 1px solid var(--border-color); }}
        div[data-testid="stExpander"] {{ background-color: var(--card-bg) !important; border: 1px solid var(--border-color); border-radius: 8px; }}
        
        /* Login Specifics */
        .login-card {{
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 20px;
            box-shadow: var(--shadow);
            text-align: center;
            max-width: 400px;
            margin: 100px auto;
            border: 1px solid var(--border-color);
            color: var(--text-main);
            backdrop-filter: blur(12px);
        }}
        .login-title {{ color: var(--primary) !important; font-size: 1.8rem; font-weight: 800; margin-bottom: 10px; }}
        .login-subtitle {{ color: var(--text-sub) !important; margin-bottom: 20px; }}
        .back-link {{ text-decoration: none; color: var(--text-sub); font-weight: 600; transition: color 0.2s; }}
        .back-link:hover {{ color: var(--primary); }}
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
# Convert to DF and Normalize Columns immediately
df_all = pd.DataFrame(all_staff_list)

if not df_all.empty:
    # 1. Normalize Column Names (lowercase, strip)
    df_all.columns = df_all.columns.str.lower().str.strip() 
    
    # 2. Normalize String Values in Critical Columns (strip whitespace)
    if 'role' in df_all.columns:
        df_all['role'] = df_all['role'].astype(str).str.strip()
    if 'cottage' in df_all.columns:
        df_all['cottage'] = df_all['cottage'].astype(str).str.strip()
    if 'name' in df_all.columns:
        df_all['name'] = df_all['name'].astype(str).str.strip()

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
    # FETCH SECRETS (Keys from secrets.toml)
    MASTER_PW = st.secrets.get("ADMIN_PASSWORD", "admin2025")  # Master Access
    PS_PW = st.secrets.get("PS_PASSWORD", "ps2025")            # Program Supervisor Code
    SS_PW = st.secrets.get("SS_PASSWORD", "ss2025")            # Shift Supervisor Code
    
    input_pw = st.session_state.password_input
    selected_user = st.session_state.user_select
    
    # Authentication Logic
    authorized = False
    
    # Case 1: Administrator Login
    if selected_user == "Administrator":
        if input_pw == MASTER_PW:
            authorized = True
            st.session_state.current_user_name = "Administrator"
            st.session_state.current_user_role = "Admin"
            st.session_state.current_user_cottage = "All"
        else:
            st.error("Incorrect Administrator Password.")
            return

    # Case 2: Staff Login (Data Dependent)
    elif not df_all.empty:
        user_row = df_all[df_all['name'] == selected_user].iloc[0]
        role_raw = user_row.get('role', 'YDP')
        cottage_raw = user_row.get('cottage', 'All')
        
        # Role Validation Logic (Uses 'in' for safety against variations)
        if "Program Supervisor" in role_raw:
            if input_pw == PS_PW or input_pw == MASTER_PW:
                authorized = True
            else:
                st.error("Incorrect Access Code for Program Supervisors.")
                return
                
        elif "Shift Supervisor" in role_raw:
            if input_pw == SS_PW or input_pw == MASTER_PW:
                authorized = True
            else:
                st.error("Incorrect Access Code for Shift Supervisors.")
                return
        
        else:
            # Fallback for other roles (e.g., YDP) - Only Master PW works currently
            if input_pw == MASTER_PW:
                authorized = True
            else:
                st.error("Access Restricted. Please contact your administrator.")
                return

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    # Finalize Authentication
    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""
        <div style="position: absolute; top: 20px; left: 20px;">
            <a href="/" target="_self" class="back-link">← Back</a>
        </div>
        <div class='login-card'>
            <div class='login-title'>Supervisor Access</div>
            <div class='login-subtitle'>Select your name and enter your role's access code.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # User Selection for RBAC
    if not df_all.empty and 'name' in df_all.columns and 'role' in df_all.columns:
        # Filter dropdown to only show leadership roles (Case insensitive check)
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Admin"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Who are you?", user_names, key="user_select")
    else:
        st.selectbox("Who are you?", ["Administrator"], key="user_select")
        
    st.text_input("Access Code", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- 6. DATA FILTERING ENGINE (RBAC) ---
# This logic filters the dataframe based on who is logged in
def get_filtered_dataframe():
    user_role = st.session_state.current_user_role
    user_cottage = st.session_state.current_user_cottage
    current_user = st.session_state.current_user_name
    
    # If Admin, return everything
    if user_role == "Admin" or current_user == "Administrator":
        return df_all
    
    # Filter logic
    filtered_df = df_all.copy()
    
    # 1. Filter by Cottage (unless user sees all)
    if 'cottage' in df_all.columns:
        if user_cottage != "All":
             filtered_df = filtered_df[filtered_df['cottage'] == user_cottage]
    
    # 2. Filter by Hierarchy (AND ensure Self is visible)
    if 'role' in df_all.columns:
        if "Program Supervisor" in user_role:
            # PS sees: Shift Supervisors + YDPs + Themselves
            # Exclude: Admin, Other PS (unless self)
            condition = (filtered_df['role'].isin(['Shift Supervisor', 'YDP'])) | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
            
        elif "Shift Supervisor" in user_role:
            # SS sees: YDPs + Themselves
            # Exclude: Admin, PS, Other SS (unless self - debateable, but usually safe to restrict)
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
            
        elif "YDP" in user_role:
            # YDP sees: Only Themselves
            filtered_df = filtered_df[filtered_df['name'] == current_user]

    return filtered_df

# Get the data visible to THIS user
df = get_filtered_dataframe()

# --- SIDEBAR INFO ---
with st.sidebar:
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    st.caption(f"Scope: **{st.session_state.current_user_cottage}**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# SUPERVISOR TOOL LOGIC STARTS HERE
# ==========================================

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# --- MASTER DATA PROFILES (FROM PDF) ---

# Standard Comm Profiles (Sections 1-2)
COMM_PROFILES = {
    "Director": {
        "bullets": [
            "**Clarity:** They prioritize the 'bottom line' over the backstory, speaking in headlines to ensure immediate understanding. Supervisors should not mistake their brevity for rudeness.",
            "**Speed:** They process information rapidly and expect others to keep up, preferring a quick 80% solution over a delayed 100% solution.",
            "**Conflict:** They view conflict as a tool for problem-solving rather than a relationship breaker. They do not take disagreement personally."
        ],
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately; avoid 'sandwiching' feedback with small talk.",
            "**Focus on Outcomes:** Tell them what needs to be achieved, but leave the how to them.",
            "**Respect Autonomy:** Give them space to operate independently; tight oversight feels like distrust to a Director."
        ]
    },
    "Encourager": {
        "bullets": [
            "**Verbal Processing:** They think out loud and prefer talking through problems rather than reading about them.",
            "**Optimism:** They naturally focus on the potential and the positive. They sell the vision effectively but may gloss over the gritty details.",
            "**Relationship-First:** They influence people through liking and charisma. They want you to like them before they want you to understand them."
        ],
        "supervising_bullets": [
            "**Allow Discussion:** Give them a few minutes to chat and connect; cutting them off too early kills their morale.",
            "**Ask for Specifics:** They speak in generalities ('It's going great!'). Ask 'What specifically is going great?' to get the data.",
            "**Follow Up in Writing:** They may agree enthusiastically in the moment but forget the details. Always send a recap email."
        ]
    },
    "Facilitator": {
        "bullets": [
            "**Listening:** They gather all perspectives before speaking. They want the full picture before they commit to an opinion.",
            "**Consensus:** They prefer group agreement over unilateral action. They view a 5-4 vote as a failure to align the team properly.",
            "**Process:** They value how a decision is made as much as the decision itself. They hate chaos and shooting from the hip without a plan."
        ],
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before asking for a decision. Send the agenda 24 hours in advance so they can prepare.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless deliberation.",
            "**Solicit Opinion:** Ask them explicitly what they think during meetings. They will not fight for airtime against louder voices."
        ]
    },
    "Tracker": {
        "bullets": [
            "**Detail-Oriented:** They communicate in spreadsheets, data, and precise details. They value accuracy above all else.",
            "**Risk-Averse:** They are cautious in their speech, avoiding definitive statements until they are 100% sure.",
            "**Process-Driven:** They talk about how we do things, not just what we do. They are the guardians of the handbook."
        ],
        "supervising_bullets": [
            "**Be Specific:** Do not use vague language like 'do it better'. Give them the metric: 'Increase accuracy by 10%'.",
            "**Provide Data:** If you want to persuade them, bring the numbers and the facts.",
            "**Written Instructions:** Follow up every verbal conversation with an email. They trust the written word more than the spoken word."
        ]
    }
}

# Standard Motivation Profiles (Sections 3-4)
MOTIV_PROFILES = {
    "Achievement": {
        "bullets": [
            "**Scoreboard:** They need to know if they are winning or losing at any given moment. Ambiguity is their enemy.",
            "**Completion:** They derive energy from finishing tasks and closing loops. An endless list of open-ended projects drains them.",
            "**Efficiency:** They hate wasted time and redundancy more than almost anything else."
        ],
        "strategies_bullets": [
            "**Visual Goals:** Use charts, dashboards, or checklists they can physically mark off.",
            "**Public Wins:** Acknowledge their success in front of peers, highlighting competence and results.",
            "**Autonomy:** Give them the goal and let them design the strategy."
        ],
        "celebrate_bullets": [
            "**Efficiency:** Celebrate specific instances where they solved a complex logistical puzzle quickly.",
            "**Clarity:** Celebrate their ability to draw a hard line or make a tough call.",
            "**Resilience:** Celebrate their ability to bounce back immediately and focus on solutions."
        ]
    },
    "Growth": {
        "bullets": [
            "**Curiosity:** They are driven to understand the 'why' and 'how' behind every rule.",
            "**Future-Focused:** They view their current role primarily as a stepping stone to the next challenge.",
            "**Feedback:** They crave constructive correction over empty praise. They view criticism as free consulting."
        ],
        "strategies_bullets": [
            "**Stretch Assignments:** Assign tasks slightly above their current skill level. They are bored by mastery.",
            "**Career Pathing:** Discuss their professional future regularly, not just at annual reviews.",
            "**Mentorship:** Connect them with leaders they admire inside or outside the organization."
        ],
        "celebrate_bullets": [
            "**Insight:** Celebrate specific moments where they identified a root cause others missed.",
            "**Development:** Celebrate a staff member who visibly improved under their guidance.",
            "**Courage:** Celebrate their willingness to try a new approach, even if it failed."
        ]
    },
    "Purpose": {
        "bullets": [
            "**Values-Driven:** They filter every decision through the lens of 'Is this right?'.",
            "**Advocacy:** They are wired to fight for the underdog. They naturally align themselves with the most vulnerable person in the room.",
            "**Meaning:** They need the 'why' connected to client well-being. They cannot work for a paycheck alone."
        ],
        "strategies_bullets": [
            "**The Why:** Explain the mission behind every mandate. Connect the rule directly to how it keeps a child safe.",
            "**Storytelling:** Share narratives of redemption and impact.",
            "**Ethics:** Allow space to voice moral concerns. Do not shut down their ethical questions."
        ],
        "celebrate_bullets": [
            "**Integrity:** Celebrate moments where they made a hard choice because it was the right thing to do.",
            "**Advocacy:** Celebrate when they gave a voice to the voiceless.",
            "**Consistency:** Celebrate their unwavering commitment to care."
        ]
    },
    "Connection": {
        "bullets": [
            "**Belonging:** They view the team as a family. Their primary goal is to ensure everyone feels they belong.",
            "**Harmony:** They are sensitive to tension and will absorb it to protect others.",
            "**Support:** They are motivated by helping peers. They will stay late to help a coworker even if their own work is done."
        ],
        "strategies_bullets": [
            "**Face Time:** Prioritize in-person check-ins. They value the relationship with you more than the tasks you assign.",
            "**Team Rituals:** Encourage meals, huddles, and traditions.",
            "**Personal Care:** Ask about life outside work. Knowing their kids' names or their hobbies matters deeply to them."
        ],
        "celebrate_bullets": [
            "**Loyalty:** Celebrate their standing up for the team.",
            "**Stabilization:** Celebrate their physical presence calming a room.",
            "**Culture:** Celebrate the strong identity of the unit. Praise the low turnover or the high morale."
        ]
    }
}

# Detailed Integrated Profiles (Sections 5-12)
INTEGRATED_PROFILES = {
    "Director-Achievement": {
        "title": "The Executive General",
        "synergy": "Operational Velocity. They don't just want to lead; they want to win. They cut through noise to identify the most efficient path to success.",
        "support": "**Operational Risk:** Name the operational risk of moving fast.\n**Burnout Watch:** They are the best person to identify when the 'ask' exceeds capacity, but they need permission to say it.",
        "thriving": "**Rapid Decision Architecture:** They make calls with partial information, preventing the team from freezing in analysis paralysis.\n**Objective Focus:** They separate story from fact, focusing on behaviors and outcomes.\n**High-Bar Accountability:** They refuse to walk past a mistake, raising the standard of care.",
        "struggling": "**The Steamroller Effect:** They announce decisions without checking if the team is emotionally ready.\n**Burnout by Intensity:** They assume everyone has their stamina and push until the team breaks.\n**Dismissing 'Soft' Data:** They ignore 'bad feelings' or intuition because there is no proof.",
        "interventions": [
            "**Phase 1: The Pause Button (0-6 Months):** You must force a deliberate delay between their initial thought and their resulting action. Require them to ask three distinct questions of their team before they are allowed to issue a final decision.",
            "**Phase 2: Narrative Leadership (6-12 Months):** Coach them to meticulously script the 'Why' behind their directives before they speak.",
            "**Phase 3: Multiplier Effect (12-18 Months):** Identify two deputies and train the supervisor to literally sit on their hands while the deputies lead the meeting."
        ],
        "questions": ["How are you defining success today beyond just metrics?", "What is one win you can celebrate right now?", "Are you driving the team too hard?", "What is the cost of speed right now?", "Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?", "Are you celebrating the small wins?", "Who helped you win this week?", "What is 'good enough' for right now?"],
        "advancement": "**Delegate Effectively:** Give away tasks they are good at to prove they can build a team.\n**Allow Safe Failure:** Let the team struggle so they can learn, rather than rescuing them.\n**Focus on Strategy:** Move from the 'how' (tactics) to the 'why' (organizational strategy)."
    },
    "Director-Growth": {
        "title": "The Restless Improver",
        "synergy": "Transformational Leadership. They don't just manage the shift; they want to upgrade it. They see potential in every staff member and are willing to push hard to unlock it.",
        "support": "**Connect Goals:** Link their personal growth goals to youth outcomes and the mission.\n**Pacing:** Remind them that not everyone learns at their speed. Coach them to wait for the team to catch up.",
        "thriving": "**Diagnostic Speed:** They quickly identify the root causes of failures rather than treating symptoms.\n**Fearless Innovation:** They are willing to break the status quo to find a better way.\n**High-Impact Coaching:** They give direct, developmental feedback that accelerates the growth of their peers.",
        "struggling": "**The Pace Mismatch:** They get visibly frustrated with slow learners or bureaucracy.\n**'Fix-It' Fatigue:** They are constantly pointing out flaws and forgetting to validate what is working.\n**Leaving People Behind:** They focus on the idea of change rather than the adoption of change.",
        "interventions": [
            "**Phase 1: Validation (0-6 Months):** Mandate that they validate the current effort before suggesting improvements.",
            "**Phase 2: Change Management (6-12 Months):** Require a 'stakeholder analysis' for their next idea (who will resist and why?).",
            "**Phase 3: Capacity Building (12-18 Months):** Shift them from being the idea generator to the facilitator of others' ideas."
        ],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?", "What are you learning from this struggle?", "Are you expecting too much too soon from others?", "How are you feeding your own curiosity?", "What is one way you can slow down for others?", "How are you measuring your own growth beyond just speed?", "Are you leaving the team behind?", "Is this change necessary right now?"],
        "advancement": "**Delegate Effectively:** Stop being the 'fixer', become the 'developer'.\n**Allow Safe Failure:** Resist the urge to jump in and correct every mistake.\n**Focus on Strategy:** Design tomorrow's solutions rather than solving today's problems."
    },
    "Director-Purpose": {
        "title": "The Mission Defender",
        "synergy": "Ethical Courage. They provide the moral backbone for the team, ensuring expediency never trumps integrity. They are the conscience of the unit.",
        "support": "**Share Values:** Share your own core values so they trust your leadership.\n**Operational Risk:** Frame slowing down as 'protecting the mission'.",
        "thriving": "**Unshakeable Advocacy:** They act immediately against injustice.\n**Clarity of 'Why':** They contextualize the grind for the staff.\n**Crisis Ethics:** They keep their moral compass even in chaos.",
        "struggling": "**Righteous Rigidity:** They struggle to see the gray areas, viewing everything as black and white.\n**The Martyr Complex:** They overwork because they don't trust others to care enough.\n**Judgmental Tone:** They come across as 'preachy' or morally superior.",
        "interventions": [
            "**Phase 1: The Gray Zone (0-6 Months):** Practice identifying validity in opposing viewpoints.",
            "**Phase 2: Sustainable Advocacy (6-12 Months):** Coach them to use a 'Tier System' for battles (Tier 1: Fight, Tier 2: Debate, Tier 3: Let go).",
            "**Phase 3: Cultural Architecture (12-18 Months):** Move from fighting battles to building systems that prevent injustice."
        ],
        "questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?", "How does flexibility serve the mission here?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast for the team?", "How does your tone land when you are stressed?"],
        "advancement": "**Delegate Effectively:** Build a team that protects children.\n**Allow Safe Failure:** Trust that others also care.\n**Focus on Strategy:** Build systems that prevent injustice."
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial.\n**Backing:** Be candid about where you can back them up (air cover).",
        "thriving": "**Decisive Care:** They fix problems for people immediately.\n**Crisis Stabilization:** They become the calm human shield during a crisis.\n**Team Loyalty:** They build a strong 'Us'.",
        "struggling": "**Us vs. Them:** They become hostile toward outsiders (admin, other units).\n**Over-Functioning:** They do everyone's job to protect them.\n**Taking Conflict Personally:** They conflate professional disagreement with personal betrayal.",
        "interventions": [
            "**Phase 1: Delegation of Care (0-6 Months):** Stop being the only fixer; assign care tasks to others.",
            "**Phase 2: Organizational Citizenship (6-12 Months):** Expand the circle of loyalty to the whole agency.",
            "**Phase 3: Mentorship (12-18 Months):** Transition from Captain to Admiral (teaching others to build loyalty)."
        ],
        "questions": ["Are you avoiding this conversation to be kind, or to be safe?", "How can you be direct and caring at the same time?", "Are you protecting them from growth?", "How is the team reacting to your directness?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast for the team?", "Who do you need to check in with today?"],
        "advancement": "**Delegate Effectively:** Stop being 'camp parent'.\n**Allow Safe Failure:** Learn the team is resilient.\n**Focus on Strategy:** Expand loyalty to the whole agency."
    },
    "Encourager-Achievement": {
        "title": "The Coach",
        "synergy": "Inspirational Performance. They make hard work feel like a game. They believe the team can win and their energy is contagious.",
        "support": "**Reality Checks:** Be the ground to their sky. Validate their enthusiasm but ask 'What is the plan if this goes wrong?'.\n**Focus:** Help them pick one lane.",
        "thriving": "**Team Morale:** The unit has high energy and believes they are the best unit in the building.\n**Rallying:** They can turn a bad shift around with a pep talk.\n**Goal-Smashing:** When locked in, they hit metrics with flair and celebrate loudly.",
        "struggling": "**Overselling:** They promise things they can't deliver to get buy-in.\n**Disorganization:** They are moving so fast and talking so much they lose paperwork or forget details.\n**Impatience:** They get frustrated when the team doesn't share their burning desire to win immediately.",
        "interventions": [
            "**Phase 1: Follow-Through (0-6 Months):** Focus on finishing. Require them to complete one project fully before starting the next exciting one.",
            "**Phase 2: Data Discipline (6-12 Months):** Move from 'feeling' to 'fact'. Require them to bring data to supervision, not just stories.",
            "**Phase 3: Grooming Talent (12-18 Months):** Challenge them to let others shine."
        ],
        "questions": ["How do we keep this energy up when things get boring?", "What are the specific steps to get to that vision?", "Who is doing the work: you or the team?", "How will you track this?", "What is the one thing we must finish this week?", "Who needs the spotlight more than you right now?", "Are you listening or just waiting to speak?", "What happens if we miss this goal?", "How are you celebrating the team's grind, not just the win?", "Is your enthusiasm masking a problem?"],
        "advancement": "**Detail Management:** They must prove they can handle the boring stuff (admin, budgets).\n**Listening:** They need to learn to sit back and let others speak.\n**Consistency:** Prove they can maintain performance when the excitement fades."
    },
    "Encourager-Growth": {
        "title": "The Mentor",
        "synergy": "Developmental Charisma. They see the gold in people and talk it out of them. They lead by selling the team on their own potential.",
        "support": "**Structure:** They have a million ideas; provide the structure to execute one at a time.\n**Patience:** Remind them that growth is messy and non-linear.",
        "thriving": "**Talent Magnet:** People want to work for them because they feel grown and seen.\n**Culture of Learning:** Mistakes are celebrated as learning opportunities, reducing fear in the unit.\n**Innovation:** They are constantly bringing in new ideas from books, podcasts, or other units.",
        "struggling": "**Shiny Object Syndrome:** They chase a new initiative every week, confusing the team.\n**Avoidance of Hard Conversations:** They want to inspire, not correct.\n**All Talk:** They talk a great game about development but lack the follow-through to document it.",
        "interventions": [
            "**Phase 1: Closing the Loop (0-6 Months):** Force them to finish what they start.",
            "**Phase 2: Difficult Feedback (6-12 Months):** Role-play giving 'hard' feedback without the fluff.",
            "**Phase 3: Systems of Growth (12-18 Months):** Turn their informal mentoring into a formal training manual or curriculum."
        ],
        "questions": ["Who are you investing in, and who are you ignoring?", "How do we turn this idea into a habit?", "Are you avoiding the hard truth to be nice?", "What is the one skill the team needs right now?", "How are you measuring that improvement?", "Are you talking more than they are?", "What did you finish this week?", "Is this practical, or just interesting?", "How does this help the client today?", "What are you reading/learning?"],
        "advancement": "**Execution:** Prove they can implement, not just ideate.\n**Toughness:** Prove they can make the hard personnel calls.\n**Focus:** Prove they can stick to a boring plan for the long haul."
    },
    "Encourager-Purpose": {
        "title": "The Heart of the Mission",
        "synergy": "Passionate Advocacy. They are the soul of the unit. They keep the emotional flame alive.",
        "support": "**Emotional Boundaries:** Help them distinguish between caring and carrying.\n**Validation:** Frequently affirm that their heart is a strength, not a weakness.",
        "thriving": "**Cultural Carrier:** They set the emotional tone for the entire workspace.\n**Advocate:** They are fearless in speaking up for kids, using their persuasion to get resources.\n**Inspiration:** They can make a tired team feel like heroes again.",
        "struggling": "**Emotional Flooding:** They get so wrapped up in the 'story' that they lose objectivity.\n**Us vs. The System:** They can whip the team into a frenzy against 'cold' administration.\n**Burnout:** They give everything and have nothing left.",
        "interventions": [
            "**Phase 1: Boundaries (0-6 Months):** Teach them to leave work at work. 'The badge stays at the door'.",
            "**Phase 2: Fact-Checking (6-12 Months):** When they tell a passionate story, ask 'Is that true, or is that how it felt?'.",
            "**Phase 3: Channeling Passion (12-18 Months):** Give them a platform (e.g., orientation training) where their passion is an asset, not a distraction."
        ],
        "questions": ["Is this feeling a fact?", "How can you care without carrying?", "Are you whipping the team up or calming them down?", "What is the most ethical choice, even if it feels bad?", "Who is supporting you?", "Is this your battle to fight?", "How does the policy actually help the child?", "Are you listening to the logic, or just the tone?", "What do you need to let go of today?", "How can we use your voice for good?"],
        "advancement": "**Objectivity:** Prove they can make dispassionate decisions.\n**Policy:** Understand the legal/fiscal reasons behind rules.\n**Resilience:** Bounce back without drama."
    },
    "Encourager-Connection": {
        "title": "The Team Builder",
        "synergy": "Social Cohesion. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy.",
        "support": "**Hard Decisions:** Step in to be the 'bad guy' so they don't have to burn social capital.\n**Focus:** Remind them that work is the goal, fun is the method.",
        "thriving": "**Zero Turnover:** People stay because they love the team.\n**Conflict Resolution:** They talk things out and smooth over rough edges.\n**Joy:** There is laughter on the unit, which is therapeutic.",
        "struggling": "**The Country Club:** Too much socializing, not enough work.\n**Gossip:** Their need to be 'in the know' and close to everyone can spiral into drama.\n**Favoritism:** They struggle to lead people they don't personally like.",
        "interventions": [
            "**Phase 1: Professionalism (0-6 Months):** Define the line between 'friend' and 'colleague' explicitly.",
            "**Phase 2: Inclusive Leadership (6-12 Months):** Challenge them to connect with the staff member they like the least.",
            "**Phase 3: Task Focus (12-18 Months):** Assign them a project that requires solitude or deep focus to build that muscle."
        ],
        "questions": ["Are we having fun, or are we working?", "Who is on the outside of the circle?", "Are you avoiding the conflict to keep the peace?", "How can you deliver that news directly?", "Are you gossiping or venting?", "Can you be friendly without being their best friend?", "How does the work get done if we talk all day?", "What is the cost of not holding them accountable?", "Who needs to hear from you today?", "How are you protecting your own energy?"],
        "advancement": "**Separation:** Prove they can lead without needing to be liked.\n**Confidentiality:** Prove they can keep secrets.\n**Productivity:** Prove they can drive results, not just vibes."
    },
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "synergy": "Methodical Progress. They don't sprint; they march with purpose and precision. They get the team to the finish line by ensuring everyone knows their role and the process is solid.",
        "support": "**Decision Speed:** Push them to decide even when they don't have 100% consensus.\n**Validation:** Praise the quiet work of organization that often goes unseen.",
        "thriving": "**Consistent Wins:** They hit the metrics every month without drama or panic.\n**Efficient Meetings:** They run meetings where everyone feels heard, but action items are clearly assigned.\n**Project Management:** They are excellent at long-term implementation of complex initiatives.",
        "struggling": "**Analysis Paralysis:** They want to achieve the goal (Achievement) but want everyone to agree on how (Facilitator), leading to stalls.\n**Frustration with Chaos:** They hate last-minute changes that disrupt the plan they worked hard to create.\n**Silent Resentment:** They work hard and resent those who don't, but won't say it aloud to avoid conflict.",
        "interventions": [
            "**Phase 1: Speaking Up (0-6 Months):** Call on them first in meetings to break the habit of waiting.",
            "**Phase 2: Imperfect Action (6-12 Months):** Assign a task with an impossible deadline to force a 'good enough' decision.",
            "**Phase 3: Direct Delegation (12-18 Months):** Challenge them to assign tasks without asking for volunteers or consensus."
        ],
        "questions": ["What is the 'good enough' decision right now?", "Are you waiting for everyone to agree?", "How can we move forward even if it's messy?", "Who is holding up the project?", "What have you achieved this week?", "Is the process helping or hurting the goal?", "How can you say 'no' to protect the timeline?", "Who needs to be cut out of the decision loop?", "Are you doing the work to avoid asking others?", "What is the next step?"],
        "advancement": "**Speed:** Make faster decisions with less data.\n**Conflict:** Call out underperformance directly and verbally.\n**Vision:** Look beyond the checklist to the strategy."
    },
    "Facilitator-Growth": {
        "title": "The Patient Gardener",
        "synergy": "Organic Development. They don't force growth; they create the conditions for it. They are incredibly patient with difficult staff or youth, believing that everyone can change if given enough time and support.",
        "support": "**Urgency:** You must provide the urgency, or they will let things grow forever.\n**Outcome Focus:** Remind them that growth must eventually result in performance.",
        "thriving": "**Turnaround Specialist:** They can take a failing staff member and slowly rehabilitate them.\n**Deep Listening:** They understand the nuance of the unit better than anyone.\n**Sustainable Pace:** They model a healthy work-life balance that prevents burnout.",
        "struggling": "**Tolerance of Mediocrity:** They give people too many chances in the name of 'growth'.\n**Slow to Launch:** They study the problem forever without fixing it.\n**Fear of Judgment:** They struggle to evaluate people because they know how hard growth is.",
        "interventions": [
            "**Phase 1: Timelines (0-6 Months):** Put a date on development goals. 'They have 3 months to improve, not forever'.",
            "**Phase 2: Judgment (6-12 Months):** Practice evaluating performance objectively based on data. 'Is this good or bad?'.",
            "**Phase 3: Pruning (12-18 Months):** They must terminate or discipline a staff member to learn that protection isn't always love."
        ],
        "questions": ["How long is too long to wait for improvement?", "Is this person actually growing, or are we just hoping?", "What is the cost to the team of keeping this person?", "Are you learning, or just stalling?", "What is the lesson here?", "How can you speed up this process?", "Who are you neglecting by focusing on the struggler?", "What does 'accountability' look like to you?", "Are you afraid to judge?", "What is the next step today?"],
        "advancement": "**Decisiveness:** Act on the data, not just the hope.\n**Speed:** Move faster than feels comfortable.\n**Standards:** Hold the line on quality without apology."
    },
    "Facilitator-Purpose": {
        "title": "The Moral Compass",
        "synergy": "Principled Consensus. They are the quiet conscience of the team. They ensure that the team doesn't just get things done, but gets them done right.",
        "support": "**Validation of Values:** Regularly affirm their role as the ethical standard-bearer.\n**Decision Frameworks:** Give them a framework for making 'imperfect' decisions (e.g., 'We are choosing the least bad option').",
        "thriving": "**Ethical Anchor:** When the team is confused, they bring everyone back to the mission statement.\n**Unified Team:** They create a team culture where everyone feels respected and heard.\n**Trust:** Staff trust them implicitly because they know they are not self-interested.",
        "struggling": "**Moral Paralysis:** They refuse to make a decision because no option is perfectly ethical.\n**Passive Resistance:** Instead of arguing openly, they simply don't do the things they disagree with.\n**Judgment:** They may silently judge others who are more pragmatic or business-minded.",
        "interventions": [
            "**Phase 1: The '51% Decision' (0-6 Months):** Teach them that in leadership, you often have to move with only 51% certainty.",
            "**Phase 2: Voice Training (6-12 Months):** Challenge them to speak their dissent in the meeting, not after it in the hallway.",
            "**Phase 3: Operational Ethics (12-18 Months):** Task them with creating a system or policy that institutionalizes their values."
        ],
        "questions": ["What moral tension are you holding right now?", "How can you speak up for your values effectively?", "Are you staying neutral when you should take a stand?", "How does your silence impact the team?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?"],
        "advancement": "**Decisiveness:** They must prove they can make hard calls when it is necessary, even if it hurts feelings.\n**Public Speaking:** They need to get comfortable projecting their voice and values to a larger audience.\n**Pragmatism:** They need to demonstrate they understand the business realities alongside the ethical ones."
    },
    "Facilitator-Connection": {
        "title": "The Peacemaker",
        "synergy": "Harmonious Inclusion. They create a psychological safety net for the team. They lead by relationship, ensuring that staff feel loved, supported, and heard so they can do the hard work of care.",
        "support": "**Conflict Coaching:** They are likely terrified of conflict and will avoid it. Role-play hard conversations with them to build muscle memory.\n**Permission to Disappoint:** Explicitly tell them, 'It is okay if they are mad at you'.",
        "thriving": "**High Retention:** People rarely leave their team because it feels good to work there.\n**Psychological Safety:** Staff admit mistakes freely because they aren't afraid of shame.\n**De-escalation:** They can calm a room just by walking in.",
        "struggling": "**The Doormat:** They let staff walk all over them to avoid a fight.\n**Exhaustion:** They carry everyone's emotional baggage and trauma.\n**Triangulation:** Instead of addressing an issue directly, they complain to others to vent.",
        "interventions": [
            "**Phase 1: Direct Address (0-6 Months):** Require them to have one direct, hard conversation per week.",
            "**Phase 2: Disappointing Others (6-12 Months):** Challenge them to make a decision they know will be unpopular with the team.",
            "**Phase 3: Self-Protection (12-18 Months):** Teach them to set boundaries on their time and empathy."
        ],
        "questions": ["What boundaries do you need to set to protect your energy?", "Are you listening too much and leading too little?", "Who is taking care of you?", "Is your silence creating confusion?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?"],
        "advancement": "**Conflict:** Prove they can handle a fight without crumbling.\n**Separation:** Prove they can lead friends and former peers.\n**Results:** Prove they value outcomes as much as feelings."
    },
    "Tracker-Achievement": {
        "title": "The Architect",
        "synergy": "Systematic Perfection. They build the systems that allow the team to succeed. They are the engineers of the unit.",
        "support": "**Clarity:** Be hyper-clear about expectations and deliverables.\n**Time:** Give them the time to do it right. If you rush them, they will panic because they cannot ensure quality.",
        "thriving": "**Flawless Execution:** Their paperwork is perfect and their data is clean.\n**System Builder:** They create new trackers or logs that save everyone time.\n**Reliability:** If they say it is done, it is done right.",
        "struggling": "**Rigidity:** They refuse to bend the rules even when it makes sense for the client.\n**Micromanagement:** If they lead others, they hover to ensure it is done 'perfectly'.\n**Critique:** They constantly point out others' errors and flaws.",
        "interventions": [
            "**Phase 1: Flexibility (0-6 Months):** Challenge them to identify one rule that can be bent for the greater good.",
            "**Phase 2: People over Process (6-12 Months):** Require them to mentor a disorganized staff member without doing the work for them.",
            "**Phase 3: Big Picture (12-18 Months):** Ask them to explain why the system exists, not just how it works."
        ],
        "questions": ["How can you measure effort, not just outcome?", "Are you valuing the data more than the person?", "Where is flexibility needed right now?", "How can you support the person, not just the process?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": "**Flexibility:** Prove they can handle chaos without breaking.\n**Delegation:** Prove they can trust others to do the work, even imperfectly.\n**Warmth:** Prove they can connect with people, not just papers."
    },
    "Tracker-Growth": {
        "title": "The Technical Expert",
        "synergy": "Knowledge Mastery. They are the walking encyclopedia of the agency. They know every rule, every regulation, and every loophole.",
        "support": "**Resources:** Give them access to the information they crave. Do not gatekeep the data or the policy.\n**Challenge:** Give them a problem that no one else can solve.",
        "thriving": "**Problem Solver:** They fix the technical issues that stump everyone else.\n**Teacher:** They patiently explain complex systems to others.\n**Innovator:** They find new tools or methods to make the work better.",
        "struggling": "**Arrogance:** They can make others feel stupid for not knowing the rules.\n**Over-Complication:** They design systems that are too complex for anyone else to use.\n**Disengagement:** If they stop learning, they check out completely.",
        "interventions": [
            "**Phase 1: Simplification (0-6 Months):** Challenge them to explain a complex idea to a layperson without using jargon.",
            "**Phase 2: Emotional Intelligence (6-12 Months):** Require them to mentor someone based on their potential, not their current knowledge.",
            "**Phase 3: Strategic Vision (12-18 Months):** Ask them to solve a problem where there is no 'right' answer, only trade-offs."
        ],
        "questions": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "Are you correcting or coaching?", "How can you make it safe to make mistakes?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": "**Communication:** Prove they can speak simply and clearly.\n**Empathy:** Prove they can care about people who aren't experts.\n**Strategy:** Prove they can think about the 'why,' not just the 'how'."
    },
    "Tracker-Purpose": {
        "title": "The Guardian",
        "synergy": "Protective Compliance. They believe that following the rules is the highest form of caring. They protect the mission by ensuring that the agency never gets in trouble.",
        "support": "**Explanation:** Explain the 'why' behind every change in policy.\n**Validation:** Validate their fears and concerns. Don't dismiss their anxiety.",
        "thriving": "**Safety Net:** They catch the errors that would cause a lawsuit or a licensing violation.\n**Moral Consistency:** They ensure that we do what we say we do.\n**Reliability:** You can trust them with the most sensitive tasks.",
        "struggling": "**Bureaucracy:** They use rules to block necessary action.\n**Fear-Mongering:** They constantly predict disaster and doom.\n**Judgment:** They view errors as moral failings.",
        "interventions": [
            "**Phase 1: Risk Assessment (0-6 Months):** When they flag a risk, ask them to rate it 1-10.",
            "**Phase 2: The 'Why' of Flexibility (6-12 Months):** Show them a case where breaking a rule saved a kid.",
            "**Phase 3: Solution Focus (12-18 Months):** Don't let them bring a problem without a solution."
        ],
        "questions": ["How can you protect the mission without being rigid?", "Are you using rules to manage your anxiety?", "Is this rule serving the child right now?", "How can you explain the 'why' behind the rule?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": "**Risk Tolerance:** Prove they can take a calculated risk.\n**Flexibility:** Prove they can adapt to change without panic.\n**Vision:** Prove they can see the forest, not just the trees."
    },
    "Tracker-Connection": {
        "title": "The Reliable Rock",
        "synergy": "Servant Consistency. They show their love for the team by doing the work perfectly. They are the backbone of the unit.",
        "support": "**Notice the Details:** Notice when they refill the copier or clean the breakroom.\n**Change Management:** Hold their hand through change. Explain how the new way will help the people they love.",
        "thriving": "**Steady Presence:** They are always there, always on time, always prepared.\n**Helper:** They use their skills to help others succeed.\n**Culture Keeper:** They maintain the traditions and the history of the unit.",
        "struggling": "**Overwhelmed:** They say 'yes' to everything to please people and then drown in the details.\n**Passive Aggressive:** If they feel unappreciated, they will slow down or withdraw.\n**Resistance to Change:** They dig their heels in when you try to change a routine.",
        "interventions": [
            "**Phase 1: Saying No (0-6 Months):** Practice saying 'no' to a request.",
            "**Phase 2: Vocalizing Needs (6-12 Months):** Ask them what they need in every meeting.",
            "**Phase 3: Leading Change (12-18 Months):** Ask them to help a new person adapt to the unit."
        ],
        "questions": ["How can you show care in a way they understand?", "Are you doing too much for others?", "Do they know you care?", "Where do you need help carrying the load?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": "**Voice:** Prove they can speak up in a meeting.\n**Boundaries:** Prove they can stop over-functioning.\n**Flexibility:** Prove they can handle a new way of doing things."
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
    # --- SAME STYLE CONFLICTS (NEW) ---
    "Director": {
        "Director": {
            "tension": "Power Struggle (Control vs. Control)",
            "psychology": "When two Directors clash, it's a battle for dominance. Both value speed, autonomy, and being 'right.' The conflict usually isn't personal; it's structural. You both want to drive the car, and neither wants to be the passenger. This leads to stepping on toes, power plays, and a chaotic environment where the team doesn't know who to follow.",
            "watch_fors": [
                "**The Public Showdown:** Arguing in front of the team to establish who is 'Alpha'.",
                "**Malicious Compliance:** 'Fine, I'll do it your way, but I'll watch it fail.'",
                "**Siloing:** Dividing the team into 'My Crew' vs. 'Your Crew'."
            ],
            "intervention_steps": [
                "**1. Define Swim Lanes (Why: You need autonomy):** Explicitly divide the turf. 'You own the schedule; I own the audit.' Do not cross lines without permission.",
                "**2. The 'Disagree and Commit' Pact (Why: Speed matters):** Agree that once a decision is made, you back each other 100% in public, even if you argued in private.",
                "**3. Scheduled Friction (Why: You need a vent):** Set a weekly 'Fight Club' meeting where you are allowed to debate strategy fiercely behind closed doors, so you don't do it on the floor."
            ],
            "scripts": {
                "Opening": "We are both strong leaders, which is great, but right now we are canceling each other out.",
                "Validation": "I respect your drive and your ability to get things done. I know you want the best for this program.",
                "The Pivot": "However, when we battle for control in front of the team, we create confusion. We need to stop competing and start coordinating.",
                "Crisis": "We don't have time for a power struggle. You take the East Wing, I'll take the West Wing. Go.",
                "Feedback": "I need you to trust me to handle my lane. When you double-check my work, it feels like you don't trust my competence."
            }
        },
        "Encourager": {
            "tension": "Efficiency vs. Empathy (Safety as Control vs. Safety as Connection)",
            "psychology": "This is the classic 'Oil and Water' dynamic. You (Director) find safety in speed, competence, and checking boxes. You view 'feelings' as variables that slow down the mission. \n\nThe Encourager finds safety in connection and harmony. When you push for speed or deliver blunt feedback, they don't just hear 'work instructions'—they feel an existential threat to the group's safety. They retreat because they feel steamrolled; you push harder because you think they are incompetent.",
            "watch_fors": [
                "**The 'Shut Down':** If they go silent, they aren't agreeing with you. They are protecting themselves from your intensity.",
                "**The 'Smile & Nod':** They may agree to a deadline they know they can't meet just to end the uncomfortable interaction.",
                "**Venting:** They will likely process their hurt feelings with peers, creating a 'shadow culture' you aren't part of."
            ],
            "intervention_steps": [
                "**1. Disarm the Threat (Why: They are in fight/flight):** Lower your volume and physical pace. Sit down. Do not start with the task; start with the person. 'How are you feeling about the shift today?'",
                "**2. Translate the Intent (Why: They think you are angry):** Explicitly state that your intensity is about the *problem*, not them. 'I am frustrated with the schedule, not with you. I value you.'",
                "**3. The 'Sandwich' Reframe (Why: They need safety to hear truth):** You hate feedback sandwiches, but they need them. Affirm the relationship, give the correction, affirm the future. It is not 'fluff'; it is the toll you pay to get on the bridge."
            ],
            "scripts": {
                "Opening": "I want to talk about [Task], but first I want to check in. I've been moving fast today—how is the team feeling?",
                "Validation": "I know my communication style can feel intense or abrupt. I validate that you prioritize the team's morale, and I don't want to damage that.",
                "The Pivot": "However, we do need to solve [Problem]. My concern is that if we don't fix this, the team will suffer in the long run.",
                "Crisis": "I need to be very direct right now because of the safety risk. This isn't personal, but I need you to do X immediately.",
                "Feedback": "I value how much the team loves you. To grow, I need you to be able to hear hard news without feeling like I'm attacking your character."
            }
        },
        "Facilitator": {
            "tension": "Speed vs. Process (Urgency vs. Fairness)",
            "psychology": "You (Director) value 'Done'. They (Facilitator) value 'Fair'. You see their desire for meetings and consensus as 'Analysis Paralysis' and a waste of time. They see your desire for quick decisions as reckless and exclusive.\n\nThey are terrified of leaving someone behind. You are terrified of missing the opportunity. You are fighting for results; they are fighting for legitimacy.",
            "watch_fors": [
                "**The 'We Need to Talk':** They will try to schedule meetings to delay decisions they feel were made too fast.",
                "**Passive Resistance:** They won't argue, but they won't implement the plan because they feel 'the team wasn't consulted'.",
                "**Moral High Ground:** They may subtly frame your speed as 'uncaring' or 'undemocratic'."
            ],
            "intervention_steps": [
                "**1. Define the Sandbox (Why: They need parameters):** Give them a clear deadline. 'We need to decide this by 3:00 PM.'",
                "**2. Assign the 'Who' (Why: They fear exclusion):** Ask them specifically: 'Who are the critical 3 people we need to ask?' Limit it to 3.",
                "**3. The 'Good Enough' Agreement (Why: They want perfection):** Remind them that a good decision today is better than a perfect decision next week. Ask: 'Is this safe enough to try?'"
            ],
            "scripts": {
                "Opening": "I know this decision feels rushed. I want to respect the process, but we have a tight timeline.",
                "Validation": "I value that you want everyone to be heard. You are the moral compass of the team.",
                "The Pivot": "The risk we face is that if we don't decide by noon, we lose the option entirely. We have to move.",
                "Crisis": "In this specific moment, I have to make the call. We can debrief the process later, but right now, follow my lead.",
                "Feedback": "Your desire for consensus is a strength, but sometimes it becomes a bottleneck. I need you to be willing to make the '51% decision'."
            }
        },
        "Tracker": {
            "tension": "Innovation vs. Compliance (Change vs. Safety)",
            "psychology": "You (Director) want to break the status quo to get better results. They (Tracker) want to protect the status quo to ensure safety. You see them as 'The Department of No.' They see you as a reckless cowboy who is going to get the agency sued.\n\nYou interpret their questions as resistance. They interpret your new ideas as chaos.",
            "watch_fors": [
                "**The Rulebook Defense:** They will quote policy to stop your new idea.",
                "**The 'Yes, But':** Every time you propose a solution, they find 10 reasons why it might fail.",
                "**Anxiety:** Your speed makes them visibly nervous."
            ],
            "intervention_steps": [
                "**1. The Pre-Mortem (Why: They need to voice risks):** Before launching a plan, ask them: 'What are the 3 biggest risks here?' Let them list them. Then solve them together.",
                "**2. Honor the Detail (Why: That is their value):** Do not dismiss the details. 'You are right, I missed that regulation. Thank you for catching it.'",
                "**3. Trial Runs (Why: They fear permanent mistakes):** Frame changes as 'experiments.' 'Let's try this for 3 days and see if it works.' It feels less permanent/risky."
            ],
            "scripts": {
                "Opening": "I have a new idea, and I need your eyes on it to make sure it's safe.",
                "Validation": "I appreciate your attention to detail. You keep us compliant and safe.",
                "The Pivot": "We need to find a way to make this work because the current system is failing our kids. How can we do this safely?",
                "Crisis": "I am taking full responsibility for this decision. If it goes wrong, it's on me. I need you to execute the plan.",
                "Feedback": "I need you to help me find the 'Yes.' Don't just tell me why we can't do it; tell me how we *could* do it."
            }
        }
    },
    "Encourager": {
        "Encourager": {
            "tension": "Artificial Harmony (Nice vs. Nice)",
            "psychology": "When two Encouragers work together, the vibe is amazing, but the accountability is zero. You both value harmony so much that you avoid hard conversations. Issues fester underground. You become 'Toxic Protectors,' shielding the team from reality until a crisis hits. You struggle to make decisions that might upset anyone.",
            "watch_fors": [
                "**The Vent Session:** Spending 30 minutes complaining about a problem but taking no action to fix it.",
                "**The 'Reply All' Apology:** Apologizing to the team for enforcing basic rules.",
                "**Ghosting:** Avoiding a staff member rather than correcting them."
            ],
            "intervention_steps": [
                "**1. The 'Safety' Contract (Why: You fear conflict):** Explicitly agree that giving feedback is safe. 'I promise I won't be mad if you tell me I'm wrong.'",
                "**2. Assign the 'Bad Guy' Role (Why: It creates distance):** Rotate who has to deliver the bad news so one person doesn't carry the emotional load.",
                "**3. Focus on the Victim (Why: You need a moral cause):** When you need to hold a staff member accountable, remind each other of the *youth* who is suffering because of that staff member's laziness."
            ],
            "scripts": {
                "Opening": "I hate having to have this conversation, but we need to talk about [Issue].",
                "Validation": "I know we both want the team to be happy. We care about these people.",
                "The Pivot": "But by not addressing this, we are actually hurting the team. True kindness is holding them to a standard.",
                "Crisis": "We can't hug our way out of this one. We have to be firm.",
                "Feedback": "I feel like we are dancing around the issue. Let's just say it directly."
            }
        },
        "Director": {
            "tension": "Warmth vs. Competence (Being Liked vs. Being Effective)",
            "psychology": "You (Encourager) value harmony and feeling connected. You interpret their (Director) lack of small talk and directness as dislike or anger. You feel unsafe around them.\n\nThey interpret your focus on feelings as incompetence or lack of focus. When you try to 'nice' them into compliance, they lose respect for you. They don't want a friend; they want a leader who can remove obstacles.",
            "watch_fors": [
                "**Apologizing:** You apologizing for giving them work to do.",
                "**Taking it Personally:** You going home feeling hurt because they didn't say 'good morning' enthusiastically.",
                "**Avoidance:** You emailing them instead of talking to them because you fear the conflict."
            ],
            "intervention_steps": [
                "**1. Cut the Fluff (Why: They value time):** Do not ask about their weekend for 10 minutes. Start with the headline. 'I need your help with X.'",
                "**2. Stand Your Ground (Why: They respect strength):** If they push back, do not fold. State your reasoning calmly. 'I hear you, but the policy is X, and that's what we are doing.'",
                "**3. Ask for Input (Why: They want to solve problems):** Frame the relationship issue as a problem. 'I feel like we are missing each other. How can I communicate better with you?'"
            ],
            "scripts": {
                "Opening": "I'm going to get straight to the point because I know you value your time.",
                "Validation": "I know you are focused on getting this done, and I appreciate your efficiency.",
                "The Pivot": "However, the way you spoke to the team caused a shutdown. We can't be efficient if no one wants to work for you.",
                "Crisis": "Stop. I need you to listen to me right now. This is a safety issue.",
                "Feedback": "You are excellent at tasks, but your delivery is costing you relationship capital. You are right on the facts, but wrong on the approach."
            }
        }
    },
    "Facilitator": {
        "Facilitator": {
            "tension": "Process Paralysis (Talk vs. Talk)",
            "psychology": "The infinite loop. You both want to make sure everyone is heard. You both want to explore every option. The result? Meetings that never end and decisions that never happen. You enable each other's worst habit: procrastination in the name of 'process.'",
            "watch_fors": [
                "**The 'Let's Circle Back':** delaying a decision to another meeting.",
                "**The Meeting About the Meeting:** Planning to plan.",
                "**Consensus Addiction:** Refusing to move until 100% of people agree (which never happens)."
            ],
            "intervention_steps": [
                "**1. The 'Shot Clock' (Why: You need external pressure):** Set a timer. 'We have 10 minutes to decide. If we don't agree, we flip a coin.'",
                "**2. Limit the Input (Why: More isn't always better):** Agree to only consult 2 people, not the whole team.",
                "**3. The 'Good Enough' Pact (Why: Perfection is the enemy):** Remind each other that a B+ decision today is better than an A+ decision next month."
            ],
            "scripts": {
                "Opening": "We are over-thinking this. We need to land the plane.",
                "Validation": "I value that we are being thorough. It's important to be fair.",
                "The Pivot": "But we are stuck in analysis paralysis. We need to pick a direction and go.",
                "Crisis": "Process is over. I am making the call now.",
                "Feedback": "We need to stop asking for permission and start giving direction."
            }
        },
        "Tracker": {
            "tension": "Consensus vs. Compliance (People vs. Policy)",
            "psychology": "You (Facilitator) want the team to agree on a solution that feels fair. They (Tracker) want the team to follow the written rule because that is safe.\n\nYou feel they are being rigid and uncaring 'robots'. They feel you are being rigid and treating safety rules as 'suggestions'. You prioritize the human element; they prioritize the systemic element.",
            "watch_fors": [
                "**The Policy War:** They quote the handbook; you quote the 'vibe' or the 'context'.",
                "**Ignoring:** You ignoring their emails about compliance because it feels like nagging.",
                "**Anxiety:** They getting visibly anxious when you say 'let's just see how it goes'."
            ],
            "intervention_steps": [
                "**1. Validate the Rule (Why: They need to know you aren't reckless):** Start by acknowledging the policy. 'I know the rule is X.'",
                "**2. Contextualize the Exception (Why: They need a reason):** Explain *why* this specific human situation requires a bend. 'Because of [Client's] history, we need to adapt.'",
                "**3. Define the New Boundary (Why: They fear chaos):** Create a new, temporary rule for this situation so they feel there is still a plan."
            ],
            "scripts": {
                "Opening": "I know this plan deviates from our standard SOP, and I want to explain why.",
                "Validation": "I appreciate you keeping us compliant. You protect the agency's license.",
                "The Pivot": "In this specific case, following the rule to the letter will cause a behavioral escalation. We need to flex here to maintain safety.",
                "Crisis": "I am taking responsibility for this exception. Please document that I made this call.",
                "Feedback": "I need you to see the gray areas. The rulebook is a map, but the territory is real people."
            }
        }
    },
    "Tracker": {
        "Tracker": {
            "tension": "The Micro-War (Detail vs. Detail)",
            "psychology": "When two Trackers clash, it is usually over *interpretation* of a rule. It becomes a court case. You both dig into the details to prove you are 'technically correct.' The team gets lost in the minutiae. You risk creating a culture where 'doing it right' is more important than 'doing it well.'",
            "watch_fors": [
                "**The Email War:** Sending long, evidence-filled emails to each other instead of talking.",
                "**Malicious Audit:** Looking for errors in each other's work to prove a point.",
                "**Stalemate:** Refusing to move until the 'policy' is clarified by upper management."
            ],
            "intervention_steps": [
                "**1. Zoom Out (Why: You are lost in the weeds):** Stop talking about the rule. Talk about the goal. 'What are we actually trying to achieve here?'",
                "**2. Pick a Lane (Why: You need ownership):** Divide the compliance tasks. 'You own Fire Safety; I own File Compliance.'",
                "**3. The 'Human Override' (Why: Systems aren't people):** Remind each other that the system serves the kid, not the other way around."
            ],
            "scripts": {
                "Opening": "We are getting lost in the weeds. Let's step back.",
                "Validation": "I know we both want to do this exactly right. I respect your attention to detail.",
                "The Pivot": "However, arguing over this specific procedure is slowing down the team. Is this critical to safety, or just a preference?",
                "Crisis": "The procedure doesn't matter right now. Safety matters. We do X.",
                "Feedback": "We need to stop using the rulebook as a weapon against each other."
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

    return {
        "s1": c_data.get('desc'), # Note: Desc field removed in master data update to use bullets only? 
                                  # Let's adjust - master data uses bullets only for Sections 1-4.
                                  # We can construct a description from bullets if needed or just use bullets.
                                  # For now, let's just use bullets as primary.
        "s1_b": c_data.get('bullets'),
        "s2": c_data.get('supervising'), # Same here - logic check
        "s2_b": c_data.get('supervising_bullets'),
        "s3": m_data.get('desc'),
        "s3_b": m_data.get('bullets'),
        "s4": m_data.get('strategies'),
        "s4_b": m_data.get('strategies_bullets'),
        # S5 is Synergy
        "s5": f"**Profile:** {i_data.get('title')}\n\n{i_data.get('synergy')}",
        "s6": i_data.get('support', ''),
        "s6_b": None, # No bullets in source for this specific section, it's paragraphs
        "s7": i_data.get('thriving', ''), # Thriving paragraphs
        "s7_b": None,
        "s8": i_data.get('struggling', ''), # Struggling paragraphs
        "s8_b": None,
        "s9": "Strategies for Course Correction:", # Intervention Header
        "s9_b": i_data.get('interventions', []),
        "s10": m_data.get('celebrate'), # Logic check - celebrate is in M_DATA
        "s10_b": m_data.get('celebrate_bullets'),
        "coaching": i_data.get('questions', []),
        "advancement": i_data.get('advancement', '')
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (1, 91, 173); black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(8)
    
    # Generate Data
    data = generate_profile_content(p_comm, p_mot)

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
    add_section(f"1. Communication Profile: {p_comm}", None, data['s1_b']) # Fixed: Pass bullets, body is None if empty
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
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---"); st.markdown(f"### 📘 Supervisory Guide: {name}"); st.divider()
    
    def show_section(title, text, bullets=None):
        st.subheader(title)
        if text: st.write(text)
        if bullets:
            for b in bullets:
                st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)

    show_section(f"1. Communication Profile: {p_comm}", None, data['s1_b'])
    show_section("2. Supervising Their Communication", None, data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    show_section("4. Motivating This Staff Member", None, data['s4_b'])
    show_section("5. Integrated Leadership Profile", data['s5'])
    show_section("6. How You Can Best Support Them", data['s6'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("7. Thriving")
        st.success(data['s7']) # Green box
    with c2:
        st.subheader("8. Struggling")
        st.error(data['s8'])   # Red box
    
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. Supervisory Interventions", None, data['s9_b'])
    show_section("10. What You Should Celebrate", None, data['s10_b'])
    
    st.subheader("11. Coaching Questions")
    for i, q in enumerate(data['coaching']):
        st.write(f"{i+1}. {q}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    show_section("12. Helping Them Prepare for Advancement", data['advancement'])

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
    if st.button("📝 Guide Generator\n\nCreate 12-point coaching manuals.", use_container_width=True): set_view("Guide Generator")
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

# 1. GUIDE GENERATOR
if st.session_state.current_view == "Guide Generator":
    st.subheader("📝 Guide Generator")
    sub1, sub2 = st.tabs(["Database", "Manual"])
    with sub1:
        if not df.empty:
            # Create dictionary from the FILTERED dataframe, not the raw list
            filtered_staff_list = df.to_dict('records')
            options = {f"{s['name']} ({s['role']})": s for s in filtered_staff_list}
            
            sel = st.selectbox("Select Staff", options.keys(), index=None, key="t1_staff_select")
            if sel:
                d = options[sel]
                c1,c2,c3 = st.columns(3)
                c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                if st.button("Generate Guide", type="primary"):
                    pdf = create_supervisor_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                    st.download_button("Download PDF", pdf, f"Guide_{d['name']}.pdf", "application/pdf")
                    display_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                st.button("Reset", on_click=reset_t1)
    with sub2:
        with st.form("manual"):
            c1,c2 = st.columns(2)
            mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
            mpc = c1.selectbox("Comm", COMM_TRAITS); mpm = c2.selectbox("Motiv", MOTIV_TRAITS)
            if st.form_submit_button("Generate") and mn:
                pdf = create_supervisor_guide(mn, mr, mpc, None, mpm, None)
                st.download_button("Download PDF", pdf, "guide.pdf", "application/pdf")
                display_guide(mn, mr, mpc, None, mpm, None)

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
                
                # DOMINANT CULTURE ANALYSIS
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
                        # BALANCED CULTURE
                        guide = TEAM_CULTURE_GUIDE.get("Balanced", {})
                        st.info("**Balanced Culture:** No single style dominates. This reduces blindspots but may increase friction.")
                        with st.expander("📖 Managing a Balanced Team", expanded=True):
                             st.markdown("""**The Balanced Friction:**
                             A diverse team has no blind spots, but it speaks 4 different languages. Your role is **The Translator**.
                             * **Translate Intent:** 'The Director isn't being mean; they are being efficient.' 'The Tracker isn't being difficult; they are being safe.'
                             * **Rotate Leadership:** Let the Director lead the crisis; let the Encourager lead the debrief; let the Tracker lead the audit.
                             * **Meeting Protocol:** Use structured turn-taking (Round Robin) so the loudest voice doesn't always win.""")

                # MISSING VOICE ANALYSIS
                present_styles = set(tdf['p_comm'].unique())
                missing_styles = set(COMM_TRAITS) - present_styles
                if missing_styles:
                    st.markdown("---")
                    st.error(f"🚫 **Missing Voices:** {', '.join(missing_styles)}")
                    cols = st.columns(len(missing_styles))
                    for idx, style in enumerate(missing_styles):
                        with cols[idx]:
                             data = MISSING_VOICE_GUIDE.get(style, {})
                             with st.container(border=True):
                                 st.markdown(f"**Without a {style}:**")
                                 st.write(data.get('risk'))
                                 st.success(f"**Supervisor Fix:** {data.get('fix')}")

            with c2:
                mot_counts = tdf['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
                
                # MOTIVATION GAP ANALYSIS
                if not mot_counts.empty:
                    dom_mot = mot_counts.idxmax()
                    st.markdown("---")
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

        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1")
        p2 = c2.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            s1, s2 = d1['p_comm'], d2['p_comm']
            m1, m2 = d1['p_mot'], d2['p_mot']
            
            st.divider()
            st.subheader(f"{s1} (Sup) vs. {s2} (Staff)")
            if s1 in SUPERVISOR_CLASH_MATRIX and s2 in SUPERVISOR_CLASH_MATRIX[s1]:
                clash = SUPERVISOR_CLASH_MATRIX[s1][s2]
                with st.expander("🔍 **Psychological Deep Dive**", expanded=True):
                    st.markdown(f"**The Core Tension:** {clash['tension']}")
                    st.markdown(f"{clash['psychology']}")
                    st.markdown("**🚩 Watch For:**")
                    for w in clash['watch_fors']: st.markdown(f"- {w}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("##### 🛠️ 3-Phase Coaching Protocol")
                    for i in clash['intervention_steps']: st.info(i)
                with c_b:
                    st.markdown("##### 🗣️ Conflict Scripts (Click to Expand)")
                    script_tabs = st.tabs(list(clash['scripts'].keys()))
                    for i, (cat, text) in enumerate(clash['scripts'].items()):
                        with script_tabs[i]:
                            st.success(f"\"{text}\"")
            else:
                st.info("No specific conflict protocol exists for this combination yet. They likely work well together!")
            
            # --- AI SUPERVISOR BOT ---
            st.markdown("---")
            with st.container(border=True):
                st.subheader("🤖 AI Supervisor Assistant")
                
                # Determine active key from variable
                active_key = user_api_key
                
                if active_key:
                    st.caption(f"Powered by Gemini 2.5 Flash | Ask specific questions about managing **{p2}** ({s2} x {m2}).")
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
                def get_smart_response(query, comm_style, motiv_driver, key):
                    # Prepare Context Data
                    comm_data = COMM_PROFILES.get(comm_style, {})
                    mot_data = MOTIV_PROFILES.get(motiv_driver, {})
                    
                    # If API Key exists, use Gemini
                    if key:
                        try:
                            # Context Prompt Construction
                            system_prompt = f"""
                            You are an expert Leadership Coach for a youth care agency.
                            You are advising a Supervisor on how to manage a staff member named {p2}.
                            
                            Here is the Staff Member's Profile:
                            - **Communication Style:** {comm_style}
                            - **Core Motivation:** {motiv_driver}
                            - **Thriving Behaviors:** {comm_data.get('bullets', [])}
                            - **Stress Behaviors:** They may become rigid, withdrawn, or aggressive when their need for {motiv_driver} is blocked.
                            
                            **Your Goal:** Answer the user's question specifically tailored to this profile.
                            Do not give generic advice. Use the profile data to explain WHY the staff member acts this way and HOW to reach them.
                            Be concise, practical, and empathetic.
                            """
                            
                            # API Call to Gemini 2.5 Flash (Standard Endpoint)
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
                            payload = {
                                "contents": [{
                                    "parts": [{"text": system_prompt + "\n\nUser Question: " + query}]
                                }]
                            }
                            headers = {'Content-Type': 'application/json'}
                            response = requests.post(url, headers=headers, data=json.dumps(payload))
                            
                            if response.status_code == 200:
                                return response.json()['candidates'][0]['content']['parts'][0]['text']
                            else:
                                return f"⚠️ **AI Error:** {response.text}. Falling back to basic database."
                        
                        except Exception as e:
                            return f"⚠️ **Connection Error:** {str(e)}. Falling back to basic database."

                    # FALLBACK: Rule-Based Logic (No API Key)
                    query = query.lower()
                    response = ""
                    
                    if "who is" in query or "tell me about" in query or "profile" in query:
                         response += f"**Profile Overview:** {p2} is a **{comm_style}** driven by **{motiv_driver}**.\n\n"
                         response += "**Communication Style:**\n"
                         for b in comm_data.get('bullets', []):
                             response += f"- {b}\n"
                         response += "**Core Driver:**\n"
                         for b in mot_data.get('bullets', []):
                             response += f"- {b}\n"

                    elif "strengths" in query or "good at" in query:
                        response += f"**Strengths:** As a {comm_style}, they excel at: \n"
                        for b in comm_data.get('bullets', []):
                            response += f"- {b}\n"
                        response += f"\nDriven by {motiv_driver}, they are motivated by: \n"
                        for b in mot_data.get('bullets', []):
                            response += f"- {b}\n"

                    elif "feedback" in query or "critical" in query or "correct" in query:
                        response += f"**On giving feedback to a {comm_style}:**\n"
                        for b in comm_data.get('supervising_bullets', []):
                            response += f"- {b}\n"
                        response += f"\n**Motivation Tip:** Frame the feedback in a way that doesn't block their drive for {motiv_driver}. "
                        if motiv_driver == "Connection": response += "Reassure them that the relationship is safe."
                        elif motiv_driver == "Achievement": response += "Focus on how fixing this helps them win."
                    
                    elif "motivate" in query or "burnout" in query:
                        response += f"**To motivate a {motiv_driver} driver:**\n"
                        for b in mot_data.get('strategies_bullets', []):
                            response += f"- {b}\n"
                    
                    else:
                        # Helpful debugging info in the fallback message
                        debug_key_info = f"Key detected: {key[:4]}..." if key else "No API Key detected"
                        response = f"I can help you manage {p2}. Try asking about:\n- How to give **feedback**\n- How to **motivate** them\n- How to handle **conflict**\n\n*Note: {debug_key_info}. Please check the sidebar.*"
                    
                    return response

                # Input
                if prompt := st.chat_input(f"Ask about {p2}..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Consulting the Compass Database..."):
                            # Pass the persistent key from variable
                            bot_reply = get_smart_response(prompt, s2, m2, active_key)
                            st.markdown(bot_reply)
                    
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
        elif p1 and p2 and p1 == p2:
             st.warning("⚠️ You selected the same person twice. Please select two **different** staff members to analyze a conflict.")
             
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
        # --- DATA PREP ---
        total_staff = len(df)
        comm_counts = df['p_comm'].value_counts(normalize=True) * 100
        mot_counts = df['p_mot'].value_counts(normalize=True) * 100
        
        # Top Metrics
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
                st.markdown("##### 🗣️ Communication Mix")
                st.plotly_chart(px.pie(df, names='p_comm', color='p_comm', color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
            with c_b: 
                st.markdown("##### 🔋 Motivation Drivers")
                st.plotly_chart(px.bar(df['p_mot'].value_counts(), orientation='h', color_discrete_sequence=[BRAND_COLORS['blue']]), use_container_width=True)

            st.divider()
            st.header("🔍 Deep Organizational Analysis")
            
            tab1, tab2, tab3 = st.tabs(["🛡️ Culture Risk Assessment", "🔥 Motivation Strategy", "🌱 Leadership Pipeline Health"])
            
            # --- TAB 1: CULTURE RISK ---
            with tab1:
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
                st.markdown("### Leadership Pipeline Analysis")
                if 'role' in df.columns:
                    # Compare Leadership Composition to General Staff
                    leaders = df[df['role'].isin(['Program Supervisor', 'Shift Supervisor', 'Manager'])]
                    if not leaders.empty:
                        l_counts = leaders['p_comm'].value_counts(normalize=True) * 100
                        
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
        else:
             st.warning("No valid data found for your selection.")

    else: st.warning("No data available.")
