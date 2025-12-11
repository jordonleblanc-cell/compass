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
        "desc": "They prioritize the 'bottom line' over the backstory, speaking in headlines to ensure immediate understanding. Supervisors should not mistake their brevity for rudeness; they are simply trying to be efficient. They process information rapidly and prefer a quick 80% solution over a delayed 100% solution.",
        "bullets": ["**Clarity:** Prioritizes bottom line over backstory.", "**Speed:** Processes rapid information; may interrupt if conversation drags.", "**Conflict:** Views conflict as a problem-solving tool, not a relationship breaker."],
        "supervising": "Get to the point immediately; avoid 'sandwiching' feedback with small talk. Tell them *what* needs to be achieved, but leave the *how* to them. Respect their autonomy; tight oversight feels like distrust.",
        "supervising_bullets": ["**Be Concise:** Don't stretch 5 mins of content into 30.", "**Focus on Outcomes:** Define the destination, not the map.", "**Respect Autonomy:** Check in at milestones, don't hover."]
    },
    "Encourager": {
        "desc": "They think out loud and prefer talking through problems. They are naturally optimistic, seeing the potential in everyone. They influence through relationship and charisma, prioritizing the 'vibe' of the interaction.",
        "bullets": ["**Verbal Processing:** Needs to talk to think.", "**Optimism:** Focuses on potential and positivity.", "**Relationship-First:** Influences through connection and liking."],
        "supervising": "Give them a few minutes to chat and connect; cutting them off too early kills their morale. Ask for specific data, as they speak in generalities ('It's going great!'). Always follow up in writing, as they may forget details once the emotion of the meeting fades.",
        "supervising_bullets": ["**Allow Discussion:** Small talk is big work for them.", "**Ask for Specifics:** Drill down to facts beneath the enthusiasm.", "**Follow Up in Writing:** Document the boring parts."]
    },
    "Facilitator": {
        "desc": "They gather all perspectives before speaking. They prefer group agreement over unilateral action. They value *how* a decision is made as much as the decision itself, hating chaos and 'shooting from the hip'.",
        "bullets": ["**Listening:** Gathers all perspectives before speaking.", "**Consensus:** Prefers group alignment over top-down orders.", "**Process:** Values structure, agendas, and fairness."],
        "supervising": "Give them time to think before asking for a decision; sending agendas in advance helps. Set clear 'decision dates' to prevent endless deliberation. Solicit their opinion explicitly, as they will not fight for airtime.",
        "supervising_bullets": ["**Advance Notice:** Don't put them on the spot.", "**Deadlines:** Prevent analysis paralysis with hard stops.", "**Solicit Opinion:** Hand them the mic; they won't grab it."]
    },
    "Tracker": {
        "desc": "They communicate in data, details, and policy. They value accuracy above all else. They are risk-averse, avoiding definitive statements until they are 100% sure. They believe rules exist to save us from chaos.",
        "bullets": ["**Detail-Oriented:** Values accuracy and precision.", "**Risk-Averse:** Cautious speech; verifies before speaking.", "**Process-Driven:** Guardians of the handbook."],
        "supervising": "Be specific; give metrics like 'increase accuracy by 10%'. Provide data and logic to persuade them, not emotional appeals. Follow up every verbal conversation with an email to provide the paper trail they crave.",
        "supervising_bullets": ["**Be Specific:** Use numbers, not feelings.", "**Provide Data:** Show the proof that your idea works.", "**Written Instructions:** Create a paper trail for security."]
    }
}

