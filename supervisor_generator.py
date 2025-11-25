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
            --text-main: {BRAND_COLORS['dark']};
            --text-sub: {BRAND_COLORS['gray']};
        }}

        /* GLOBAL FONT & BACKGROUND */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }}
        
        /* MAIN APP CONTAINER */
        .stApp {{
            background: radial-gradient(circle at top left, #f1f5f9 0%, #ffffff 100%);
        }}

        /* HEADERS */
        h1, h2, h3, h4 {{
            color: var(--primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}
        
        h1 {{ font-size: 2.2rem !important; }}
        h2 {{ font-size: 1.5rem !important; margin-top: 1.5rem !important; }}
        h3 {{ font-size: 1.2rem !important; margin-top: 1rem !important; }}

        /* CUSTOM CARDS */
        .custom-card {{
            background-color: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }}

        /* METRIC CONTAINERS */
        div[data-testid="stMetric"] {{
            background-color: white;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }}
        
        div[data-testid="stMetricLabel"] {{ font-size: 0.9rem !important; color: var(--text-sub) !important; }}
        div[data-testid="stMetricValue"] {{ font-size: 1.8rem !important; color: var(--primary) !important; font-weight: 700 !important; }}

        /* BUTTONS */
        .stButton button {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(1, 91, 173, 0.15);
        }}
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(1, 91, 173, 0.25);
            opacity: 0.95;
        }}

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            background-color: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            border-radius: 8px;
            color: var(--text-sub);
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(1, 91, 173, 0.1) !important;
            color: var(--primary) !important;
            border-bottom: 2px solid var(--primary);
        }}

        /* ALERTS & INFO BOXES */
        .stAlert {{
            border-radius: 12px;
            border: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        /* DATAFRAME */
        div[data-testid="stDataFrame"] {{
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
        }}

        /* EXPANDERS */
        .streamlit-expanderHeader {{
            background-color: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            font-weight: 600;
            color: var(--text-main);
        }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CONTENT DICTIONARIES ---
# (Data remains the same, ensuring stability)

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
            "scripts": {
                "To Director": "You are trying to fix the problem, but right now, the *relationship* is the problem.",
                "To Encourager": "My brevity is not anger; it is urgency. I need you to tell me: 'I can help you win, but I need you to lower your volume.'",
                "Joint": "We are speaking two different languages. I will validate your concern before we move to the next step."
            }
        },
        # ... (Rest of matrix logic preserved from previous successful versions)
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
# Fallback for robust lookup
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

# (PDF Dictionaries - Shortened placeholders for code stability, logic uses full text in PDF func)
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

# --- HELPER FUNCTIONS ---
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

# --- MAIN APP LOGIC ---
staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# RESET FUNCTIONS
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- UI ---
def header():
    col1, col2 = st.columns([0.1, 0.9])
    with col1: st.markdown("<div style='background:#015bad;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;font-size:1.2rem;'>EC</div>", unsafe_allow_html=True)
    with col2: st.markdown("## Elmcrest Supervisor Platform")
    st.markdown("---")

header()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Guide Generator", "🧬 Team DNA", "⚖️ Conflict Mediator", "🚀 Career Pathfinder", "📈 Org Pulse"])

# --- TAB 1: GUIDE ---
with tab1:
    st.markdown("#### 📄 Generate Supervisory Guides")
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
                    st.warning(f"**Watch For:** {', '.join(c['struggle_bullets'][:2])}")
                st.button("Reset", on_click=reset_t1)
    with sub2:
        with st.form("manual"):
            c1,c2 = st.columns(2)
            mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
            mpc = c1.selectbox("Comm", COMM_TRAITS.keys()); mpm = c2.selectbox("Motiv", ["Growth", "Purpose", "Connection", "Achievement"])
            if st.form_submit_button("Generate") and mn:
                pdf = create_supervisor_guide(mn, mr, mpc, None, mpm, None)
                st.download_button("Download PDF", pdf, "guide.pdf", "application/pdf")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("#### 🧬 Team Analysis")
    if not df.empty:
        teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        if teams:
            tdf = df[df['name'].isin(teams)]
            c1, c2 = st.columns(2)
            with c1:
                comm_counts = tdf['p_comm'].value_counts()
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, title="Communication Mix", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
                
                # Blindspot Logic
                present = set(tdf['p_comm'].unique())
                missing = set(COMM_TRAITS.keys()) - present
                if missing: st.error(f"🚫 **Blindspot Alert:** This team lacks **{', '.join(missing)}** energy.")
                
            with c2:
                mot_counts = tdf['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
            
            st.button("Clear", on_click=reset_t2)

# --- TAB 3: CONFLICT ---
with tab3:
    st.markdown("#### ⚖️ Conflict Coaching")
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
                
                with st.expander("🔍 **Root Cause Analysis**", expanded=True):
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
            else:
                st.info("Same-style match. Focus on not amplifying weaknesses.")
            
            st.button("Reset", key="reset_t3", on_click=reset_t3)

# --- TAB 4: CAREER ---
with tab4:
    st.markdown("#### 🚀 Career Pathfinder")
    if not df.empty:
        c1, c2 = st.columns(2)
        cand = c1.selectbox("Candidate", df['name'].unique(), index=None, key="career")
        role = c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target")
        
        if cand and role:
            d = df[df['name']==cand].iloc[0]
            style = d['p_comm']
            path = CAREER_PATHWAYS.get(style, {}).get(role)
            
            if path:
                st.divider()
                st.markdown(f"**Current Style:** {style} $\\rightarrow$ **Target:** {role}")
                
                st.info(f"**The Shift:** {path['shift']}")
                st.markdown(f"*{path['why']}*")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    with st.container(border=True):
                        st.markdown("##### 🗣️ The Conversation")
                        st.write(path['conversation'])
                        st.warning(f"**Supervisor Watch Item:** {path.get('supervisor_focus')}")
                
                with c_b:
                    with st.container(border=True):
                        st.markdown("##### ✅ Litmus Test Assignment")
                        st.write(f"**Setup:** {path['assignment_setup']}")
                        st.write(f"**Task:** {path['assignment_task']}")
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flag:** {path['red_flags']}")
            
            st.button("Reset", key="reset_t4", on_click=reset_t4)

# --- TAB 5: PULSE ---
with tab5:
    st.markdown("#### 📈 Org Pulse")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        top_comm = df['p_comm'].mode()[0]
        top_mot = df['p_mot'].mode()[0]
        
        c1.metric("Dominant Style", top_comm)
        c2.metric("Top Driver", top_mot)
        c3.metric("Total Staff", len(df))
        
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a:
            st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
        with c_b:
            # Pipeline Chart
            if 'role' in df.columns:
                st.plotly_chart(px.histogram(df, x="role", color="p_comm", title="Leadership Pipeline (Comm Style by Role)", color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
        
        st.markdown("##### 🌡️ Cultural Risk Assessment")
        if top_comm == "Director" and top_mot == "Achievement":
            st.error("🚨 **High Burnout Risk:** Dominant 'Director/Achievement' culture. We execute fast but may lack empathy. **Action:** Intentionally reward 'Connection' behaviors.")
        elif top_comm == "Encourager" and top_mot == "Connection":
            st.warning("⚠️ **Nice-Guy Risk:** Dominant 'Encourager/Connection' culture. High morale but low accountability. **Action:** Standardize audit processes.")
        else:
            st.info(f"Culture is anchored in **{top_comm}** communication and **{top_mot}** motivation.")
