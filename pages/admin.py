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
        div[data-testid="column"] .stButton button {{
            background-color: var(--card-bg);
            background-image: none;
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            height: 140px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            padding: 20px;
            white-space: pre-wrap;
            text-align: left;
            transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
        }}

        div[data-testid="column"] .stButton button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            border-color: var(--primary);
            color: var(--primary) !important;
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

        /* Standard Buttons (Generate, Reset, etc.) */
        .stButton button:not([style*="height: 140px"]) {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important; border: none; border-radius: 8px;
            font-weight: 600; box-shadow: 0 4px 10px rgba(1, 91, 173, 0.2);
        }}
        
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

# --- 4. CONTENT DICTIONARIES ---

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
            "psychology": "This conflict stems from a fundamental mismatch in **Currency**. You value **Utility** (is this useful?), while they value **Affirmation** (am I valued?). When you skip the 'human connection' to get straight to work, the Encourager feels dehumanized and unsafe. You interpret their subsequent withdrawal as incompetence or lack of focus, but it is actually a stress response to your intensity.",
            "watch_fors": ["The Encourager stops contributing in meetings (silent withdrawal).", "You start interrupting or finishing their sentences because they take too long.", "They complain to peers that you are 'mean', 'cold', or 'don't care'.", "You feel exhausted by their constant need for what you perceive as 'hand-holding'."],
            "intervention_steps": ["**Step 1: Pre-Meeting Mindset.** Remind yourself: 'Efficiency without Empathy is Inefficiency.' If you break the relationship, the work stops. You must invest 5 minutes to save 5 hours of friction.", "**Step 2: The Translate.** In the meeting, translate their feelings into data. 'When they say they are stressed, they are giving me data about team risk.'", "**Step 3: The Deal.** Explicitly agree to a protocol: You will listen for 5 minutes without solving, if they agree to move to action steps immediately after."],
            "scripts": {
                "To Director": "You are trying to fix the problem, but right now, the *relationship* is the problem. You cannot optimize a broken machine. Stop solving and start listening.",
                "To Encourager": "The Director's brevity is not anger; it is urgency. They are stressed about the goal. You don't need to protect yourself from them; you need to tell them clearly: 'I can help you win, but I need you to lower your volume so I can think.'",
                "Joint": "We are speaking two different languages. [Director] is speaking 'Task'; [Encourager] is speaking 'Team'. Both are valid. [Director], please validate [Encourager]'s concern before we move to the next step."
            }
        },
        "Facilitator": {
            "tension": "The 'Gas vs. Brake' Dynamic.",
            "psychology": "This conflict is about **Risk Perception**. You fear **Stagnation** (doing nothing); they fear **Error** (doing the wrong thing). You operate on 'Ready, Fire, Aim'; they operate on 'Ready, Aim, Aim...'. You feel slowed down and obstructed; they feel steamrolled and unsafe.",
            "watch_fors": ["You issue commands via email to avoid a meeting.", "They keep saying 'We need to talk about this' but never decide.", "You visibly roll your eyes when they ask for 'thoughts'.", "Decisions are made by you but passively resisted/ignored by the team."],
            "intervention_steps": ["**Step 1: Define the Clock.** They need time; you need a deadline. Negotiate it upfront. 'We will discuss for 30 mins, then decide.'", "**Step 2: Define the Veto.** Tell them they have a 'Red Flag' right. If they see a major risk, they can stop you. Otherwise, you drive.", "**Step 3: The Debrief.** After the action, review: 'Did we move too fast? Or did we wait too long?'"],
            "scripts": {"To Director": "Force = Compliance, not Buy-in.", "To Facilitator": "Silence = Agreement. Speak up.", "Joint": "Set a timer for discussion."}
        },
        "Tracker": {
            "tension": "The 'Vision vs. Obstacle' Dynamic.",
            "psychology": "This is a clash of **Authority Sources**. You trust **Intuition** and results; they trust **The Handbook** and process. You say 'Make it happen'; they say 'But Regulation 14.B says...'. You feel they are the 'Department of No'; they feel you are a liability lawsuit waiting to happen.",
            "watch_fors": ["They quote policy numbers in arguments.", "You say 'Ask for forgiveness, not permission.'", "They hoard information or access to prove a point.", "You bypass them to get things done, creating compliance risks."],
            "intervention_steps": ["**Step 1: Clarify Roles.** You own the 'What' (Destination). They own the 'How' (Safe Route).", "**Step 2: The 'Yes, If' Rule.** Coach them to never say 'No'. Instead say: 'Yes, we can do that, *if* we sign this waiver/change this budget.'", "**Step 3: Risk Acceptance.** You must explicitly state: 'I accept the risk of deviating from the standard here.'"],
            "scripts": {"To Director": "They are protecting you from liability.", "To Tracker": "Start with the solution, not the problem.", "Joint": "Director sets destination; Tracker checks brakes."}
        },
        "Director": {
            "tension": "The 'King vs. King' Dynamic.",
            "psychology": "This is a pure **Dominance** struggle. Both of you define safety as **Control**. When the other person takes control, you feel unsafe or disrespected. The conversation becomes a debate about who is right rather than what is best.",
            "watch_fors": ["Interruptions and talking over each other.", "Public debates that feel like combat.", "Refusal to implement the other's idea.", "The team looking awkward while 'Mom and Dad fight'."],
            "intervention_steps": ["**Step 1: Separate Lanes.** You cannot drive the same car. Give them distinct domains where they have total authority.", "**Step 2: The Truce.** Acknowledge the power struggle explicitly. 'We are both fighting for the wheel.'", "**Step 3: Disagree and Commit.** Once a decision is made by the final authority, the debate ends."],
            "scripts": {"To Director": "Fighting to be right vs effective.", "To Other": "Strip the tone.", "Joint": "Stop fighting for the wheel."}
        }
    },
    "Encourager": {
        "Director": {
            "tension": "The 'Sensitivity Gap'.",
            "psychology": "Mismatch in **Validation Style**. You need **External** validation (words/affirmation); they rely on **Internal** validation (results). You feel personally attacked by their brevity. They feel annoyed by your 'fluff'. You over-explain to get validation; they tune out.",
            "watch_fors": ["You apologizing before asking for something.", "You venting to peers about how 'mean' they are.", "They avoid meetings with you because 'it takes too long'.", "You feeling exhausted/crying after supervision."],
            "intervention_steps": ["**Step 1: The Headline.** Start with the conclusion, then the feelings. 'We need to fire Bob because he hurt the team.'", "**Step 2: The 'Why'.** Ask them to explain the *reason* for their speed, so you don't invent a story that they are angry.", "**Step 3: Scheduled Venting.** Ask for 5 mins to process feelings, then promise to hard pivot to tasks."],
            "scripts": {"To Encourager": "Translate feelings to business risk.", "To Director": "Please/Thank you buys speed.", "Joint": "Timeline vs Communication Plan."}
        },
        "Facilitator": {
            "tension": "The 'Polite Stagnation'.",
            "psychology": "This is **Conflict Avoidance**. You fear **Rejection**; they fear **Unfairness**. You want to protect the individual; they want to be fair to the group. You both avoid conflict, so decisions stall indefinitely because neither wants to be the 'bad guy'.",
            "watch_fors": ["Endless meetings where everyone agrees but nothing changes.", "Problems being 'managed' rather than 'solved'.", "Using passive language: 'It would be nice if...' instead of 'You must...'.", "Resentment building because no one is leading."],
            "intervention_steps": ["**Step 1: Name the Fear.** 'We are scared to upset [Person], so we are hurting the program.'", "**Step 2: Assign the 'Bad Guy'.** Supervisor acts as the heavy: 'Blame me. Say I ordered it.'", "**Step 3: Script the Hard Conversation.** Don't let them ad-lib; write the script together."],
            "scripts": {"To Encourager": "Protecting feelings hurts program.", "To Facilitator": "Consensus search is procrastination.", "Joint": "Who delivers the news?"}
        },
        "Tracker": {
            "tension": "The 'Rigidity vs. Flow' Dynamic.",
            "psychology": "Mismatch in **Safety Source**. You find safety in **Connection**; they find safety in **Consistency**. You bend rules to help people; they enforce rules to protect people. They think you are unsafe; you think they are cold.",
            "watch_fors": ["You making 'secret deals' with staff/youth to bypass rules.", "They police you publicly.", "You feeling judged; them feeling undermined.", "Inconsistent application of consequences."],
            "intervention_steps": ["**Step 1: The 'Why' of Rules.** Remind yourself that rules protect the most vulnerable youth by creating predictability.", "**Step 2: The 'Why' of Exceptions.** Show them that rigid rules break rapport, which causes danger.", "**Step 3: The Hybrid.** 'We follow the rule (Tracker), but we deliver it with maximum empathy (Encourager).'"],
            "scripts": {"To Encourager": "Bending rules makes Tracker the bad guy.", "To Tracker": "Right policy, cold delivery."}
        },
        "Encourager": {
            "tension": "The 'Echo Chamber'.",
            "psychology": "This is **Emotional Contagion**. You amplify each other's feelings. Stress becomes shared panic. Joy becomes a party. There is no grounding force, leading to high warmth but low accountability.",
            "watch_fors": ["Supervision turning into a venting session.", "Lack of clear action items.", "Creating 'Us vs. Them' narratives about other departments.", "Ignoring metrics/data because 'we feel like we're doing good'."],
            "intervention_steps": ["**Step 1: The 5-Minute Rule.** Only 5 minutes of venting allowed.", "**Step 2: The Pivot.** 'I hear that is hard. What is the first step to fixing it?'", "**Step 3: External Data.** Bring in a chart/checklist to force a reality check beyond feelings."],
            "scripts": {"To Encourager": "We are spinning.", "Joint": "Challenge each other."}
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "The 'Steamroll'.",
            "psychology": "Mismatch in **Processing**. You process **Externally** (group talk). They process **Internally** (gut check). By the time you ask a question, they have already moved on. You feel disrespected and silenced.",
            "watch_fors": ["You staying silent in meetings then complaining later.", "They look bored while you talk.", "You asking 'Does everyone agree?' and them saying 'Moving on.'", "The team looking confused about who is in charge."],
            "intervention_steps": ["**Step 1: Interrupt.** Learn to say 'Hold on'.", "**Step 2: Pre-Meeting.** Brief them beforehand. 'I am going to ask for feedback on X. Please don't answer first.'", "**Step 3: The Frame.** Frame process as 'Risk Management' (which Directors value) not 'Inclusion' (which they might not)."],
            "scripts": {"To Director": "Moving too fast.", "To Facilitator": "Speak up."}
        },
        "Tracker": {
            "tension": "The 'Details Loop'.",
            "psychology": "Mismatch in **Scope**. You are **Horizontal** (scanning everyone). They are **Vertical** (drilling down). You want to talk about the *concept*; they want to talk about the *form*. You get bogged down in logistics before agreeing on the idea.",
            "watch_fors": ["Long email chains about minor details.", "Meetings running overtime.", "You feeling nitpicked; them feeling vague.", "Great ideas dying in the 'how-to' phase."],
            "intervention_steps": ["**Step 1: Concept First.** 'We are not discussing the form yet. Do we agree on the goal?'", "**Step 2: Detail Second.** 'Now that we agree, please build the checklist.'", "**Step 3: The Parking Lot.** Park detailed questions until the end of the meeting."],
            "scripts": {"To Tracker": "30,000 ft view.", "To Facilitator": "Testing the idea."}
        },
        "Encourager": {
            "tension": "The 'Fairness vs. Feelings' Dynamic.",
            "psychology": "Mismatch in **Focus**. You focus on the **System** (Fairness); they focus on the **Person** (Feelings). You might struggle to rein them in when they over-function for a client, creating inequity in the program.",
            "watch_fors": ["They want an exception; you want a precedent.", "You feel they are playing favorites.", "They feel you are being too clinical."],
            "intervention_steps": ["**Step 1: Validate Intent.** 'I see how much you care about [Youth]. Your heart is in the right place.'", "**Step 2: Explain Inequity.** 'However, if we make a special exception for him, it creates unfairness for the other 10 kids.'", "**Step 3: Return to Standard.** 'We need a solution that is fair to everyone.'"],
            "scripts": {"To Encourager": "Fairness scales.", "To Facilitator": "Validate heart first."}
        }
    },
    "Tracker": {
        "Director": {
            "tension": "The 'Micromanagement Trap'.",
            "psychology": "Mismatch in **Trust**. You trust **Verification**; they trust **Competence**. You verify by checking; they verify by doing. You see their broad strokes as reckless. You ask 10 questions; they get annoyed.",
            "watch_fors": ["You sending emails with 'Corrections'.", "They avoid you.", "You feeling anxious that 'it's all going to fall apart'.", "They withhold info so you don't 'slow them down'."],
            "intervention_steps": ["**Step 1: Pick Battles.** Differentiate between 'Safety Critical' (Intervene) and 'Preference' (Let it go).", "**Step 2: The Sandbox.** Give them a space where they can break things safely.", "**Step 3: Solution-First.** Don't say 'We can't.' Say 'We can, IF we do X.'"],
            "scripts": {"To Director": "Compliance safety.", "To Tracker": "Stop correcting spelling."}
        },
        "Encourager": {
            "tension": "The 'Rules vs. Relationship' Dynamic.",
            "psychology": "Mismatch in **Priorities**. You see their exceptions as chaos. They feel judged by your clipboard. You risk becoming the 'Principal' to their 'Cool Teacher'. They think you care more about the paperwork than the people.",
            "watch_fors": ["You correct them publicly; they shut down.", "You quote policy; they quote feelings.", "Resentment builds over 'nitpicking'."],
            "intervention_steps": ["**Step 1: Connect Before Correct.** Did I say hello before I pointed out the error?", "**Step 2: The 'Why'.** Is this rule critical for safety? Explain that.", "**Step 3: Effectiveness.** Am I being right or being effective?"],
            "scripts": {"To Tracker": "Connect then correct.", "To Encourager": "Rules protect safety."}
        },
        "Facilitator": {
            "tension": "The 'Details vs. Concepts' Dynamic.",
            "psychology": "Mismatch in **Output**. You want a **Checklist**; they want a **Conversation**. You get frustrated when meetings end without a clear 'To-Do' list. They feel you are rushing the relational process.",
            "watch_fors": ["You check your watch while they talk.", "They feel you are transactional.", "You leave meetings confused about next steps."],
            "intervention_steps": ["**Step 1: Self-Check.** Am I being too rigid? Sometimes the 'deliverable' is just alignment.", "**Step 2: Operationalize.** I can help them turn their ideas into steps.", "**Step 3: Collaborate.** Ask permission to capture next steps."],
            "scripts": {"To Tracker": "Alignment is the deliverable.", "To Facilitator": "Define the to-do."}
        }
    }
}

