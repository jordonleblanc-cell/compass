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

# MOVED TO TOP TO FIX NAME ERROR
COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

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
df_all = pd.DataFrame(all_staff_list)

if not df_all.empty:
    df_all.columns = df_all.columns.str.lower().str.strip() 
    for col in ['role', 'cottage', 'name']:
        if col in df_all.columns:
            df_all[col] = df_all[col].astype(str).str.strip()

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

    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""<div class='login-card'><div class='login-title'>Supervisor Access</div></div>""", unsafe_allow_html=True)
    if not df_all.empty:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Admin"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Who are you?", user_names, key="user_select")
    else:
        st.selectbox("Who are you?", ["Administrator"], key="user_select")
    st.text_input("Access Code", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- 6. DATA FILTERING ---
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
        elif "YDP" in user_role:
            filtered_df = filtered_df[filtered_df['name'] == current_user]
    return filtered_df

df = get_filtered_dataframe()

with st.sidebar:
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# EXPANDED CONTENT DICTIONARIES
# ==========================================

FULL_COMM_PROFILES = {
    "Director": {
        "description": "This staff member communicates primarily as a **Director**. They lead with clarity, structure, and urgency.\n\nThey often strip away emotional context to get straight to the facts, prioritizing the 'bottom line' over the backstory. While this efficiency is a major asset, they can sometimes appear blunt or dismissive of feelings, which may alienate more sensitive team members.",
        "desc_bullets": [
            "**Clarity:** They prioritize headlines over paragraphs to ensure immediate understanding.",
            "**Speed:** They process information rapidly and expect others to keep up.",
            "**Conflict:** They view conflict as a tool for problem-solving, not a relationship breaker."
        ],
        "supervising": "To supervise a Director effectively, match their directness. Do not 'sandwich' feedback with small talk; give it to them straight. They respect competence and time management above all else.\n\nFocus on outcomes rather than micromanaging the process. Give them a goal and the autonomy to achieve it, and trust them to come to you if they hit a roadblock.",
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately; they value their time and yours.",
            "**Focus on Outcomes:** Tell them *what* needs to be achieved, but leave the *how* to them.",
            "**Respect Autonomy:** Give them space to operate independently; tight oversight feels like distrust."
        ],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?"]
    },
    "Encourager": {
        "description": "This staff member communicates primarily as an **Encourager**. They lead with empathy, warmth, and emotional presence.\n\nThey act as the 'glue' of the team, ensuring everyone feels seen and included. They process information verbally and socially, often thinking out loud to find clarity. They are naturally optimistic and focus on potential.",
        "desc_bullets": [
            "**Verbal Processing:** They think out loud and need dialogue to process ideas.",
            "**Optimism:** They focus on potential and bring hope to difficult situations.",
            "**Relationship-First:** They influence people through connection and charisma."
        ],
        "supervising": "Start every interaction with connection before content. If you jump straight to business, they may feel you are cold or angry. Validate their positive intent before correcting the impact of their behavior.\n\nBe specific with feedback, as they can sometimes speak in generalities. Ensure you follow up verbally agreed-upon tasks with written documentation, as they may focus more on the feeling of the meeting than the details.",
        "supervising_bullets": [
            "**Allow Discussion:** Give space to connect before diving into business.",
            "**Ask for Specifics:** Drill down to facts when they speak in broad strokes.",
            "**Follow Up in Writing:** Document everything important to ensure alignment."
        ],
        "questions": ["Are you avoiding the hard truth to be nice?", "Is your silence creating confusion?", "What boundaries do you need to set to protect your energy?"]
    },
    "Facilitator": {
        "description": "This staff member communicates primarily as a **Facilitator**. They lead by listening, building consensus, and ensuring fairness across the board.\n\nThey are the 'calm bridge' who de-escalates tension and ensures all voices are heard before a decision is made. They value the process of decision-making as much as the outcome itself, ensuring that no one is left behind.",
        "desc_bullets": [
            "**Listening:** They gather all perspectives before forming a judgment.",
            "**Consensus:** They prefer group agreement and dislike polarization.",
            "**Process:** They value fairness and want a just process for everyone."
        ],
        "supervising": "Give them time to process. Do not demand immediate decisions on complex issues if possible. They need to weigh the options and consider the impact on the team.\n\nSet clear deadlines to prevent 'analysis paralysis.' Encourage them to speak first in meetings to ensure their valuable insights aren't drowned out by louder voices.",
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before demanding a response.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless deliberation.",
            "**Solicit Opinion:** Ask them explicitly for their view, as they may not fight for airtime."
        ],
        "questions": ["Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?", "How does your silence impact the team?"]
    },
    "Tracker": {
        "description": "This staff member communicates primarily as a **Tracker**. They lead with details, accuracy, and safety.\n\nThey find comfort in rules and consistency, protecting the agency and youth by noticing the small risks that others miss. They value precision and are risk-averse, preferring to verify facts before speaking or acting.",
        "desc_bullets": [
            "**Detail-Oriented:** They value accuracy and speak in specifics.",
            "**Risk-Averse:** They are cautious and verify facts before acting.",
            "**Process-Driven:** They trust the handbook and follow protocol."
        ],
        "supervising": "Provide clear, written expectations. Do not be vague. Honor their need for 'the plan' and specific metrics. When plans change, explain the 'why' clearly so they don't feel the change is arbitrary or unsafe.\n\nUse logic and data to persuade them, not emotional appeals. They respect competence and consistency above charisma.",
        "supervising_bullets": [
            "**Be Specific:** Use metrics and data when giving feedback.",
            "**Provide Data:** Use logic over emotion to persuade them.",
            "**Written Instructions:** Document everything important in writing."
        ],
        "questions": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "How can you support the person, not just the process?"]
    }
}

FULL_MOTIV_PROFILES = {
    "Achievement": {
        "description": "Their primary motivator is **Achievement**. They thrive when they can see progress, check boxes, and win.\n\nThey hate stagnation and ambiguity. They want to know they are doing a good job based on objective evidence, not just feelings. They are driven by the scoreboard and the satisfaction of completion.",
        "desc_bullets": [
            "**Scoreboard:** They need to know if they are winning or losing.",
            "**Completion:** They get energy from finishing tasks and closing loops.",
            "**Efficiency:** They hate wasted time and redundancy."
        ],
        "strategies": "Set clear, measurable goals. Use visual trackers or dashboards. Celebrate 'wins' explicitly and publicly. Give them projects where they can own the result from start to finish.\n\nEnsure they have a way to track their own progress. They will work incredibly hard if they can see the finish line.",
        "strategies_bullets": [
            "**Visual Goals:** Use charts or checklists they can physically mark off.",
            "**Public Wins:** Acknowledge their success in front of peers.",
            "**Autonomy:** Give them the goal and let them design the strategy."
        ],
        "celebrate": "Celebrate concrete outcomes, finished projects, improved metrics, and their reliability in getting things done. They want to be recognized for their competence and output.",
        "celebrate_bullets": [
            "**Outcomes:** 'You hit 100% on documentation.'",
            "**Reliability:** 'I know I can count on you to finish this.'",
            "**Speed:** 'You got this done faster than anyone else.'"
        ],
        "questions": ["How are you defining success today beyond just metrics?", "What is one win you can celebrate right now?", "Are you driving the team too hard?"]
    },
    "Growth": {
        "description": "Their primary motivator is **Growth**. They thrive when they are learning, stretching, and mastering new skills.\n\nThey hate feeling stuck or bored. They view their role as a stepping stone to greater competence and are constantly looking for the next challenge. They value feedback as a tool for improvement.",
        "desc_bullets": [
            "**Curiosity:** They are driven to understand the 'why' and 'how'.",
            "**Future-Focused:** They are thinking about their next career step.",
            "**Feedback:** They crave constructive correction over empty praise."
        ],
        "strategies": "Feed their curiosity. Assign them 'stretch' projects that require new skills. Frame feedback as 'coaching' for their future career. Connect mundane tasks to their long-term professional development.\n\n regularly discuss their career path and facilitate mentorship opportunities with leaders they admire.",
        "strategies_bullets": [
            "**Stretch Assignments:** Give them tasks slightly above their current skill level.",
            "**Career Pathing:** Regularly discuss their professional future.",
            "**Mentorship:** Connect them with leaders they admire."
        ],
        "celebrate": "Celebrate new skills learned, adaptability, taking on new challenges, and their personal development trajectory. Validate their intellect and insight.",
        "celebrate_bullets": [
            "**Insight:** Celebrate specific moments where they identified a root cause others missed.",
            "**Development:** A staff member who visibly improved under their guidance.",
            "**Courage:** Their willingness to try a new approach, even if it failed."
        ],
        "questions": ["What are you learning from this struggle?", "Are you expecting too much too soon from others?", "How are you feeding your own curiosity?"]
    },
    "Purpose": {
        "description": "Their primary motivator is **Purpose**. They thrive when they feel their work aligns with deep values and makes a real difference for kids.\n\nThey hate bureaucracy that feels meaningless or performative. They will endure difficult conditions if they believe the 'Why' is noble, but they will rebel against policies that feel unjust.",
        "desc_bullets": [
            "**Values-Driven:** Decisions must align with their moral compass.",
            "**Advocacy:** They are wired to fight for the underdog.",
            "**Meaning:** They need the 'why' connected to client well-being."
        ],
        "strategies": "Connect every rule to a 'Why.' Validate their passion for justice and advocacy. Share specific stories of their impact on youth. When assigning tasks, explain how this helps the youth or the mission.\n\nAllow space for them to voice moral concerns without penalty. Even if you can't change the decision, listening builds trust.",
        "strategies_bullets": [
            "**The Why:** Always explain the mission behind the mandate.",
            "**Storytelling:** Share stories of life-change and impact.",
            "**Ethics:** Allow space for them to voice moral concerns."
        ],
        "celebrate": "Celebrate their advocacy for youth, their integrity, ethical decision making, and specific 'mission moments' where they changed a life. Validate their heart.",
        "celebrate_bullets": [
            "**Integrity:** Celebrate moments where they made a hard ethical choice.",
            "**Advocacy:** Celebrate when they gave a voice to the voiceless.",
            "**Consistency:** Celebrate their unwavering commitment to care."
        ],
        "questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?"]
    },
    "Connection": {
        "description": "Their primary motivator is **Connection**. They thrive when they feel part of a tight-knit team and have a sense of belonging.\n\nThey hate isolation and unresolved conflict. For them, the 'who' is more important than the 'what.' If the team is fractured, their performance will suffer.",
        "desc_bullets": [
            "**Belonging:** They view the team as family.",
            "**Harmony:** They are sensitive to tension and avoid conflict.",
            "**Support:** They are motivated by helping their peers."
        ],
        "strategies": "Prioritize face time. Check in on them as a person, not just an employee. Build team rituals (food, shout-outs). Ensure they don't work in a silo.\n\nWhen giving feedback, reassure them of their belonging in the team. They need to know the relationship is safe even when the work needs correction.",
        "strategies_bullets": [
            "**Face Time:** Prioritize in-person check-ins.",
            "**Team Rituals:** Encourage meals and team bonding.",
            "**Personal Care:** Ask about their life outside work."
        ],
        "celebrate": "Celebrate team cohesion, their support of peers, morale building, and their role in conflict resolution. Validate their invisible labor of culture building.",
        "celebrate_bullets": [
            "**Loyalty:** Celebrate their standing up for the team.",
            "**Stabilization:** Celebrate their presence calming a room.",
            "**Culture:** Celebrate the strong identity they build."
        ],
        "questions": ["Are you avoiding this conversation to be kind, or to be safe?", "How is the team reacting to your directness?", "Who do you need to check in with today?"]
    }
}

INTEGRATED_PROFILES = {
    "Director-Achievement": {
        "title": "THE EXECUTIVE GENERAL",
        "lead": "The synergy here is **Operational Velocity**. They don't just want to lead; they want to win. They cut through noise to identify the most efficient path to success. They are excellent at turnarounds or crisis management where decisive action is required immediately.",
        "support": ["**Operational Risk:** Name the operational risk of moving fast. 'We can do this quickly if we build in these guardrails.' This validates their speed while protecting the agency from errors.", "**Burnout Watch:** They are the best person to identify when the 'ask' exceeds capacity, but they need permission to say it. They often view endurance as a badge of honor and will work until they collapse."],
        "thriving": ["**Rapid Decision Architecture:** They make calls with partial information, preventing the team from freezing in analysis paralysis. They create a sense of momentum.", "**Objective Focus:** They separate story from fact, focusing on behaviors and outcomes. This helps de-escalate emotional situations by grounding them in reality.", "**High-Bar Accountability:** They refuse to walk past a mistake, raising the standard of care. They hold peers accountable naturally, often elevating the performance of the whole group."],
        "struggling": ["**The Steamroller Effect:** They announce decisions without checking if the team is emotionally ready. This can alienate staff who feel unheard or bulldozed.", "**Burnout by Intensity:** They assume everyone has their stamina and push until the team breaks. They struggle to understand why others can't just 'power through.'", "**Dismissing 'Soft' Data:** They ignore 'bad feelings' or intuition because there is no proof. This leads to missing early warning signs of cultural toxicity."],
        "interventions": ["**Phase 1: The Pause Button (0-6 Months):** Force a delay between thought and action. Require them to ask three questions of their team before issuing a command.", "**Phase 2: Narrative Leadership (6-12 Months):** Coach them to script the 'Why' behind their directives. They need to learn that explaining logic is not a waste of time, but an investment.", "**Phase 3: Multiplier Effect (12-18 Months):** Identify two deputies and train the supervisor to sit on their hands while the deputies lead. This shifts their focus from 'doing' to 'developing'."],
        "questions": ["How are you defining success today beyond just metrics?", "What is one win you can celebrate right now?", "Are you driving the team too hard?", "What is the cost of speed right now?", "Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?", "Are you celebrating the small wins?", "Who helped you win this week?", "What is 'good enough' for right now?"],
        "advancement": ["**Delegate Effectively:** Give away tasks they are good at to prove they can build a team. They must learn that their value comes from their team's output, not just their own.", "**Allow Safe Failure:** Let the team struggle so they can learn, rather than rescuing them. Rescuing robs the team of the learning opportunity.", "**Focus on Strategy:** Move from the 'how' (tactics) to the 'why' (organizational strategy). Advancement requires thinking about the next year, not just the next shift."]
    },
    "Director-Growth": {
        "title": "THE RESTLESS IMPROVER",
        "lead": "The synergy here is **Transformational Leadership**. They don't just manage the shift; they want to upgrade it. They see potential in every staff member and are willing to push hard to unlock it. They are natural disruptors who prevent the agency from stagnating.",
        "support": ["**Connect Goals:** Link their personal growth goals to youth outcomes and the mission. Help them see that 'getting better' isn't just about their resume, but about serving the client better.", "**Pacing:** Remind them that not everyone learns at their speed. They need help understanding that organizational change is a marathon, not a sprint."],
        "thriving": ["**Diagnostic Speed:** They quickly identify the root causes of failures rather than treating symptoms. They are excellent at analyzing a crisis to prevent it from recurring.", "**Fearless Innovation:** They are willing to break the status quo to find a better way. They are not afraid of administrative pushback if they believe their idea improves care.", "**High-Impact Coaching:** They give direct, developmental feedback that accelerates the growth of their peers. They are often the 'tough love' mentor on the unit."],
        "struggling": ["**The Pace Mismatch:** They get visibly frustrated with slow learners or bureaucracy. This impatience can leak out as arrogance or disdain.", "**'Fix-It' Fatigue:** They are constantly pointing out flaws and forgetting to validate what is working. The team may feel that nothing is ever good enough for them.", "**Leaving People Behind:** They focus on the *idea* of change rather than the *adoption* of change. They implement new systems without getting buy-in, leading to failure."],
        "interventions": ["**Phase 1: Validation (0-6 Months):** Mandate that they validate the current effort before suggesting improvements. They must catch people doing things right to build trust.", "**Phase 2: Change Management (6-12 Months):** Require a 'stakeholder analysis' for their next idea (who will resist and why?). This forces them to consider the human element of change.", "**Phase 3: Capacity Building (12-18 Months):** Shift them from being the idea generator to the facilitator of *others'* ideas. Challenge them to help a peer implement a change project."],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?", "What are you learning from this struggle?", "Are you expecting too much too soon from others?", "How are you feeding your own curiosity?", "What is one way you can slow down for others?", "How are you measuring your own growth beyond just speed?", "Are you leaving the team behind?", "Is this change necessary right now?"],
        "advancement": ["**Delegate Effectively:** Stop being the 'fixer,' become the 'developer.' They must learn to guide others to the answer rather than providing it.", "**Allow Safe Failure:** Resist the urge to jump in and correct every mistake. They need to learn that struggle is a necessary part of the learning process.", "**Focus on Strategy:** Design tomorrow's solutions rather than solving today's problems. Shift their gaze from 'immediate fix' to 'systemic prevention.'"]
    },
    "Director-Purpose": {
        "title": "THE MISSION DEFENDER",
        "lead": "The synergy here is **Ethical Courage**. They provide the moral backbone for the team, ensuring expediency never trumps integrity. They are the conscience of the unit and will speak truth to power without hesitation.",
        "support": ["**Share Values:** Share your own core values so they trust your leadership. They need to know you are 'one of the good guys.' If they trust your heart, they will follow your orders.", "**Operational Risk:** Frame slowing down as 'protecting the mission.' Help them see that rushing can lead to mistakes that hurt the client."],
        "thriving": ["**Unshakeable Advocacy:** They act immediately against injustice. They do not wait for permission to stop something unsafe or unethical.", "**Clarity of 'Why':** They contextualize the grind for the staff. When the team is tired, they remind everyone why the work matters.", "**Crisis Ethics:** They keep their moral compass even in chaos. When everyone else is panicking, they are asking 'What is the right thing to do?'"],
        "struggling": ["**Righteous Rigidity:** They struggle to see the gray areas, viewing everything as black and white. This can make them inflexible and difficult to negotiate with.", "**The Martyr Complex:** They overwork because they don't trust others to care enough. They believe that if they stop, the clients will suffer.", "**Judgmental Tone:** They come across as 'preachy' or morally superior. They may unintentionally shame staff who are just trying to get through the day."],
        "interventions": ["**Phase 1: The Gray Zone (0-6 Months):** Practice identifying validity in opposing viewpoints. Require them to argue the 'other side' of an ethical debate to build cognitive flexibility.", "**Phase 2: Sustainable Advocacy (6-12 Months):** Coach them to use a 'Tier System' for battles (Tier 1: Fight, Tier 2: Debate, Tier 3: Let go).", "**Phase 3: Cultural Architecture (12-18 Months):** Move from fighting battles to building systems that prevent injustice. Challenge them to write the policy rather than just complaining."],
        "questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?", "How does flexibility serve the mission here?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast for the team?", "How does your tone land when you are stressed?"],
        "advancement": ["**Delegate Effectively:** Build a team that protects children. They must learn that they can multiply their impact by teaching others to care.", "**Allow Safe Failure:** Trust that others also care. They need to learn that a mistake by a staff member doesn't mean that staff member is 'bad.'", "**Focus on Strategy:** Build systems that prevent injustice. They need to move from reacting to individual crises to preventing them through policy and culture."]
    },
    "Director-Connection": {
        "title": "THE PROTECTIVE CAPTAIN",
        "lead": "The synergy here is **Safe Enclosure**. They create a perimeter of safety where staff and youth feel protected. They lead from the front, taking the hits so their team doesn't have to. They are the 'Mama Bear' or 'Papa Bear' of the unit.",
        "support": ["**Touchpoints:** Short, genuine check-ins are crucial. You don't need a one-hour meeting; you need five minutes of real connection.", "**Backing:** Be candid about where you can back them up (air cover). They need to know you are in their corner. If they feel exposed, they will withdraw."],
        "thriving": ["**Decisive Care:** They fix problems for people immediately. They don't just sympathize; they solve. They use their Director power to remove obstacles.", "**Crisis Stabilization:** They become the calm human shield during a crisis. Staff look to them for physical and emotional safety.", "**Team Loyalty:** They build a strong 'Us.' The team has a distinct identity and high morale. People protect each other and cover for each other."],
        "struggling": ["**Us vs. Them:** They become hostile toward outsiders (admin, other units). They circle the wagons and view any critique of their team as an attack.", "**Over-Functioning:** They do everyone's job to protect them. They burn themselves out trying to carry the load for 'weaker' team members.", "**Taking Conflict Personally:** They conflate professional disagreement with personal betrayal. If you correct them, they feel unloved."],
        "interventions": ["**Phase 1: Delegation of Care (0-6 Months):** Stop being the only fixer; assign care tasks to others. Require them to let someone else handle a crisis.", "**Phase 2: Organizational Citizenship (6-12 Months):** Expand the circle of loyalty to the whole agency. Challenge them to partner with another unit or department.", "**Phase 3: Mentorship (12-18 Months):** Transition from Captain to Admiral (teaching others to build loyalty). Task them with training a new supervisor on how to build culture."],
        "questions": ["Are you avoiding this conversation to be kind, or to be safe?", "How can you be direct and caring at the same time?", "Are you protecting them from growth?", "How is the team reacting to your directness?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where are you moving too fast for the team?", "Who do you need to check in with today?"],
        "advancement": ["**Delegate Effectively:** Stop being 'camp parent.' They must prove they can manage managers, not just staff. This means letting go of the daily emotional caretaking.", "**Allow Safe Failure:** Learn the team is resilient. They need to see that the team won't break if they step back. This builds their confidence in the system.", "**Focus on Strategy:** Expand loyalty to the whole agency. They need to advocate for the organization, not just their unit. This is the shift to executive thinking."]
    },
    "Encourager-Achievement": {
        "title": "THE COACH",
        "lead": "The synergy here is **Inspirational Performance**. They make hard work feel like a game. They believe the team can win and their energy is contagious. They drive results not by demanding them, but by pumping the team up to chase them.",
        "support": ["**Reality Checks:** Be the ground to their sky. Validate their enthusiasm but ask 'What is the plan if this goes wrong?' You provide the tether.", "**Focus:** Help them pick one lane. They want to achieve everything at once; force them to prioritize. You are the editor of their ambition."],
        "thriving": ["**Team Morale:** The unit has high energy and believes they are the best unit in the building. There is a 'swag' to the team.", "**Rallying:** They can turn a bad shift around with a pep talk. They refuse to let the team wallow in defeat. They are resilient optimists.", "**Goal-Smashing:** When locked in, they hit metrics with flair and celebrate loudly. They make success look fun. They normalize high performance."],
        "struggling": ["**Overselling:** They promise things they can't deliver to get buy-in. This leads to disappointment and loss of trust later.", "**Disorganization:** They are moving so fast and talking so much they lose paperwork or forget details. They leave a wake of administrative chaos.", "**Impatience:** They get frustrated when the team doesn't share their burning desire to win immediately. They can't understand low energy."],
        "interventions": ["**Phase 1: Follow-Through (0-6 Months):** Focus on finishing. Require them to complete one project fully before starting the next exciting one.", "**Phase 2: Data Discipline (6-12 Months):** Move from 'feeling' to 'fact.' Require them to bring data to supervision, not just stories. 'Show me, don't just tell me.'", "**Phase 3: Grooming Talent (12-18 Months):** Challenge them to let others shine. The 'Coach' needs to get off the field and let the players score."],
        "questions": ["How do we keep this energy up when things get boring?", "What are the specific steps to get to that vision?", "Who is doing the work: you or the team?", "How will you track this?", "What is the one thing we must finish this week?", "Who needs the spotlight more than you right now?", "Are you listening or just waiting to speak?", "What happens if we miss this goal?", "How are you celebrating the team's grind, not just the win?", "Is your enthusiasm masking a problem?"],
        "advancement": ["**Detail Management:** They must prove they can handle the boring stuff (admin, budgets). If they can't do the paperwork, they can't run the department.", "**Listening:** They need to learn to sit back and let others speak. They must prove they can intake information, not just output it.", "**Consistency:** Prove they can maintain performance when the excitement fades. They need to show they can grind."]
    },
    "Encourager-Growth": {
        "title": "THE MENTOR",
        "lead": "The synergy here is **Developmental Charisma**. They see the gold in people and talk it out of them. They make people feel smarter and more capable just by being around them. They lead by selling the team on their own potential.",
        "support": ["**Structure:** They have a million ideas; provide the structure to execute one. You are the trellis for their vine. Help them focus their creative energy.", "**Patience:** Remind them that growth is messy and non-linear. They can get discouraged when people slide back. Be the steady hand."],
        "thriving": ["**Talent Magnet:** People want to work for them because they feel grown and seen. They attract high-potential staff. They build a deep bench.", "**Culture of Learning:** Mistakes are celebrated as learning opportunities, reducing fear in the unit. They create a safe laboratory for growth.", "**Innovation:** They are constantly bringing in new ideas from books, podcasts, or other units. They keep the agency fresh."],
        "struggling": ["**Shiny Object Syndrome:** They chase a new initiative every week, confusing the team. The staff gets whiplash from the constant pivots.", "**Avoidance of Hard Conversations:** They want to inspire, not correct. They struggle to give negative feedback that might 'hurt' the relationship.", "**All Talk:** They talk a great game about development but lack the follow-through to document it. Great visions, poor execution."],
        "interventions": ["**Phase 1: Closing the Loop (0-6 Months):** Force them to finish what they start. No new ideas until the last one is implemented. Make them live with their creations.", "**Phase 2: Difficult Feedback (6-12 Months):** Role-play giving 'hard' feedback. Teach them that clarity is kind. They must learn to break the news without breaking the bond.", "**Phase 3: Systems of Growth (12-18 Months):** Turn their informal mentoring into a formal training manual. Capture their genius in a document."],
        "questions": ["Who are you investing in, and who are you ignoring?", "How do we turn this idea into a habit?", "Are you avoiding the hard truth to be nice?", "What is the one skill the team needs right now?", "How are you measuring that improvement?", "Are you talking more than they are?", "What did you finish this week?", "Is this practical, or just interesting?", "How does this help the client today?", "What are you reading/learning?"],
        "advancement": ["**Execution:** Prove they can implement, not just ideate. They need to show they can land the plane, not just fly it.", "**Toughness:** Prove they can make the hard personnel calls. They need to show they can fire someone if necessary.", "**Focus:** Prove they can stick to a boring plan for the long haul. They need to show they can survive the mundane."]
    },
    "Encourager-Purpose": {
        "title": "THE HEART OF THE MISSION",
        "lead": "The synergy here is **Passionate Advocacy**. They are the soul of the unit. They keep the emotional flame alive. When everyone else is cynical, they are the ones reminding the team why this work matters. They lead with raw emotion and belief.",
        "support": ["**Emotional Boundaries:** Help them distinguish between caring and carrying. They will burn out by taking home the trauma. You must be the wall that keeps the flood out.", "**Validation:** Frequently affirm that their heart is a strength, not a weakness. They often feel 'too soft' for the work; remind them that softness is a tool."],
        "thriving": ["**Cultural Carrier:** They set the emotional tone. If they are up, the unit is up. They are the thermostat of the team, regulating the emotional temperature.", "**Advocate:** They are fearless in speaking up for kids, using their persuasion to get resources. They can charm the resources out of administration.", "**Inspiration:** They can make a tired team feel like heroes again. They bring the magic back to the work."],
        "struggling": ["**Emotional Flooding:** They get so wrapped up in the 'story' they lose objectivity. They might cry in meetings or get irrationally angry at perceived slights.", "**Us vs. The System:** They can whip the team into a frenzy against 'cold' administration. They become the ringleader of the rebellion.", "**Burnout:** They give everything and have nothing left. They crash hard and often abruptly because they have no reserves."],
        "interventions": ["**Phase 1: Boundaries (0-6 Months):** Teach them to leave work at work. 'The badge stays at the door.' Create specific rituals for disconnecting.", "**Phase 2: Fact-Checking (6-12 Months):** When they tell a passionate story, ask 'Is that true, or is that how it felt?' Force them to separate emotion from data.", "**Phase 3: Channeling Passion (12-18 Months):** Give them a platform (e.g., orientation training) where their passion is an asset, not a distraction."],
        "questions": ["Is this feeling a fact?", "How can you care without carrying?", "Are you whipping the team up or calming them down?", "What is the most ethical choice, even if it feels bad?", "Who is supporting you?", "Is this your battle to fight?", "How does the policy actually help the child?", "Are you listening to the logic, or just the tone?", "What do you need to let go of today?", "How can we use your voice for good?"],
        "advancement": ["**Objectivity:** Prove they can make dispassionate decisions. They need to show they can look at a spreadsheet without crying.", "**Policy:** Understand the legal/fiscal reasons behind rules. They need to learn the language of administration and risk management.", "**Resilience:** Bounce back without drama. They need to show they can take a hit and keep moving without needing constant reassurance."]
    },
    "Encourager-Connection": {
        "title": "THE TEAM BUILDER",
        "lead": "The synergy here is **Social Cohesion**. They are the social cruise director of the unit. They ensure everyone feels included, liked, and happy. They lead by making the workplace feel like a community.",
        "support": ["**Hard Decisions:** Step in to be the 'bad guy' so they don't have to burn social capital. Lend them your spine until they grow theirs.", "**Focus:** Remind them that work is the goal, fun is the method. Don't let the party overtake the mission. Keep the main thing the main thing."],
        "thriving": ["**Zero Turnover:** People stay because they love the team. They create a sticky culture that is hard to leave. Staff feel at home and supported.", "**Conflict Resolution:** They talk things out and smooth over rough edges. They keep the social machinery oiled. They heal rifts before they become canyons.", "**Joy:** There is laughter on the unit, which is therapeutic. They make the heavy work lighter. They bring the fun to the grind."],
        "struggling": ["**The Country Club:** Too much socializing, not enough work. The unit becomes a hangout spot where standards slip. Productivity drops.", "**Gossip:** Their need to be 'in the know' and close to everyone can spiral into drama. They trade secrets for connection. They become the center of the rumor mill.", "**Favoritism:** They struggle to lead people they don't personally like. They create an 'in-crowd' and an 'out-crowd.' They alienate the outliers."],
        "interventions": ["**Phase 1: Professionalism (0-6 Months):** Define the line between 'friend' and 'colleague' explicitly. They often blur these lines.", "**Phase 2: Inclusive Leadership (6-12 Months):** Challenge them to connect with the staff member they like the least. Break up their clique.", "**Phase 3: Task Focus (12-18 Months):** Assign them a project that requires solitude or deep focus to build that muscle. Teach independence."],
        "questions": ["Are we having fun, or are we working?", "Who is on the outside of the circle?", "Are you avoiding the conflict to keep the peace?", "How can you deliver that news directly?", "Are you gossiping or venting?", "Can you be friendly without being their best friend?", "How does the work get done if we talk all day?", "What is the cost of not holding them accountable?", "Who needs to hear from you today?", "How are you protecting your own energy?"],
        "advancement": ["**Separation:** Prove they can lead without needing to be liked. They need to be respected first, liked second. This is the hardest hurdle.", "**Confidentiality:** Prove they can keep secrets. They need to show they aren't a sieve for information.", "**Productivity:** Prove they can drive results, not just vibes. They need to show they can hit the numbers and hold others to them."]
    },
    "Facilitator-Achievement": {
        "title": "THE STEADY MOVER",
        "lead": "The synergy here is **Methodical Progress**. They don't sprint; they march. They get the team to the finish line by ensuring everyone knows their role and the process is solid. They are the engine that keeps the unit moving forward without chaos.",
        "support": ["**Decision Speed:** Push them to decide even when they don't have 100% consensus. Appeal to their need to 'finish' the task. Frame indecision as failure.", "**Validation:** Praise the quiet work of organization. Notice the spreadsheets, the schedules, and the well-run meetings. Acknowledge their structure."],
        "thriving": ["**Consistent Wins:** They hit the metrics every month without drama or panic. They are boringly successful. They are the metronome of the department.", "**Efficient Meetings:** They run meetings where everyone feels heard, but action items are clearly assigned. They master the follow-up.", "**Project Management:** They are excellent at long-term implementation of complex initiatives. They don't drop the ball on details or deadlines."],
        "struggling": ["**Analysis Paralysis:** They freeze at the intersection of speed and agreement. They want to achieve the goal but want everyone to agree on how.", "**Frustration with Chaos:** They hate last-minute changes that disrupt the plan they worked hard to create. They can be rigid when the plan changes.", "**Silent Resentment:** They work hard and resent those who don't, but won't say it aloud to avoid conflict. They steam internally."],
        "interventions": ["**Phase 1: Speaking Up (0-6 Months):** Call on them first in meetings to break the habit of waiting. Force them to voice their messy thoughts.", "**Phase 2: Imperfect Action (6-12 Months):** Assign a task with an impossible deadline to force a 'good enough' decision. Make them move before they are ready.", "**Phase 3: Direct Delegation (12-18 Months):** Challenge them to assign tasks without asking for volunteers. They must learn to command, not just coordinate."],
        "questions": ["What is the 'good enough' decision right now?", "Are you waiting for everyone to agree?", "How can we move forward even if it's messy?", "Who is holding up the project?", "What have you achieved this week?", "Is the process helping or hurting the goal?", "How can you say 'no' to protect the timeline?", "Who needs to be cut out of the decision loop?", "Are you doing the work to avoid asking others?", "What is the next step?"],
        "advancement": ["**Speed:** Make faster decisions with less data. They need to prove they can move at the speed of the crisis.", "**Conflict:** Call out underperformance directly. They need to show they can have the hard talk without crumbling.", "**Vision:** Look beyond the checklist to the strategy. They need to lift their eyes to the horizon and see what's coming."]
    },
    "Facilitator-Growth": {
        "title": "THE PATIENT GARDENER",
        "lead": "The synergy here is **Organic Development**. They don't force growth; they create the conditions for it. They are incredibly patient with difficult staff or youth, believing that everyone can change if given enough time and support. They nurture rather than drive.",
        "support": ["**Urgency:** You must provide the urgency, or they will let things grow forever. Remind them that sometimes we need to prune (fire/discipline) for the health of the whole.", "**Outcome Focus:** Remind them that growth must eventually result in performance. Potential is not enough; we need kinetic energy and results."],
        "thriving": ["**Turnaround Specialist:** They can take a failing staff member and slowly rehabilitate them. They save people others would fire by finding their hidden strengths.", "**Deep Listening:** They understand the nuance of the unit better than anyone. They know the root system of the culture and the hidden dynamics.", "**Sustainable Pace:** They model a healthy work-life balance that prevents burnout. They run a marathon pace, not a sprint."],
        "struggling": ["**Tolerance of Mediocrity:** They give people too many chances in the name of 'growth.' They enable bad behavior by refusing to set hard limits.", "**Slow to Launch:** They study the problem forever without fixing it. They get stuck in diagnosis and analysis paralysis.", "**Fear of Judgment:** They struggle to evaluate people because they know how hard growth is. They don't want to play judge or executioner."],
        "interventions": ["**Phase 1: Timelines (0-6 Months):** Put a date on development goals. 'They have 3 months to improve.' Create a kill switch for their patience.", "**Phase 2: Judgment (6-12 Months):** Practice evaluating performance objectively based on data. 'Is this good or bad?' Force them to use binary labels.", "**Phase 3: Pruning (12-18 Months):** They must terminate or discipline a staff member to learn that protection isn't always love. They must experience the necessity of the cut."],
        "questions": ["How long is too long to wait for improvement?", "Is this person actually growing, or are we just hoping?", "What is the cost to the team of keeping this person?", "Are you learning, or just stalling?", "What is the lesson here?", "How can you speed up this process?", "Who are you neglecting by focusing on the struggler?", "What does 'accountability' look like to you?", "Are you afraid to judge?", "What is the next step today?"],
        "advancement": ["**Decisiveness:** Act on the data, not just the hope. They must show they can call the game based on facts. They need to be firm when necessary.", "**Speed:** Move faster than feels comfortable. They must match the market's pace and urgency. They need to accelerate their decision-making.", "**Standards:** Hold the line on quality without apology. They must show they have a floor for performance. They need to demand excellence."]
    },
    "Facilitator-Purpose": {
        "title": "THE MORAL COMPASS",
        "lead": "The synergy here is **Principled Consensus**. They are the quiet conscience of the team. They ensure that the team doesn't just get things done, but gets them done *right*. They build unity around shared values and mission, creating a deeply ethical culture.",
        "support": ["**Validation of Values:** Regularly affirm their role as the ethical standard-bearer. Tell them, 'I appreciate that you always keep the client's needs in focus.'", "**Decision Frameworks:** Give them a framework for making 'imperfect' decisions (e.g., 'We are choosing the least bad option'). Help them navigate the gray."],
        "thriving": ["**Ethical Anchor:** When the team is confused, they bring everyone back to the mission statement. They center the boat in the storm.", "**Unified Team:** They create a team culture where everyone feels respected and heard. They build a moral community based on trust.", "**Trust:** Staff trust them implicitly because they know they are not self-interested. They have high credibility because their motives are pure."],
        "struggling": ["**Moral Paralysis:** They refuse to make a decision because no option is perfectly ethical. They freeze in the face of ambiguity.", "**Passive Resistance:** Instead of arguing openly, they simply don't do the things they disagree with. They silently rebel against policies they dislike.", "**Judgment:** They may silently judge others who are more pragmatic or business-minded. They can become self-righteous and isolated."],
        "interventions": ["**Phase 1: The '51% Decision' (0-6 Months):** Teach them that in leadership, you often have to move with only 51% certainty. Require them to make calls even when uncomfortable.", "**Phase 2: Voice Training (6-12 Months):** Challenge them to speak their dissent in the meeting, not after. They need to learn to be a 'vocal conscience.'", "**Phase 3: Operational Ethics (12-18 Months):** Task them with creating a system or policy that institutionalizes their values. Move them from complaining to building."],
        "questions": ["What moral tension are you holding right now?", "How can you speak up for your values effectively?", "Are you staying neutral when you should take a stand?", "How does your silence impact the team?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?"],
        "advancement": ["**Decisiveness:** They must prove they can make hard calls when it is necessary, even if it hurts feelings.", "**Public Speaking:** They need to get comfortable projecting their voice and values to a larger audience. They need to lead out loud.", "**Pragmatism:** They need to demonstrate they understand the business realities alongside the ethical ones. They need balance."]
    },
    "Facilitator-Connection": {
        "title": "THE PEACEMAKER",
        "lead": "The synergy here is **Harmonious Inclusion**. They create a psychological safety net for the team. They lead by relationship, ensuring that staff feel loved, supported, and heard so they can do the hard work of care.",
        "support": ["**Conflict Coaching:** They are likely terrified of conflict. Role-play hard conversations with them to build muscle memory. Be their sparring partner.", "**Permission to Disappoint:** Explicitly tell them, 'It is okay if they are mad at you.' Absolve them of the need to please everyone."],
        "thriving": ["**High Retention:** People rarely leave their team because it feels good to work there. They build deep loyalty and connection.", "**Psychological Safety:** Staff admit mistakes freely because they aren't afraid of shame. The environment is low-fear and high-trust.", "**De-escalation:** They can calm a room just by walking in. They are a sedative for chaos and stress. They bring the peace."],
        "struggling": ["**The Doormat:** They let staff walk all over them to avoid a fight. They lose respect and authority. They become a pushover.", "**Exhaustion:** They carry everyone's emotional baggage and trauma. They develop compassion fatigue from over-caring.", "**Triangulation:** Instead of addressing an issue directly, they complain to others to vent. They create side conversations to avoid the main conflict."],
        "interventions": ["**Phase 1: Direct Address (0-6 Months):** Require them to have one direct, hard conversation per week. Inspect the result. Build calluses on their empathy.", "**Phase 2: Disappointing Others (6-12 Months):** Challenge them to make a decision they know will be unpopular. Support them through the backlash.", "**Phase 3: Self-Protection (12-18 Months):** Teach them to set boundaries on their time and empathy. They must learn to say 'no' to protect their own health."],
        "questions": ["What boundaries do you need to set to protect your energy?", "Are you listening too much and leading too little?", "Who is taking care of you?", "Is your silence creating confusion?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?"],
        "advancement": ["**Conflict:** Prove they can handle a fight without crumbling. They need to show toughness and the ability to hold a line.", "**Separation:** Prove they can lead friends and former peers. They need to show authority and professional distance.", "**Results:** Prove they value outcomes as much as feelings. They need to show performance metrics, not just morale scores."]
    },
    "Tracker-Achievement": {
        "title": "THE ARCHITECT",
        "lead": "The synergy here is **Systematic Perfection**. They build the systems that allow the team to succeed. They are the engineers of the unit. They ensure that nothing falls through the cracks and that every procedure is followed to the letter.",
        "support": ["**Clarity:** Be hyper-clear about expectations. Ambiguity is torture for them.", "**Time:** Give them the time to do it right. Respect their need for precision."],
        "thriving": ["**Flawless Execution:** Their paperwork is perfect. Their audits are 100% compliant. You never have to check their work twice.", "**System Builder:** They create new trackers or logs that save everyone time. They build infrastructure.", "**Reliability:** If they say it is done, it is done right. They are a safe pair of hands."],
        "struggling": ["**Rigidity:** They refuse to bend rules even when it makes sense. They become the 'bureaucrat'.", "**Micromanagement:** They hover to ensure it is done 'perfectly'. They can't let go.", "**Critique:** They constantly point out errors. They become the 'compliance police'."],
        "interventions": ["**Phase 1: Flexibility (0-6 Months):** Challenge them to identify one rule that can be bent for the greater good. Force them to operate in the gray.", "**Phase 2: People over Process (6-12 Months):** Require them to mentor a disorganized staff member without doing the work for them. They must learn to tolerate imperfection.", "**Phase 3: Big Picture (12-18 Months):** Ask them to explain *why* the system exists, not just *how* it works. Move them from the weeds to the sky."],
        "questions": ["How can you measure effort, not just outcome?", "Are you valuing the data more than the person?", "Where is flexibility needed right now?", "How can you support the person, not just the process?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": ["**Flexibility:** Prove they can handle chaos without breaking. They need to show adaptability when the plan fails.", "**Delegation:** Prove they can trust others to do the work, even imperfectly. They need to let go of the control to scale.", "**Warmth:** Prove they can connect with people, not just papers. They need to build relationships to influence the team."]
    },
    "Tracker-Growth": {
        "title": "THE TECHNICAL EXPERT",
        "lead": "The synergy here is **Knowledge Mastery**. They are the walking encyclopedia of the agency. They know every rule, every regulation, and every loophole. They lead by being the authority that everyone turns to for the answer.",
        "support": ["**Resources:** Give them access to information. Do not gatekeep data.", "**Challenge:** Give them a problem no one else can solve. Test their skills."],
        "thriving": ["**Problem Solver:** They fix technical issues that stump everyone else. They are the 'IT support' for the program logic.", "**Teacher:** They raise the unit's IQ by sharing knowledge. They empower the team.", "**Innovator:** They find new tools to make work better. They upgrade the operating system."],
        "struggling": ["**Arrogance:** They weaponize knowledge to dominate. They value IQ over EQ.", "**Over-Complication:** They design systems too complex for users. They create barriers.", "**Disengagement:** If they stop learning, they check out. They need stimulation."],
        "interventions": ["**Phase 1: Simplification (0-6 Months):** Challenge them to explain a complex idea to a layperson without using jargon. You are teaching communication.", "**Phase 2: Emotional Intelligence (6-12 Months):** Require them to mentor someone based on their *potential*, not their current knowledge. Focus on the relationship.", "**Phase 3: Strategic Vision (12-18 Months):** Ask them to solve a problem where there is no 'right' answer, only trade-offs. You are teaching executive judgment."],
        "questions": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "Are you correcting or coaching?", "How can you make it safe to make mistakes?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": ["**Communication:** Prove they can speak simply and clearly. They need to translate the technical to the practical for leadership.", "**Empathy:** Prove they can care about people who aren't experts. They need to show patience with learners and strugglers.", "**Strategy:** Prove they can think about the 'why,' not just the 'how.' They need to see the business case and the mission impact."]
    },
    "Tracker-Purpose": {
        "title": "THE GUARDIAN",
        "lead": "The synergy here is **Protective Compliance**. They believe that following the rules is the highest form of caring. They protect the mission by ensuring that the agency never gets in trouble. They are the shield that keeps the organization safe.",
        "support": ["**Explanation:** Explain the 'why' behind policy changes. Give them the rationale.", "**Validation:** Validate their fears. Honor their watchfulness as a skill."],
        "thriving": ["**Safety Net:** They catch errors that would cause liability. They save the agency's life.", "**Moral Consistency:** They ensure we do what we say. They keep us honest.", "**Reliability:** They are a vault for secrets and safety. They are dependable."],
        "struggling": ["**Bureaucracy:** They use rules to block action. They get stuck in red tape.", "**Fear-Mongering:** They predict disaster. They spread anxiety.", "**Judgment:** They view errors as moral failings. They judge harshly."],
        "interventions": ["**Phase 1: Risk Assessment (0-6 Months):** Rate risks 1-10. Teach perspective.", "**Phase 2: The 'Why' of Flexibility (6-12 Months):** Show where breaking a rule saved a kid. Teach judgment.", "**Phase 3: Solution Focus (12-18 Months):** Don't bring problems without solutions. Teach leadership."],
        "questions": ["How can you protect the mission without being rigid?", "Are you using rules to manage your anxiety?", "Is this rule serving the child right now?", "How can you explain the 'why' behind the rule?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": ["**Risk Tolerance:** Take a calculated risk. Learn that growth requires risk.", "**Flexibility:** Adapt to change without panic. Bend without breaking.", "**Vision:** See the forest, not just the trees. Rise above daily compliance."]
    },
    "Tracker-Connection": {
        "title": "THE RELIABLE ROCK",
        "lead": "The synergy here is **Servant Consistency**. They show their love for the team by doing the work perfectly. They are the backbone of the unit. They don't want the spotlight; they just want to be useful and safe within the group.",
        "support": ["**Notice the Details:** Validate the invisible labor that keeps the office running.", "**Change Management:** Hold their hand through change. Be their anchor."],
        "thriving": ["**Steady Presence:** They are always there and prepared. They provide stability.", "**Helper:** They support the lead without ego. They make everyone look good.", "**Culture Keeper:** They maintain traditions and history. They nurture the bond."],
        "struggling": ["**Overwhelmed:** They say 'yes' to everything and drown. They suffer in silence.", "**Passive Aggressive:** They withdraw if unappreciated. They resent lack of thanks.", "**Resistance to Change:** They love the rut because it is safe. They block innovation."],
        "interventions": ["**Phase 1: Saying No (0-6 Months):** Practice saying 'no'. Teach self-respect.", "**Phase 2: Vocalizing Needs (6-12 Months):** Ask for what they need. Teach assertiveness.", "**Phase 3: Leading Change (12-18 Months):** Help a new person adapt. Teach mentorship."],
        "questions": ["How can you show care in a way they understand?", "Are you doing too much for others?", "Do they know you care?", "Where do you need help carrying the load?", "What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?", "Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?"],
        "advancement": ["**Voice:** Speak up in meetings. Learn to advocate verbally.", "**Boundaries:** Stop over-functioning. Protect your time.", "**Flexibility:** Handle a new way of doing things. Navigate change."]
    }
}

# 5c. DYNAMIC GUIDE GENERATION (Updated Logic)
def generate_profile_content(comm, motiv):
    combo_key = f"{comm}-{motiv}"
    
    # 1. Fetch Generic Data
    comm_data = FULL_COMM_PROFILES.get(comm, {})
    mot_data = FULL_MOTIV_PROFILES.get(motiv, {})
    
    # 2. Fetch Integrated Data
    int_data = INTEGRATED_PROFILES.get(combo_key, {})
    
    # 3. Construct Data Packet
    return {
        "s1": comm_data.get("description", ""),
        "s1_b": comm_data.get("bullets", []),
        "s2": "To supervise this staff member effectively, you must match their communication style while guiding them toward the team's goals.",
        "s2_b": comm_data.get("supervising", []),
        "s3": mot_data.get("description", ""),
        "s3_b": mot_data.get("bullets", []),
        "s4": "Use these strategies to keep them engaged and productive.",
        "s4_b": mot_data.get("motivating", []),
        "s5": int_data.get("lead", ""),
        "s6": "Support them by honoring their unique combination of traits.",
        "s6_b": int_data.get("support", []),
        "s7": int_data.get("thriving", []),
        "s8": int_data.get("struggling", []),
        "s9": int_data.get("interventions", []),
        "s10": int_data.get("title", ""), # Using title for section header context if needed
        "s10_b": mot_data.get("celebrate", []),
        "coaching": int_data.get("questions", []),
        "advancement": int_data.get("advancement", [])
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (1, 91, 173); black = (0, 0, 0)
    
    # Generate Data
    data = generate_profile_content(p_comm, p_mot)
    title = INTEGRATED_PROFILES.get(f"{p_comm}-{p_mot}", {}).get("title", "Supervisory Guide")

    # Header
    pdf.set_font("Arial", 'B', 16); pdf.set_text_color(*blue); pdf.cell(0, 10, "ELMCREST SUPERVISORY GUIDE", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14); pdf.set_text_color(*black); pdf.cell(0, 10, title, ln=True, align='C')
    pdf.set_font("Arial", '', 10); pdf.cell(0, 5, clean_text(f"For: {name} ({role}) | Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(5)
    
    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 11); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 7, title, ln=True, fill=True); pdf.ln(1)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(*black)
        
        if body:
            clean_body = body.replace("**", "").replace("* ", "")
            pdf.multi_cell(0, 5, clean_text(clean_body))
            pdf.ln(1)
        
        if bullets:
            for b in bullets:
                pdf.set_font("Arial", 'B', 10)
                clean_b = b.replace("**", "").split(":", 1)
                if len(clean_b) > 1:
                    pdf.write(5, clean_text(f"- {clean_b[0]}:"))
                    pdf.set_font("Arial", '', 10)
                    pdf.multi_cell(0, 5, clean_text(clean_b[1]))
                else:
                    pdf.set_font("Arial", '', 10)
                    pdf.multi_cell(0, 5, clean_text(f"- {clean_b[0]}"))
            pdf.ln(2)

    # Content Building
    add_section(f"1. COMMUNICATION PROFILE: {p_comm.upper()}", data['s1'], data['s1_b'])
    add_section("2. SUPERVISING THEIR COMMUNICATION", None, data['s2_b'])
    add_section(f"3. MOTIVATION PROFILE: {p_mot.upper()}", data['s3'], data['s3_b'])
    add_section("4. MOTIVATING THIS STAFF MEMBER", None, data['s4_b'])
    add_section("5. INTEGRATED LEADERSHIP PROFILE", data['s5'])
    add_section("6. HOW YOU CAN BEST SUPPORT THEM", None, data['s6_b'])
    add_section("7. WHAT THEY LOOK LIKE WHEN THRIVING", None, data['s7'])
    add_section("8. WHAT THEY LOOK LIKE WHEN STRUGGLING", None, data['s8'])
    add_section("9. SUPERVISORY INTERVENTIONS (Strategic Roadmap)", None, data['s9'])
    add_section("10. WHAT YOU SHOULD CELEBRATE", None, data['s10_b'])
    
    # 11. Coaching Questions
    pdf.set_font("Arial", 'B', 11); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 7, "11. COACHING QUESTIONS", ln=True, fill=True); pdf.ln(1)
    pdf.set_font("Arial", '', 10); pdf.set_text_color(*black)
    for i, q in enumerate(data['coaching']):
        pdf.multi_cell(0, 5, clean_text(f"{i+1}. {q}"))
    pdf.ln(2)

    # 12. Advancement
    add_section("12. HELPING THEM PREPARE FOR ADVANCEMENT", None, data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)
    title = INTEGRATED_PROFILES.get(f"{p_comm}-{p_mot}", {}).get("title", "Supervisory Guide")

    st.markdown("---")
    st.markdown(f"## {title}")
    st.caption(f"**For:** {name} ({role}) | **Profile:** {p_comm} x {p_mot}")
    st.divider()
    
    def show_section(title, text, bullets=None):
        st.markdown(f"### {title}")
        if text: st.write(text)
        if bullets:
            for b in bullets:
                st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)

    show_section(f"1. COMMUNICATION PROFILE: {p_comm.upper()}", data['s1'], data['s1_b'])
    show_section("2. SUPERVISING THEIR COMMUNICATION", None, data['s2_b'])
    show_section(f"3. MOTIVATION PROFILE: {p_mot.upper()}", data['s3'], data['s3_b'])
    show_section("4. MOTIVATING THIS STAFF MEMBER", None, data['s4_b'])
    show_section("5. INTEGRATED LEADERSHIP PROFILE", data['s5'])
    show_section("6. HOW YOU CAN BEST SUPPORT THEM", None, data['s6_b'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 7. THRIVING")
        for b in data['s7']: st.success(b)
    with c2:
        st.markdown("### 8. STRUGGLING")
        for b in data['s8']: st.error(b)
    
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. SUPERVISORY INTERVENTIONS", None, data['s9'])
    show_section("10. WHAT YOU SHOULD CELEBRATE", None, data['s10_b'])
    
    st.markdown("### 11. COACHING QUESTIONS")
    for i, q in enumerate(data['coaching']):
        st.write(f"**{i+1}.** {q}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("12. HELPING THEM PREPARE FOR ADVANCEMENT", None, data['advancement'])

# --- 6. MAIN APP LOGIC (unchanged) ---
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
            # Create dictionary from the FILTERED dataframe
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
                        guide = TEAM_CULTURE_GUIDE.get("Balanced", {})
                        st.info("**Balanced Culture:** No single style dominates. This reduces blindspots but may increase friction.")
                        with st.expander("📖 Managing a Balanced Team", expanded=True):
                             st.markdown("""**The Balanced Friction:**
                             A diverse team has no blind spots, but it speaks 4 different languages. Your role is **The Translator**.
                             * **Translate Intent:** 'The Director isn't being mean; they are being efficient.' 'The Tracker isn't being difficult; they are being safe.'
                             * **Rotate Leadership:** Let the Director lead the crisis; let the Encourager lead the debrief; let the Tracker lead the audit.
                             * **Meeting Protocol:** Use structured turn-taking (Round Robin) so the loudest voice doesn't always win.""")

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
                
                if not mot_counts.empty:
                    dom_mot = mot_counts.idxmax()
                    st.markdown("---")
                    st.subheader(f"⚠️ Motivation Gap: {dom_mot} Driven")
                    
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
        with st.sidebar:
            secret_key = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
            user_api_key = st.text_input(
                "🔑 Gemini API Key", 
                value=st.session_state.get("gemini_key_input", secret_key),
                type="password",
                help="Get a key at aistudio.google.com"
            )
            
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
                
                active_key = user_api_key
                
                if active_key:
                    st.caption(f"Powered by Gemini 2.5 Flash | Ask specific questions about managing **{p2}** ({s2} x {m2}).")
                else:
                    st.caption("Basic Mode | Add an API Key in the sidebar to unlock full AI capabilities.")
                
                st.info("⬇️ **Type your question in the chat bar at the bottom of the screen.**")
                
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                def get_smart_response(query, comm_style, motiv_driver, key):
                    comm_data = FULL_COMM_PROFILES.get(comm_style, {})
                    mot_data = FULL_MOTIV_PROFILES.get(motiv_driver, {})
                    
                    if key:
                        try:
                            system_prompt = f"""
                            You are an expert Leadership Coach for a youth care agency.
                            You are advising a Supervisor on how to manage a staff member named {p2}.
                            
                            Here is the Staff Member's Profile:
                            - **Communication Style:** {comm_style} ({comm_data.get('description', '')})
                            - **Core Motivation:** {motiv_driver} ({mot_data.get('description', '')})
                            - **Thriving Behaviors:** {comm_data.get('desc_bullets', [])}
                            - **Stress Behaviors:** They may become rigid, withdrawn, or aggressive when their need for {motiv_driver} is blocked.
                            
                            **Your Goal:** Answer the user's question specifically tailored to this profile.
                            Do not give generic advice. Use the profile data to explain WHY the staff member acts this way and HOW to reach them.
                            Be concise, practical, and empathetic.
                            """
                            
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

                    query = query.lower()
                    response = ""
                    
                    if "who is" in query or "tell me about" in query or "profile" in query:
                         response += f"**Profile Overview:** {p2} is a **{comm_style}** driven by **{motiv_driver}**.\n\n"
                         response += f"**Communication Style:** {comm_data.get('description', '')}\n\n"
                         response += f"**Core Driver:** {mot_data.get('description', '')}"

                    elif "strengths" in query or "good at" in query:
                        response += f"**Strengths:** As a {comm_style}, they excel at: \n"
                        for b in comm_data.get('desc_bullets', []):
                            response += f"- {b}\n"
                        response += f"\nDriven by {motiv_driver}, they are motivated by: \n"
                        for b in mot_data.get('desc_bullets', []):
                            response += f"- {b}\n"

                    elif "feedback" in query or "critical" in query or "correct" in query:
                        response += f"**On giving feedback to a {comm_style}:** {comm_data.get('supervising', 'Be clear.')}\n\n"
                        response += f"**Motivation Tip:** Frame the feedback in a way that doesn't block their drive for {motiv_driver}. "
                        if motiv_driver == "Connection": response += "Reassure them that the relationship is safe."
                        elif motiv_driver == "Achievement": response += "Focus on how fixing this helps them win."
                    
                    elif "motivate" in query or "burnout" in query:
                        response += f"**To motivate a {motiv_driver} driver:** {mot_data.get('strategies', 'Ask them what they need.')}\n\n"
                    
                    else:
                        debug_key_info = f"Key detected: {key[:4]}..." if key else "No API Key detected"
                        response = f"I can help you manage {p2}. Try asking about:\n- How to give **feedback**\n- How to **motivate** them\n- How to handle **conflict**\n\n*Note: {debug_key_info}. Please check the sidebar.*"
                    
                    return response

                if prompt := st.chat_input(f"Ask about {p2}..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Consulting the Compass Database..."):
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

            st.divider()
            st.header("🔍 Deep Organizational Analysis")
            
            tab1, tab2, tab3 = st.tabs(["🛡️ Culture Risk Assessment", "🔥 Motivation Strategy", "🌱 Leadership Pipeline Health"])
            
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

            with tab3:
                st.markdown("### Leadership Pipeline Analysis")
                if 'role' in df.columns:
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
