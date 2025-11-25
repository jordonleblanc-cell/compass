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
    # Defaults to 'elmcrest2025' if secret not set
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

        div[data-testid="column"] .stButton button {{
            background-color: var(--card-bg); color: var(--text-main) !important; border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 140px; display: flex; flex-direction: column;
            align-items: flex-start; justify-content: center; padding: 20px; white-space: pre-wrap; text-align: left; transition: all 0.2s;
        }}
        div[data-testid="column"] .stButton button:hover {{
            transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); border-color: var(--primary); color: var(--primary) !important;
        }}
        
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

# --- 4. CONTENT DICTIONARIES (FULL RICH CONTENT) ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# (A) TEAM CULTURE GUIDE
TEAM_CULTURE_GUIDE = {
    "Director": {
        "title": "The 'Action' Culture",
        "impact_analysis": "**What it feels like:** This unit operates like a high-stakes trading floor. The energy is intense, fast, and results-oriented. Decisions are made quickly, often by the loudest voice. Competence is the primary currency of trust.\n\n**The Good:** You will rarely miss a deadline. Crises are handled with military precision. Productivity is high.\n**The Bad:** You risk 'Burnout by Urgency.' Quiet staff members will be steamrolled and stop contributing. You may solve the wrong problems very quickly because no one paused to ask 'Why?'.",
        "management_strategy": "**Your Role: The 'Governor'.** Your team has a heavy gas pedal; you must be the brake and the steering wheel.\n* **Slow them down:** Do not reward speed for speed's sake. Praise thoroughness.\n* **Protect the minority:** Actively solicit the opinion of the quietest person in the room.\n* **Enforce breaks:** This culture treats exhaustion as a badge of honor. You must mandate rest.",
        "meeting_protocol": "1. **The Devil's Advocate Rule:** Assign one person per meeting to specifically challenge the speed of the decision. Ask: 'What happens if we wait 24 hours?'\n2. **Forced Silence:** Implement a '2-minute silence' after a proposal is made to allow internal processors time to think before the Directors dominate the verbal space.\n3. **The 'Who' Check:** End every meeting by asking, 'Who might feel hurt or left out by this decision?'"
    },
    "Encourager": {
        "title": "The 'Family' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a family gathering. There is laughter, food, and deep personal connection. People feel safe, seen, and cared for. Staff retention is often high because people don't want to leave their friends.\n\n**The Good:** High psychological safety and trust. Staff support each other through personal crises. Resilience in hard times.\n**The Bad:** The 'Nice Guy Trap.' Bad behavior is tolerated because no one wants to be 'mean.' Accountability is viewed as aggression. Decisions are made based on what makes people happy, not what is effective.",
        "management_strategy": "**Your Role: The 'Bad Guy'.** They have enough warmth; they need you to provide the spine.\n* **Normalize Conflict:** Teach them that disagreement is not disrespect.\n* **Separate Friends from Work:** Remind them that 'liking' someone doesn't mean letting them slide on safety protocols.\n* **Focus on the 'Who':** Frame accountability as 'protecting the team' rather than 'punishing the individual.'",
        "meeting_protocol": "1. **The 'Blockers' Agenda:** Start meetings with 'What is broken?' instead of 'How are we doing?'. Force negative feedback into the open.\n2. **Data-Driven Reviews:** Use dashboards to review performance. It depersonalizes the feedback. 'The chart says we are late' is easier for an Encourager to hear than 'You are late.'\n3. **Time-Box Venting:** Allow exactly 10 minutes for feelings/venting at the start, then physically set a timer to pivot to tasks.",
        "team_building": "Potlucks, appreciation circles, storytelling. Focus on connection and shared history."
    },
    "Facilitator": {
        "title": "The 'Consensus' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a democratic senate. Every voice is heard, every angle is considered, and fairness is the ultimate goal. There is a deep sense of stability and equity.\n\n**The Good:** High buy-in. Few errors because decisions are vetted thoroughly. An equitable environment where no one is left behind.\n**The Bad:** Analysis Paralysis. This team struggles to move during a crisis. They will form a committee to decide where to order lunch. They risk 'death by meeting,' where the process of deciding becomes more important than the decision itself.",
        "management_strategy": "**Your Role: The 'Closer'.** They have enough inputs; they need you to force the output.\n* **Set the Deadline:** Do not ask 'When should we decide?'. Tell them 'We decide on Tuesday.'\n* **Define 'Consensus':** Teach them that consensus means 'I can live with it,' not 'I love it.'\n* **Authorize Imperfection:** Give them permission to make mistakes. They are terrified of being wrong.",
        "meeting_protocol": "1. **The 'Disagree & Commit' Rule:** Establish a norm that once a decision is made, debate ends. No meeting-after-the-meeting.\n2. **Hard Deadlines:** Set the decision date BEFORE the discussion starts.\n3. **Opt-Out Rights:** Allow people to skip meetings if they trust the group to decide. Reduce the committee bloat.",
        "team_building": "Collaborative problem solving (e.g., Desert Survival). Activities where the group must agree to win."
    },
    "Tracker": {
        "title": "The 'Safety' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a well-oiled machine or a laboratory. Everything has a place, a time, and a label. Documentation is impeccable. Risks are anticipated and managed before they happen.\n\n**The Good:** Safety and reliability. You never have to worry about an audit. Shifts run like clockwork.\n**The Bad:** Rigidity. This team struggles when the 'Plan' fails. They may quote the policy manual while a kid is in crisis, prioritizing the rule over the relationship. Innovation is low because 'we've always done it this way.'",
        "management_strategy": "**Your Role: The 'Visionary'.** They are looking at their feet (the steps); you must make them look at the horizon (the goal).\n* **Challenge the Rule:** Regularly ask 'Does this rule still serve us?'\n* **Humanize the Data:** Remind them that every number on the spreadsheet represents a human being.\n* **Encourage Flex:** Reward them for adapting to a crisis, not just for following the script.",
        "meeting_protocol": "1. **The 'Intent' Explain:** Trackers must explain the *intent* behind a rule (e.g., 'Safety') not just the rule itself.\n2. **Pilot Programs:** Frame innovation as a 'Controlled Experiment.' Trackers hate chaos, but they love data collection. Let them 'test' a new idea to gather data.\n3. **The Human Impact:** End every meeting by asking: 'How will this decision make the youth/staff *feel*?'",
        "team_building": "Logic puzzles, building projects (Lego), process improvement workshops. Avoid 'vague' creative tasks."
    }
}

