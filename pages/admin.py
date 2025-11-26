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

# --- 4. SECURITY: PASSWORD CHECK ---
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
        <div style="position: absolute; top: 20px; left: 20px;">
            <a href="/" target="_self" class="back-link">← Back</a>
        </div>
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

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# --- 5. DATA DICTIONARIES (DEFINED AT TOP LEVEL) ---

# (D) CONFLICT MATRIX (MOVED UP TO FIX NAME ERROR)
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "Bulldozer vs. Doormat", 
            "psychology": "This conflict stems from a fundamental mismatch in **Currency**. You value **Utility** (is this useful?), while they value **Affirmation** (am I valued?). When you skip the 'human connection' to get straight to work, the Encourager feels dehumanized and unsafe. You interpret their subsequent withdrawal as incompetence or lack of focus, but it is actually a stress response to your intensity. They withdraw to protect themselves.",
            "watch_fors": ["The Encourager stops contributing in meetings (silent withdrawal).", "You start interrupting or finishing their sentences because they take too long.", "They complain to peers that you are 'mean', 'cold', or 'don't care'.", "You feel exhausted by their constant need for what you perceive as 'hand-holding'."],
            "intervention_steps": ["**1. Pre-Frame (Mindset):** Remind yourself: 'Efficiency without Empathy is Inefficiency.' If you break the relationship, the work stops. You must invest 5 minutes to save 5 hours of friction.", "**2. The Translate (Action):** In the meeting, translate their feelings into data. 'When they say they are stressed, they are giving me data about team risk.'", "**3. The Deal (Closing):** Explicitly agree to a protocol: You will listen for 5 minutes without solving, if they agree to move to action steps immediately after."],
            "scripts": {
                "To Director": "Stop solving, start listening. You are trying to fix the problem, but right now the relationship IS the problem.",
                "To Encourager": "My brevity is not anger; it is urgency. I value you, I am just stressed about the goal.",
                "Joint": "We speak different languages. Director speaks Task; Encourager speaks Team. Both are valid."
            }
        },
        "Facilitator": {
            "tension": "Gas vs. Brake",
            "psychology": "This conflict is about **Risk Perception**. You fear **Stagnation** (doing nothing); they fear **Error** (doing the wrong thing). You operate on 'Ready, Fire, Aim'; they operate on 'Ready, Aim, Aim...'. You feel slowed down and obstructed; they feel steamrolled and unsafe.",
            "watch_fors": ["You issue commands via email to avoid a meeting.", "They keep saying 'We need to talk about this' but never decide.", "You visibly roll your eyes when they ask for 'thoughts'.", "Decisions are made by you but passively resisted/ignored by the team."],
            "intervention_steps": ["**1. Define the Clock:** They need time; you need a deadline. Negotiate it upfront. 'We will discuss for 30 mins, then decide.'", "**2. Define the Veto:** Tell them they have a 'Red Flag' right. If they see a major risk, they can stop you. Otherwise, you drive.", "**3. The Debrief:** After the action, review: 'Did we move too fast? Or did we wait too long?' This builds trust for next time."],
            "scripts": {"To Director": "Force = Compliance, not Buy-in. If you push now, they will nod yes but do nothing.", "To Facilitator": "Silence = Agreement. If you disagree, you must speak up.", "Joint": "We have a pace mismatch. We are going to set a timer for discussion, then we decide."}
        },
        "Tracker": {
            "tension": "Vision vs. Obstacle",
            "psychology": "This is a clash of **Authority Sources**. You trust **Intuition** and results; they trust **The Handbook** and process. You say 'Make it happen'; they say 'But Regulation 14.B says...'. You feel they are the 'Department of No'; they feel you are a liability lawsuit waiting to happen.",
            "watch_fors": ["They quote policy numbers in arguments.", "You say 'Ask for forgiveness, not permission.'", "They hoard information or access to prove a point.", "You bypass them to get things done, creating compliance risks."],
            "intervention_steps": ["**1. Clarify Roles:** You own the 'What' (Destination). They own the 'How' (Safe Route).", "**2. The 'Yes, If' Rule:** Coach them to never say 'No'. Instead say: 'Yes, we can do that, *if* we sign this waiver/change this budget.'", "**3. Risk Acceptance:** You must explicitly state: 'I accept the risk of deviating from the standard here.' This relieves their anxiety."],
            "scripts": {"To Director": "They are protecting you from liability.", "To Tracker": "Start with the solution, not the problem.", "Joint": "Director sets destination; Tracker checks brakes."}
        },
        "Director": {
            "tension": "King vs. King",
            "psychology": "This is a pure **Dominance** struggle. Both of you define safety as **Control**. When the other person takes control, you feel unsafe or disrespected. The conversation becomes a debate about who is right rather than what is best.",
            "watch_fors": ["Interruptions and talking over each other.", "Public debates that feel like combat.", "Refusal to implement the other's idea.", "The team looking awkward while 'Mom and Dad fight'."],
            "intervention_steps": ["**1. Separate Lanes:** You cannot drive the same car. Give them distinct domains where they have total authority.", "**2. The Truce:** Acknowledge the power struggle explicitly. 'We are both fighting for the wheel.'", "**3. Disagree and Commit.** Once a decision is made by the final authority, the debate ends."],
            "scripts": {"To Director": "Fighting to be right vs effective.", "To Other": "Strip the tone.", "Joint": "Stop fighting for the wheel."}
        }
    },
    "Encourager": {
        "Director": {
            "tension": "Sensitivity Gap",
            "psychology": "Mismatch in **Validation Style**. You need **External** validation (words/affirmation); they rely on **Internal** validation (results). You feel personally attacked by their brevity. They feel annoyed by your 'fluff'. You over-explain to get validation; they tune out.",
            "watch_fors": ["You apologizing before asking for something.", "You venting to peers about how 'mean' they are.", "They avoid meetings with you because 'it takes too long'.", "You feeling exhausted/crying after supervision."],
            "intervention_steps": ["**1. The Headline:** Start with the conclusion, then the feelings. 'We need to fire Bob because he hurt the team.'", "**2. The 'Why':** Ask them to explain the *reason* for their speed, so you don't invent a story that they are angry.", "**3. Scheduled Venting.** Ask for 5 mins to process feelings, then promise to hard pivot to tasks."],
            "scripts": {"To Encourager": "Translate feelings to risk.", "To Director": "Kindness buys speed.", "Joint": "Timeline vs Plan."}
        },
        "Facilitator": {
            "tension": "Polite Stagnation",
            "psychology": "This is **Conflict Avoidance**. You fear **Rejection**; they fear **Unfairness**. You want to protect the individual; they want to be fair to the group. You both avoid conflict, so decisions stall indefinitely because neither wants to be the 'bad guy'.",
            "watch_fors": ["Endless meetings where everyone agrees but nothing changes.", "Problems being 'managed' rather than 'solved'.", "Using passive language: 'It would be nice if...' instead of 'You must...'.", "Resentment building because no one is leading."],
            "intervention_steps": ["**1. Name the Fear:** 'We are scared to upset [Person], so we are hurting the program.'", "**2. Assign the 'Bad Guy':** Supervisor acts as the heavy: 'Blame me. Say I ordered it.'", "**3. Script the Hard Conversation.** Don't let them ad-lib; write the script together."],
            "scripts": {"To Encourager": "Protecting feelings hurts program.", "Joint": "Who delivers the news?"}
        },
        "Tracker": {
            "tension": "Rigidity vs Flow",
            "psychology": "Mismatch in **Safety Source**. You find safety in **Connection**; they find safety in **Consistency**. You bend rules to help people; they enforce rules to protect people. They think you are unsafe; you think they are cold.",
            "watch_fors": ["You making 'secret deals' with staff/youth to bypass rules.", "They police you publicly.", "You feeling judged; them feeling undermined.", "Inconsistent application of consequences."],
            "intervention_steps": ["**1. The 'Why' of Rules.** Remind yourself that rules protect the most vulnerable youth by creating predictability.", "**2. The 'Why' of Exceptions.** Show them that rigid rules break rapport, which causes danger.", "**3. The Hybrid.** 'We follow the rule (Tracker), but we deliver it with maximum empathy (Encourager).'"],
            "scripts": {"To Encourager": "Bending rules makes Tracker the bad guy.", "To Tracker": "Right policy, cold delivery."}
        },
        "Encourager": {
            "tension": "Echo Chamber",
            "psychology": "This is **Emotional Contagion**. You amplify each other's feelings. Stress becomes shared panic. Joy becomes a party. There is no grounding force, leading to high warmth but low accountability.",
            "watch_fors": ["Supervision turning into a venting session.", "Lack of clear action items.", "Creating 'Us vs. Them' narratives about other departments.", "Ignoring metrics/data because 'we feel like we're doing good'."],
            "intervention_steps": ["**1. The 5-Minute Rule:** Only 5 minutes of venting allowed.", "**2. The Pivot:** 'I hear that is hard. What is the first step to fixing it?'", "**3. External Data:** Bring in a chart/checklist to force a reality check beyond feelings."],
            "scripts": {"To Encourager": "We are spinning.", "Joint": "Challenge each other."}
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "Steamroll",
            "psychology": "Mismatch in **Processing**. You process **Externally** (group talk). They process **Internally** (gut check). By the time you ask a question, they have already moved on. You feel disrespected and silenced.",
            "watch_fors": ["You staying silent in meetings then complaining later.", "They look bored while you talk.", "You asking 'Does everyone agree?' and them saying 'Moving on.'", "The team looking confused about who is in charge."],
            "intervention_steps": ["**1. Interrupt:** Learn to say 'Hold on'.", "**2. Pre-Meeting:** Brief them beforehand. 'I am going to ask for feedback on X. Please don't answer first.'", "**3. The Frame:** Frame process as 'Risk Management' (which Directors value) not 'Inclusion' (which they might not)."],
            "scripts": {"To Director": "Moving too fast.", "To Facilitator": "Speak up."}
        },
        "Tracker": {
            "tension": "Details Loop",
            "psychology": "Mismatch in **Scope**. You are **Horizontal** (scanning everyone). They are **Vertical** (drilling down). You want to talk about the *concept*; they want to talk about the *form*. You get bogged down in logistics before agreeing on the idea.",
            "watch_fors": ["Long email chains about minor details.", "Meetings running overtime.", "You feeling nitpicked; them feeling vague.", "Great ideas dying in the 'how-to' phase."],
            "intervention_steps": ["**1. Concept First.** 'We are not discussing the form yet. Do we agree on the goal?'", "**2. Detail Second.** 'Now that we agree, please build the checklist.'", "**3. The Parking Lot.** Park detailed questions until the end of the meeting."],
            "scripts": {"To Tracker": "30k view.", "To Facilitator": "Testing idea."}
        },
        "Encourager": {
            "tension": "Fairness vs Feelings",
            "psychology": "Mismatch in **Focus**. You focus on the **System** (Fairness); they focus on the **Person** (Feelings). You might struggle to rein them in when they over-function for a client, creating inequity in the program.",
            "watch_fors": ["They want an exception; you want a precedent.", "You feel they are playing favorites.", "They feel you are being too clinical."],
            "intervention_steps": ["**1. Validate Intent.** 'I see how much you care about [Youth]. Your heart is in the right place.'", "**2. Explain Inequity.** 'However, if we make a special exception for him, it creates unfairness for the other 10 kids.'", "**3. Return to Standard.** 'We need a solution that is fair to everyone.'"],
            "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart first."}
        },
        "Facilitator": {
            "tension": "The Committee",
            "psychology": "Diffusion of Responsibility. No one drives. Endless meetings. Great process, low output. You both listen, nod, and validate, but no one directs. The team feels heard but leaderless.",
            "watch_fors": ["Conversations go in circles.", "Everyone feels good but nothing gets done.", "Conflict is buried under politeness."],
            "intervention_steps": ["**1. Designate Driver.** 'I am facilitating; you are deciding.'", "**2. Time Limit.** Force a vote at 45 mins.", "**3. Vote.** Use a thumb vote to force positions."],
            "scripts": {"Joint": "We are spinning. Who is deciding?"}
        }
    },
    "Tracker": {
        "Director": {
            "tension": "Micromanagement",
            "psychology": "Mismatch in **Trust**. You trust **Verification**; they trust **Competence**. You verify by checking; they verify by doing. You see their broad strokes as reckless. You ask 10 questions; they get annoyed.",
            "watch_fors": ["You sending emails with 'Corrections'.", "They avoid you.", "You feeling anxious that 'it's all going to fall apart'.", "They withhold info so you don't 'slow them down'."],
            "intervention_steps": ["**1. Pick Battles.** Differentiate between 'Safety Critical' (Intervene) and 'Preference' (Let it go).", "**2. The Sandbox.** Give them a space where they can break things safely.", "**3. Solution-First.** Don't say 'We can't.' Say 'We can, IF we do X.'"],
            "scripts": {"To Director": "Compliance safety.", "To Tracker": "Stop correcting spelling."}
        },
        "Encourager": {
            "tension": "Rules vs Relationship",
            "psychology": "Mismatch in **Priorities**. You see their exceptions as chaos. They feel judged by your clipboard. You risk becoming the 'Principal' to their 'Cool Teacher'. They think you care more about the paperwork than the people.",
            "watch_fors": ["You correct them publicly; they shut down.", "You quote policy; they quote feelings.", "Resentment builds over 'nitpicking'."],
            "intervention_steps": ["**1. Connect Before Correct.** Did I say hello before I pointed out the error?", "**2. The 'Why':** Is this rule critical for safety? Explain that.", "**3. Effectiveness:** Am I being right or being effective?"],
            "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect."}
        },
        "Facilitator": {
            "tension": "Details vs Concepts",
            "psychology": "Mismatch in **Output**. You want a **Checklist**; they want a **Conversation**. You get frustrated when meetings end without a clear 'To-Do' list. They feel you are rushing the relational process.",
            "watch_fors": ["You check your watch while they talk.", "They feel you are transactional.", "You leave meetings confused about next steps."],
            "intervention_steps": ["**1. Self-Check.** Am I being too rigid? Sometimes the 'deliverable' is just alignment.", "**2. Operationalize.** I can help them turn their ideas into steps.", "**3. Collaborate.** Ask permission to capture next steps."],
            "scripts": {"To Tracker": "Alignment is deliverable.", "To Facilitator": "Define to-do."}
        },
        "Tracker": {
            "tension": "The Audit",
            "psychology": "Perfectionism loop. Missing the forest for the trees.",
            "watch_fors": ["Formatting wars", "Lost purpose"], 
            "intervention_steps": ["**1. Zoom Out.**", "**2. 'Good Enough'.**", "**3. Client Outcome.**"],
            "scripts": {"Joint": "Does this change the result?"}
        }
    }
}
# Fallback for robust lookup
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {"tension": "Perspective difference", "psychology": "Priorities", "watch_fors": [], "intervention_steps": ["Listen", "Align"], "scripts": {"Joint": "Align"}}

