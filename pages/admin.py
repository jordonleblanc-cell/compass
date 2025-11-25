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

# --- NAVIGATION HELPER ---
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
            color: #0f172a;
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
        .stChatMessage {{ background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. RICH CONTENT DICTIONARIES (RESTORED) ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# (A) CONFLICT SCRIPTS (Deep Dive)
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "Bulldozer vs. Doormat", "psychology": "Utility vs. Affirmation", "watch_fors": ["Silent withdrawal", "Director interrupting"], 
            "intervention_steps": ["**1. Pre-Frame:** 'Efficiency without Empathy is Inefficiency.'", "**2. Translate:** Feelings are data.", "**3. The Deal:** Listen for 5 mins before solving."],
            "scripts": {"To Director": "Stop solving, start listening.", "To Encourager": "My brevity is not anger.", "Joint": "Director speaks Task; Encourager speaks Team."}
        },
        "Facilitator": {
            "tension": "Gas vs. Brake", "psychology": "Stagnation vs. Error", "watch_fors": ["Email commands", "Indecision"], 
            "intervention_steps": ["**1. Define Clock:** Set deadline.", "**2. Veto:** Give them a Red Flag right.", "**3. Debrief:** Did we move too fast?"],
            "scripts": {"To Director": "Force is compliance.", "To Facilitator": "Silence is agreement.", "Joint": "Set a timer."}
        },
        "Tracker": {
            "tension": "Vision vs. Obstacle", "psychology": "Intuition vs. Handbook", "watch_fors": ["Quoting policy", "Bypassing tracker"], 
            "intervention_steps": ["**1. Clarify Roles:** What vs How.", "**2. Yes If:** Coach 'Yes, if...'", "**3. Risk Acceptance:** Explicitly accept risk."],
            "scripts": {"To Director": "They protect you.", "To Tracker": "Start with solution.", "Joint": "Destination vs. Brakes."}
        },
        "Director": {
            "tension": "King vs. King", "psychology": "Dominance", "watch_fors": ["Interruptions", "Debates"], 
            "intervention_steps": ["**1. Separate Lanes:** Distinct domains.", "**2. The Truce:** Acknowledge power struggle.", "**3. Disagree & Commit.**"],
            "scripts": {"To Director": "Fighting to be right vs effective.", "Joint": "Stop fighting for the wheel"}
        }
    },
    "Encourager": {
        "Director": {
            "tension": "Sensitivity Gap", "psychology": "External vs Internal Validation", "watch_fors": ["Apologizing", "Avoiding meetings"], 
            "intervention_steps": ["**1. Headline First.**", "**2. Explain Why.**", "**3. Scheduled Venting.**"],
            "scripts": {"To Encourager": "Translate feelings to risk.", "To Director": "Kindness buys speed.", "Joint": "Timeline vs Plan."}
        },
        "Facilitator": {
            "tension": "Polite Stagnation", "psychology": "Rejection vs Unfairness", "watch_fors": ["Endless meetings", "Passive language"], 
            "intervention_steps": ["**1. Name Fear.**", "**2. Assign Bad Guy.**", "**3. Script It.**"],
            "scripts": {"To Encourager": "Protecting feelings hurts program.", "Joint": "Who delivers the news?"}
        },
        "Tracker": {
            "tension": "Rigidity vs Flow", "psychology": "Connection vs Consistency", "watch_fors": ["Secret deals", "Policing"], 
            "intervention_steps": ["**1. Why of Rules.**", "**2. Why of Exceptions.**", "**3. Hybrid.**"],
            "scripts": {"To Encourager": "Bending rules makes Tracker the bad guy.", "To Tracker": "Connect then correct."}
        },
        "Encourager": {
            "tension": "Echo Chamber", "psychology": "Emotional Contagion", "watch_fors": ["Venting", "Us vs Them"], 
            "intervention_steps": ["**1. 5-Min Rule.**", "**2. Pivot to Action.**", "**3. External Data.**"],
            "scripts": {"Joint": "Challenge each other."}
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "Steamroll", "psychology": "External vs Internal Processing", "watch_fors": ["Silence", "Assumed agreement"], 
            "intervention_steps": ["**1. Interrupt.**", "**2. Pre-Meeting.**", "**3. Frame Risk.**"],
            "scripts": {"To Director": "Moving too fast.", "To Facilitator": "Speak up."}
        },
        "Tracker": {
            "tension": "Details Loop", "psychology": "Horizontal vs Vertical Scope", "watch_fors": ["Email chains", "Overtime"], 
            "intervention_steps": ["**1. Concept First.**", "**2. Detail Second.**", "**3. Parking Lot.**"],
            "scripts": {"To Tracker": "30k view.", "To Facilitator": "Testing idea."}
        },
        "Encourager": {
            "tension": "Fairness vs Feelings", "psychology": "System vs Person", "watch_fors": ["Exceptions", "Inequity"], 
            "intervention_steps": ["**1. Validate Intent.**", "**2. Explain Inequity.**", "**3. Standard.**"],
            "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart."}
        }
    },
    "Tracker": {
        "Director": {
            "tension": "Micromanagement", "psychology": "Verification vs Competence", "watch_fors": ["Corrections", "Avoidance"], 
            "intervention_steps": ["**1. Pick Battles.**", "**2. Sandbox.**", "**3. Solution First.**"],
            "scripts": {"To Director": "Compliance safety.", "To Tracker": "Stop correcting spelling."}
        },
        "Encourager": {
            "tension": "Rules vs Relationship", "psychology": "Priorities mismatch", "watch_fors": ["Public correction", "Resentment"], 
            "intervention_steps": ["**1. Connect First.**", "**2. Explain Why.**", "**3. Effectiveness.**"],
            "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect."}
        },
        "Facilitator": {
            "tension": "Details vs Concepts", "psychology": "Output mismatch", "watch_fors": ["Frustration", "Confusion"], 
            "intervention_steps": ["**1. Self-Check.**", "**2. Operationalize.**", "**3. Collaborate.**"],
            "scripts": {"To Tracker": "Alignment is deliverable.", "To Facilitator": "Define to-do."}
        }
    }
}
# Fallback
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {"tension": "Perspective difference", "psychology": "Priorities", "watch_fors": [], "intervention_steps": ["Listen", "Align"], "scripts": {"Joint": "Align"}}