# (B) MISSING VOICE GUIDE
MISSING_VOICE_GUIDE = {
    "Director": {"risk": "**Risk of Stagnation.** Without Director energy, this team may talk in circles, create perfect plans that never launch, or prioritize comfort over results. You risk becoming a 'social club' that doesn't achieve outcomes.", "fix": "**Supervisor Strategy:** You must be the driver. Set hard deadlines. Interrupt circular conversations. Be the 'bad guy' who demands output. End every meeting with 'Who is doing What by When?'"},
    "Encourager": {"risk": "**Risk of Burnout & Coldness.** Without Encourager energy, this team becomes transactional. Staff feel like cogs in a machine. You will likely see high turnover because no one feels 'seen' or 'cared for' personally.", "fix": "**Supervisor Strategy:** You must prioritize the 'Human Element'. Start meetings with personal check-ins. Schedule fun (yes, mandatory fun). Manually recognize effort, not just results. Send handwritten notes."},
    "Facilitator": {"risk": "**Risk of Tunnel Vision.** Without Facilitator energy, the loudest voices will dominate. You will have 'Blind spots' because no one is stepping back to ask 'What about X?'. Dissent will be crushed or ignored.", "fix": "**Supervisor Strategy:** You must slow down the room. Use 'Round Robin' turn-taking so quiet people speak. Ask 'Who disagrees?' before moving on. Actively solicit the minority opinion."},
    "Tracker": {"risk": "**Risk of Chaos & Liability.** Without Tracker energy, details will slip. Documentation will fail. Safety risks will be missed until they become accidents. The program will feel chaotic and reactive.", "fix": "**Supervisor Strategy:** You must be the auditor. Bring the checklist. Don't assume it's done; check it. Create visual trackers on the wall. Ask 'What is the backup plan?' repeatedly."}
}

