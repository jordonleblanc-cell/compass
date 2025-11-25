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

# --- 4. RICH CONTENT DICTIONARIES ---

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
        "meeting_protocol": "1. **The Devil's Advocate Rule:** Assign one person per meeting to specifically challenge the speed of the decision. Ask: 'What happens if we wait 24 hours?'\n2. **Forced Silence:** Implement a '2-minute silence' after a proposal is made to allow internal processors time to think before the Directors dominate the verbal space.\n3. **The 'Who' Check:** End every meeting by asking, 'Who might feel hurt or left out by this decision?' Directors naturally skip this step."
    },
    "Encourager": {
        "title": "The 'Family' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a family gathering. There is laughter, food, and deep personal connection. People feel safe, seen, and cared for. Staff retention is often high because people don't want to leave their friends.\n\n**The Good:** High psychological safety and trust. Staff support each other through personal crises. Resilience in hard times.\n**The Bad:** The 'Nice Guy Trap.' Bad behavior is tolerated because no one wants to be 'mean.' Accountability is viewed as aggression. Decisions are made based on what makes people happy, not what is effective.",
        "management_strategy": "**Your Role: The 'Bad Guy'.** They have enough warmth; they need you to provide the spine.\n* **Normalize Conflict:** Teach them that disagreement is not disrespect.\n* **Separate Friends from Work:** Remind them that 'liking' someone doesn't mean letting them slide on safety protocols.\n* **Focus on the 'Who':** Frame accountability as 'protecting the team' rather than 'punishing the individual.'",
        "meeting_protocol": "1. **The 'Blockers' Agenda:** Start meetings with 'What is broken?' instead of 'How are we doing?'. Force negative feedback into the open.\n2. **Data-Driven Reviews:** Use dashboards to review performance. It depersonalizes the feedback. 'The chart says we are late' is easier for an Encourager to hear than 'You are late.'\n3. **Time-Box Venting:** Allow exactly 10 minutes for feelings/venting at the start, then physically set a timer to pivot to tasks."
    },
    "Facilitator": {
        "title": "The 'Consensus' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a democratic senate. Every voice is heard, every angle is considered, and fairness is the ultimate goal. There is a deep sense of stability and equity.\n\n**The Good:** High buy-in. Few errors because decisions are vetted thoroughly. An equitable environment where no one is left behind.\n**The Bad:** Analysis Paralysis. This team struggles to move during a crisis. They will form a committee to decide where to order lunch. They risk 'death by meeting,' where the process of deciding becomes more important than the decision itself.",
        "management_strategy": "**Your Role: The 'Closer'.** They have enough inputs; they need you to force the output.\n* **Set the Deadline:** Do not ask 'When should we decide?'. Tell them 'We decide on Tuesday.'\n* **Define 'Consensus':** Teach them that consensus means 'I can live with it,' not 'I love it.'\n* **Authorize Imperfection:** Give them permission to make mistakes. They are terrified of being wrong.",
        "meeting_protocol": "1. **The 'Disagree & Commit' Rule:** Establish a norm that once a decision is made, debate ends. No meeting-after-the-meeting.\n2. **Hard Deadlines:** Set the decision date BEFORE the discussion starts.\n3. **Opt-Out Rights:** Allow people to skip meetings if they trust the group to decide. Reduce the committee bloat."
    },
    "Tracker": {
        "title": "The 'Safety' Culture",
        "impact_analysis": "**What it feels like:** This unit feels like a well-oiled machine or a laboratory. Everything has a place, a time, and a label. Documentation is impeccable. Risks are anticipated and managed before they happen.\n\n**The Good:** Safety and reliability. You never have to worry about an audit. Shifts run like clockwork.\n**The Bad:** Rigidity. This team struggles when the 'Plan' fails. They may quote the policy manual while a kid is in crisis, prioritizing the rule over the relationship. Innovation is low because 'we've always done it this way.'",
        "management_strategy": "**Your Role: The 'Visionary'.** They are looking at their feet (the steps); you must make them look at the horizon (the goal).\n* **Challenge the Rule:** Regularly ask 'Does this rule still serve us?'\n* **Humanize the Data:** Remind them that every number on the spreadsheet represents a human being.\n* **Encourage Flex:** Reward them for adapting to a crisis, not just for following the script.",
        "meeting_protocol": "1. **The 'Intent' Explain:** Trackers must explain the *intent* behind a rule (e.g., 'Safety') not just the rule itself.\n2. **Pilot Programs:** Frame innovation as a 'Controlled Experiment.' Trackers hate chaos, but they love data collection. Let them 'test' a new idea to gather data.\n3. **The Human Impact:** End every meeting by asking: 'How will this decision make the youth/staff *feel*?'"
    }
}