# Fallback for robust lookup
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {
                "tension": "Differing perspectives.", "psychology": "Priorities.", "watch_fors": [], "intervention_steps": ["Listen", "Align"], "scripts": {"To Supervisor": "Align.", "To Staff": "Align.", "Joint": "Align."}
            }

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "why": "Directors act fast. They see a problem and fix it. As a Shift Sup, if they fix everything, their team learns nothing. They become the bottleneck.",
            "conversation": "You have high capacity and speed, which is a gift. To succeed as a Shift Supervisor, you have to resist the urge to 'rescue' the shift by doing everything yourself. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless absolute safety dictates otherwise).",
            "assignment_task": "They must run the shift entirely through verbal direction and delegation to peers. They cannot touch paperwork or intervene in minor conflicts.",
            "success_indicators": "Did they let a staff member struggle through a task without jumping in? Did they give clear verbal instructions? Did they debrief afterwards?",
            "red_flags": "They ran out of the office to 'just do it quick'. They complain that their team is 'too slow'. They took over the radio.",
            "supervisor_focus": "Watch for 'Hero Mode'. If you see them jumping in to fix a crisis that their staff could handle, intervene. Pull them back and say, 'Let your team handle this. Coach them, don't save them.'"
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "why": "Program Sups need buy-in from people they don't supervise (School, Clinical). Directors tend to order people around, which alienates peers.",
            "conversation": "You are excellent at execution within your unit. However, program leadership requires getting buy-in from people you don't supervise (School, Clinical, other cottages). You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment_setup": "Identify a peer in another department (School/Clinical) they have friction with.",
            "assignment_task": "Task them with a cross-departmental project (e.g., improving school transitions). They must interview stakeholders and present a plan that incorporates *their* feedback.",
            "success_indicators": "The plan includes ideas that clearly didn't come from the Director. The peer reports feeling heard. The tone is collaborative.",
            "red_flags": "They present a plan that is 100% their own idea and complain that the other dept is 'difficult'. They try to use your authority to force the change.",
            "supervisor_focus": "Monitor their patience. If they complain about 'meetings' or 'politics', reframe it: 'That isn't politics; that is relationship building. That is the job now.'"
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
            "why": "Directors love fighting fires. Managers need to prevent fires. Directors often struggle to sit still long enough to plan.",
            "conversation": "You react beautifully to problems. The next level requires you to prevent them 6 months in advance. You need to shift from reliance on your force of will to reliance on sustainable systems.",
            "assignment_setup": "Assign a long-term strategic plan for a recurring seasonal issue (e.g., Summer Break Structure).",
            "assignment_task": "They must submit a plan with data projections, budget needs, and staffing models 3 months in advance.",
            "success_indicators": "The plan relies on systems, not just 'working harder'. They anticipate risks.",
            "red_flags": "They delay the planning until the last minute. The plan is just 'we will figure it out'.",
            "supervisor_focus": "Check their horizon. Are they talking about today's crisis or next month's risk? Push them to think longer term."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Guardian'.",
            "why": "Encouragers want to be liked. Shift Sups must be respected. If they can't hold a boundary, the shift becomes unsafe.",
            "conversation": "Your empathy is your superpower, but if you avoid hard conversations to keep the peace, you create an unsafe environment. The team needs you to be a 'Guardian' of the standard. Accountability is kindness.",
            "assignment_setup": "Identify a staff member who is consistently late or missing protocols.",
            "assignment_task": "Lead a policy reinforcement meeting with that staff member. You (Supervisor) observe but do not speak.",
            "success_indicators": "They state the expectation clearly without apologizing. They don't use 'The boss wants...' language.",
            "red_flags": "They apologize for the rule ('Sorry I have to tell you this...'). They make a joke to deflect the tension.",
            "supervisor_focus": "Watch for 'Apology Language'. If they give a directive and then apologize for it, correct them immediately. 'Do not apologize for leading.'"
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "why": "Encouragers run on personality. Programs run on structure. They need to master the boring parts (budgets, audits) to protect the team.",
            "conversation": "You create an amazing climate. To lead a program, that climate must be backed by unshakeable structure. You need to master the unsexy parts of leadership so your team is protected.",
            "assignment_setup": "Assign ownership of a compliance audit or a complex schedule overhaul.",
            "assignment_task": "They must present the data and the rationale to the team, standing on the facts rather than just their relationship.",
            "success_indicators": "The audit is accurate. They can explain the 'why' without appealing to emotion.",
            "red_flags": "They ask a Tracker to do it for them. They procrastinate the paperwork to hang out with staff.",
            "supervisor_focus": "Inspect what you expect. Encouragers can be disorganized. Help them build a personal organization system so their administrative balls don't drop."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "why": "Managers deal with resource scarcity. Encouragers take 'No' personally and burn out trying to save everyone.",
            "conversation": "You naturally carry the emotions of your people. At the manager level, the weight is too heavy to carry alone. Your growth edge is caring deeply about the person without taking responsibility for their feelings.",
            "assignment_setup": "Have them manage a resource allocation conflict (e.g., denying a budget request or staffing request).",
            "assignment_task": "Deliver a 'No' to a request, explain the business reason, and withstand the disappointment of the staff member.",
            "success_indicators": "They hold the line. They don't promise to 'fix it later' just to stop the person from being sad.",
            "red_flags": "They cave to the request. They vent to the staff member about 'Upper Management' making them do it.",
            "supervisor_focus": "Watch for burnout. If they look exhausted, they are likely over-functioning emotionally. Ask: 'Who are you trying to save right now?'"
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Peer' to 'Decider'.",
            "why": "Facilitators freeze when the team is split. Safety requires immediate direction without consensus.",
            "conversation": "You are gifted at ensuring everyone feels heard. As a Shift Sup, there will be moments where consensus is impossible and safety requires speed. You need to get comfortable making the '51% decision'—listening to input, but making the call even if 49% disagree.",
            "assignment_setup": "Put them in charge of a time-sensitive crisis drill or transition.",
            "assignment_task": "They must make immediate calls on staff positioning. Debrief afterwards: 'Where did you hesitate? How did it feel to give a direct command?' Affirm their authority.",
            "success_indicators": "They gave direct commands. They didn't ask 'What do you guys think?' during the crisis.",
            "red_flags": "They stood back and let a Director take over. They tried to have a meeting in the middle of a transition.",
            "supervisor_focus": "Push for speed. When they ask 'What do you think?', throw it back: 'You tell me. You're the leader.' Force them to exercise their judgment muscle."
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "why": "Facilitators lead from the middle. Program Sups must lead from the front and set the vision.",
            "conversation": "You act as a great buffer. But we need you to inject your own vision. Don't just wait to see what the group wants; tell us where you think the group needs to go.",
            "assignment_setup": "Ask them to propose a new initiative for the program culture.",
            "assignment_task": "Present it to the team as a direction, not a discussion topic. 'This is where we are going.'",
            "success_indicators": "They use declarative statements ('We will...'). They handle pushback without folding.",
            "red_flags": "They frame it as a question ('How would you guys feel about...?'). They retreat at the first sign of resistance.",
            "supervisor_focus": "Watch for 'The Buffer'. Are they just passing messages between staff and admin? Challenge them to take a stand on issues."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
            "why": "Facilitators get bogged down in fairness and stall critical changes.",
            "conversation": "Fair process is vital, but sometimes it yields poor results. At this level, you must prioritize the outcome over the comfort of the process. You need to be willing to disrupt the harmony to achieve the mission.",
            "assignment_setup": "Task them with implementing a necessary but unpopular policy change.",
            "assignment_task": "Listen to complaints, validate feelings, but do NOT change the decision.",
            "success_indicators": "The policy gets implemented on time. They survive the team being unhappy with them.",
            "red_flags": "They delay implementation to 'get more feedback'. They water down the policy to make it nicer.",
            "supervisor_focus": "Monitor their tolerance for conflict. If they start delaying a necessary change to avoid upset, step in. 'The upset is inevitable; the delay is optional.'"
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Executor' to 'Overseer'.",
            "why": "Trackers don't trust others to do it right, so they micromanage. They burn out trying to do 5 jobs.",
            "conversation": "You are brilliant at the details. But you cannot track every detail personally. You have to let the team do the checklist, even if they do it differently than you would.",
            "assignment_setup": "The 'Hands-Off' Day. Assign them to supervise a complex task (intake/search).",
            "assignment_task": "Strictly prohibited from touching paperwork. Must guide a peer to do it verbally.",
            "success_indicators": "They kept their hands in their pockets. They gave clear corrections without taking over.",
            "red_flags": "They grabbed the pen. They sighed and said 'I'll just do it'.",
            "supervisor_focus": "Watch for micromanagement. If they are re-doing someone else's work, stop them. 'If it is 80% right, it is right enough. Move on.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "why": "Trackers want a rule for everything. Leadership involves judgment calls where no rule exists.",
            "conversation": "You excel when rules are clear. Leadership is full of gray areas. You need to develop your intuition to navigate dynamics that don't fit the spreadsheet.",
            "assignment_setup": "Handle a complex parent/youth complaint where standard rules don't apply.",
            "assignment_task": "Make a principle-based decision (fairness/safety) rather than a rule-based one.",
            "success_indicators": "They made a decision that wasn't in the handbook but made sense. They can explain the 'spirit' of the rule.",
            "red_flags": "They froze because 'there's no policy'. They applied a rule rigidly that made no sense in context.",
            "supervisor_focus": "Challenge their rigidity. If they say 'We can't do that, it's not the rule', ask 'What is the *intent* of the rule? Can we meet the intent a different way?'"
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "why": "Trackers value efficiency over connection, risking a sterile, unhappy culture.",
            "conversation": "Culture eats strategy (and checklists) for breakfast. If you prioritize efficiency over connection, you will have a compliant but brittle organization. You need to invest as much energy in 'how people feel' as 'what people do'.",
            "assignment_setup": "Task them with a retention or morale initiative.",
            "assignment_task": "Spend one week focusing solely on staff development/relationships. Delegate metrics to a deputy.",
            "success_indicators": "They had non-work conversations. Staff report feeling seen.",
            "red_flags": "They turned the morale initiative into a checklist ('Did you have fun? Check yes').",
            "supervisor_focus": "Look for the 'Human Element'. In every supervision, ask them a question about people, not tasks. 'How is [Staff Name] doing really?'"
        }
    }
}

# (PDF Dictionaries - Shortened for file size, full content generated in PDF function)
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
                    st.markdown(f"**Psychology:** {clash['psychology']}")
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
                st.markdown(f"**Why it's hard:** {path['why']}")
                c_a, c_b = st.columns(2)
                with c_a:
                    with st.container(border=True):
                        st.markdown("##### 🗣️ The Conversation")
                        st.write(path['conversation'])
                        st.warning(f"**Supervisor Watch Item:** {path.get('supervisor_focus')}")
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