# (C) MOTIVATION GAP GUIDE
MOTIVATION_GAP_GUIDE = {
    "Growth": "Your team wants to learn, but the role might be repetitive. **Fix:** Rotate responsibilities. Create 'Specialist' roles.",
    "Purpose": "Your team wants to save the world, but the paperwork is heavy. **Fix:** Connect every form to a client outcome. Tell 'Mission Stories'.",
    "Connection": "Your team wants to be a family, but the work is isolated. **Fix:** Create 'Buddy Systems' for shifts. Eat lunch together.",
    "Achievement": "Your team wants to win, but the goals are vague. **Fix:** Create a scoreboard. Track daily wins. Gamify the mundane tasks."
}

# (D) SUPERVISOR CLASH MATRIX (COMPLETE - NO PLACEHOLDERS)
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "Bulldozer vs. Doormat", 
            "psychology": "You value **Utility** (usefulness); they value **Affirmation** (feeling valued). When you skip the human element, they feel unsafe and withdraw.",
            "watch_fors": ["Silent withdrawal", "Director interrupting", "Complaints of 'meanness'"],
            "intervention_steps": ["**1. Pre-Frame:** 'Efficiency without Empathy is Inefficiency.'", "**2. Translate:** Feelings are data.", "**3. The Deal:** Listen for 5 mins before solving."],
            "scripts": {"To Director": "Stop solving, start listening.", "To Encourager": "Brevity is not anger.", "Joint": "Director speaks Task; Encourager speaks Team."}
        },
        "Facilitator": {
            "tension": "Gas vs. Brake", 
            "psychology": "Risk Perception: You fear **Stagnation**; they fear **Error**. You feel obstructed; they feel steamrolled.",
            "watch_fors": ["Email commands", "Indecision", "Eye rolling"],
            "intervention_steps": ["**1. Define Clock:** Set deadline.", "**2. Veto:** Give 'Red Flag' right.", "**3. Debrief:** Did we move too fast?"],
            "scripts": {"To Director": "Force is compliance.", "To Facilitator": "Silence is agreement.", "Joint": "Set a timer."}
        },
        "Tracker": {
            "tension": "Vision vs. Obstacle", 
            "psychology": "Authority: You trust **Intuition**; they trust **Handbook**. You feel blocked; they feel reckless.",
            "watch_fors": ["Quoting policy", "Bypassing tracker"],
            "intervention_steps": ["**1. Clarify Roles:** What vs How.", "**2. Yes If:** Coach 'Yes, if...'", "**3. Risk Acceptance:** Explicitly accept risk."],
            "scripts": {"To Director": "They protect you.", "To Tracker": "Start with solution.", "Joint": "Destination vs. Brakes."}
        },
        "Director": {
            "tension": "King vs. King", 
            "psychology": "Dominance battle. Both define safety as Control.",
            "watch_fors": ["Interruptions", "Public debates"],
            "intervention_steps": ["**1. Separate Lanes.**", "**2. The Truce.**", "**3. Disagree & Commit.**"],
            "scripts": {"To Director": "Right vs Effective", "Joint": "Stop fighting for the wheel"}
        }
    },
    "Encourager": {
        "Director": {
            "tension": "Sensitivity Gap", 
            "psychology": "Validation: You need **External**; they rely on **Internal**. You feel attacked by brevity.",
            "watch_fors": ["Apologizing", "Avoiding meetings"], 
            "intervention_steps": ["**1. Headline First.**", "**2. Explain Why.**", "**3. Scheduled Venting.**"],
            "scripts": {"To Encourager": "Translate feelings to risk.", "To Director": "Kindness buys speed.", "Joint": "Timeline vs Plan."}
        },
        "Facilitator": {
            "tension": "Polite Stagnation", 
            "psychology": "Conflict Avoidance: Rejection vs Unfairness. Decisions stall.",
            "watch_fors": ["Endless meetings", "Passive language"], 
            "intervention_steps": ["**1. Name Fear.**", "**2. Assign Bad Guy.**", "**3. Script It.**"],
            "scripts": {"To Encourager": "Protecting feelings hurts program.", "Joint": "Who delivers the news?"}
        },
        "Tracker": {
            "tension": "Rigidity vs Flow", 
            "psychology": "Safety Source: Connection vs Consistency.",
            "watch_fors": ["Secret deals", "Public policing"], 
            "intervention_steps": ["**1. Why of Rules.**", "**2. Why of Exceptions.**", "**3. Hybrid.**"],
            "scripts": {"To Encourager": "Bending rules makes Tracker the bad guy.", "To Tracker": "Right policy, cold delivery."}
        },
        "Encourager": {
            "tension": "Echo Chamber", 
            "psychology": "Emotional Contagion. High warmth, low accountability.",
            "watch_fors": ["Venting", "Us vs Them"], 
            "intervention_steps": ["**1. 5-Min Rule.**", "**2. Pivot to Action.**", "**3. External Data.**"],
            "scripts": {"Joint": "Challenge each other."}
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "Steamroll", 
            "psychology": "Processing: External vs Internal. You feel silenced.",
            "watch_fors": ["Silence", "Assumed agreement"], 
            "intervention_steps": ["**1. Interrupt.**", "**2. Pre-Meeting.**", "**3. Frame Risk.**"],
            "scripts": {"To Director": "Moving too fast.", "To Facilitator": "Speak up."}
        },
        "Tracker": {
            "tension": "Details Loop", 
            "psychology": "Scope: Horizontal vs Vertical. Ideas die in the 'how-to'.",
            "watch_fors": ["Email chains", "Overtime"], 
            "intervention_steps": ["**1. Concept First.**", "**2. Detail Second.**", "**3. Parking Lot.**"],
            "scripts": {"To Tracker": "30k view.", "To Facilitator": "Testing idea."}
        },
        "Encourager": {
            "tension": "Fairness vs Feelings", 
            "psychology": "Focus: System vs Person. Inequity risks.",
            "watch_fors": ["Exceptions", "Inequity"], 
            "intervention_steps": ["**1. Validate Intent.**", "**2. Explain Inequity.**", "**3. Standard.**"],
            "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart."}
        },
        "Facilitator": {
            "tension": "The Committee",
            "psychology": "Diffusion of Responsibility. No one wants to drive.",
            "watch_fors": ["Conversations go in circles.", "Everyone feels good but nothing gets done."],
            "intervention_steps": ["**1. Designate Driver.**", "**2. Time Limit.**", "**3. Vote.**"],
            "scripts": {"Joint": "We are spinning. Who is deciding?"}
        }
    },
    "Tracker": {
        "Director": {
            "tension": "Micromanagement", 
            "psychology": "Trust: Verification vs Competence. You ask questions; they feel distrusted.",
            "watch_fors": ["Corrections", "Avoidance"], 
            "intervention_steps": ["**1. Pick Battles.**", "**2. Sandbox.**", "**3. Solution First.**"],
            "scripts": {"To Director": "Compliance safety.", "To Tracker": "Stop correcting spelling."}
        },
        "Encourager": {
            "tension": "Rules vs Relationship", 
            "psychology": "Priorities mismatch. You see chaos; they see care.",
            "watch_fors": ["Public correction", "Resentment"], 
            "intervention_steps": ["**1. Connect First.**", "**2. Explain Why.**", "**3. Effectiveness.**"],
            "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect."}
        },
        "Facilitator": {
            "tension": "Details vs Concepts", 
            "psychology": "Output: Checklist vs Conversation.",
            "watch_fors": ["Frustration", "Confusion"], 
            "intervention_steps": ["**1. Self-Check.**", "**2. Operationalize.**", "**3. Collaborate.**"],
            "scripts": {"To Tracker": "Alignment is deliverable.", "To Facilitator": "Define to-do."}
        },
        "Tracker": {
            "tension": "The Audit",
            "psychology": "Perfectionism loop. Missing the forest for the trees.",
            "watch_fors": ["Arguments over semantics.", "Email wars.", "Lost purpose."],
            "intervention_steps": ["**1. Zoom Out.**", "**2. 'Good Enough'.**", "**3. Client Outcome.**"],
            "scripts": {"Joint": "Does this change the result?"}
        }
    }
}