# (B) CAREER PATHWAYS (Deep Dive)
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

# (C) PDF PROFILES (FULL RICH CONTENT RESTORED)
COMM_PROFILES = {
    "Director": {
        "s1_profile": {"text": "This staff member communicates primarily as a Director. They lead with clarity, structure, and urgency. In the complex environment of residential care, they act as a stabilizing force during chaos, naturally stepping up to fill leadership vacuums. They process information quickly and prefer to move to action immediately, often becoming impatient with long deliberations or ambiguous processes.", "bullets": ["Prioritizes efficiency and results over process.", "Speaks in headlines; brief and to the point.", "Comfortable making unpopular decisions if they believe it solves the problem.", "Views competence as the primary language of trust."]},
        "s2_supervising": {"text": "Supervising a Director requires a high-trust, low-friction approach. They respect leaders who are direct, competent, and concise. They will likely disengage if they feel micromanaged or if meetings feel like 'talking in circles' without resolution. Your goal is to be a remover of obstacles, allowing them to execute.", "bullets": ["Be concise: Lead with the bottom line, then fill in details.", "Grant autonomy: Define the 'what' clearly, but let them own the 'how'.", "Expect pushback: They often view debate as healthy problem-solving, not insubordination.", "Focus on outcomes: Measure their success by results, not just hours or methods."]},
        "s8_struggling": {"text": "Under stress, the Director's greatest strength (decisiveness) becomes their greatest liability (domination). When they feel a loss of control or perceive incompetence around them, they may double down on command-and-control tactics, alienating their team and reducing psychological safety.", "bullets": ["Steamrolling quieter voices in meetings.", "Becoming visibly irritable or sarcastic with 'slow' processes.", "Making unilateral decisions without consulting stakeholders.", "Sacrificing long-term relationships for short-term compliance."]},
        "s11_coaching": ["What is the risk of moving this fast? Who might we be leaving behind?", "How can you frame this directive so the team feels supported rather than just commanded?", "I noticed you made that call quickly. Walk me through the alternatives you considered.", "Who haven't we heard from yet? What perspective might the quietest person in the room have?", "If you had to achieve this result without giving a single order, how would you do it?", "How is your current pace affecting the morale of your newest staff members?", "What is the difference between being 'right' and being 'effective' in this situation?", "How can you use your authority to empower someone else to lead this?", "You value competence. How are you teaching others to be competent rather than just fixing it for them?", "What emotional wake are you leaving behind you right now?"],
        "s12_advancement": {"text": "For a Director to advance to senior leadership, they must shift from 'Command' to 'Influence'. They are likely already good at execution; their gap is political capital and consensus building. They need to learn that slowing down to bring people along is not a waste of time, but a strategic investment in sustainability.", "bullets": ["Assign cross-departmental projects where they have no direct authority and must use persuasion.", "Challenge them to mentor a 'Facilitator' type, forcing them to value a different style.", "Require them to present 3 options for a decision rather than just their favorite one.", "Focus development on 'soft skills': active listening, validation, and patience."]}
    },
    "Encourager": {
        "s1_profile": {"text": "This staff member communicates primarily as an Encourager. They act as the emotional glue of the team, leading with warmth, optimism, and high emotional intelligence. They are naturally attuned to the 'vibe' of the unit and will prioritize the well-being of staff and youth above almost everything else. They are persuasive, engaging, and often the person others go to for venting or support.", "bullets": ["Prioritizes relationships and harmony over efficiency.", "Highly empathetic; feels the emotions of the room.", "Communicates through stories and connection.", "Views emotional safety as the prerequisite for work."]},
        "s2_supervising": {"text": "Supervising an Encourager requires a relational investment. If you jump straight to business without checking in on them as a person, they may feel undervalued or commoditized. They need to know you care about them. Feedback must be delivered carefully, as they often struggle to separate professional critique from personal rejection.", "bullets": ["Connect first: Spend 5 minutes on rapport before tackling the agenda.", "Validate the invisible work: Acknowledge the emotional labor they do for the team.", "Frame feedback as 'growth': Show how changing a behavior helps them help others.", "Provide structure: They may need help organizing their ideas and time."]},
        "s8_struggling": {"text": "Under stress, the Encourager's desire for harmony can lead to conflict avoidance and a lack of accountability. They may struggle to hold boundaries with youth or staff because they don't want to be 'mean.' This can result in a chaotic environment where rules are applied inconsistently based on feelings.", "bullets": ["Avoiding necessary hard conversations.", "Venting or gossiping as a way to manage stress.", "Disorganization or missed deadlines due to social distractions.", "Taking youth behaviors personally or becoming emotionally enmeshed."]},
        "s11_coaching": ["How can you deliver this hard truth while still remaining kind?", "Are we prioritizing popularity over effectiveness in this situation?", "What boundaries do you need to set right now to protect your own energy?", "If you avoid this conflict today, what is the cost to the team next week?", "How does holding this standard actually create safety for the youth?", "I know you want to help, but are you enabling them or empowering them?", "What is the data telling us, regardless of how we feel about it?", "How can you separate your personal worth from this professional outcome?", "You are carrying a lot of the team's emotions. Who is carrying yours?", "What is one thing you need to say 'No' to this week?"],
        "s12_advancement": {"text": "For an Encourager to advance, they must master the 'Business' side of care. Their high EQ is a massive asset, but it must be backed by operational reliability. They need to learn that clarity and accountability are forms of kindness. Their growth lies in becoming a leader who is respected for their competence, not just liked for their personality.", "bullets": ["Assign responsibility for a compliance audit or budget management.", "Role-play disciplinary conversations until they can deliver them without apologizing.", "Challenge them to organize a project using a project management tool, not just conversation.", "Focus development on: Time management, objective decision-making, and professional boundaries."]}
    },
    "Facilitator": {
        "s1_profile": {"text": "This staff member communicates primarily as a Facilitator. They are the steady, calming presence in the room who seeks to ensure every voice is heard. They value fairness, process, and consensus. They rarely rush to judgment, preferring to gather all perspectives before deciding. They are excellent at de-escalating conflict and preventing rash decisions.", "bullets": ["Prioritizes fairness and inclusion over speed.", "Great listener; asks questions rather than giving orders.", "Dislikes conflict and sudden change.", "Views the 'process' as just as important as the 'result'."]},
        "s2_supervising": {"text": "Supervising a Facilitator requires patience. Do not pressure them for an immediate answer in the hallway; give them time to think and process. They often have brilliant insights into team dynamics but will not share them unless explicitly invited. You must create a safe space for them to voice dissenting opinions.", "bullets": ["Give advance notice: Send agendas early so they can prepare.", "Invite their voice: Ask 'What are you seeing that I am missing?'", "Validate fairness: Explain how your decisions consider the whole group.", "Push for closure: Gently help them land the plane when they are over-processing."]},
        "s8_struggling": {"text": "Under stress, the Facilitator can fall into 'Analysis Paralysis,' delaying critical decisions in a futile search for total consensus. They may become passive-aggressive or silent, holding tension internally rather than addressing it. They risk becoming a bottleneck because they are afraid of making a decision that might upset someone.", "bullets": ["Stalling projects to 'get more feedback'.", "Saying 'it's fine' when they clearly disagree.", "Letting poor performance slide to avoid rocking the boat.", "Being perceived by the team as indecisive or weak in a crisis."]},
        "s11_coaching": ["If you had to make a decision right now with only 80% of the info, what would it be?", "What is the cost to the team of waiting for total consensus?", "Where are you holding tension for the team that you need to release?", "Who specifically are you trying not to upset with this decision?", "How can you support the team's direction even if you don't fully agree?", "What is the 'least worst' option we have right now?", "You are listening to everyone else. What do *you* think?", "Is this a moment for collaboration or a moment for direction?", "How can we make this process fair without making it slow?", "What is the risk of doing nothing?"],
        "s12_advancement": {"text": "For a Facilitator to advance, they must develop 'Executive Presence.' They need to learn to be decisive even when the room is split. Leadership often involves making 51/49 calls where half the people are unhappy. Their growth is shifting from a mediator (who stands in the middle) to a visionary (who stands in front).", "bullets": ["Assign them to lead a crisis response or a time-sensitive project.", "Challenge them to make a decision without calling a meeting first.", "Practice 'Disagree and Commit' strategies.", "Focus development on: Assertiveness, crisis command, and strategic vision."]}
    },
    "Tracker": {
        "s1_profile": {"text": "This staff member communicates primarily as a Tracker. They lead with data, details, and systems. They act as the guardian of quality and safety, noticing risks and gaps that others miss. They value logic, consistency, and accuracy. To them, the policy manual is not a suggestion; it is the roadmap to safety.", "bullets": ["Prioritizes accuracy and safety over speed.", "Detailed-oriented; loves checklists and plans.", "Skeptical of 'big ideas' without a plan.", "Views rules as the method to protect staff and youth."]},
        "s2_supervising": {"text": "Supervising a Tracker requires clarity and consistency. Ambiguity is their enemy. If you change direction frequently without explanation, they will lose trust in your leadership. Provide them with clear expectations, written instructions, and the 'why' behind decisions. They respond well to competence and reliability.", "bullets": ["Be specific: Avoid vague instructions like 'make it better'.", "Respect the system: Don't disrupt their workflow without cause.", "Show the logic: Explain the data or reasoning behind changes.", "Follow through: If you say you will do it, you must do it."]},
        "s8_struggling": {"text": "Under stress, the Tracker can become rigid, critical, and perfectionistic. They may get stuck in the weeds, nitpicking minor documentation errors while the house is on fire emotionally. They can come across as cold or uncaring to youth because they prioritize the rule over the relationship.", "bullets": ["Refusing to adapt to a crisis because 'it's not the procedure'.", "Correcting staff publicly on minor errors.", "Becoming cynical or blocking new initiatives.", "Overwhelming others with excessive details or emails."]},
        "s11_coaching": ["Does this specific detail change the safety outcome of the situation?", "How can we meet the standard here while keeping the relationship warm?", "What is the big picture goal, and are we sacrificing it for a minor procedural win?", "If we follow the rule perfectly but lose the kid's trust, did we succeed?", "What is the 'Good Enough' version of this task for right now?", "How can you delegate this task without hovering over them?", "I appreciate the data. What is the human story behind these numbers?", "Are you trying to be right, or are you trying to be helpful?", "How can we adapt the system to fit the current reality?", "What is the risk of being too rigid in this moment?"],
        "s12_advancement": {"text": "For a Tracker to advance, they must shift from 'Compliance' to 'Strategy'. They need to learn to tolerate ambiguity and navigate the gray areas of leadership where no policy exists. They must learn to trust people, not just systems. Their growth involves delegating the details so they can focus on the horizon.", "bullets": ["Assign them a role that requires 'gray area' judgment calls (e.g., family negotiations).", "Challenge them to launch a project at 80% readiness ('Iterative design').", "Force them to delegate a complex task and only check the final result.", "Focus development on: Strategic thinking, adaptability, and people development."]}
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "s3_profile": {"text": "Primary motivator: Growth. Energized by development, learning, and mastery. Bored by repetition.", "bullets": ["Seeks feedback and constructive criticism.", "Bored by status quo; loves 'pilots' and new initiatives.", "Values mentorship and training opportunities."]},
        "s4_motivating": {"text": "To motivate them, you must feed their curiosity. Frame tasks as 'challenges' or 'learning opportunities.' Give them problems to solve, not just lists to execute. If they feel they are stagnating, they will check out.", "bullets": ["Assign 'stretch' projects that require new skills.", "Ask 'What are you learning right now?' in supervision.", "Connect their daily grunt work to their long-term career goals."]},
        "s6_support": {"text": "Support them by being a sponsor. Advocate for them to attend trainings or shadow other departments. Ensure they have a clear developmental pathway. If you can't offer a promotion yet, offer a new responsibility that builds their resume.", "bullets": ["Sponsor them for external certifications.", "Delegate tasks that 'level them up'.", "Be transparent about the skills they need for the next level."]},
        "s7_thriving": {"text": "When thriving, they are the innovators of the team.", "bullets": ["Proactive questions about the 'why' and 'how'.", "Volunteering for difficult tasks.", "Mentoring peers on new skills.", "High energy during change initiatives."]},
        "s10_celebrate": {"text": "Celebrate their adaptability and skill acquisition. Do not just praise the result; praise the growth it took to get there.", "bullets": ["'I saw how you learned that new system—great work.'", "'You've really grown in your de-escalation skills.'", "Publicly acknowledging their professional development."]}
    },
    "Purpose": {
        "s3_profile": {"text": "Primary motivator: Purpose. This staff member is driven by meaning, alignment, and values. They need to know that their work matters and makes a tangible difference in the lives of youth. They will endure difficult conditions if they believe the cause is just.", "bullets": ["Deeply committed to the mission and the youth.", "Sensitive to perceived injustice or lack of care.", "Values 'The Why' above 'The What'."]},
        "s4_motivating": {"text": "To motivate them, connect every directive back to the mission. Don't just say 'Fill out the log'; say 'This log helps us advocate for the youth in court.' Be transparent about the ethical reasoning behind decisions.", "bullets": ["Start meetings with a 'mission moment' or success story.", "Invite their input on decisions that impact client care.", "Explain the 'why' behind unpopular policies."]},
        "s6_support": {"text": "Support them by validating their passion. When they raise concerns, listen seriously—they are often the conscience of the team. Help them navigate the bureaucracy without losing their heart. Protect them from cynicism.", "bullets": ["Create space for them to voice ethical concerns.", "Remind them of the long-term impact they are having.", "Shield them from unnecessary 'corporate' noise."]},
        "s7_thriving": {"text": "When thriving, they are the passionate advocates of the program.", "bullets": ["Going the extra mile for a youth.", "High integrity and ethical standards.", "Inspiring peers with their dedication.", "Resilient in the face of client trauma."]},
        "s10_celebrate": {"text": "Celebrate their impact. Use specific stories of how they changed a life. Public praise should focus on their character and dedication.", "bullets": ["'That youth trusts you because you showed up.'", "'Thank you for keeping us focused on what matters.'", "Sharing a specific success story involving a youth."]}
    },
    "Connection": {
        "s3_profile": {"text": "Primary motivator: Connection. This staff member is energized by relationships, belonging, and team cohesion. They work for the 'who', not just the 'what'. If the team feels like a family, they will work tirelessly. If they feel isolated, they will wither.", "bullets": ["Values harmony, collaboration, and inclusion.", "Highly sensitive to team conflict or cliques.", "Energized by group work and shared success."]},
        "s4_motivating": {"text": "To motivate them, prioritize the team dynamic. Use 'We' language. Creating opportunities for them to collaborate with others rather than working solo. Recognize the team's success, not just individuals.", "bullets": ["Facilitate team lunches or bonding moments.", "Assign them to work in pairs or groups.", "Check in on them personally before talking business."]},
        "s6_support": {"text": "Support them by ensuring they are not isolated. Be a warm, accessible presence. If there is conflict on the team, intervene quickly, as it drains them faster than anyone else.", "bullets": ["Be available for quick check-ins.", "Repair relational ruptures immediately.", "Ensure they feel 'part of the inner circle'."]},
        "s7_thriving": {"text": "When thriving, they are the morale boosters of the unit.", "bullets": ["Collaborative and supportive of peers.", "Creating a warm, welcoming atmosphere.", "High morale and laughter.", "Strong rapport with difficult staff and youth."]},
        "s10_celebrate": {"text": "Celebrate their contribution to the culture. Acknowledge how they support others.", "bullets": ["'You really held the team together today.'", "'Thanks for checking in on [New Staff Member].'", "Publicly appreciating their positivity."]}
    },
    "Achievement": {
        "s3_profile": {"text": "Primary motivator: Achievement. This staff member loves progress, clarity, and winning. They want to know the score. They feel satisfied when they can check items off a list and see concrete evidence of their hard work.", "bullets": ["Goal-oriented and competitive (with self or others).", "Loves data, metrics, and completed checklists.", "Frustrated by ambiguity or moving goalposts."]},
        "s4_motivating": {"text": "To motivate them, set clear, measurable goals. Define exactly what 'success' looks like. Give them autonomy to figure out the path, but be rigid about the deadline and the standard. Use visual trackers.", "bullets": ["Use checklists or dashboards to show progress.", "Set daily or weekly 'wins'.", "Give them autonomy to crush the goal their way."]},
        "s6_support": {"text": "Support them by removing blockers. They hate inefficiency. Protect their time from useless meetings. Give them the resources they need to execute. Be decisive.", "bullets": ["Clarify expectations in writing.", "Eliminate red tape where possible.", "Provide the right tools/resources immediately."]},
        "s7_thriving": {"text": "When thriving, they are the engines of productivity.", "bullets": ["High volume of high-quality work.", "Meeting deadlines consistently.", "Organized and efficient.", "Driving projects to completion."]},
        "s10_celebrate": {"text": "Celebrate the win. Acknowledge the output and the reliability.", "bullets": ["'You said you'd do it, and you did it.'", "'Great job hitting that deadline.'", "Recognizing their reliability and high standards."]}
    }
}

