import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px
import random

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
            --card-bg: #ffffff;
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
                --card-bg: #1e293b;
                --border-color: #334155;
                --shadow: 0 4px 20px rgba(0,0,0,0.4);
                --input-bg: #0f172a;
            }}
        }}

        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: var(--text-main) !important; }}
        .stApp {{ background: radial-gradient(circle at top left, var(--bg-start) 0%, var(--bg-end) 100%); }}
        h1, h2, h3, h4 {{ color: var(--primary) !important; font-weight: 700 !important; letter-spacing: -0.02em; }}
        
        .custom-card {{ background-color: var(--card-bg); padding: 24px; border-radius: 16px; box-shadow: var(--shadow); border: 1px solid var(--border-color); margin-bottom: 20px; color: var(--text-main); }}
        
        .hero-box {{ background: linear-gradient(135deg, #015bad 0%, #0f172a 100%); padding: 30px; border-radius: 16px; color: white !important; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(1, 91, 173, 0.2); }}
        .hero-title {{ color: white !important; font-size: 2rem; font-weight: 800; margin-bottom:10px; }}
        .hero-subtitle {{ color: #e2e8f0 !important; font-size: 1.1rem; opacity: 0.9; max-width: 800px; line-height: 1.6; }}

        /* NAVIGATION BUTTONS */
        div[data-testid="column"] .stButton button {{
            background-color: var(--card-bg); color: var(--text-main) !important; border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 140px; display: flex; flex-direction: column;
            align-items: flex-start; justify-content: center; padding: 20px; white-space: pre-wrap; text-align: left; transition: all 0.2s;
        }}
        div[data-testid="column"] .stButton button:hover {{
            transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); border-color: var(--primary); color: var(--primary) !important;
        }}
        
        /* STANDARD BUTTONS */
        .stButton button:not([style*="height: 140px"]) {{
            background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white !important; border: none; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 10px rgba(1, 91, 173, 0.2);
        }}

        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; border-color: var(--border-color) !important; }}
        div[data-baseweb="popover"] {{ background-color: var(--card-bg) !important; }}
        div[data-baseweb="menu"] {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; }}
        div[data-testid="stDataFrame"] {{ border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }}
        .streamlit-expanderHeader {{ background-color: var(--card-bg) !important; color: var(--text-main) !important; border: 1px solid var(--border-color); }}
        div[data-testid="stExpander"] {{ background-color: var(--card-bg) !important; border: 1px solid var(--border-color); border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CONTENT DICTIONARIES ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# (A) COMMUNICATION PROFILES
COMM_PROFILES = {
    "Director": {
        "s1_profile": {"text": "This staff member communicates primarily as a Director. They lead with clarity, structure, and urgency. They process information quickly and prefer to move to action immediately.", "bullets": ["Prioritizes efficiency over process.", "Speaks in headlines.", "Comfortable making unpopular decisions."]},
        "s2_supervising": {"text": "Supervising a Director requires a high-trust, low-friction approach. They respect leaders who are direct, competent, and concise.", "bullets": ["Be concise.", "Grant autonomy.", "Expect pushback as healthy debate.", "Focus on outcomes."]},
        "s8_struggling": {"text": "Under stress, their decisiveness becomes domination. They may double down on command-and-control.", "bullets": ["Steamrolling quieter voices.", "Visibly irritable.", "Unilateral decision making."]},
        "s11_coaching": ["What is the risk of moving this fast?", "Who haven't we heard from yet?", "How can you frame this so the team feels supported?", "What is the difference between being 'right' and being 'effective'?"],
        "s12_advancement": {"text": "To advance, they must shift from 'Command' to 'Influence'. They need to learn that slowing down to bring people along is a strategic investment.", "bullets": ["Assign cross-dept projects.", "Challenge them to mentor a Facilitator.", "Focus on 'soft skills' development."]}
    },
    "Encourager": {
        "s1_profile": {"text": "This staff member communicates as an Encourager. They are the emotional glue of the team, leading with warmth and optimism. They prioritize well-being above almost everything else.", "bullets": ["Prioritizes harmony.", "Highly empathetic.", "Communicates through connection."]},
        "s2_supervising": {"text": "Supervising an Encourager requires relational investment. If you jump to business without checking in, they feel undervalued.", "bullets": ["Connect first.", "Validate emotional labor.", "Frame feedback as growth."]},
        "s8_struggling": {"text": "Under stress, they avoid conflict and lack accountability. They may struggle to hold boundaries because they don't want to be 'mean'.", "bullets": ["Avoiding hard conversations.", "Venting or gossiping.", "Taking things personally."]},
        "s11_coaching": ["How can you deliver this hard truth while remaining kind?", "Are we prioritizing popularity over effectiveness?", "What boundaries do you need to set?", "Who is carrying your emotional load?"],
        "s12_advancement": {"text": "To advance, they must master the 'Business' side. Their high EQ must be backed by operational reliability.", "bullets": ["Assign compliance audits.", "Role-play disciplinary conversations.", "Focus on time management."]}
    },
    "Facilitator": {
        "s1_profile": {"text": "This staff member communicates as a Facilitator. They are the steady presence who seeks to ensure every voice is heard. They value fairness, process, and consensus.", "bullets": ["Prioritizes inclusion over speed.", "Great listener.", "Dislikes sudden change."]},
        "s2_supervising": {"text": "Supervising them requires patience. Give them time to process. They have insights but won't share unless invited.", "bullets": ["Give advance notice.", "Invite their voice.", "Validate fairness."]},
        "s8_struggling": {"text": "Under stress, they fall into 'Analysis Paralysis,' delaying decisions to avoid upsetting anyone.", "bullets": ["Stalling projects.", "Saying 'it's fine' when it isn't.", "Being perceived as indecisive."]},
        "s11_coaching": ["If you had to decide right now with 80% info, what would it be?", "What is the cost of waiting?", "Where are you holding tension for the team?", "Is this moment for collaboration or direction?"],
        "s12_advancement": {"text": "To advance, they must develop 'Executive Presence' and learn to make the 51/49 call where not everyone agrees.", "bullets": ["Assign time-sensitive projects.", "Challenge them to decide without a meeting.", "Focus on assertiveness."]}
    },
    "Tracker": {
        "s1_profile": {"text": "This staff member communicates as a Tracker. They lead with data and details. They act as the guardian of safety, noticing risks others miss.", "bullets": ["Prioritizes accuracy over speed.", "Detail-oriented.", "Skeptical of big ideas without plans."]},
        "s2_supervising": {"text": "Supervising them requires clarity. Ambiguity is their enemy. Provide clear expectations and written instructions.", "bullets": ["Be specific.", "Respect the system.", "Show the logic."]},
        "s8_struggling": {"text": "Under stress, they become rigid and critical. They get stuck in the weeds, nitpicking minor errors while missing the big picture.", "bullets": ["Refusing to adapt.", "Correcting staff publicly.", "Cynicism."]},
        "s11_coaching": ["Does this detail change the safety outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the 'Good Enough' version?", "Are you being right or effective?"],
        "s12_advancement": {"text": "To advance, they must shift from 'Compliance' to 'Strategy'. They need to learn to tolerate ambiguity and trust people, not just systems.", "bullets": ["Assign 'gray area' roles.", "Launch projects at 80% readiness.", "Focus on strategic thinking."]}
    }
}

# (B) MOTIVATION PROFILES
MOTIVATION_PROFILES = {
    "Growth": {
        "s3_profile": {"text": "Primary motivator: Growth. Energized by development, learning, and mastery. Bored by repetition.", "bullets": ["Seeks feedback.", "Loves pilots.", "Values mentorship."]},
        "s4_motivating": {"text": "Feed their curiosity. Give them problems to solve, not lists to execute.", "bullets": ["Assign stretch projects.", "Connect work to career goals."]},
        "s6_support": {"text": "Be a sponsor. Advocate for their training. Ensure they have a developmental pathway.", "bullets": ["Sponsor for certifications.", "Delegate leveling-up tasks."]},
        "s7_thriving": {"text": "Innovators of the team.", "bullets": ["Proactive questions.", "Volunteering.", "Mentoring peers."]},
        "s10_celebrate": {"text": "Celebrate adaptability and skill acquisition.", "bullets": ["'I saw how you learned X.'", "Publicly acknowledging growth."]}
    },
    "Purpose": {
        "s3_profile": {"text": "Primary motivator: Purpose. Driven by meaning and alignment. Needs to know work matters.", "bullets": ["Committed to mission.", "Sensitive to injustice.", "Values 'The Why'."]},
        "s4_motivating": {"text": "Connect directives to the mission. Be transparent about the 'why'.", "bullets": ["Start with mission moments.", "Invite ethical input."]},
        "s6_support": {"text": "Validate their passion. Listen when they raise ethical concerns.", "bullets": ["Create space for concerns.", "Remind them of impact."]},
        "s7_thriving": {"text": "Passionate advocates.", "bullets": ["Going the extra mile.", "High integrity.", "Resilient."]},
        "s10_celebrate": {"text": "Celebrate impact on youth.", "bullets": ["Specific stories of change.", "Acknowledging character."]}
    },
    "Connection": {
        "s3_profile": {"text": "Primary motivator: Connection. Energized by belonging and cohesion. Works for the 'who'.", "bullets": ["Values harmony.", "Sensitive to conflict.", "Energized by groups."]},
        "s4_motivating": {"text": "Prioritize team dynamic. Use 'We' language. Recognize shared wins.", "bullets": ["Facilitate bonding.", "Personal check-ins."]},
        "s6_support": {"text": "Ensure they aren't isolated. Repair relational ruptures quickly.", "bullets": ["Be accessible.", "Address conflict fast."]},
        "s7_thriving": {"text": "Morale boosters.", "bullets": ["Collaborative.", "High morale.", "Strong rapport."]},
        "s10_celebrate": {"text": "Celebrate culture contribution.", "bullets": ["'You held the team together.'", "Appreciating positivity."]}
    },
    "Achievement": {
        "s3_profile": {"text": "Primary motivator: Achievement. Loves progress, clarity, and winning. Wants to know the score.", "bullets": ["Goal-oriented.", "Loves metrics.", "Frustrated by ambiguity."]},
        "s4_motivating": {"text": "Set clear goals. Define 'success'. Give autonomy to reach the target.", "bullets": ["Use checklists.", "Set weekly wins."]},
        "s6_support": {"text": "Remove blockers. Protect their time. Be decisive.", "bullets": ["Clarify expectations.", "Eliminate red tape."]},
        "s7_thriving": {"text": "Engines of productivity.", "bullets": ["High volume.", "Meeting deadlines.", "Organized."]},
        "s10_celebrate": {"text": "Celebrate the win.", "bullets": ["'You said you'd do it, and you did.'", "Recognizing reliability."]}
    }
}

# (C) SUPERVISOR CLASH MATRIX
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {"tension": "Bulldozer vs. Doormat", "psychology": "Utility vs. Affirmation", "watch_fors": ["Silent withdrawal", "Director interrupting"], "intervention_steps": ["Pre-Frame Empathy", "Translate Feelings to Data", "Listen First"], "scripts": {"To Director": "Stop solving, start listening.", "To Encourager": "Brevity is not anger.", "Joint": "Task vs. Team balance."}},
        "Facilitator": {"tension": "Gas vs. Brake", "psychology": "Stagnation vs. Error", "watch_fors": ["Email commands", "Indecision"], "intervention_steps": ["Define Clock", "Define Veto", "Debrief"], "scripts": {"To Director": "Force is compliance.", "To Facilitator": "Silence is agreement.", "Joint": "Set a timer."}},
        "Tracker": {"tension": "Vision vs. Obstacle", "psychology": "Intuition vs. Handbook", "watch_fors": ["Quoting policy", "Bypassing"], "intervention_steps": ["Clarify Roles", "Yes If", "Risk Acceptance"], "scripts": {"To Director": "They protect you.", "To Tracker": "Start with solution.", "Joint": "Destination vs. Brakes."}},
        "Director": {"tension": "King vs. King", "psychology": "Dominance", "watch_fors": ["Interruptions", "Debates"], "intervention_steps": ["Separate Lanes", "Truce", "Commit"], "scripts": {"To Director": "Right vs Effective", "Joint": "Stop fighting for wheel"}}
    },
    "Encourager": {
        "Director": {"tension": "Sensitivity Gap", "psychology": "External vs Internal Validation", "watch_fors": ["Apologizing", "Avoiding meetings"], "intervention_steps": ["Headline First", "Explain Why", "Scheduled Venting"], "scripts": {"To Encourager": "Translate feelings to risk.", "To Director": "Kindness buys speed.", "Joint": "Timeline vs Plan."}},
        "Facilitator": {"tension": "Polite Stagnation", "psychology": "Rejection vs Unfairness", "watch_fors": ["Endless meetings", "Passive language"], "intervention_steps": ["Name Fear", "Assign Bad Guy", "Script It"], "scripts": {"To Encourager": "Feelings vs Program.", "Joint": "Who delivers news?"}},
        "Tracker": {"tension": "Rigidity vs Flow", "psychology": "Connection vs Consistency", "watch_fors": ["Secret deals", "Policing"], "intervention_steps": ["Why of Rules", "Why of Exceptions", "Hybrid"], "scripts": {"To Encourager": "Bending rules hurts team.", "To Tracker": "Connect then correct."}},
        "Encourager": {"tension": "Echo Chamber", "psychology": "Emotional Contagion", "watch_fors": ["Venting", "Us vs Them"], "intervention_steps": ["5 Min Rule", "Pivot", "External Data"], "scripts": {"Joint": "Challenge each other."}}
    },
    "Facilitator": {
        "Director": {"tension": "Steamroll", "psychology": "External vs Internal Processing", "watch_fors": ["Silence", "Assumed agreement"], "intervention_steps": ["Interrupt", "Pre-Meeting", "Frame Risk"], "scripts": {"To Director": "Too fast.", "To Facilitator": "Speak up."}},
        "Tracker": {"tension": "Details Loop", "psychology": "Horizontal vs Vertical Scope", "watch_fors": ["Email chains", "Overtime"], "intervention_steps": ["Concept First", "Detail Second", "Parking Lot"], "scripts": {"To Tracker": "30k view.", "To Facilitator": "Testing idea."}},
        "Encourager": {"tension": "Fairness vs Feelings", "psychology": "System vs Person", "watch_fors": ["Exceptions", "Inequity"], "intervention_steps": ["Validate Intent", "Explain Inequity", "Standard"], "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart."}}
    },
    "Tracker": {
        "Director": {"tension": "Micromanagement", "psychology": "Verification vs Competence", "watch_fors": ["Corrections", "Avoidance"], "intervention_steps": ["Pick Battles", "Sandbox", "Solution First"], "scripts": {"To Director": "Compliance.", "To Tracker": "Stop spellchecking."}},
        "Encourager": {"tension": "Rules vs Relationship", "psychology": "Safety Mismatch", "watch_fors": ["Public correction", "Resentment"], "intervention_steps": ["Connect First", "Explain Why", "Effectiveness"], "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect."}},
        "Facilitator": {"tension": "Details vs Concepts", "psychology": "Checklist vs Conversation", "watch_fors": ["Frustration", "Confusion"], "intervention_steps": ["Self-Check", "Operationalize", "Collaborate"], "scripts": {"To Tracker": "Alignment is deliverable.", "To Facilitator": "Define to-do."}}
    }
}
# Fallback
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {"tension": "Perspective difference", "psychology": "Priorities", "watch_fors": [], "intervention_steps": ["Listen", "Align"], "scripts": {"Joint": "Align"}}