# (E) CAREER PATHWAYS (Deep Dive)
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {"shift": "Doing -> Enabling", "why": "Directors act fast. As a Shift Sup, if you fix everything, your team learns nothing.", "conversation": "Sit on your hands. Success is team confidence.", "assignment_setup": "Lead shift from office.", "assignment_task": "Verbal direction only.", "success_indicators": "Clear verbal commands.", "red_flags": "Running out to fix it.", "debrief_questions": ["How hard was it to not jump in?", "Who stepped up?"], "supervisor_focus": "Hero Mode"},
        "Program Supervisor": {"shift": "Command -> Influence", "why": "Can't order peers. Need political capital.", "conversation": "Slow down to build relationships.", "assignment_setup": "Peer project.", "assignment_task": "Cross-dept interview.", "success_indicators": "Incorporated feedback.", "red_flags": "100% own idea.", "debrief_questions": ["What did you learn about their constraints?"], "supervisor_focus": "Patience"},
        "Manager": {"shift": "Tactical -> Strategic", "why": "Prevent fires.", "conversation": "Reliance on systems.", "assignment_setup": "Strategic plan.", "assignment_task": "Data/Budget projection.", "success_indicators": "Systems thinking.", "red_flags": "Last minute.", "debrief_questions": ["What data did you use?"], "supervisor_focus": "Horizon check"}
    },
    "Encourager": {
        "Shift Supervisor": {"shift": "Friend -> Guardian", "why": "Accountability is kindness.", "conversation": "Be a guardian of the standard.", "assignment_setup": "Policy reset.", "assignment_task": "Lead accountability meeting.", "success_indicators": "No apologies.", "red_flags": "Joking.", "debrief_questions": ["Did you feel the urge to apologize?"], "supervisor_focus": "Apology Language"},
        "Program Supervisor": {"shift": "Vibe -> Structure", "why": "Structure protects.", "conversation": "Master boring parts.", "assignment_setup": "Audit.", "assignment_task": "Present data.", "success_indicators": "Accurate.", "red_flags": "Delegating.", "debrief_questions": ["How does this data help the team?"], "supervisor_focus": "Organization"},
        "Manager": {"shift": "Caregiver -> Director", "why": "Weight too heavy.", "conversation": "Set boundaries.", "assignment_setup": "Resource conflict.", "assignment_task": "Deliver No.", "success_indicators": "Holding line.", "red_flags": "Caving.", "debrief_questions": ["How did you handle their disappointment?"], "supervisor_focus": "Burnout"}
    },
    "Facilitator": {
        "Shift Supervisor": {"shift": "Peer -> Decider", "why": "Consensus isn't safe.", "conversation": "Make 51% decision.", "assignment_setup": "Crisis drill.", "assignment_task": "Immediate calls.", "success_indicators": "Direct commands.", "red_flags": "Seeking consensus.", "debrief_questions": ["Where did you hesitate?"], "supervisor_focus": "Speed"},
        "Program Supervisor": {"shift": "Mediator -> Visionary", "why": "Lead from front.", "conversation": "Inject vision.", "assignment_setup": "Culture initiative.", "assignment_task": "Present as direction.", "success_indicators": "Declarative.", "red_flags": "Asking permission.", "debrief_questions": ["Did you ask for permission or support?"], "supervisor_focus": "The Buffer"},
        "Manager": {"shift": "Process -> Outcome", "why": "Fairness stalls.", "conversation": "Outcome over comfort.", "assignment_setup": "Unpopular policy.", "assignment_task": "Implement.", "success_indicators": "On time.", "red_flags": "Delays.", "debrief_questions": ["How did you handle the complaints?"], "supervisor_focus": "Conflict Tolerance"}
    },
    "Tracker": {
        "Shift Supervisor": {"shift": "Executor -> Overseer", "why": "Micromanagement burns.", "conversation": "Trust team.", "assignment_setup": "Hands-off day.", "assignment_task": "Supervise verbally.", "success_indicators": "Hands in pockets.", "red_flags": "Grabbing pen.", "debrief_questions": ["What did they do differently than you would have?"], "supervisor_focus": "Micromanagement"},
        "Program Supervisor": {"shift": "Black/White -> Gray", "why": "Rules don't cover all.", "conversation": "Develop intuition.", "assignment_setup": "Complex complaint.", "assignment_task": "Principle decision.", "success_indicators": "Sensible exception.", "red_flags": "Freezing.", "debrief_questions": ["What principle guided your decision?"], "supervisor_focus": "Rigidity"},
        "Manager": {"shift": "Compliance -> Culture", "why": "Efficiency breaks culture.", "conversation": "Invest in feelings.", "assignment_setup": "Retention.", "assignment_task": "Relationships.", "success_indicators": "Non-work chats.", "red_flags": "Checklist morale.", "debrief_questions": ["What did you learn about them personally?"], "supervisor_focus": "Human Element"}
    }
}