# --- 5. HELPER FUNCTIONS ---

def clean_text(text):
    if not text: return ""
    text = str(text)
    replacements = {'\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2013': '-', '—': '-'}
    for k, v in replacements.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

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
    
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(8)
    
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True); pdf.ln(2)
        pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
        pdf.multi_cell(0, 5, clean_text(body))
        if bullets:
            for b in bullets: pdf.cell(5, 5, "-", 0, 0); pdf.multi_cell(0, 5, clean_text(b))
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

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])
    st.markdown("---"); st.markdown(f"### 📘 Supervisory Guide: {name}"); st.divider()
    st.subheader(f"1. Communication Profile: {p_comm}"); st.write(c['s1_profile']['text'])
    for b in c['s1_profile']['bullets']: st.markdown(f"- {b}")
    st.subheader("2. Supervising Their Communication"); st.write(c['s2_supervising']['text'])
    for b in c['s2_supervising']['bullets']: st.markdown(f"- {b}")
    st.subheader(f"3. Motivation Profile: {p_mot}"); st.write(m['s3_profile']['text'])
    for b in m['s3_profile']['bullets']: st.markdown(f"- {b}")
    st.subheader("4. Motivating This Staff Member"); st.write(m['s4_motivating']['text'])
    for b in m['s4_motivating']['bullets']: st.markdown(f"- {b}")
    
    st.subheader("5. Integrated Leadership Profile")
    comm_snippet = c['s1_profile']['text'].split(".")[1]
    motiv_snippet = m['s3_profile']['text'].split(".")[1] if len(m['s3_profile']['text'].split('.')) > 2 else m['s3_profile']['text']
    integrated_text = f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. {comm_snippet} At the same time, {motiv_snippet} This combination creates a unique leadership style: they will pursue their goal of {p_mot} using the tools of a {p_comm}."
    st.write(integrated_text)
    
    st.subheader("6. How You Can Best Support Them"); st.write(m['s6_support']['text'])
    for b in m['s6_support']['bullets']: st.markdown(f"- {b}")
    st.subheader("7. What They Look Like When Thriving"); st.write(m['s7_thriving']['text'])
    for b in m['s7_thriving']['bullets']: st.markdown(f"- {b}")
    st.subheader("8. What They Look Like When Struggling"); st.write(c['s8_struggling']['text'])
    for b in c['s8_struggling']['bullets']: st.markdown(f"- {b}")
    st.subheader("9. Supervisory Interventions"); st.write(f"When struggling, validate {p_mot} first.")
    st.markdown(f"- Validate Motivation ({p_mot})"); st.markdown("- Address Stress"); st.markdown("- Re-align Expectations")
    st.subheader("10. What You Should Celebrate"); st.write(m['s10_celebrate']['text'])
    for b in m['s10_celebrate']['bullets']: st.markdown(f"- {b}")
    st.subheader("11. Coaching Questions"); 
    for q in c['s11_coaching']: st.markdown(f"- {q}")
    st.subheader("12. Helping Them Prepare for Advancement"); st.write(c['s12_advancement']['text'])
    for b in c['s12_advancement']['bullets']: st.markdown(f"- {b}")

# --- 6. MAIN APP LOGIC ---
staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# Reset Helpers
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- HERO SECTION ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Elmcrest Leadership Intelligence</div>
    <div class="hero-subtitle">Your command center for staff development. Select a tool below to begin.</div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
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
                    st.markdown("**🚩 Watch For:**")
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
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flags:** {path['red_flags']}")
            st.button("Reset", key="reset_t4", on_click=reset_t4)

elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        top_comm = df['p_comm'].mode()[0]; top_mot = df['p_mot'].mode()[0]
        c1.metric("Dominant Style", top_comm); c2.metric("Top Driver", top_mot); c3.metric("Total Staff", len(df))
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
        with c_b: 
            if 'role' in df.columns: st.plotly_chart(px.histogram(df, x="role", color="p_comm", title="Leadership Pipeline", color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
    else: st.warning("No data available.")