# (D) CAREER PATHWAYS
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {"shift": "Doing -> Enabling", "why": "If you fix everything, team learns nothing.", "conversation": "Sit on your hands. Success is team confidence.", "assignment_setup": "Lead shift from office.", "assignment_task": "Verbal direction only.", "success_indicators": "Clear verbal commands.", "red_flags": "Running out to fix it."},
        "Program Supervisor": {"shift": "Command -> Influence", "why": "Can't order peers.", "conversation": "Slow down to build relationships.", "assignment_setup": "Peer project.", "assignment_task": "Cross-dept interview.", "success_indicators": "Incorporated feedback.", "red_flags": "100% own idea."},
        "Manager": {"shift": "Tactical -> Strategic", "why": "Prevent fires.", "conversation": "Reliance on systems.", "assignment_setup": "Strategic plan.", "assignment_task": "Data/Budget projection.", "success_indicators": "Systems thinking.", "red_flags": "Last minute."}
    },
    "Encourager": {
        "Shift Supervisor": {"shift": "Friend -> Guardian", "why": "Accountability is kindness.", "conversation": "Be a guardian of the standard.", "assignment_setup": "Policy reset.", "assignment_task": "Lead accountability meeting.", "success_indicators": "No apologies.", "red_flags": "Joking."},
        "Program Supervisor": {"shift": "Vibe -> Structure", "why": "Structure protects.", "conversation": "Master boring parts.", "assignment_setup": "Audit.", "assignment_task": "Present data.", "success_indicators": "Accurate.", "red_flags": "Delegating."},
        "Manager": {"shift": "Caregiver -> Director", "why": "Weight too heavy.", "conversation": "Set boundaries.", "assignment_setup": "Resource conflict.", "assignment_task": "Deliver No.", "success_indicators": "Holding line.", "red_flags": "Caving."}
    },
    "Facilitator": {
        "Shift Supervisor": {"shift": "Peer -> Decider", "why": "Consensus isn't safe.", "conversation": "Make 51% decision.", "assignment_setup": "Crisis drill.", "assignment_task": "Immediate calls.", "success_indicators": "Direct commands.", "red_flags": "Seeking consensus."},
        "Program Supervisor": {"shift": "Mediator -> Visionary", "why": "Lead from front.", "conversation": "Inject vision.", "assignment_setup": "Culture initiative.", "assignment_task": "Present as direction.", "success_indicators": "Declarative.", "red_flags": "Asking permission."},
        "Manager": {"shift": "Process -> Outcome", "why": "Fairness stalls.", "conversation": "Outcome over comfort.", "assignment_setup": "Unpopular policy.", "assignment_task": "Implement.", "success_indicators": "On time.", "red_flags": "Delays."}
    },
    "Tracker": {
        "Shift Supervisor": {"shift": "Executor -> Overseer", "why": "Micromanagement burns.", "conversation": "Trust team.", "assignment_setup": "Hands-off day.", "assignment_task": "Supervise verbally.", "success_indicators": "Hands in pockets.", "red_flags": "Grabbing pen."},
        "Program Supervisor": {"shift": "Black/White -> Gray", "why": "Rules don't cover all.", "conversation": "Develop intuition.", "assignment_setup": "Complex complaint.", "assignment_task": "Principle decision.", "success_indicators": "Sensible exception.", "red_flags": "Freezing."},
        "Manager": {"shift": "Compliance -> Culture", "why": "Efficiency breaks culture.", "conversation": "Invest in feelings.", "assignment_setup": "Retention.", "assignment_task": "Relationships.", "success_indicators": "Non-work chats.", "red_flags": "Checklist morale."}
    }
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

