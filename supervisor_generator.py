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
            "**Clarity:** They prioritize the 'bottom line' over the backstory, speaking in headlines to ensure immediate understanding. Supervisors should not mistake their brevity for rudeness; they are simply trying to be efficient. When communicating with them, start with the conclusion first, then fill in details if asked. They often strip away emotional context to get straight to the facts, viewing feelings as distractions from the data.",
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

# Standard Motivation Profiles (Sections 3-4)
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

# Detailed Integrated Profiles (Sections 5-12)
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
        "advancement": "**Delegate Effectively:** Build a team that protects children. They must learn that they can multiply their impact by teaching others to care, rather than doing all the caring themselves. Trusting others' hearts is a key step.\n\n**Allow Safe Failure:** Trust that others also care. They need to learn that a mistake by a staff member doesn't mean that staff member is 'bad.' They must separate competence from character.\n\n**Focus on Strategy:** Build systems that prevent injustice. They need to move from reacting to individual crises to preventing them through policy and culture. This is the shift from tactical advocacy to strategic advocacy."
    },
    "Director-Connection": {
        "title": "The Protective Captain",
        "synergy": "Safe Enclosure. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to. They are the 'Mama Bear' or 'Papa Bear' of the unit.",
        "support": "**Touchpoints:** Short, genuine check-ins are crucial. You don't need a one-hour meeting; you need five minutes of real connection. Consistency matters more than duration.\n\n**Backing:** Be candid about where you can back them up (air cover). They need to know you are in their corner. If they feel exposed or unsupported, they will withdraw their loyalty.",
        "thriving": "**Decisive Care:** They fix problems for people immediately. They don't just sympathize; they solve. They use their Director power to remove obstacles for their people.\n\n**Crisis Stabilization:** They become the calm human shield during a crisis. Staff look to them for physical and emotional safety. Their presence alone can de-escalate a room.\n\n**Team Loyalty:** They build a strong 'Us.' The team has a distinct identity and high morale. People protect each other and cover for each other because the Captain has set the standard.",
        "struggling": "**Us vs. Them:** They become hostile toward outsiders (admin, other units). They circle the wagons and view any critique of their team as an attack. They can create a silo that is hard to penetrate.\n\n**Over-Functioning:** They do everyone's job to protect them. They burn themselves out trying to carry the load for 'weaker' team members. They enable underperformance in the name of loyalty.\n\n**Taking Conflict Personally:** They conflate professional disagreement with personal betrayal. If you correct them, they feel unloved. This makes supervision very tricky and emotional.",
        "interventions": [
            "**Phase 1: Delegation of Care (0-6 Months):** Stop being the only fixer; assign care tasks to others. Require them to let someone else handle a crisis or plan a party. They must learn that the team can survive without their constant intervention. You are breaking the dependency cycle.",
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

# 5c. INTEGRATED PROFILES (Expanded & 10 Coaching Questions Logic)
def generate_profile_content(comm, motiv):
    
    # This dictionary holds the specific text for the 16 combinations
    combo_key = f"{comm}-{motiv}"
    
    # Lookup individual profiles
    c_data = COMM_PROFILES.get(comm, {})
    m_data = MOTIV_PROFILES.get(motiv, {})
    i_data = INTEGRATED_PROFILES.get(combo_key, {})

    return {
        "s1_b": c_data.get('bullets'),
        "s2_b": c_data.get('supervising_bullets'),
        "s3_b": m_data.get('bullets'),
        "s4_b": m_data.get('strategies_bullets'),
        # S5 is Synergy
        "s5": f"**Profile:** {i_data.get('title')}\n\n{i_data.get('synergy')}",
        "s6": i_data.get('support', ''),
        "s7": i_data.get('thriving', ''), # Thriving paragraphs
        "s8": i_data.get('struggling', ''), # Struggling paragraphs
        "s9": "Strategies for Course Correction:", # Intervention Header
        "s9_b": i_data.get('interventions', []),
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