# (F) PDF PROFILES
COMM_PROFILES = {
    "Director": {"s1_profile":{"text":"Leads with clarity...","bullets":["Efficiency"]},"s2_supervising":{"text":"Be direct...","bullets":["Autonomy"]},"s8_struggling":{"text":"Becomes dominating...","bullets":["Steamrolling"]},"s11_coaching":["Risk of speed?","Who haven't we heard?"],"s12_advancement":{"text":"Shift to Influence","bullets":["Patience"]}},
    "Encourager": {"s1_profile":{"text":"Leads with warmth...","bullets":["Harmony"]},"s2_supervising":{"text":"Connect first...","bullets":["Validation"]},"s8_struggling":{"text":"Avoids conflict...","bullets":["Venting"]},"s11_coaching":["Hard truths?","Boundaries?"],"s12_advancement":{"text":"Master structure","bullets":["Operations"]}},
    "Facilitator": {"s1_profile":{"text":"Leads by listening...","bullets":["Consensus"]},"s2_supervising":{"text":"Give time...","bullets":["Advance notice"]},"s8_struggling":{"text":"Analysis paralysis...","bullets":["Indecision"]},"s11_coaching":["Cost of waiting?","Decision?"],"s12_advancement":{"text":"Executive presence","bullets":["Decisiveness"]}},
    "Tracker": {"s1_profile":{"text":"Leads with details...","bullets":["Accuracy"]},"s2_supervising":{"text":"Provide clarity...","bullets":["Specifics"]},"s8_struggling":{"text":"Rigid...","bullets":["Micromanagement"]},"s11_coaching":["Safety impact?","Big picture?"],"s12_advancement":{"text":"Strategy","bullets":["Delegation"]}}
}
MOTIVATION_PROFILES = {
    "Growth": {"s3_profile":{"text":"Driven by progress...","bullets":["Challenge"]},"s4_motivating":{"text":"Feed curiosity...","bullets":["Problems to solve"]},"s6_support":{"text":"Sponsor training...","bullets":["Mentorship"]},"s7_thriving":{"text":"Innovators...","bullets":["Proactive"]},"s10_celebrate":{"text":"Skill growth...","bullets":["Adaptability"]}},
    "Purpose": {"s3_profile":{"text":"Driven by meaning...","bullets":["Mission"]},"s4_motivating":{"text":"Connect to why...","bullets":["Ethics"]},"s6_support":{"text":"Validate passion...","bullets":["Space for concerns"]},"s7_thriving":{"text":"Advocates...","bullets":["Integrity"]},"s10_celebrate":{"text":"Impact...","bullets":["Stories"]}},
    "Connection": {"s3_profile":{"text":"Driven by belonging...","bullets":["Team"]},"s4_motivating":{"text":"Prioritize cohesion...","bullets":["Bonding"]},"s6_support":{"text":"No isolation...","bullets":["Check-ins"]},"s7_thriving":{"text":"Morale boosters...","bullets":["Rapport"]},"s10_celebrate":{"text":"Culture...","bullets":["Support"]}},
    "Achievement": {"s3_profile":{"text":"Driven by goals...","bullets":["Winning"]},"s4_motivating":{"text":"Clear metrics...","bullets":["Checklists"]},"s6_support":{"text":"Remove blockers...","bullets":["Decisive"]},"s7_thriving":{"text":"Engines...","bullets":["Volume"]},"s10_celebrate":{"text":"Reliability...","bullets":["Output"]}}
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
    integrated = f"Leads with {p_comm} traits to achieve {p_mot} goals. When aligned, they are unstoppable. Conflict between speed ({p_comm}) and needs ({p_mot}) causes stress."
    add_section("5. Integrated Leadership Profile", integrated)
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
    st.subheader("5. Integrated Leadership Profile"); st.write(f"Leads with {p_comm} traits to achieve {p_mot} goals.")
    st.subheader("6. How You Can Best Support Them"); st.write(m['s6_support']['text'])
    for b in m['s6_support']['bullets']: st.markdown(f"- {b}")
    st.subheader("7. What They Look Like When Thriving"); st.write(m['s7_thriving']['text'])
    for b in m['s7_thriving']['bullets']: st.markdown(f"- {b}")
    st.subheader("8. What They Look Like When Struggling"); st.write(c['s8_struggling']['text'])
    for b in c['s8_struggling']['bullets']: st.markdown(f"- {b}")
    st.subheader("9. Supervisory Interventions"); st.write("Validate Motivation. Address Stress. Re-align Expectations.")
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
                missing_styles = set(COMM_TRAITS.keys()) - present_styles
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
                    if dom_mot == "Connection":
                        st.warning("This team is driven by **Relationships**. If you manage them with cold metrics and checklists, they will disengage. You must lead with warmth.")
                    elif dom_mot == "Achievement":
                        st.warning("This team is driven by **Winning**. If goals are vague or accomplishments aren't recognized, they will leave. You must lead with clear scoreboards.")
                    elif dom_mot == "Growth":
                        st.warning("This team is driven by **Learning**. If they feel stagnant, they will quit. You must provide new challenges and training.")
                    elif dom_mot == "Purpose":
                        st.warning("This team is driven by **Mission**. If you focus only on policy compliance, they will rebel. You must connect every task to the 'Why'.")
            
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
        c1, c2, c3 = st.columns(3)
        top_comm = df['p_comm'].mode()[0]; top_mot = df['p_mot'].mode()[0]
        c1.metric("Dominant Style", top_comm); c2.metric("Top Driver", top_mot); c3.metric("Total Staff", len(df))
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
        with c_b: 
            if 'role' in df.columns: st.plotly_chart(px.histogram(df, x="role", color="p_comm", title="Leadership Pipeline", color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
    else: st.warning("No data available.")