# (B) CONFLICT MATRIX (Deep Dive - The "Masterclass" Edition)
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "The 'Bulldozer vs. Doormat' Dynamic.",
            "psychology": "This conflict stems from a fundamental mismatch in **Currency**. You value **Utility** (is this useful?), while they value **Affirmation** (am I valued?). When you skip the 'human connection' to get straight to work, the Encourager feels dehumanized and unsafe. You interpret their subsequent withdrawal as incompetence or lack of focus, but it is actually a stress response to your intensity. They withdraw to protect themselves.",
            "watch_fors": ["Silent withdrawal (they stop arguing and just nod).", "You interrupting them to 'speed them up'.", "Complaints to peers that you are 'cold' or 'mean'.", "You feeling exhausted by their 'neediness'."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nBefore you meet, you must shift your internal goal. Your goal is not to 'fix the problem'; your goal is to 'repair the safety'. If you try to fix the problem while they feel unsafe, they will agree to your face and sabotage it behind your back. Remind yourself: 'Efficiency without Empathy is Inefficiency.'",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nStart with a relational check-in. Do not skip this. Ask 'How are you holding up?' and listen for 3 minutes. Then, translate your intensity: 'I know I'm moving fast. That isn't because I'm angry; it's because I'm stressed about the goal. I need your help to slow me down if I'm missing the human cost.'",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nAfter a hard conversation, circle back 2 hours later with a warm, non-work interaction (a meme, a coffee, a 'thanks'). This proves to the Encourager that the relationship survived the conflict. This is crucial for their psychological safety.",
            "script_staff": "**To Encourager:** \"I want to apologize if my pace earlier felt like I didn't care. I get tunnel vision on the goal. I value your heart for the team. Can we reset? I need you to help me understand how the team is feeling about this change.\"",
            "script_why_staff": "Validates their value (Affirmation) and admits your own weakness, which builds trust.",
            "script_self": "**Internal Monologue:** \"I am not wasting time by listening; I am refueling their engine so they can work.\""
        },
        "Facilitator": {
            "tension": "The 'Gas vs. Brake' Dynamic.",
            "psychology": "This conflict is about **Risk Perception**. You fear **Stagnation** (doing nothing); they fear **Error** (doing the wrong thing). You operate on 'Ready, Fire, Aim'; they operate on 'Ready, Aim, Aim...'. You feel slowed down and obstructed; they feel steamrolled and unsafe. You think they are indecisive; they think you are reckless.",
            "watch_fors": ["You issuing commands via email to avoid a meeting.", "They saying 'We need to talk about this' but never deciding.", "You visibly rolling your eyes when they ask for 'more thoughts'.", "Decisions made by you but passively resisted by the team."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nRecognize that their slowness is a feature, not a bug. They are your risk management system. Your goal for the meeting is not to force a 'Yes', but to negotiate a 'When'.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nDon't ask 'Can we decide?'. Ask 'What specific data do you need to feel safe deciding?'. Then, set a deadline. 'We will gather that data until Tuesday. On Tuesday at 2pm, we decide.' This gives them space to process but gives you the certainty of action.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nAfter the decision is made, ask them to design the implementation plan. This gives them back control over the 'How' even if you forced the 'What'.",
            "script_staff": "**To Facilitator:** \"I feel a lot of urgency to move this forward, but I know you need to ensure we aren't missing perspectives. I can't wait forever, but I can wait 24 hours. What specific input do you need before we make the final call tomorrow?\"",
            "script_why_staff": "Acknowledges your need (Speed) while respecting their need (Process). Sets a boundary without being aggressive.",
            "script_self": "**Internal Monologue:** \"Their hesitation is not resistance; it is caution. I can use that.\""
        },
        "Tracker": {
            "tension": "The 'Vision vs. Obstacle' Dynamic.",
            "psychology": "This is a clash of **Authority Sources**. You trust **Intuition** and results; they trust **The Handbook** and process. You say 'Make it happen'; they say 'But Regulation 14.B says...'. You feel they are the 'Department of No'; they feel you are a liability lawsuit waiting to happen.",
            "watch_fors": ["They quote policy numbers in arguments.", "You say 'Ask for forgiveness, not permission.'", "They hoard information to prove a point.", "You bypass them to get things done, creating compliance risks."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nRealize that they are terrified you are going to break something important. They aren't trying to annoy you; they are trying to protect you from liability. Approach them as a consultant, not an adversary.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nStart with the goal, not the method. 'Here is the outcome I need. The standard way won't work. Help me find a compliant way to get there.' Give them the problem to solve. If they say 'No', ask 'How can we get to Yes safely?'",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nExplicitly state: 'I accept the risk of this decision.' Relieve them of the anxiety of being blamed if it goes wrong. That is usually what they are afraid of.",
            "script_staff": "**To Tracker:** \"I appreciate you watching the compliance side. I know I miss those details sometimes. I feel frustrated when I hear 'No' without a 'How'. Instead of telling me why we can't do it, can you map out the safest path to get us to 'Yes'?\"",
            "script_why_staff": "Validates their role (Safety) while reframing their job as 'Solution Finding' rather than 'Gatekeeping'.",
            "script_self": "**Internal Monologue:** \"They are the brakes on my race car. I need brakes to win the race.\""
        },
        "Director": {
            "tension": "The 'King vs. King' Dynamic.",
            "psychology": "This is a pure **Dominance** struggle. Both of you define safety as **Control**. When the other person takes control, you feel unsafe or disrespected. The conversation becomes a debate about who is right rather than what is best.",
            "watch_fors": ["Interruptions and talking over each other.", "Public debates that feel like combat.", "Refusal to implement the other's idea.", "The team looking awkward while 'Mom and Dad fight'."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nDrop the ego. You are fighting to be 'Right', not 'Effective'. Ask yourself: 'If I let them win this point, does the program actually suffer?' If not, yield.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nName the dynamic. 'We are both fighting for the wheel.' Then, separate lanes. 'You own Project A entirely. I own Project B entirely. We don't micromanage each other.'",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nPublicly back them up. Show the team that you trust their authority. It signals the war is over.",
            "script_staff": "**To Director:** \"We both have strong opinions and want to move fast. I think we are getting in each other's way. I'm going to define the 'What' (the Goal), and I'm going to trust you with the 'How'. I won't micromanage it. Go run with it.\"",
            "script_why_staff": "Grants them what they want (Autonomy/Control) while keeping what you want (The Outcome).",
            "script_self": "**Internal Monologue:** \"I don't need to win every battle to win the war.\""
        }
    },
    "Encourager": {
        "Director": {
            "tension": "The 'Sensitivity Gap'.",
            "psychology": "Mismatch in **Validation Style**. You need **External** validation (words/affirmation); they rely on **Internal** validation (results). You feel personally attacked by their brevity. They feel annoyed by your 'fluff'. You over-explain to get validation; they tune out.",
            "watch_fors": ["You apologizing before asking for something.", "You venting to peers about how 'mean' they are.", "They avoid meetings with you because 'it takes too long'.", "You feeling exhausted/crying after supervision."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nStop looking for your emotional needs to be met by your boss. They are dry wells. Bring them solutions, not feelings. Remind yourself: 'Their silence is not anger, it is focus.'",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nUse the BLUF method (Bottom Line Up Front). Start with the result. Then, explain the 'People Impact' as a business risk. 'If we do this, morale drops, and turnover rises.' That is language they understand.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nAsk for specific feedback on your *performance*, not your *personality*. Force them to be specific.",
            "script_staff": "**To Director:** \"I know you value efficiency. I need you to know that when you cut me off, I shut down, and you lose my best ideas. If you can give me 2 minutes to explain the context, I promise I will get to the point.\"",
            "script_why_staff": "Sets a boundary while acknowledging their value system (efficiency).",
            "script_self": "**Internal Monologue:** \"I am safe even if they aren't smiling.\""
        },
        "Facilitator": {
            "tension": "The 'Polite Stagnation'.",
            "psychology": "This is **Conflict Avoidance**. You fear **Rejection**; they fear **Unfairness**. You want to protect the individual; they want to be fair to the group. You both avoid conflict, so decisions stall indefinitely because neither wants to be the 'bad guy'.",
            "watch_fors": ["Endless meetings where everyone agrees but nothing changes.", "Problems being 'managed' rather than 'solved'.", "Using passive language: 'It would be nice if...' instead of 'You must...'.", "Resentment building because no one is leading."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nAdmit that being 'nice' is hurting the team. You are choosing comfort over cure. You must agree that one of you will play the 'Bad Guy'.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nScript the hard conversation together. Literally write it down. 'If we don't fire Bob, we are hurting the other 5 staff.' Use 'We' language to bolster courage.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nDebrief after the conflict. 'We did it. We survived. The team is okay.' Reinforce that conflict is safe.",
            "script_staff": "**To Facilitator:** \"I feel like we are both trying to be kind here, but the lack of a decision is actually hurting the team. I'm going to make the call to move forward, even though it might be uncomfortable. I need you to back me up.\"",
            "script_why_staff": "Acknowledges the shared weakness and takes responsibility for the solution.",
            "script_self": "**Internal Monologue:** \"Clarity is kindness. Stalling is cruelty.\""
        },
        "Tracker": {
            "tension": "The 'Rigidity vs. Flow' Dynamic.",
            "psychology": "Mismatch in **Safety Source**. You find safety in **Connection**; they find safety in **Consistency**. You bend rules to help people; they enforce rules to protect people. They think you are unsafe; you think they are cold.",
            "watch_fors": ["You making 'secret deals' with staff/youth to bypass rules.", "They police you publicly.", "You feeling judged; them feeling undermined.", "Inconsistent application of consequences."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nUnderstand that your 'exceptions' drive them crazy because it destroys their data reliability. You are breaking their machine.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nValidate the rule first. 'I know Rule X exists for safety.' Then ask for the exception as a specific, one-time deviation, not a lifestyle. Ask them to help you document it so it stays 'in the system'.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nPublicly validate their role. 'I'm so glad [Tracker] keeps us compliant.'",
            "script_staff": "**To Tracker:** \"I know my flexibility stresses you out because you value consistency. I value it too. But right now, the relationship with this youth is fragile. Can we find a way to bend the rule this one time, while documenting it so we stay safe?\"",
            "script_why_staff": "Validates their need (Consistency) while advocating for your need (Relationship).",
            "script_self": "**Internal Monologue:** \"Structure protects the relationship.\""
        },
        "Encourager": {
            "tension": "The 'Echo Chamber'.",
            "psychology": "This is **Emotional Contagion**. You amplify each other's feelings. Stress becomes shared panic. Joy becomes a party. There is no grounding force, leading to high warmth but low accountability.",
            "watch_fors": ["Supervision turning into a venting session.", "Lack of clear action items.", "Creating 'Us vs. Them' narratives about other departments.", "Ignoring metrics/data because 'we feel like we're doing good'."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nWe are addicted to validation. We need to pivot to action. We need to be professionals, not just friends.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nSet a timer. 5 minutes for feelings. Then ask: 'What are we going to DO about it?'. If you catch yourselves spiraling, use a code word like 'Pivot'.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nCheck on the *task* completion, not just the feeling. Hold each other accountable.",
            "script_staff": "**To Encourager:** \"I love that we support each other. But we are spinning. Let's put our feelings in a box for 10 minutes and just solve the logistics. We need a plan, not just a vent.\"",
            "script_why_staff": "Interrupts the emotional spiral without rejecting the person.",
            "script_self": "**Internal Monologue:** \"I can be supportive without joining their chaos.\""
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "The 'Steamroll'.",
            "psychology": "Mismatch in **Processing**. You process **Externally** (group talk). They process **Internally** (gut check). By the time you ask a question, they have already moved on. You feel disrespected and silenced.",
            "watch_fors": ["You staying silent in meetings then complaining later.", "They look bored while you talk.", "You asking 'Does everyone agree?' and them saying 'Moving on.'", "The team looking confused about who is in charge."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThey aren't trying to silence you; they think you have nothing to say because you aren't speaking. You must interrupt to be heard.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nStop asking permission ('Can I say something?'). Just speak ('I have a concern'). Use the 'Timeout' hand signal if they are steamrolling. Demand a pause.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nSend a follow-up email summarizing the decision. This forces clarity.",
            "script_staff": "**To Director:** \"You are moving too fast. If you want this decision to stick, you have to let me get the team on board. Give me 10 minutes to facilitate the discussion, then we can decide.\"",
            "script_why_staff": "Frames your process as a way to ensure *their* success (stickiness).",
            "script_self": "**Internal Monologue:** \"My voice matters. Slowing down is safe.\""
        },
        "Tracker": {
            "tension": "The 'Details Loop'.",
            "psychology": "Mismatch in **Scope**. You are **Horizontal** (scanning everyone). They are **Vertical** (drilling down). You want to talk about the *concept*; they want to talk about the *form*. You get bogged down in logistics before agreeing on the idea.",
            "watch_fors": ["Long email chains about minor details.", "Meetings running overtime.", "You feeling nitpicked; them feeling vague.", "Great ideas dying in the 'how-to' phase."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThey are testing your idea to see if it breaks. That is valuable.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nUse 'Parking Lot' tactics. 'That is a great detail questions, let's park it. Do we agree on the concept first?'. Keep pulling them up to the 30,000 foot view.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nHand the detailed execution to them. 'You are the expert on the form. I trust you to build it.'",
            "script_staff": "**To Tracker:** \"We are at the 30,000-foot view right now. I need you to fly up here with me for 5 minutes. We will land and check the tires later. Do you agree with the destination?\"",
            "script_why_staff": "Validates their detail orientation but sets a boundary on when to use it.",
            "script_self": "**Internal Monologue:** \"Details are necessary, but not yet.\""
        },
        "Encourager": {
            "tension": "The 'Fairness vs. Feelings' Dynamic.",
            "psychology": "Mismatch in **Focus**. You focus on the **System** (Fairness); they focus on the **Person** (Feelings). You might struggle to rein them in when they over-function for a client, creating inequity in the program.",
            "watch_fors": ["They want an exception; you want a precedent.", "You feel they are playing favorites.", "They feel you are being too clinical."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThey need to feel seen before they will listen to the logic. Empathy first, Logic second.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nValidate the specific case ('I know that kid is suffering'). Then widen the lens ('But if we do X for him, we hurt Y and Z'). Make them see the whole board.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nAsk them to help you design the 'Fair' solution so it feels human.",
            "script_staff": "**To Encourager:** \"I see how much you care about [Youth]. However, if we make a special exception for him, it creates unfairness for the other 10 kids. We need a solution that is fair to everyone. How do we do that?\"",
            "script_why_staff": "Appeals to their desire to help people, but broadens the scope of 'people'.",
            "script_self": "**Internal Monologue:** \"Fairness is a form of care.\""
        },
        "Facilitator": {
            "tension": "The 'Committee'.",
            "psychology": "Diffusion of Responsibility. No one drives. Endless meetings. Great process, low output. You both listen, nod, and validate, but no one directs. The team feels heard but leaderless.",
            "watch_fors": ["Conversations go in circles.", "Everyone feels good but nothing gets done.", "Conflict is buried under politeness."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nIf I don't drive, we crash. Someone has to be the Director.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nAssign a 'Driver' at the start of the meeting. 'I am facilitating; you are deciding.' Or vice versa. Do not leave it ambiguous.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nTrack decisions, not just discussions.",
            "script_staff": "**To Facilitator:** \"We are spinning. I'm going to step out of 'listening mode' and into 'directing mode'. Here is the plan we are going with.\"",
            "script_why_staff": "Breaks the loop by explicitly changing roles.",
            "script_self": "**Internal Monologue:** \"Deciding is my job.\""
        }
    },
    "Tracker": {
        "Director": {
            "tension": "The 'Micromanagement Trap'.",
            "psychology": "Mismatch in **Trust**. You trust **Verification**; they trust **Competence**. You verify by checking; they verify by doing. You see their broad strokes as reckless. You ask 10 questions; they get annoyed.",
            "watch_fors": ["You sending emails with 'Corrections'.", "They avoid you.", "You feeling anxious that 'it's all going to fall apart'.", "They withhold info so you don't 'slow them down'."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThey are not reckless; they are fast. I need to trust them until they give me a reason not to.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nAsk for 'Veto Power' on safety issues only. Let them own the rest. Stop correcting spelling mistakes. Focus on liability.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nWhen they succeed, tell them. 'You moved fast and it worked. Good job.'",
            "script_staff": "**To Director:** \"I'm not trying to slow you down; I'm trying to ensure this sticks. I don't need to control the whole project, but I do need veto power on these two specific safety compliance items. The rest is yours.\"",
            "script_why_staff": "Grants autonomy while protecting the critical safety boundary.",
            "script_self": "**Internal Monologue:** \"I can let go of the small stuff.\""
        },
        "Encourager": {
            "tension": "The 'Rules vs. Relationship' Dynamic.",
            "psychology": "Mismatch in **Priorities**. You see their exceptions as chaos. They feel judged by your clipboard. You risk becoming the 'Principal' to their 'Cool Teacher'. They think you care more about the paperwork than the people.",
            "watch_fors": ["You correct them publicly; they shut down.", "You quote policy; they quote feelings.", "Resentment builds over 'nitpicking'."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThey are the gas; I am the brakes. We need both. Without them, the kids hate us. Without me, the kids aren't safe.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nConnect before you correct. Ask about the kid before you ask about the form. Explain the 'Safety Why' behind the rule.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nAsk them to teach you how to build better rapport.",
            "script_staff": "**To Encourager:** \"When you bend the rule for that youth, it makes the shift unsafe for the rest of us because we don't know what to expect. I need you to follow the protocol, not to be mean, but to keep us safe.\"",
            "script_why_staff": "Reframes the rule from 'bureaucracy' to 'safety tool'.",
            "script_self": "**Internal Monologue:** \"They care about the kids just as much as I do.\""
        },
        "Facilitator": {
            "tension": "The 'Details vs. Concepts' Dynamic.",
            "psychology": "Mismatch in **Output**. You want a **Checklist**; they want a **Conversation**. You get frustrated when meetings end without a clear 'To-Do' list. They feel you are rushing the relational process.",
            "watch_fors": ["You check your watch while they talk.", "They feel you are transactional.", "You leave meetings confused about next steps."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nThe conversation IS the work for them. I need to be patient.",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nListen first. Then, offer to be the scribe. 'I love these ideas. Can I capture them into a checklist for us?' Be the operationalizer of their vision.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nShow them the checklist and ask 'Did I capture the spirit of what you said?'",
            "script_staff": "**To Facilitator:** \"I appreciate the discussion. To help me execute this, can we spend the last 5 minutes defining exactly who is doing what by when?\"",
            "script_why_staff": "Validates the discussion but enforces a concrete output.",
            "script_self": "**Internal Monologue:** \"I can help turn this talk into reality.\""
        },
        "Tracker": {
            "tension": "The 'Audit'.",
            "psychology": "Perfectionism loop. You both love details. You might argue over *which* rule applies or the specific formatting of a document. You risk missing the forest for the trees, creating a perfect system that no one uses.",
            "watch_fors": ["Arguments over semantics.", "Email wars with bullet points.", "Zero emotional connection."],
            "protocol_1": "**Phase 1: Preparation (Mindset)**\nDoes this actually matter to the client? Or is this just preference?",
            "protocol_2": "**Phase 2: The Conversation (Tactics)**\nZoom out. 'What is the goal?' Agree on the 'Good Enough' standard.",
            "protocol_3": "**Phase 3: The Follow-Up (Repair)**\nStop talking about work. Ask about their weekend.",
            "script_staff": "**To Tracker:** \"We are getting stuck in the weeds. Let's pause the detail work. What is the actual outcome we need for the client today? Let's solve for that first.\"",
            "script_why_staff": "Forces a perspective shift from micro to macro.",
            "script_self": "**Internal Monologue:** \"Perfect is the enemy of good.\""
        }
    }
}

# (D) CAREER PATHWAYS (Deep Dive)
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {"shift": "Doing -> Enabling", "why": "Directors act fast. As a Shift Sup, if you fix everything, your team learns nothing. You become the bottleneck.", "conversation": "Sit on your hands. Success is team confidence, not your speed.", "assignment_setup": "Lead shift from office.", "assignment_task": "Verbal direction only. No touching paperwork.", "success_indicators": "Did they let staff struggle without jumping in?", "red_flags": "Running out to fix it.", "supervisor_focus": "Hero Mode"},
        "Program Supervisor": {"shift": "Command -> Influence", "why": "Can't order peers. Need political capital.", "conversation": "Slow down to build relationships.", "assignment_setup": "Peer project.", "assignment_task": "Cross-dept interview.", "success_indicators": "Incorporated feedback.", "red_flags": "100% own idea.", "supervisor_focus": "Patience"},
        "Manager": {"shift": "Tactical -> Strategic", "why": "Prevent fires, don't just fight them.", "conversation": "Reliance on systems vs will.", "assignment_setup": "Strategic plan.", "assignment_task": "Data/Budget projection.", "success_indicators": "Systems thinking.", "red_flags": "Last minute.", "supervisor_focus": "Horizon check"}
    },
    "Encourager": {
        "Shift Supervisor": {"shift": "Friend -> Guardian", "why": "Accountability is kindness.", "conversation": "Be a guardian of the standard.", "assignment_setup": "Policy reset.", "assignment_task": "Lead accountability meeting.", "success_indicators": "No apologies.", "red_flags": "Joking.", "supervisor_focus": "Apology Language"},
        "Program Supervisor": {"shift": "Vibe -> Structure", "why": "Structure protects team.", "conversation": "Master boring parts.", "assignment_setup": "Audit.", "assignment_task": "Present data.", "success_indicators": "Accurate.", "red_flags": "Delegating.", "supervisor_focus": "Organization"},
        "Manager": {"shift": "Caregiver -> Director", "why": "Weight too heavy.", "conversation": "Set boundaries.", "assignment_setup": "Resource conflict.", "assignment_task": "Deliver No.", "success_indicators": "Holding line.", "red_flags": "Caving.", "supervisor_focus": "Burnout"}
    },
    "Facilitator": {
        "Shift Supervisor": {"shift": "Peer -> Decider", "why": "Consensus isn't safe.", "conversation": "Make 51% decision.", "assignment_setup": "Crisis drill.", "assignment_task": "Immediate calls.", "success_indicators": "Direct commands.", "red_flags": "Seeking consensus.", "supervisor_focus": "Speed"},
        "Program Supervisor": {"shift": "Mediator -> Visionary", "why": "Lead from front.", "conversation": "Inject vision.", "assignment_setup": "Culture initiative.", "assignment_task": "Present as direction.", "success_indicators": "Declarative.", "red_flags": "Asking permission.", "supervisor_focus": "The Buffer"},
        "Manager": {"shift": "Process -> Outcome", "why": "Fairness stalls.", "conversation": "Outcome over comfort.", "assignment_setup": "Unpopular policy.", "assignment_task": "Implement.", "success_indicators": "On time.", "red_flags": "Delays.", "supervisor_focus": "Conflict Tolerance"}
    },
    "Tracker": {
        "Shift Supervisor": {"shift": "Executor -> Overseer", "why": "Micromanagement burns.", "conversation": "Trust team.", "assignment_setup": "Hands-off day.", "assignment_task": "Supervise verbally.", "success_indicators": "Hands in pockets.", "red_flags": "Grabbing pen.", "supervisor_focus": "Micromanagement"},
        "Program Supervisor": {"shift": "Black/White -> Gray", "why": "Rules don't cover all.", "conversation": "Develop intuition.", "assignment_setup": "Complex complaint.", "assignment_task": "Principle decision.", "success_indicators": "Sensible exception.", "red_flags": "Freezing.", "supervisor_focus": "Rigidity"},
        "Manager": {"shift": "Compliance -> Culture", "why": "Efficiency breaks culture.", "conversation": "Invest in feelings.", "assignment_setup": "Retention.", "assignment_task": "Relationships.", "success_indicators": "Non-work chats.", "red_flags": "Checklist morale.", "supervisor_focus": "Human Element"}
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
                        if not guide:
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
                    st.markdown(f"**Why this works:** {clash['scripts'].get('script_why_staff', 'Builds psychological safety.')}")
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
                        st.markdown("##### 🗣️ The Coaching Conversation")
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
