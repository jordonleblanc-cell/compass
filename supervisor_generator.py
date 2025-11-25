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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Default (Light Mode) Variables */
        :root {
            --login-bg: radial-gradient(circle at center, #f1f5f9 0%, #cbd5e1 100%);
            --card-bg: #ffffff;
            --text-title: #015bad;
            --text-body: #0f172a;
            --text-sub: #64748b;
            --input-bg: #ffffff;
            --border-color: #e2e8f0;
        }

        /* Dark Mode Overrides */
        @media (prefers-color-scheme: dark) {
            :root {
                --login-bg: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
                --card-bg: #1e293b;
                --text-title: #51c3c5; /* Teal for contrast on dark */
                --text-body: #f1f5f9;
                --text-sub: #94a3b8;
                --input-bg: #0f172a;
                --border-color: #334155;
            }
        }

        .stApp { background: var(--login-bg); }
        [data-testid="stHeader"] { background: transparent; }
        
        .login-card {
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 400px;
            margin: 100px auto;
            border: 1px solid var(--border-color);
        }
        
        .login-title {
            color: var(--text-title);
            font-family: 'Inter', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        
        .login-subtitle {
            color: var(--text-sub);
            font-family: 'Inter', sans-serif;
            margin-bottom: 20px;
        }
        
        /* Force input styling to match theme */
        .stTextInput input {
            background-color: var(--input-bg) !important;
            color: var(--text-body) !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Hide the default label to keep card clean */
        .stTextInput label {
            display: none;
        }
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

# --- 4. CONTENT DICTIONARIES ---

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

# (C) MOTIVATION GAP GUIDE (Expanded)
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

# (D) CONFLICT MATRIX (Preserved)
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
        # ... (Other Director combos would be here)
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

# (F) PDF PROFILES (Full)
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
                    if dom_mot in MOTIVATION_GAP_GUIDE:
                         gap_data = MOTIVATION_GAP_GUIDE[dom_mot]
                         st.warning(f"**Risk:** {gap_data['risk']}")
                         with st.expander("📚 Motivation Playbook", expanded=True):
                             st.markdown(f"**Symptoms:** {gap_data['symptoms']}")
                             st.markdown(f"**Strategy:**\n{gap_data['strategy']}")
            
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