# --- ON-SCREEN DISPLAY FUNCTION ---
def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])
    
    st.markdown("---")
    st.markdown(f"### 📘 Supervisory Guide: {name}")
    st.markdown(f"**Role:** {role} | **Profile:** {p_comm} × {p_mot}")
    st.divider()
    
    st.subheader(f"1. Communication Profile: {p_comm}")
    st.write(c['s1_profile']['text'])
    for b in c['s1_profile']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("2. Supervising Their Communication")
    st.write(c['s2_supervising']['text'])
    for b in c['s2_supervising']['bullets']: st.markdown(f"- {b}")
    
    st.subheader(f"3. Motivation Profile: {p_mot}")
    st.write(m['s3_profile']['text'])
    for b in m['s3_profile']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("4. Motivating This Staff Member")
    st.write(m['s4_motivating']['text'])
    for b in m['s4_motivating']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("5. Integrated Leadership Profile")
    comm_snippet = c['s1_profile']['text'].split(".")[1]
    motiv_snippet = m['s3_profile']['text'].split(".")[1] if len(m['s3_profile']['text'].split('.')) > 2 else m['s3_profile']['text']
    integrated_text = f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. {comm_snippet} At the same time, {motiv_snippet} This combination creates a unique leadership style: they will pursue their goal of {p_mot} using the tools of a {p_comm}. When these align, they are unstoppable. When they conflict, frustration mounts quickly."
    st.write(integrated_text)
    
    st.subheader("6. How You Can Best Support Them")
    st.write(m['s6_support']['text'])
    for b in m['s6_support']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("7. What They Look Like When Thriving")
    st.write(m['s7_thriving']['text'])
    for b in m['s7_thriving']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("8. What They Look Like When Struggling")
    st.write(c['s8_struggling']['text'])
    for b in c['s8_struggling']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("9. Supervisory Interventions")
    st.write("When this staff member is struggling, use these targeted interventions:")
    interventions = [
        f"Validate their Motivation ({p_mot}) before correcting behavior.",
        f"Address the Stress Response: Gently point out if they are becoming {c['s8_struggling']['bullets'][0].lower()}.",
        "Re-align Expectations: Ensure they know exactly what success looks like in this specific situation.",
        "Check for Burnout: Are they over-functioning in their style?"
    ]
    for i in interventions: st.markdown(f"- {i}")
    
    st.subheader("10. What You Should Celebrate")
    st.write(m['s10_celebrate']['text'])
    for b in m['s10_celebrate']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("11. Coaching Questions")
    for q in c['s11_coaching']: st.markdown(f"- {q}")
    
    st.subheader("12. Helping Them Prepare for Advancement")
    st.write(c['s12_advancement']['text'])
    for b in c['s12_advancement']['bullets']: st.markdown(f"- {b}")