# (A) TEAM CULTURE GUIDE (EXPANDED)
TEAM_CULTURE_GUIDE = {
    "Director": {
        "title": "The 'Action' Culture",
        "impact_analysis": "**What it feels like:** This unit operates like a high-stakes trading floor. The energy is intense, fast, and results-oriented. Decisions are made quickly, often by the loudest voice. Competence is the primary currency of trust.\n\n**The Good:** You will rarely miss a deadline. Crises are handled with military precision. Productivity is high.\n**The Bad:** You risk 'Burnout by Urgency.' Quiet staff members will be steamrolled and stop contributing. You may solve the wrong problems very quickly because no one paused to ask 'Why?'.",
        "management_strategy": "**Your Role: The 'Governor'.** Your team has a heavy gas pedal; you must be the brake and the steering wheel.\n* **Slow them down:** Do not reward speed for speed's sake. Praise thoroughness.\n* **Protect the minority:** Actively solicit the opinion of the quietest person in the room.\n* **Enforce breaks:** This culture treats exhaustion as a badge of honor. You must mandate rest.",
        "meeting_protocol": "1. **The Devil's Advocate Rule:** Assign one person per meeting to specifically challenge the speed of the decision. Ask: 'What happens if we wait 24 hours?'\n2. **Forced Silence:** Implement a '2-minute silence' after a proposal is made to allow internal processors time to think before the Directors dominate the verbal space.\n3. **The 'Who' Check:** End every meeting by asking, 'Who might feel hurt or left out by this decision?'",
        "team_building": "Strategic games, escape rooms, competitions (with caution)."
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

# (B) MISSING VOICE GUIDE (EXPANDED)
MISSING_VOICE_GUIDE = {
    "Director": {"risk": "**Risk of Stagnation.** Without Director energy, this team may talk in circles, create perfect plans that never launch, or prioritize comfort over results. You risk becoming a 'social club' that doesn't achieve outcomes.", "fix": "**Supervisor Strategy:** You must be the driver. Set hard deadlines. Interrupt circular conversations. Be the 'bad guy' who demands output. End every meeting with 'Who is doing What by When?'"},
    "Encourager": {"risk": "**Risk of Burnout & Coldness.** Without Encourager energy, this team becomes transactional. Staff feel like cogs in a machine. You will likely see high turnover because no one feels 'seen' or 'cared for' personally.", "fix": "**Supervisor Strategy:** You must prioritize the 'Human Element'. Start meetings with personal check-ins. Schedule fun (yes, mandatory fun). Manually recognize effort, not just results. Send handwritten notes."},
    "Facilitator": {"risk": "**Risk of Tunnel Vision.** Without Facilitator energy, the loudest voices will dominate. You will have 'Blind spots' because no one is stepping back to ask 'What about X?'. Dissent will be crushed or ignored.", "fix": "**Supervisor Strategy:** You must slow down the room. Use 'Round Robin' turn-taking so quiet people speak. Ask 'Who disagrees?' before moving on. Actively solicit the minority opinion."},
    "Tracker": {"risk": "**Risk of Chaos & Liability.** Without Tracker energy, details will slip. Documentation will fail. Safety risks will be missed until they become accidents. The program will feel chaotic and reactive.", "fix": "**Supervisor Strategy:** You must be the auditor. Bring the checklist. Don't assume it's done; check it. Create visual trackers on the wall. Ask 'What is the backup plan?' repeatedly."}
}

# (C) MOTIVATION GAP GUIDE (EXPANDED)
MOTIVATION_GAP_GUIDE = {
    "Growth": {
        "title": "The Restless Team",
        "description": "This team is driven by progress, competence, and future potential. They view the job as a stepping stone. If they aren't learning, they are leaving.",
        "risk": "Boredom & Stagnation. If the work becomes repetitive without new challenges, they will disengage or find a new job that offers 'growth'.",
        "symptoms": "High turnover among top performers. Complaints about 'doing the same thing every day'. Disengagement during routine tasks.",
        "strategy": "**Feed the Beast.**\n* **Rotate Roles:** Don't let them do the same task for 6 months. Rotate 'Shift Lead', 'Safety Captain', etc.\n* **The 'Pilot' Frame:** Frame boring changes as 'Experiments' they get to lead and evaluate.\n* **Career Pathing:** Talk about their next job explicitly. 'Doing this well helps you get to [Goal].'"
    },
    "Purpose": {
        "title": "The Crusader Team",
        "description": "This team is driven by the mission, justice, and 'The Why'. They will endure hard conditions if they believe it matters. They rebel against anything that feels bureaucratic or heartless.",
        "risk": "Cynicism & Burnout. If they feel the agency cares more about liability/paperwork than the kids, they will become toxic/cynical defenders of the youth against management.",
        "symptoms": "Moral outrage at policy changes. Refusal to do paperwork ('It takes time away from kids'). Us vs. Them mentality with Admin.",
        "strategy": "**Connect the Dots.**\n* **Mission Moments:** Start every meeting with a client success story.\n* **Explain the Why:** Never give a raw order. Always link compliance to client advocacy. 'This form gets the kid funding.'\n* **Validate Passion:** When they push back, say 'I love that you care so much', then redirect."
    },
    "Connection": {
        "title": "The Relational Team",
        "description": "This team is driven by belonging, mutual support, and 'feeling' good. They work for each other. If the team is tight, they can handle anything.",
        "risk": "Cliques & Drama. If the relational glue fails (conflict) or if they feel isolated by management, productivity halts. They prioritize harmony over accountability.",
        "symptoms": "High interpersonal drama or gossip. Productivity drops when a specific friend is absent. Resistance to new staff who 'don't fit in'.",
        "strategy": "**Shepherd the Flock.**\n* **Relationship First:** Do not start a meeting with tasks. Start with a check-in.\n* **Repair Conflict:** You cannot ignore interpersonal friction; it stops the work. Mediate immediately.\n* **Visual Belonging:** Swag, team photos, inside jokes—these matter to them."
    },
    "Achievement": {
        "title": "The Winning Team",
        "description": "This team is driven by clarity, goals, and winning. They want to know the score. They hate ambiguity and moving goalposts.",
        "risk": "Frustration & Checking Out. If success isn't defined, they feel like they are losing. They hate inefficiency and 'endless talking' without action.",
        "symptoms": "Checking out during long discussions. Asking 'Is this on the test/evaluation?'. Frustration with peers who are 'slow' or 'emotional'.",
        "strategy": "**Keep Score.**\n* **Gamify:** Use leaderboards, checklists, or visual trackers for shift tasks.\n* **Definition of Done:** Be hyper-specific about expectations. 'Clean the room' is bad; 'Floor swept, beds made' is good.\n* **Cut the Fluff:** Keep meetings short and action-oriented."
    }
}

FULL_COMM_PROFILES = {
    "Director": {
        "description": "This staff member communicates primarily as a **Director**. They lead with clarity, structure, and urgency. They prioritize efficiency and competence, often serving as the 'spine' of the team during chaos.\n\nThey view problems as obstacles to be removed quickly rather than processed emotionally. While this decisiveness is a huge asset in a crisis, it can sometimes steamroll slower processors or make the staff member appear unapproachable or impatient.",
        "desc_bullets": [
            "**Clarity:** They speak in headlines, not paragraphs.",
            "**Speed:** They prefer quick decisions over long debates.",
            "**Conflict:** They are comfortable with direct conflict if it solves a problem."
        ],
        "supervising": "To supervise a Director effectively, match their directness. Do not 'sandwich' feedback; give it to them straight. They respect competence and strength, so avoiding hard conversations will cause you to lose credibility.\n\nIt is also critical to help them build patience for process. Frame relationship-building not as 'fluff' but as a strategic tool for efficiency. Help them see that taking time to listen actually speeds up adoption of their ideas.",
        "supervising_bullets": [
            "**Be Concise:** Get to the bottom line quickly.",
            "**Focus on Outcomes:** Explain 'what' needs to happen, let them figure out 'how'.",
            "**Respect Autonomy:** Avoid micromanagement unless safety is at risk."
        ],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?"]
    },
    "Encourager": {
        "description": "This staff member communicates primarily as an **Encourager**. They lead with empathy, warmth, and emotional presence. They act as the 'glue' of the team, ensuring people feel seen and safe. They are often the first to notice when morale is low or when a specific staff member is struggling.\n\nTheir communication style is highly relational, which helps in de-escalation but can sometimes make it harder for them to deliver difficult feedback or hold firm boundaries under stress. They may avoid conflict to preserve harmony.",
        "desc_bullets": [
            "**Warmth:** They lead with relationship and connection.",
            "**Empathy:** They naturally validate feelings before facts.",
            "**Harmony:** They may struggle to be the 'bad guy'."
        ],
        "supervising": "Start every interaction with connection before content. If you jump straight to business, they may feel you are cold or angry. Validate their positive intent ('I know you care deeply') before correcting the impact of their behavior.\n\nHelp them separate their personal worth from the team's happiness. They need to know they are valued even when they make mistakes or when the team is unhappy.",
        "supervising_bullets": [
            "**Connect First:** Spend 2 minutes on rapport before tasks.",
            "**Validate Intent:** Acknowledge their heart before correcting their actions.",
            "**Reassurance:** Be explicit that feedback is about the work, not their worth."
        ],
        "questions": ["Where are you avoiding a hard conversation?", "Are you prioritizing being liked over being effective?", "What boundaries do you need to set today?"]
    },
    "Facilitator": {
        "description": "This staff member communicates primarily as a **Facilitator**. They lead by listening, building consensus, and ensuring fairness across the board. They are the 'calm bridge' who de-escalates tension and ensures all voices are heard before a decision is made.\n\nThey add immense value by preventing rash decisions and ensuring buy-in. However, they can struggle with 'analysis paralysis' or delay necessary actions because they are waiting for everyone to agree, which is not always possible in a crisis environment.",
        "desc_bullets": [
            "**Listening:** They ensure everyone has a say.",
            "**Consensus:** They prefer decisions that everyone can live with.",
            "**Process:** They value the 'how' as much as the 'what'."
        ],
        "supervising": "Give them time to process. Do not demand immediate decisions on complex issues if possible. They need to weigh the options. Reinforce that their slowness is a strength (deliberation), but help them define a 'hard stop' for decision making.\n\nEncourage them to speak first in meetings to prevent them from simply harmonizing with the loudest voice in the room. Validate their desire for fairness while pushing them to be decisive.",
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before a meeting.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless debate.",
            "**Solicit Opinion:** Ask them explicitly what they think, as they may not interrupt."
        ],
        "questions": ["Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?", "What is the cost of delaying this decision?"]
    },
    "Tracker": {
        "description": "This staff member communicates primarily as a **Tracker**. They lead with details, accuracy, and safety. They find comfort in rules and consistency, protecting the agency and youth by noticing the small risks that others miss. They are the 'historian' of the unit.\n\nWhile they provide critical structure, they can become rigid or hyper-critical when stressed. They may view rule-bending as a moral failing rather than a situational necessity.",
        "desc_bullets": [
            "**Precision:** They value accuracy and specific details.",
            "**Rules:** They see policies as safety nets, not suggestions.",
            "**Risk-Averse:** They spot potential problems before they happen."
        ],
        "supervising": "Provide clear, written expectations. Do not be vague. Honor their need for 'the plan.' When plans change, explain the 'why' clearly so they don't feel the change is arbitrary or unsafe.\n\nThey respect competence and consistency. If you are disorganized, you may lose their trust. Help them distinguish between 'safety-critical' rules and 'preferences' where they can flex.",
        "supervising_bullets": [
            "**Be Specific:** Use writing and checklists where possible.",
            "**Explain Why:** Give the rationale behind changes to routine.",
            "**Consistency:** Do what you say you will do."
        ],
        "questions": ["Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?", "How can you show flexibility without losing safety?"]
    }
}

FULL_MOTIV_PROFILES = {
    "Achievement": {
        "description": "Their primary motivator is **Achievement**. They thrive when they can see progress, check boxes, and win. They hate stagnation and ambiguity. They want to know they are doing a good job based on objective evidence, not just feelings.\n\nUnderstanding this means realizing they will work incredibly hard if they can see the scoreboard, but they will burn out if the goalposts keep moving or if success is never defined. They need to feel like they are winning.",
        "desc_bullets": [
            "**Scoreboard:** They need to know if they are winning or losing.",
            "**Completion:** They get energy from finishing tasks.",
            "**Efficiency:** They hate wasted time."
        ],
        "strategies": "Set clear, measurable goals. Use visual trackers or dashboards. Celebrate 'wins' explicitly and publicly. Give them projects where they can own the result from start to finish. Avoid vague feedback like 'good job'; instead say 'You hit X target, which improved Y.'",
        "strategies_bullets": [
            "**Visual Goals:** Use charts or checklists they can mark off.",
            "**Public Wins:** Acknowledge their success in front of peers.",
            "**Autonomy:** Give them the 'what' and let them decide the 'how'."
        ],
        "celebrate": "Celebrate concrete outcomes, finished projects, improved metrics, and their reliability in getting things done. They want to be recognized for their competence and output.",
        "celebrate_bullets": [
            "**Outcomes:** 'You hit 100% on documentation.'",
            "**Reliability:** 'I know I can count on you to finish this.'",
            "**Speed:** 'You got this done faster than anyone else.'"
        ],
        "questions": ["How are you defining success today beyond just metrics?", "Are you celebrating the small wins?", "Who helped you win this week?"]
    },
    "Growth": {
        "description": "Their primary motivator is **Growth**. They thrive when they are learning, stretching, and mastering new skills. They hate feeling stuck or bored. They view their role as a stepping stone to greater competence.\n\nThey are energized by feedback, provided it is constructive and helps them level up. If they feel they aren't growing, they will likely disengage or leave. They need to see a path forward.",
        "desc_bullets": [
            "**Curiosity:** They always want to know 'why' and 'how'.",
            "**Future-Focused:** They are thinking about their next step.",
            "**Feedback:** They crave coaching, not just praise."
        ],
        "strategies": "Feed their curiosity. Assign them 'stretch' projects that require new skills. Frame feedback as 'coaching' for their future career. Connect mundane tasks to their long-term professional development. Ask them: 'What do you want to learn next?'",
        "strategies_bullets": [
            "**Stretch Assignments:** Give them tasks slightly above their current skill level.",
            "**Career Pathing:** Regularly discuss their professional future.",
            "**Mentorship:** Connect them with leaders they admire."
        ],
        "celebrate": "Celebrate new skills learned, adaptability, taking on new challenges, and their personal development trajectory.",
        "celebrate_bullets": [
            "**Learning:** 'I saw how you applied that new technique.'",
            "**Adaptability:** 'You handled that new situation perfectly.'",
            "**Effort:** 'I appreciate how hard you worked to learn this.'"
        ],
        "questions": ["What are you learning from this struggle?", "Are you expecting too much too soon from others?", "How are you feeding your own curiosity?"]
    },
    "Purpose": {
        "description": "Their primary motivator is **Purpose**. They thrive when they feel their work aligns with deep values and makes a real difference for kids. They hate bureaucracy that feels meaningless or performative.\n\nThey will endure difficult conditions if they believe the 'Why' is noble, but they will rebel against policies that feel unjust. They need to feel they are part of a cause, not just a company.",
        "desc_bullets": [
            "**Values-Driven:** Decisions must align with their moral compass.",
            "**Advocacy:** They fight for the underdog.",
            "**Meaning:** They need to see the human impact of their work."
        ],
        "strategies": "Connect every rule to a 'Why.' Validate their passion for justice and advocacy. Share specific stories of their impact on youth. When assigning tasks, explain how this helps the youth or the mission.",
        "strategies_bullets": [
            "**The Why:** Always explain the mission behind the mandate.",
            "**Storytelling:** Share stories of life-change, not just data.",
            "**Ethics:** Allow space for them to voice moral concerns."
        ],
        "celebrate": "Celebrate their advocacy for youth, their integrity, ethical decision making, and specific 'mission moments' where they changed a life. Validate their heart.",
        "celebrate_bullets": [
            "**Advocacy:** 'Thank you for speaking up for that youth.'",
            "**Integrity:** 'I admire how you stood by your values.'",
            "**Impact:** 'You made a real difference in that life today.'"
        ],
        "questions": ["How does this boring task connect to the mission?", "Where are you feeling moral distress?", "How can you advocate effectively right now?"]
    },
    "Connection": {
        "description": "Their primary motivator is **Connection**. They thrive when they feel part of a tight-knit team. They hate isolation and unresolved conflict. For them, the 'who' is more important than the 'what.'\n\nIf the team is fractured, their performance will suffer, no matter how clear the tasks are. They need to feel a sense of belonging and safety within the group to function at their best.",
        "desc_bullets": [
            "**Belonging:** Being part of the tribe is safety.",
            "**Harmony:** Conflict feels dangerous and draining.",
            "**Support:** They are motivated by helping their peers."
        ],
        "strategies": "Prioritize face time. Check in on them as a person, not just an employee. Build team rituals (food, shout-outs). Ensure they don't work in a silo. When giving feedback, reassure them of their belonging in the team.",
        "strategies_bullets": [
            "**Face Time:** Prioritize in-person or video check-ins.",
            "**Team Rituals:** Include them in team bonding activities.",
            "**Personal Care:** Ask about their life outside of work."
        ],
        "celebrate": "Celebrate team cohesion, their support of peers, morale building, and their role in conflict resolution.",
        "celebrate_bullets": [
            "**Teamwork:** 'The team feels so much closer because of you.'",
            "**Support:** 'Thank you for helping X when they were down.'",
            "**Vibe:** 'You bring such a great energy to the room.'"
        ],
        "questions": ["Who do you need to check in with today?", "Are you taking this team conflict personally?", "How can you build belonging in this meeting?"]
    }
}

# (E) CAREER PATHWAYS
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

# 5c. INTEGRATED PROFILES (Expanded & 10 Coaching Questions Logic)
def generate_profile_content(comm, motiv):
    
    # This dictionary holds the specific text for the 16 combinations
    combo_key = f"{comm}-{motiv}"
    
    # Logic to generate "Thriving" descriptions
    thriving_desc = f"When this staff member is thriving, they seamlessly blend the strengths of the {comm} style with the drive of {motiv}. They are operating in their zone of genius, where their communication style feels authentic and their motivational needs are being fully met by the environment. They feel both competent and connected, leading to high performance and sustainability."
    
    # Logic to generate "Struggling" descriptions
    struggling_desc = f"When struggling, the shadow sides of the {comm} and {motiv} traits collide. They may feel that their need for {motiv} is being blocked, causing them to double down on {comm} behaviors in unhealthy ways (e.g., becoming rigid, withdrawing, or over-functioning). They likely feel misunderstood or undervalued."

    # Specific Bullets for Integrated Profiles (Mix of Comm + Motiv traits)
    thriving_bullets = []
    struggling_bullets = []
    
    if comm == "Director":
        thriving_bullets.append("**Decisive Action:** They move the team forward with clarity and speed.")
        struggling_bullets.append("**Steamrolling:** They may bypass others' input to get results quickly.")
    elif comm == "Encourager":
        thriving_bullets.append("**High Morale:** They keep the team's energy and hope alive.")
        struggling_bullets.append("**Conflict Avoidance:** They may hide hard truths to keep the peace.")
    elif comm == "Facilitator":
        thriving_bullets.append("**Inclusive Decisions:** They ensure everyone is heard and on board.")
        struggling_bullets.append("**Indecision:** They may stall out waiting for total consensus.")
    elif comm == "Tracker":
        thriving_bullets.append("**Reliable Systems:** They create safety through order and consistency.")
        struggling_bullets.append("**Rigidity:** They may quote the rulebook instead of solving the human problem.")
        
    if motiv == "Achievement":
        thriving_bullets.append("**Goal Crushing:** They consistently hit targets and improve metrics.")
        struggling_bullets.append("**Burnout:** They push themselves and others past reasonable limits.")
    elif motiv == "Growth":
        thriving_bullets.append("**Continuous Improvement:** They are constantly learning and upgrading skills.")
        struggling_bullets.append("**Boredom:** They check out if the work feels repetitive or stagnant.")
    elif motiv == "Purpose":
        thriving_bullets.append("**Mission Alignment:** They act as a moral compass for the team.")
        struggling_bullets.append("**Moral Outrage:** They become resentful if asked to do 'meaningless' tasks.")
    elif motiv == "Connection":
        thriving_bullets.append("**Team Cohesion:** They foster a deep sense of belonging.")
        struggling_bullets.append("**Personalization:** They take feedback or team friction as a personal attack.")

    # Add a 3rd unique bullet based on the combo
    thriving_bullets.append(f"**{comm}-{motiv} Synergy:** They use {comm} skills to satisfy their {motiv} drive.")
    struggling_bullets.append("**Stress Response:** When {motiv} is threatened, they default to extreme {comm} behaviors.")

    # Base Summaries
    summaries = {
        "Director-Achievement": "The 'General'. Wants to win and do it fast. Excellent at operationalizing goals.",
        "Director-Growth": "The 'Restless Improver'. Pushes the pace of change. Impatient with stagnation.",
        "Director-Purpose": "The 'Warrior for the Cause'. Fights for what is right. Can be rigid if mission is compromised.",
        "Director-Connection": "The 'Protective Captain'. Leads firmly to protect the tribe. Balances strength and care.",
        "Encourager-Achievement": "The 'Coach'. Wants the team to be happy AND winning. Struggles if vibes are good but results are bad.",
        "Encourager-Growth": "The 'Mentor'. Uses warmth to help people grow. Believes deeply in potential.",
        "Encourager-Purpose": "The 'Heart of the Mission'. Keeps the emotional flame alive. Deeply impacted by youth suffering.",
        "Encourager-Connection": "The 'Team Builder'. Prioritizes harmony. Creates safety but may avoid necessary conflict.",
        "Facilitator-Achievement": "The 'Steady Mover'. Wants results without leaving anyone behind. Moves slowly but surely.",
        "Facilitator-Growth": "The 'Patient Gardener'. Creates safe space for learning. Tolerates mistakes for the sake of growth.",
        "Facilitator-Purpose": "The 'Moral Compass'. Ensures decisions are fair. Will slow down to ensure ethics are met.",
        "Facilitator-Connection": "The 'Peacemaker'. Ensures cohesion. Absorbs toxicity to protect the peace.",
        "Tracker-Achievement": "The 'Architect'. Builds systems for success. Loves data and hates chaos.",
        "Tracker-Growth": "The 'Technical Expert'. Masters the craft. Improves the unit by refining processes.",
        "Tracker-Purpose": "The 'Guardian'. Uses rules to protect the mission. Safety is their love language.",
        "Tracker-Connection": "The 'Reliable Rock'. Shows care through consistency. Builds trust by being steady."
    }
    
    # Integrated Questions Lookup
    integrated_qs_map = {
         "Director-Achievement": ["How are you defining success today?", "What is one win you can celebrate right now?", "Are you driving the team too hard?", "What is the cost of speed right now?"],
         "Director-Growth": ["What is one way you can slow down for others?", "How are you measuring your own growth beyond just speed?", "Are you leaving the team behind?", "Is this change necessary right now?"],
         "Director-Purpose": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?", "How does flexibility serve the mission here?"],
         "Director-Connection": ["Are you avoiding this conversation to be kind, or to be safe?", "How can you be direct and caring at the same time?", "Are you protecting them from growth?", "How is the team reacting to your directness?"],
         "Encourager-Achievement": ["How can you celebrate effort, not just the result?", "Are you taking their failure personally?", "Is the team winning, or just happy?", "What helps you stay motivated when results are slow?"],
         "Encourager-Growth": ["Who are you working harder than right now?", "How can you give feedback that helps them grow?", "Are you enabling or empowering?", "What is one hard truth they need to hear?"],
         "Encourager-Purpose": ["What emotional weight are you carrying that isn't yours?", "How does holding this boundary actually help the youth?", "Are you taking care of yourself?", "Where is your empathy causing burnout?"],
         "Encourager-Connection": ["Are you prioritizing peace or safety?", "How can you lean into conflict to build stronger connection?", "What is the cost of avoiding this issue?", "Who is being hurt by the lack of boundaries?"],
         "Facilitator-Achievement": ["How can you be clearer about what you need?", "Are you apologizing for having standards?", "What needs to move faster?", "Where are you holding back your authority?"],
         "Facilitator-Growth": ["Where are you hesitating to lead?", "How can you be kind and firm at the same time?", "Are you waiting too long to act?", "What is the risk of doing nothing?"],
         "Facilitator-Purpose": ["What moral tension are you holding right now?", "How can you speak up for your values effectively?", "Are you staying neutral when you should take a stand?", "How does your silence impact the team?"],
         "Facilitator-Connection": ["What boundaries do you need to set to protect your energy?", "Are you listening too much and leading too little?", "Who is taking care of you?", "Is your silence creating confusion?"],
         "Tracker-Achievement": ["How can you measure effort, not just outcome?", "Are you valuing the data more than the person?", "Where is flexibility needed right now?", "How can you support the person, not just the process?"],
         "Tracker-Growth": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "Are you correcting or coaching?", "How can you make it safe to make mistakes?"],
         "Tracker-Purpose": ["How can you protect the mission without being rigid?", "Are you using rules to manage your anxiety?", "Is this rule serving the child right now?", "How can you explain the 'why' behind the rule?"],
         "Tracker-Connection": ["How can you show care in a way they understand?", "Are you doing too much for others?", "Do they know you care?", "Where do you need help carrying the load?"]
    }

    # 10 Coaching Questions Assembly
    questions = []
    # 3 from Comm Style
    if comm in FULL_COMM_PROFILES: questions += FULL_COMM_PROFILES[comm]["questions"]
    # 3 from Motivation
    if motiv in FULL_MOTIV_PROFILES: questions += FULL_MOTIV_PROFILES[motiv]["questions"]
    # 4 Integrated Questions
    questions += integrated_qs_map.get(combo_key, ["What do you need right now?", "Where are you stuck?", "How can I help?", "What is the goal?"])

    return {
        "s1": FULL_COMM_PROFILES[comm]["description"],
        "s1_b": FULL_COMM_PROFILES[comm]["desc_bullets"],
        "s2": FULL_COMM_PROFILES[comm]["supervising"],
        "s2_b": FULL_COMM_PROFILES[comm]["supervising_bullets"],
        "s3": FULL_MOTIV_PROFILES[motiv]["description"],
        "s3_b": FULL_MOTIV_PROFILES[motiv]["desc_bullets"],
        "s4": FULL_MOTIV_PROFILES[motiv]["strategies"],
        "s4_b": FULL_MOTIV_PROFILES[motiv]["strategies_bullets"],
        "s5": f"This staff member leads with a **{comm}** style driven by **{motiv}**. {summaries.get(combo_key, '')}\n\nThey bring a unique strength to the team: the ability to communicate via {comm} channels to achieve {motiv}-aligned outcomes. However, they may struggle when the environment blocks their drive or misinterprets their style.",
        "s6": f"Support them by honoring their **{comm}** need for communication style and their **{motiv}** need for reward. Ensure they feel seen for both their impact and their intent.\n\nSpecifically, give them opportunities to use their natural style to achieve things that matter to them.",
        "s6_b": [f"**Honor:** Validate their {comm} strengths publicly.", f"**Feed:** Ensure their {motiv} needs are met weekly.", "**Clear Feedback:** Be specific about what they are doing right."],
        "s7": thriving_desc,
        "s7_b": thriving_bullets,
        "s8": struggling_desc,
        "s8_b": struggling_bullets,
        "s9": f"When this staff member is struggling, address their **{motiv}** need first. If they are a {comm}, they are likely stressed by a loss of control or connection.\n\nRe-align expectations and help them regulate by returning to their core strengths.",
        "s9_b": ["**Address Root Cause:** Look for the blocked motivation.", "**Re-align Goals:** Make sure they see a path to success.", "**Coach on Style:** Help them adjust their communication volume."],
        "s10": FULL_MOTIV_PROFILES[motiv]["celebrate"],
        "s10_b": FULL_MOTIV_PROFILES[motiv]["celebrate_bullets"],
        "coaching": questions
    }

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
        
        # Body Paragraph
        clean_body = body.replace("**", "").replace("* ", "- ")
        pdf.multi_cell(0, 5, clean_text(clean_body))
        
        # Bullet Points
        if bullets:
            pdf.ln(1)
            for b in bullets:
                pdf.cell(5, 5, "-", 0, 0)
                # Handle bolding in bullets manually for PDF (simple removal for now)
                clean_b = b.replace("**", "") 
                pdf.multi_cell(0, 5, clean_text(clean_b))
        pdf.ln(4)

    # Sections 1-10
    add_section(f"1. Communication Profile: {p_comm}", data['s1'], data['s1_b'])
    add_section("2. Supervising Their Communication", data['s2'], data['s2_b'])
    add_section(f"3. Motivation Profile: {p_mot}", data['s3'], data['s3_b'])
    add_section("4. Motivating This Staff Member", data['s4'], data['s4_b'])
    add_section("5. Integrated Leadership Profile", data['s5']) 
    add_section("6. How You Can Best Support Them", data['s6'], data['s6_b'])
    add_section("7. What They Look Like When Thriving", data['s7'], data['s7_b'])
    add_section("8. What They Look Like When Struggling", data['s8'], data['s8_b'])
    add_section("9. Supervisory Interventions", data['s9'], data['s9_b'])
    add_section("10. What You Should Celebrate", data['s10'], data['s10_b'])

    # 11. Coaching Questions (10 questions)
    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "11. Coaching Questions", ln=True, fill=True); pdf.ln(2)
    pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
    for i, q in enumerate(data['coaching']):
        pdf.multi_cell(0, 5, clean_text(f"{i+1}. {q}"))
    pdf.ln(4)

    # 12. Advancement
    adv_text = "Help them master the operational side. Challenge them to see clarity and accountability as kindness.\n\nTo advance, they must move beyond their natural strengths and develop their blind spots. This requires intentional coaching and 'safe failure' opportunities."
    adv_bullets = ["Master operations", "See accountability as kindness"]
    
    if p_comm == "Director": 
        adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn. They need to move from being the hero to being the guide.\n\nTheir natural instinct is to take over when things get slow or messy. Advancement requires them to tolerate the messiness of other people's learning curves."
        adv_bullets = ["Delegate effectively", "Allow safe failure", "Focus on strategy vs tactics"]
    elif p_comm == "Encourager": 
        adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness. They need to learn that being 'nice' isn't always being 'kind'.\n\nThey naturally lean into relationships. Advancement requires them to lean into the structural and operational pillars of leadership without losing their heart."
        adv_bullets = ["Master structure", "Hold boundaries", "Separate niceness from kindness"]
    elif p_comm == "Facilitator": 
        adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible. They need to get comfortable with not everyone agreeing.\n\nThey naturally seek harmony and input. Advancement requires them to become comfortable with the loneliness of making the final call when the team is divided."
        adv_bullets = ["Executive presence", "Decisive action", "Limit consensus-seeking"]
    elif p_comm == "Tracker": 
        adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance. They need to learn to read the room, not just the rulebook.\n\nThey naturally lean into safety and rules. Advancement requires them to understand the 'spirit of the law' and to build relational capital that allows them to lead people, not just processes."
        adv_bullets = ["Develop intuition", "Prioritize relationships", "Flexibility"]
    
    add_section("12. Helping Them Prepare for Advancement", adv_text, adv_bullets)

    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---"); st.markdown(f"### 📘 Supervisory Guide: {name}"); st.divider()
    
    def show_section(title, text, bullets=None):
        st.subheader(title)
        st.write(text)
        if bullets:
            for b in bullets:
                st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)

    show_section(f"1. Communication Profile: {p_comm}", data['s1'], data['s1_b'])
    show_section("2. Supervising Their Communication", data['s2'], data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", data['s3'], data['s3_b'])
    show_section("4. Motivating This Staff Member", data['s4'], data['s4_b'])
    
    st.subheader("5. Integrated Leadership Profile")
    st.info(data['s5'])
    st.markdown("<br>", unsafe_allow_html=True)
    
    show_section("6. How You Can Best Support Them", data['s6'], data['s6_b'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("7. Thriving")
        st.write(data['s7'])
        for b in data['s7_b']: st.success(f"- {b}")
    with c2:
        st.subheader("8. Struggling")
        st.write(data['s8'])
        for b in data['s8_b']: st.error(f"- {b}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. Supervisory Interventions", data['s9'], data['s9_b'])
    show_section("10. What You Should Celebrate", data['s10'], data['s10_b'])
    
    st.subheader("11. Coaching Questions")
    for i, q in enumerate(data['coaching']):
        st.write(f"{i+1}. {q}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 12. Advancement logic for display
    adv_text = "Help them master the operational side."
    adv_bullets = ["Master operations"]
    if p_comm == "Director": 
        adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn. They need to move from being the hero to being the guide.\n\nTheir natural instinct is to take over when things get slow or messy. Advancement requires them to tolerate the messiness of other people's learning curves."
        adv_bullets = ["Delegate effectively", "Allow safe failure", "Focus on strategy vs tactics"]
    elif p_comm == "Encourager": 
        adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness. They need to learn that being 'nice' isn't always being 'kind'.\n\nThey naturally lean into relationships. Advancement requires them to lean into the structural and operational pillars of leadership without losing their heart."
        adv_bullets = ["Master structure", "Hold boundaries", "Separate niceness from kindness"]
    elif p_comm == "Facilitator": 
        adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible. They need to get comfortable with not everyone agreeing.\n\nThey naturally seek harmony and input. Advancement requires them to become comfortable with the loneliness of making the final call when the team is divided."
        adv_bullets = ["Executive presence", "Decisive action", "Limit consensus-seeking"]
    elif p_comm == "Tracker": 
        adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance. They need to learn to read the room, not just the rulebook.\n\nThey naturally lean into safety and rules. Advancement requires them to understand the 'spirit of the law' and to build relational capital that allows them to lead people, not just processes."
        adv_bullets = ["Develop intuition", "Prioritize relationships", "Flexibility"]

    show_section("12. Helping Them Prepare for Advancement", adv_text, adv_bullets)

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
                             st.markdown(guide.get('impact_analysis'))
                             st.markdown(guide.get('management_strategy'))

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
                                 st.markdown(f"**If you are missing a {style}:**")
                                 st.write(data.get('risk'))
                                 st.success(data.get('fix'))

            with c2:
                mot_counts = tdf['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4), use_container_width=True)
                
                # MOTIVATION GAP ANALYSIS
                present_motivs = set(tdf['p_mot'].unique())
                missing_motivs = set(MOTIV_TRAITS) - present_motivs
                
                if missing_motivs:
                    st.markdown("---")
                    st.subheader(f"⚠️ Motivation Blindspots")
                    for motiv in missing_motivs:
                        m_data = MOTIVATION_GAP_GUIDE.get(motiv, {})
                        with st.expander(f"Missing Drive: {motiv} - {m_data.get('title')}", expanded=True):
                             st.warning(m_data.get('description'))
                             st.markdown(m_data.get('strategy'))
            
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