# Standard Motivation Profiles (Sections 3-4)
MOTIV_PROFILES = {
    "Achievement": {
        "desc": "They need to know if they are winning or losing. Ambiguity is their enemy. They derive energy from finishing tasks and closing loops. They hate wasted time and redundancy.",
        "bullets": ["**Scoreboard:** Needs quantifiable metrics to judge performance.", "**Completion:** Craves the dopamine hit of marking 'Done'.", "**Efficiency:** Hates wasted time and bottlenecks."],
        "strategies": "Use charts, dashboards, or checklists they can physically mark off. Acknowledge their success in front of peers, using specific data. Give them the goal and let them design the strategy.",
        "strategies_bullets": ["**Visual Goals:** Use dashboards they can self-monitor.", "**Public Wins:** Celebrate specific, data-driven achievements.", "**Autonomy:** Let them design the path to the goal."],
        "celebrate": "Celebrate specific instances where they solved a complex logistical puzzle quickly. Quantify the time or money they saved.",
        "celebrate_bullets": ["**Efficiency:** 'You saved us 3 hours.'", "**Clarity:** 'Thanks for making the tough call.'", "**Resilience:** 'You bounced back immediately.'"]
    },
    "Growth": {
        "desc": "They are driven to understand the 'why' and 'how'. They view their current role as a stepping stone. They crave constructive correction over empty praise, viewing criticism as free consulting.",
        "bullets": ["**Curiosity:** Needs to understand the mechanism behind the rule.", "**Future-Focused:** Constantly scanning for the next challenge.", "**Feedback:** Wants to be sharper, not just happier."],
        "strategies": "Assign tasks slightly above their skill level ('Stretch Assignments'). Map out exactly how their work contributes to their 5-year plan. Connect them with leaders they admire for mentorship.",
        "strategies_bullets": ["**Stretch Assignments:** Bored by mastery; needs tension.", "**Career Pathing:** Discuss future goals regularly.", "**Mentorship:** Facilitate access to senior leaders."],
        "celebrate": "Celebrate specific moments where they identified a root cause others missed. Celebrate their willingness to try new approaches, even if they failed.",
        "celebrate_bullets": ["**Insight:** 'You saw beneath the surface.'", "**Development:** 'Look how much X grew under your coaching.'", "**Courage:** 'I love that you tried a new way.'"]
    },
    "Purpose": {
        "desc": "They filter every decision through the lens of 'Is this right?' They naturally align with the underdog (client/new staff). They need to feel they are part of a crusade, not just a company.",
        "bullets": ["**Values-Driven:** Acts as the moral conscience.", "**Advocacy:** Wired to fight for the vulnerable.", "**Meaning:** Needs the 'why' connected to client well-being."],
        "strategies": "Explain the mission behind every mandate. Share narratives of redemption and impact. Allow space for them to voice moral concerns without shutting them down.",
        "strategies_bullets": ["**The Why:** Connect rules to child safety/healing.", "**Storytelling:** Use qualitative data (stories) to motivate.", "**Ethics:** Validate their moral struggles."],
        "celebrate": "Celebrate moments where they made a hard choice because it was right. Celebrate when they gave a voice to the voiceless.",
        "celebrate_bullets": ["**Integrity:** 'You prioritized values over convenience.'", "**Advocacy:** 'Thank you for protecting that client.'", "**Consistency:** 'You keep us honest.'"]
    },
    "Connection": {
        "desc": "They view the team as a family. Their primary goal is belonging. They are sensitive to tension and will absorb it to protect others. They see service to the team as their primary job.",
        "bullets": ["**Belonging:** Fears exclusion; measures success by group tightness.", "**Harmony:** Will fight to impose peace if necessary.", "**Support:** Will stay late to help a peer."],
        "strategies": "Prioritize in-person check-ins ('Face Time'). Encourage team rituals and traditions. Ask about life outside work; knowing their hobbies matters to them.",
        "strategies_bullets": ["**Face Time:** Relationships require presence, not just emails.", "**Team Rituals:** Give them space to create culture.", "**Personal Care:** Bring your whole self to the interaction."],
        "celebrate": "Celebrate their standing up for the team. Celebrate their physical presence calming a room. Praise the strong identity of the unit.",
        "celebrate_bullets": ["**Loyalty:** 'You make people feel safe.'", "**Stabilization:** 'Your presence lowered the temperature.'", "**Culture:** 'People stay because of the environment you built.'"]
    }
}