# --- PDF GENERATOR ---
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

    add_section(f"1. Communication: {p_comm}", c['s1_profile']['text'], c['s1_profile']['bullets'])
    add_section("2. Supervising Their Communication", c['s2_supervising']['text'], c['s2_supervising']['bullets'])
    add_section(f"3. Motivation: {p_mot}", m['s3_profile']['text'], m['s3_profile']['bullets'])
    add_section("4. Motivating Them", m['s4_motivating']['text'], m['s4_motivating']['bullets'])
    
    comm_snippet = c['s1_profile']['text'].split(".")[1]
    motiv_snippet = m['s3_profile']['text'].split(".")[1] if len(m['s3_profile']['text'].split('.')) > 2 else m['s3_profile']['text']
    integrated_text = f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. {comm_snippet} At the same time, {motiv_snippet} This combination creates a unique leadership style: they will pursue their goal of {p_mot} using the tools of a {p_comm}. When these align, they are unstoppable. When they conflict, frustration mounts quickly."
    add_section("5. Integrated Leadership Profile", integrated_text)
    
    add_section("6. Best Support", m['s6_support']['text'], m['s6_support']['bullets'])
    add_section("7. Thriving Signs", "Look for:", m['s7_thriving']['bullets'])
    add_section("8. Struggling Signs", "Look for:", c['s8_struggling']['bullets'])
    
    intervention_text = f"When struggling, validate {p_mot} first. Watch for {c['s8_struggling']['bullets'][0].lower()}."
    add_section("9. Interventions", intervention_text, ["Validate Motivation", "Address Stress", "Re-align Expectations"])
    
    add_section("10. Celebrate", m['s10_celebrate']['text'], m['s10_celebrate']['bullets'])
    add_section("11. Coaching Questions", "Ask these:", c['s11_coaching'])
    add_section("12. Advancement", c['s12_advancement']['text'], c['s12_advancement']['bullets'])
    
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

# --- NAVIGATION BUTTONS ---
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
                    display_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                st.button("Reset", on_click=reset_t1)
    with sub2:
        with st.form("manual"):
            c1,c2 = st.columns(2)
            mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
            mpc = c1.selectbox("Comm", COMM_TRAITS.keys()); mpm = c2.selectbox("Motiv", ["Growth", "Purpose", "Connection", "Achievement"])
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
        p1 = c1.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1")
        p2 = c2.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            s1, s2 = d1['p_comm'], d2['p_comm']
            
            st.divider()
            st.subheader(f"{s1} (Sup) vs. {s2} (Staff)")
            
            if s1 in SUPERVISOR_CLASH_MATRIX and s2 in SUPERVISOR_CLASH_MATRIX[s1]:
                clash = SUPERVISOR_CLASH_MATRIX[s1][s2]
                with st.expander("🔍 **Psychological Deep Dive**", expanded=True):
                    st.markdown(f"**The Dynamic:** {clash['tension']}")
                    st.markdown(f"**Psychology:** {clash['psychology']}")
                    st.markdown("---")
                    st.markdown("**🚩 Warning Signs:**")
                    for w in clash['watch_fors']: st.markdown(f"- {w}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("##### 🛠️ 3-Phase Protocol")
                    for i in clash['intervention_steps']: st.info(i)
                with c_b:
                    st.markdown("##### 🗣️ Scripts")
                    st.success(f"**To Them:** \"{clash['scripts'].get('To '+s2, '...')}\"")
                    st.info(f"**Joint:** \"{clash['scripts'].get('Joint', '...')}\"")
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
                        if 'supervisor_focus' in path:
                            st.warning(f"**Watch For:** {path['supervisor_focus']}")
                with c_b:
                    with st.container(border=True):
                        st.markdown("##### ✅ Assignment")
                        st.write(f"**Setup:** {path['assignment_setup']}")
                        st.write(f"**Task:** {path['assignment_task']}")
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flags:** {path['red_flags']}")
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