# Detailed Integrated Profiles (Sections 5-12)
INTEGRATED_PROFILES = {
    "Director-Achievement": {
        "title": "The Executive General",
        "synergy": "Operational Velocity. They don't just want to lead; they want to win. They cut through noise to identify the most efficient path to success.",
        "support": "**Operational Risk:** Name the risk of moving fast. 'We can do this quickly if we build guardrails.'\n**Burnout Watch:** They view endurance as a badge of honor. Ask about their fuel tank before they run dry.",
        "thriving": "**Rapid Decision Architecture:** Makes calls with partial info, energizing the team.\n**Objective Focus:** Separates story from fact.\n**High-Bar Accountability:** Refuses to walk past a mistake.",
        "struggling": "**The Steamroller Effect:** Announces decisions without checking if the team is ready.\n**Burnout by Intensity:** Pushes until the team breaks.\n**Dismissing 'Soft' Data:** Ignores feelings/intuition.",
        "interventions": [
            "**Phase 1: The Pause Button.** Require them to ask 3 questions of their team before issuing a final decision.",
            "**Phase 2: Narrative Leadership.** Coach them to script the 'Why' (backstory) before giving the directive.",
            "**Phase 3: Multiplier Effect.** Train them to sit on their hands while deputies lead the meeting."
        ],
        "questions": ["How are you defining success today beyond just metrics?", "What is one win you can celebrate right now?", "Are you driving the team too hard?", "What is the cost of speed right now?", "Where are you moving too fast for the team?", "Who haven't you heard from?", "How does your tone land when stressed?", "Are you celebrating small wins?", "Who helped you win this week?", "What is 'good enough' for right now?"],
        "advancement": "**Delegate Effectively:** Give away tasks to prove they can build a team.\n**Allow Safe Failure:** Let the team struggle to build resilience.\n**Focus on Strategy:** Move from the 'how' to the 'why'."
    },
    "Director-Growth": {
        "title": "The Restless Improver",
        "synergy": "Transformational Leadership. They don't just manage the shift; they want to upgrade it. They are natural disruptors.",
        "support": "**Connect Goals:** Link personal growth to youth outcomes.\n**Pacing:** Remind them that organizational change is a marathon. Coach them to wait for the team to catch up.",
        "thriving": "**Diagnostic Speed:** Quickly identifies root causes of failure.\n**Fearless Innovation:** Willing to break status quo for better care.\n**High-Impact Coaching:** Gives direct, developmental feedback.",
        "struggling": "**The Pace Mismatch:** Visibly frustrated with slow learners.\n**'Fix-It' Fatigue:** Constantly pointing out flaws, demoralizing the team.\n**Leaving People Behind:** Implements systems without buy-in.",
        "interventions": [
            "**Phase 1: Validation.** Mandate they validate the current effort before suggesting improvements.",
            "**Phase 2: Change Management.** Require a 'stakeholder analysis' (who will resist?) for their next idea.",
            "**Phase 3: Capacity Building.** Shift them from idea generator to facilitator of others' ideas."
        ],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from?", "How does your tone land when stressed?", "What are you learning from this struggle?", "Are you expecting too much too soon?", "How are you feeding your curiosity?", "What is one way you can slow down?", "How are you measuring growth beyond speed?", "Are you leaving the team behind?", "Is this change necessary right now?"],
        "advancement": "**Delegate Effectively:** Stop being the 'fixer', become the 'developer'.\n**Allow Safe Failure:** Resist the urge to jump in and correct every mistake.\n**Focus on Strategy:** Design tomorrow's solutions, not today's fixes."
    },
    "Director-Purpose": {
        "title": "The Mission Defender",
        "synergy": "Ethical Courage. They provide the moral backbone, ensuring expediency never trumps integrity. They speak truth to power.",
        "support": "**Share Values:** Share your own values so they trust you.\n**Operational Risk:** Frame slowing down as 'protecting the mission' to align their speed with care.",
        "thriving": "**Unshakeable Advocacy:** Acts immediately against injustice.\n**Clarity of 'Why':** Contextualizes the grind for staff.\n**Crisis Ethics:** Keeps moral compass even in chaos.",
        "struggling": "**Righteous Rigidity:** Struggles to see gray areas.\n**The Martyr Complex:** Overworks because they don't trust others to care enough.\n**Judgmental Tone:** Alienates allies by demanding ideological purity.",
        "interventions": [
            "**Phase 1: The Gray Zone.** Require them to argue the 'other side' of an ethical debate.",
            "**Phase 2: Sustainable Advocacy.** Coach them to use a 'Tier System' for battles (Fight vs. Let Go).",
            "**Phase 3: Cultural Architecture.** Challenge them to write the policy rather than complaining about it."
        ],
        "questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?", "How does flexibility serve the mission?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast?", "How does your tone land?"],
        "advancement": "**Delegate Effectively:** Multiply impact by teaching others to care.\n**Allow Safe Failure:** Separate competence from character.\n**Focus on Strategy:** Build systems that prevent injustice."
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff feel protected. They are the 'Mama/Papa Bear' of the unit.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial.\n**Backing:** Be candid about where you can provide air cover. They need to know you are in their corner.",
        "thriving": "**Decisive Care:** Fixes problems for people immediately.\n**Crisis Stabilization:** Becomes the calm human shield.\n**Team Loyalty:** Builds a strong 'Us' identity.",
        "struggling": "**Us vs. Them:** Becomes hostile toward outsiders/admin.\n**Over-Functioning:** Burns out carrying the load for 'weaker' staff.\n**Taking Conflict Personally:** Conflates professional disagreement with betrayal.",
        "interventions": [
            "**Phase 1: Delegation of Care.** Stop being the only fixer; assign care tasks to others.",
            "**Phase 2: Organizational Citizenship.** Expand the circle of loyalty to the whole agency (break silos).",
            "**Phase 3: Mentorship.** Task them with training a new supervisor on culture building."
        ],
        "questions": ["Are you avoiding this conversation to be kind or safe?", "How can you be direct and caring?", "Are you protecting them from growth?", "How is the team reacting to your directness?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast?", "Who do you need to check in with?"],
        "advancement": "**Delegate Effectively:** Stop being 'camp parent'.\n**Allow Safe Failure:** Learn the team won't break if you step back.\n**Focus on Strategy:** Advocate for the organization, not just the unit."
    },
    "Encourager-Achievement": {
        "title": "The Coach",
        "synergy": "Inspirational Performance. They make hard work feel like a game. They believe the team can win and their energy is contagious.",
        "support": "**Reality Checks:** Validate enthusiasm but ask for the 'Plan B'.\n**Focus:** Help them pick one lane; be the editor of their ambition.",
        "thriving": "**Team Morale:** The unit has 'swag' and high energy.\n**Rallying:** Can turn a bad shift around with a pep talk.\n**Goal-Smashing:** Hits metrics with flair and celebrates loudly.",
        "struggling": "**Overselling:** Promises things they can't deliver.\n**Disorganization:** Moves so fast they lose paperwork/details.\n**Impatience:** Gets frustrated when the team doesn't share their burning desire to win.",
        "interventions": [
            "**Phase 1: Follow-Through.** Require completion of one project before starting the next.",
            "**Phase 2: Data Discipline.** Require data in supervision, not just stories.",
            "**Phase 3: Grooming Talent.** Challenge them to let others shine (get off the field)."
        ],
        "questions": ["How do we keep energy up when things get boring?", "What are the specific steps to the vision?", "Who is doing the work: you or the team?", "How will you track this?", "What is the one thing we must finish?", "Who needs the spotlight more than you?", "Are you listening or waiting to speak?", "What happens if we miss this?", "How are you celebrating the grind?", "Is your enthusiasm masking a problem?"],
        "advancement": "**Detail Management:** Prove they can handle budgets/admin.\n**Listening:** Learn to sit back and master the pause.\n**Consistency:** Prove they can grind when excitement fades."
    },
    "Encourager-Growth": {
        "title": "The Mentor",
        "synergy": "Developmental Charisma. They see the gold in people and talk it out of them. They lead by selling the team on their own potential.",
        "support": "**Structure:** Provide the trellis for their vine. Help them focus creative energy.\n**Patience:** Remind them that growth is messy and non-linear.",
        "thriving": "**Talent Magnet:** Attracts high-potential staff.\n**Culture of Learning:** Mistakes are celebrated as learning opportunities.\n**Innovation:** Constantly injecting new thought/ideas.",
        "struggling": "**Shiny Object Syndrome:** Chases new initiatives, confusing the team.\n**Avoidance of Hard Conversations:** Sugarcoats poison to avoid being the 'bad guy'.\n**All Talk:** Great visions, poor execution.",
        "interventions": [
            "**Phase 1: Closing the Loop.** No new ideas until the last one is implemented.",
            "**Phase 2: Difficult Feedback.** Role-play giving hard feedback without fluff.",
            "**Phase 3: Systems of Growth.** Turn informal mentoring into formal training manuals."
        ],
        "questions": ["Who are you investing in?", "How do we turn this idea into a habit?", "Are you avoiding hard truth to be nice?", "What is the one skill the team needs?", "How are you measuring improvement?", "Are you talking more than they are?", "What did you finish this week?", "Is this practical or just interesting?", "How does this help the client?", "What are you reading?"],
        "advancement": "**Execution:** Prove they can land the plane, not just fly it.\n**Toughness:** Prove they can make hard personnel calls.\n**Focus:** Prove they can stick to a boring plan."
    },
    "Encourager-Purpose": {
        "title": "The Heart of the Mission",
        "synergy": "Passionate Advocacy. They are the soul of the unit. They keep the emotional flame alive and lead with raw emotion and belief.",
        "support": "**Emotional Boundaries:** Help them distinguish between caring and carrying.\n**Validation:** Affirm that their heart is a strength, not a weakness.",
        "thriving": "**Cultural Carrier:** Sets the emotional tone; the thermostat of the team.\n**Advocate:** Fearless in speaking up for kids.\n**Inspiration:** Makes a tired team feel like heroes again.",
        "struggling": "**Emotional Flooding:** Loses objectivity in the 'story'.\n**Us vs. The System:** Vilifies leadership to protect the team.\n**Burnout:** Functions on adrenaline until they crash.",
        "interventions": [
            "**Phase 1: Boundaries.** Teach them to leave work at work ('Badge at the door').",
            "**Phase 2: Fact-Checking.** Ask 'Is that true, or is that how it felt?'",
            "**Phase 3: Channeling Passion.** Give them a platform (e.g., training) where passion is an asset."
        ],
        "questions": ["Is this feeling a fact?", "How can you care without carrying?", "Are you whipping the team up or calming them?", "What is the most ethical choice?", "Who is supporting you?", "Is this your battle to fight?", "How does policy help the child?", "Are you listening to logic or tone?", "What do you need to let go of?", "How can we use your voice for good?"],
        "advancement": "**Objectivity:** Prove they can make dispassionate decisions.\n**Policy:** Understand the legal/fiscal reasons behind rules.\n**Resilience:** Bounce back without drama."
    },
    "Encourager-Connection": {
        "title": "The Team Builder",
        "synergy": "Social Cohesion. They are the social cruise director. They ensure everyone feels included, liked, and happy.",
        "support": "**Hard Decisions:** Step in to be the 'bad guy' so they don't burn social capital.\n**Focus:** Remind them work is the goal, fun is the method.",
        "thriving": "**Zero Turnover:** People stay because they love the team.\n**Conflict Resolution:** Heals rifts before they become canyons.\n**Joy:** Brings fun to the grind, preventing toxicity.",
        "struggling": "**The Country Club:** Too much socializing, standards slip.\n**Gossip:** Trades secrets for connection.\n**Favoritism:** Struggles to lead people they don't personally like.",
        "interventions": [
            "**Phase 1: Professionalism.** Define the line between 'friend' and 'colleague'.",
            "**Phase 2: Inclusive Leadership.** Challenge them to connect with the person they like least.",
            "**Phase 3: Task Focus.** Assign projects requiring solitude/focus."
        ],
        "questions": ["Are we having fun or working?", "Who is outside the circle?", "Are you avoiding conflict to keep peace?", "How can you deliver that news directly?", "Are you gossiping or venting?", "Can you be friendly without being best friends?", "How does work get done if we talk?", "What is the cost of not holding them accountable?", "Who needs to hear from you?", "How are you protecting your energy?"],
        "advancement": "**Separation:** Prove they can lead without needing to be liked.\n**Confidentiality:** Prove they can keep secrets.\n**Productivity:** Prove they can drive results, not just vibes."
    },
    "Facilitator-Achievement": {
        "title": "The Steady Mover",
        "synergy": "Methodical Progress. They don't sprint; they march. They get the team to the finish line by ensuring the process is solid.",
        "support": "**Decision Speed:** Push them to decide even without 100% consensus.\n**Validation:** Praise the quiet work of organization (spreadsheets, schedules).",
        "thriving": "**Consistent Wins:** Hits metrics every month without drama.\n**Efficient Meetings:** Balances voice with velocity.\n**Project Management:** Excellent at long-term implementation.",
        "struggling": "**Analysis Paralysis:** Freezes at the intersection of speed and agreement.\n**Frustration with Chaos:** Hates last-minute changes.\n**Silent Resentment:** Works hard but resents those who don't.",
        "interventions": [
            "**Phase 1: Speaking Up.** Call on them first in meetings.",
            "**Phase 2: Imperfect Action.** Assign tasks with impossible deadlines to force 'good enough' decisions.",
            "**Phase 3: Direct Delegation.** Challenge them to assign tasks without asking for volunteers."
        ],
        "questions": ["What is 'good enough' right now?", "Are you waiting for everyone to agree?", "How can we move forward even if it's messy?", "Who is holding up the project?", "What have you achieved this week?", "Is the process helping or hurting?", "How can you say 'no'?", "Who needs to be cut out of the decision loop?", "Are you doing work to avoid asking others?", "What is the next step?"],
        "advancement": "**Speed:** Make faster decisions with less data.\n**Conflict:** Call out underperformance directly.\n**Vision:** Look beyond the checklist to the strategy."
    },
    "Facilitator-Growth": {
        "title": "The Patient Gardener",
        "synergy": "Organic Development. They don't force growth; they create conditions for it. They nurture rather than drive.",
        "support": "**Urgency:** You must provide the urgency, or they will let things grow forever.\n**Outcome Focus:** Remind them that growth must eventually result in performance.",
        "thriving": "**Turnaround Specialist:** Rehabilitates failing staff others would fire.\n**Deep Listening:** Diagnoses the root cultural disease.\n**Sustainable Pace:** Models healthy work-life balance.",
        "struggling": "**Tolerance of Mediocrity:** Confuses kindness with weakness.\n**Slow to Launch:** Over-analyzes without fixing.\n**Fear of Judgment:** Struggles to give a failing grade.",
        "interventions": [
            "**Phase 1: Timelines.** Put hard dates on development goals.",
            "**Phase 2: Judgment.** Practice evaluating performance objectively (Binary: Good/Bad).",
            "**Phase 3: Pruning.** They must terminate/discipline to learn that protection isn't always love."
        ],
        "questions": ["How long is too long to wait?", "Is this person growing or are we hoping?", "What is the cost of keeping them?", "Are you learning or stalling?", "What is the lesson?", "How can you speed this up?", "Who are you neglecting?", "What does accountability look like?", "Are you afraid to judge?", "What is the next step?"],
        "advancement": "**Decisiveness:** Act on data, not hope.\n**Speed:** Move faster than feels comfortable.\n**Standards:** Hold the line on quality without apology."
    },
    "Facilitator-Purpose": {
        "title": "The Moral Compass",
        "synergy": "Principled Consensus. They are the quiet conscience. They ensure the team gets things done *right*.",
        "support": "**Validation:** Affirm their role as ethical standard-bearer.\n**Decision Frameworks:** Provide tools for ethical triage (choosing the 'least bad' option).",
        "thriving": "**Ethical Anchor:** Centers the boat in the storm.\n**Unified Team:** Builds a moral community based on trust.\n**Trust:** High credibility because motives are pure.",
        "struggling": "**Moral Paralysis:** Freezes because no option is perfect.\n**Passive Resistance:** Silently rebels against policies they dislike.\n**Judgment:** Becomes self-righteous or isolated.",
        "interventions": [
            "**Phase 1: The '51% Decision'.** Teach them to move with partial certainty.",
            "**Phase 2: Voice Training.** Challenge them to speak dissent in the meeting, not the hallway.",
            "**Phase 3: Operational Ethics.** Task them with creating systems that institutionalize values."
        ],
        "questions": ["What moral tension are you holding?", "How can you speak up effectively?", "Are you staying neutral when you should stand?", "How does silence impact the team?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need a 51% decision?", "Are you waiting for consensus?"],
        "advancement": "**Decisiveness:** Make hard calls even if it hurts feelings.\n**Public Speaking:** Project voice and values to larger audiences.\n**Pragmatism:** Balance money and mission."
    },
    "Facilitator-Connection": {
        "title": "The Peacemaker",
        "synergy": "Harmonious Inclusion. They create a psychological safety net. They lead by relationship, ensuring staff feel loved.",
        "support": "**Conflict Coaching:** Role-play hard conversations.\n**Permission to Disappoint:** Absolve them of the need to please everyone.",
        "thriving": "**High Retention:** Staff stay for the leader.\n**Psychological Safety:** Low-fear, high-trust environment.\n**De-escalation:** Presence alone lowers blood pressure.",
        "struggling": "**The Doormat:** Lets staff walk over them.\n**Exhaustion:** Compassion fatigue from over-caring.\n**Triangulation:** Vents to others instead of addressing conflict.",
        "interventions": [
            "**Phase 1: Direct Address.** Require one direct hard conversation per week.",
            "**Phase 2: Disappointing Others.** Challenge them to make an unpopular decision.",
            "**Phase 3: Self-Protection.** Teach them to set boundaries on empathy."
        ],
        "questions": ["What boundaries do you need?", "Are you listening too much?", "Who is taking care of you?", "Is your silence creating confusion?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need a 51% decision?", "Are you waiting for consensus?"],
        "advancement": "**Conflict:** Prove they can handle a fight.\n**Separation:** Prove they can lead friends.\n**Results:** Prove they value outcomes as much as feelings."
    },
    "Tracker-Achievement": {
        "title": "The Architect",
        "synergy": "Systematic Perfection. They build systems that allow the team to succeed. They ensure nothing falls through cracks.",
        "support": "**Clarity:** Be hyper-clear about deliverables.\n**Time:** Give them time to do it right; rushing causes panic.",
        "thriving": "**Flawless Execution:** Zero-error reports and clean data.\n**System Builder:** Creates infrastructure that outlasts them.\n**Reliability:** The most dependable person on staff.",
        "struggling": "**Rigidity:** Refuses to bend rules even when it makes sense.\n**Micromanagement:** Hovers to ensure perfection.\n**Critique:** Becomes the 'compliance police'.",
        "interventions": [
            "**Phase 1: Flexibility.** Challenge them to identify one rule to bend for the greater good.",
            "**Phase 2: People over Process.** Require them to mentor a disorganized staff member.",
            "**Phase 3: Big Picture.** Ask them to explain *why* the system exists."
        ],
        "questions": ["How can you measure effort, not just outcome?", "Are you valuing data more than people?", "Where is flexibility needed?", "How can you support the person?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on rule or relationship?", "What is 'good enough'?"],
        "advancement": "**Flexibility:** Prove they can handle chaos.\n**Delegation:** Prove they can trust others' imperfect work.\n**Warmth:** Prove they can connect with people, not just papers."
    },
    "Tracker-Growth": {
        "title": "The Technical Expert",
        "synergy": "Knowledge Mastery. They are the walking encyclopedia. They lead by being the authority everyone turns to.",
        "support": "**Resources:** Do not gatekeep data; open the books.\n**Challenge:** Give them a problem no one else can solve.",
        "thriving": "**Problem Solver:** Fixes technical issues that stump others.\n**Teacher:** Raises unit IQ by sharing knowledge.\n**Innovator:** Upgrades the operating system of the team.",
        "struggling": "**Arrogance:** Weaponizes knowledge to dominate.\n**Over-Complication:** Engineers for experts, not users.\n**Disengagement:** Checks out if bored.",
        "interventions": [
            "**Phase 1: Simplification.** Challenge them to explain complex ideas simply.",
            "**Phase 2: Emotional Intelligence.** Mentor based on potential, not knowledge.",
            "**Phase 3: Strategic Vision.** Solve problems with no 'right' answer."
        ],
        "questions": ["Are you focusing on system or person?", "What is 'good enough'?", "Are you correcting or coaching?", "How can you make it safe to fail?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Focusing on rule or relationship?", "What is 'good enough'?"],
        "advancement": "**Communication:** Speak simply and clearly.\n**Empathy:** Patience with learners.\n**Strategy:** Connect expertise to organizational goals."
    },
    "Tracker-Purpose": {
        "title": "The Guardian",
        "synergy": "Protective Compliance. Following rules is the highest form of caring. They protect the mission from external threat.",
        "support": "**Explanation:** Explain the 'why' behind policy changes.\n**Validation:** Validate their fears/concerns before mitigating.",
        "thriving": "**Safety Net:** Catches errors that cause lawsuits.\n**Moral Consistency:** Closes gap between values and behavior.\n**Reliability:** A vault for secrets and safety.",
        "struggling": "**Bureaucracy:** Uses rules to block action.\n**Fear-Mongering:** Predicts disaster constantly.\n**Judgment:** Views errors as moral failings.",
        "interventions": [
            "**Phase 1: Risk Assessment.** Ask them to rate risks 1-10 (triage).",
            "**Phase 2: The 'Why' of Flexibility.** Show where breaking a rule saved a kid.",
            "**Phase 3: Solution Focus.** Don't bring a problem without a solution."
        ],
        "questions": ["How can you protect without being rigid?", "Are you using rules to manage anxiety?", "Is this rule serving the child?", "How can you explain the 'why'?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Rule or relationship?", "What is 'good enough'?"],
        "advancement": "**Risk Tolerance:** Take calculated risks.\n**Flexibility:** Adapt to change without panic.\n**Vision:** See the forest, not just the trees."
    },
    "Tracker-Connection": {
        "title": "The Reliable Rock",
        "synergy": "Servant Consistency. Shows love by doing the work perfectly. They are the backbone of the unit.",
        "support": "**Notice Details:** Validate invisible labor.\n**Change Management:** Hold their hand through transitions.",
        "thriving": "**Steady Presence:** Always there, always prepared.\n**Helper:** Supports the lead without ego.\n**Culture Keeper:** Maintains traditions and history.",
        "struggling": "**Overwhelmed:** Says 'yes' to everything.\n**Passive Aggressive:** Punishes with silence if unappreciated.\n**Resistance to Change:** Digs heels in to stay safe.",
        "interventions": [
            "**Phase 1: Saying No.** Practice boundaries.",
            "**Phase 2: Vocalizing Needs.** Force them to take up space.",
            "**Phase 3: Leading Change.** Help a new person adapt."
        ],
        "questions": ["How can you show care with words?", "Are you doing too much?", "Do they know you care?", "Where do you need help?", "What do you need?", "Where are you stuck?", "How can I help?", "What is the goal?", "Rule or relationship?", "What is 'good enough'?"],
        "advancement": "**Voice:** Speak up in meetings.\n**Boundaries:** Stop over-functioning.\n**Flexibility:** Handle new ways of doing things."
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
        "s1": c_data.get('desc'),
        "s1_b": c_data.get('bullets'),
        "s2": c_data.get('supervising'),
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
        "s10": m_data.get('celebrate'),
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
    add_section(f"1. Communication Profile: {p_comm}", data['s1'], data['s1_b'])
    add_section("2. Supervising Their Communication", data['s2'], data['s2_b'])
    add_section(f"3. Motivation Profile: {p_mot}", data['s3'], data['s3_b'])
    add_section("4. Motivating This Staff Member", data['s4'], data['s4_b'])
    add_section("5. Integrated Leadership Profile", data['s5']) 
    add_section("6. How You Can Best Support Them", data['s6'])
    add_section("7. What They Look Like When Thriving", data['s7'])
    add_section("8. What They Look Like When Struggling", data['s8'])
    add_section("9. Supervisory Interventions (Roadmap)", None, data['s9_b'])
    add_section("10. What You Should Celebrate", data['s10'], data['s10_b'])

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

    show_section(f"1. Communication Profile: {p_comm}", data['s1'], data['s1_b'])
    show_section("2. Supervising Their Communication", data['s2'], data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", data['s3'], data['s3_b'])
    show_section("4. Motivating This Staff Member", data['s4'], data['s4_b'])
    show_section("5. Integrated Leadership Profile", data['s5'])
    show_section("6. How You Can Best Support Them", data['s6'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("7. Thriving")
        st.write(data['s7'])
    with c2:
        st.subheader("8. Struggling")
        st.write(data['s8'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. Supervisory Interventions", None, data['s9_b'])
    show_section("10. What You Should Celebrate", data['s10'], data['s10_b'])
    
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
                    # Prepare Context Data (Updated to use new Master Profiles if needed)
                    # Note: Conflict mediator relies on basic profiles for now for simplicity
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
                            - **Communication Style:** {comm_style} ({comm_data.get('desc', '')})
                            - **Core Motivation:** {motiv_driver} ({mot_data.get('desc', '')})
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
                         response += f"**Communication Style:** {comm_data.get('desc', '')}\n\n"
                         response += f"**Core Driver:** {mot_data.get('desc', '')}"

                    elif "strengths" in query or "good at" in query:
                        response += f"**Strengths:** As a {comm_style}, they excel at: \n"
                        for b in comm_data.get('bullets', []):
                            response += f"- {b}\n"
                        response += f"\nDriven by {motiv_driver}, they are motivated by: \n"
                        for b in mot_data.get('bullets', []):
                            response += f"- {b}\n"

                    elif "feedback" in query or "critical" in query or "correct" in query:
                        response += f"**On giving feedback to a {comm_style}:** {comm_data.get('supervising', 'Be clear.')}\n\n"
                        response += f"**Motivation Tip:** Frame the feedback in a way that doesn't block their drive for {motiv_driver}. "
                        if motiv_driver == "Connection": response += "Reassure them that the relationship is safe."
                        elif motiv_driver == "Achievement": response += "Focus on how fixing this helps them win."
                    
                    elif "motivate" in query or "burnout" in query:
                        response += f"**To motivate a {motiv_driver} driver:** {mot_data.get('strategies', 'Ask them what they need.')}\n\n"
                    
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
