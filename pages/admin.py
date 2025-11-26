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

# --- 5. EXTENDED CONTENT DICTIONARIES ---

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# 5a. COMMUNICATION PROFILES (Expanded)
FULL_COMM_PROFILES = {
    "Director": {
        "description": "This staff member communicates primarily as a **Director**. They lead with clarity, structure, and urgency, often serving as the 'spine' of the team during chaos. They prioritize efficiency and competence, viewing problems as obstacles to be removed quickly rather than processed emotionally.\n\nWhen communication is flowing well, they are decisive and clear. However, they may inadvertently steamroll others or move faster than the team can follow, creating a wake of confusion or resentment if not managed carefully.",
        "desc_bullets": ["Leads with 'the plan' rather than 'the feeling'", "High tolerance for conflict if it solves the problem", "Values brevity and bottom-line results", "Can appear impatient with long processing times"],
        "supervising": "To supervise them effectively, you must match their directness. Do not 'sandwich' feedback; give it to them straight. They respect competence and strength, so avoiding hard conversations will cause you to lose credibility with them.\n\nFrame relationship-building not as 'fluff' but as a strategic tool for efficiency. Help them see that taking time to listen actually speeds up adoption of their ideas.",
        "supervising_bullets": ["Be concise and clear in your directions", "Focus on outcomes rather than methods", "Respect their autonomy and need for speed", "Don't micromanage unless safety is at risk"],
        "questions": ["Where are you moving too fast for the team?", "Who haven't you heard from on this issue?", "How does your tone land when you are stressed?"]
    },
    "Encourager": {
        "description": "This staff member communicates primarily as an **Encourager**. They lead with empathy, warmth, and emotional presence, acting as the 'glue' that holds the team together during stress. They are highly attuned to the emotional climate of the unit and often serve as the first line of defense against low morale.\n\nThey prioritize relationships above all else, which makes them excellent at de-escalation but can lead to conflict avoidance. They may struggle to deliver hard news or hold firm boundaries if they fear it will damage their connection with others.",
        "desc_bullets": ["High emotional intelligence", "Values harmony and connection", "Avoids conflict to keep the peace", "Often serves as the team's confidant"],
        "supervising": "Start every interaction with connection before content. If you jump straight to business, they may feel you are cold or angry. Validate their positive intent ('I know you care deeply') before correcting the impact of their behavior.\n\nHelp them separate their personal worth from the team's happiness. They need to know they are valued even when they make mistakes or when the team is unhappy.",
        "supervising_bullets": ["Connect personally before correcting professionally", "Validate their feelings and intent", "Provide reassurance during hard feedback", "Focus on 'we' language to build partnership"],
        "questions": ["Where are you avoiding a hard conversation?", "Are you prioritizing being liked over being effective?", "What boundaries do you need to set today?"]
    },
    "Facilitator": {
        "description": "This staff member communicates primarily as a **Facilitator**. They lead by listening, building consensus, and ensuring fairness across the board. They are the 'calm bridge' who de-escalates tension and ensures all voices are heard before a decision is made.\n\nThey add immense value by preventing rash decisions and ensuring buy-in. However, they can struggle with 'analysis paralysis' or delay necessary actions because they are waiting for everyone to agree, which is not always possible.",
        "desc_bullets": ["Calm, steady presence", "Excellent listener", "Values fairness and process", "Seeks consensus before acting"],
        "supervising": "Give them time to process. Do not demand immediate decisions on complex issues if possible. They need to weigh the options. Reinforce that their slowness is a strength (deliberation), but help them define a 'hard stop' for decision making.\n\nEncourage them to speak first in meetings to prevent them from simply harmonizing with the loudest voice in the room.",
        "supervising_bullets": ["Give advance notice for changes", "Allow processing time before demanding answers", "Ask for their opinion explicitly", "Create a safe space for dissent"],
        "questions": ["Where do you need to make a 51% decision?", "Are you waiting for consensus that isn't coming?", "What is the cost of delaying this decision?"]
    },
    "Tracker": {
        "description": "This staff member communicates primarily as a **Tracker**. They lead with details, accuracy, and safety. They find comfort in rules and consistency, protecting the agency and youth by noticing the small risks that others miss. They are often the 'historian' of the unit.\n\nWhile they provide critical structure, they can become rigid or hyper-critical when stressed. They may view rule-bending as a moral failing rather than a situational necessity, which can create friction with more flexible staff.",
        "desc_bullets": ["Detail-oriented and precise", "Values structure and rules", "Risk-averse and safety-conscious", "Critical thinker who spots errors"],
        "supervising": "Provide clear, written expectations. Do not be vague. Honor their need for 'the plan.' When plans change, explain the 'why' clearly so they don't feel the change is arbitrary or unsafe.\n\nThey respect competence and consistency. If you are disorganized, you may lose their trust. Help them distinguish between 'safety-critical' rules and 'preferences' where they can flex.",
        "supervising_bullets": ["Provide written details and instructions", "Be consistent in your own leadership", "Explain the 'why' behind changes", "Respect the rules they are trying to uphold"],
        "questions": ["Are you focusing on the rule or the relationship?", "What is 'good enough' for right now?", "How can you show flexibility without losing safety?"]
    }
}

# 5b. MOTIVATION PROFILES (Expanded)
FULL_MOTIV_PROFILES = {
    "Achievement": {
        "description": "Their primary motivator is **Achievement**. They thrive when they can see progress, check boxes, and win. They hate stagnation and ambiguity. They want to know they are doing a good job based on objective evidence, not just feelings.\n\nUnderstanding this means realizing they will work incredibly hard if they can see the scoreboard, but they will burn out if the goalposts keep moving or if success is never defined.",
        "desc_bullets": ["Driven by clear goals", "Loves checking boxes", "Competitor mindset", "Results-oriented"],
        "strategies": "Set clear, measurable goals. Use visual trackers or dashboards. Celebrate 'wins' explicitly and publicly. Give them projects where they can own the result from start to finish. Avoid vague feedback like 'good job'; instead say 'You hit X target, which improved Y.'",
        "strategies_bullets": ["Use visual trackers for progress", "Define 'Done' clearly", "Celebrate wins publicly", "Give autonomy over the 'how'"],
        "celebrate": "Celebrate concrete outcomes, finished projects, improved metrics, and their reliability in getting things done.",
        "celebrate_bullets": ["Metrics improved", "Deadlines met", "Projects completed", "Reliability under pressure"],
        "questions": ["How are you defining success today beyond just metrics?", "Are you celebrating the small wins?", "Who helped you win this week?"]
    },
    "Growth": {
        "description": "Their primary motivator is **Growth**. They thrive when they are learning, stretching, and mastering new skills. They hate feeling stuck or bored. They view their role as a stepping stone to greater competence and are constantly looking for the 'next level.'\n\nThey are energized by feedback, provided it is constructive and helps them level up. If they feel they aren't growing, they will likely disengage or leave.",
        "desc_bullets": ["Learner mindset", "Seeks challenges", "Future-focused", "Curious and inquisitive"],
        "strategies": "Feed their curiosity. Assign them 'stretch' projects that require new skills. Frame feedback as 'coaching' for their future career. Connect mundane tasks to their long-term professional development. Ask them: 'What do you want to learn next?'",
        "strategies_bullets": ["Assign stretch projects", "Provide mentorship opportunities", "Discuss career pathing regularly", "Offer training and development"],
        "celebrate": "Celebrate new skills learned, adaptability, taking on new challenges, and their personal development trajectory.",
        "celebrate_bullets": ["Skills mastered", "Adaptability in crisis", "Initiative to learn", "Personal growth milestones"],
        "questions": ["What are you learning from this struggle?", "Are you expecting too much too soon from others?", "How are you feeding your own curiosity?"]
    },
    "Purpose": {
        "description": "Their primary motivator is **Purpose**. They thrive when they feel their work aligns with deep values and makes a real difference for kids. They hate bureaucracy that feels meaningless or performative.\n\nThey will endure difficult conditions if they believe the 'Why' is noble, but they will rebel against policies that feel unjust. They need to feel they are part of a cause, not just a company.",
        "desc_bullets": ["Values-driven", "Mission-focused", "Advocate for the vulnerable", "Ethical and principled"],
        "strategies": "Connect every rule to a 'Why.' Validate their passion for justice and advocacy. Share specific stories of their impact on youth. When assigning tasks, explain how this helps the youth or the mission. Allow them space to voice ethical concerns without judgment.",
        "strategies_bullets": ["Explain the 'Why' behind tasks", "Share impact stories", "Validate their advocacy", "Connect daily work to mission"],
        "celebrate": "Celebrate their advocacy for youth, their integrity, ethical decision making, and specific 'mission moments' where they changed a life.",
        "celebrate_bullets": ["Advocacy wins", "Ethical choices", "Client impact stories", "Integrity in difficult moments"],
        "questions": ["How does this boring task connect to the mission?", "Where are you feeling moral distress?", "How can you advocate effectively right now?"]
    },
    "Connection": {
        "description": "Their primary motivator is **Connection**. They thrive when they feel part of a tight-knit team. They hate isolation and unresolved conflict. For them, the 'who' is more important than the 'what.'\n\nIf the team is fractured, their performance will suffer, no matter how clear the tasks are. They need to feel a sense of belonging and safety within the group to function at their best.",
        "desc_bullets": ["Team-oriented", "Relational", "Values belonging", "Harmony-seeker"],
        "strategies": "Prioritize face time. Check in on them as a person, not just an employee. Build team rituals (food, shout-outs). Ensure they don't work in a silo. When giving feedback, reassure them of their belonging in the team.",
        "strategies_bullets": ["Personal check-ins", "Team rituals and bonding", "Face-to-face time", "Reassurance of belonging"],
        "celebrate": "Celebrate team cohesion, their support of peers, morale building, and their role in conflict resolution.",
        "celebrate_bullets": ["Team building efforts", "Supporting peers", "Positive attitude", "Conflict repair"],
        "questions": ["Who do you need to check in with today?", "Are you taking this team conflict personally?", "How can you build belonging in this meeting?"]
    }
}

# 5c. INTEGRATED PROFILES (Expanded & 10 Coaching Questions Logic)
def get_integrated_data(comm, motiv):
    # BASE DATA FOR EACH COMBINATION
    profiles = {
        "Director-Achievement": {
            "summary": "This staff member leads with a high-drive, decisive style to achieve concrete wins. They are the 'General' of the unit. They want to win, and they want to do it fast. They are excellent at operationalizing goals but may run over people to get there.\n\nThey are at their best when the objective is clear and the timeline is tight. They struggle when the work requires slow, relational tending without immediate visible results.",
            "support": "Partner to define realistic pacing. Set process goals (we did the steps) not just outcome goals (the kid behaved). Contextualize metrics so they aren't personal verdicts.",
            "thriving": "- High follow-through on tasks\n- Sets clear goals for the team\n- Moves metrics in the right direction\n- Decisive in crisis",
            "struggling": "- Treats trauma behavior as a problem to 'solve' quickly\n- Micromanages peers\n- Judges self harshly when metrics dip\n- Becomes impatient with 'slow' staff",
            "interventions": "Contextualize metrics. Celebrate the 'small wins' so they don't burn out chasing perfection. Remind them that relationships are the vehicle for results.",
            "integrated_questions": ["How are you defining success today?", "What is one win you can celebrate right now?", "Are you driving the team too hard?", "What is the cost of speed right now?"]
        },
        "Director-Growth": {
            "summary": "This staff member leads with decisive action and is hungry to improve. They are a restless improver. They lead by pushing the pace of change and expecting everyone to level up. They can be impatient with stagnation.\n\nThey are excellent change agents but risk leaving their team behind. They need to learn that not everyone moves at their speed.",
            "support": "Ask for a small number of focused projects rather than trying to fix everything at once. Co-design development goals. Give them autonomy to pilot new ideas.",
            "thriving": "- Quick to turn learning into practice\n- Coaches peers effectively\n- Refines decisions based on new data\n- Innovative problem solver",
            "struggling": "- Moves faster than the team can handle\n- Becomes impatient with 'slow' learners\n- Defaults to control in crisis\n- Changes things too often",
            "interventions": "Slow down. Focus on one change at a time. Ask: 'Who is left behind by this speed?' Help them pace their ambition.",
            "integrated_questions": ["What is one way you can slow down for others?", "How are you measuring your own growth beyond just speed?", "Are you leaving the team behind?", "Is this change necessary right now?"]
        },
        "Director-Purpose": {
            "summary": "This staff member is driven to make clear, firm decisions that align with deep values. They are a 'Warrior for the Cause.' They use their strength to fight for what is right. They are fierce advocates but can be rigid if they feel the mission is compromised.\n\nThey will go to the mat for a kid, but they may burn bridges with administration in the process if they feel ignored.",
            "support": "Share your top core values so they understand your decisions. Translate clinical values into concrete rules. Allow them space to advocate before deciding.",
            "thriving": "- Advocates strongly for youth safety\n- Holds boundaries even when unpopular\n- Seen as a moral anchor\n- Protects the team from bad policy",
            "struggling": "- Becomes rigid or righteous when values are threatened\n- Excessive frustration with 'the system'\n- Moral outrage\n- Refusal to compromise",
            "interventions": "Validate the value (e.g. safety) before asking for flexibility. Help them pick battles. Connect compliance to client care.",
            "integrated_questions": ["Where do you feel the system is failing your values?", "How can you advocate without burning bridges?", "Is this a hill worth dying on?", "How does flexibility serve the mission here?"]
        },
        "Director-Connection": {
            "summary": "This staff member wants the team to feel supported but communicates with directness. They are a 'Protective Captain.' They lead the team firmly but doing so to protect the 'tribe.' They want the team to be strong and successful together.\n\nThey can confuse the team by switching between 'Authoritarian' and 'Best Friend' depending on their stress level.",
            "support": "Script phrases that are both firm and relational. Schedule short relational touchpoints during tough weeks. Reassure them that directness doesn't mean disconnection.",
            "thriving": "- Anchors the team in crisis while checking on feelings\n- Firm but not distant\n- Protective of the team\n- Clear communication",
            "struggling": "- Holds back hard conversations to avoid being 'mean'\n- Swings between 'all business' and 'all buddy'\n- Personalizes conflict\n- Over-protects the team",
            "interventions": "Role-play the 'Hard Conversation' so they feel safe being direct. Remind them that clarity is kindness. Validate their intent to protect.",
            "integrated_questions": ["Are you avoiding this conversation to be kind, or to be safe?", "How can you be direct and caring at the same time?", "Are you protecting them from growth?", "How is the team reacting to your directness?"]
        },
        "Encourager-Achievement": {
            "summary": "This staff member wants the team to feel good *and* win. They are the 'Coach' who cheers the loudest. They want people to feel good and do well. Motivated when encouragement translates into visible progress.\n\nThey struggle deeply when the team is happy but losing (poor outcomes). They may feel like a personal failure if the vibe is good but the metrics are bad.",
            "support": "Define realistic progress for complex youth. Build in micro-celebrations. Help them see that 'good vibes' aren't the only metric of success.",
            "thriving": "- Celebrates wins constantly\n- Makes goals feel inspiring\n- Energizes the team to try new things\n- High morale and high effort",
            "struggling": "- Pushes too hard on 'potential'\n- Feels personally failed when goals aren't met\n- Focuses only on big wins\n- Burnout from cheering",
            "interventions": "Redefine success: 'Success is sticking to the plan, not fixing the kid'. Help them separate their worth from the outcome.",
            "integrated_questions": ["How can you celebrate effort, not just the result?", "Are you taking their failure personally?", "Is the team winning, or just happy?", "What helps you stay motivated when results are slow?"]
        },
        "Encourager-Growth": {
            "summary": "This staff member loves helping people grow. They are a 'Natural Mentor.' They use their warmth to help people grow. They are excellent with new staff but may struggle to give hard feedback that might hurt feelings.\n\nThey see potential in everyone, sometimes to a fault. They may keep investing in staff or youth who are not showing signs of change, leading to exhaustion.",
            "support": "Help them choose a small number of people to invest in so they don't spread thin. Pair encouragement with specific targets. Validate their mentorship role.",
            "thriving": "- Natural mentor\n- Youth feel believed in\n- Invests in peer development\n- Creates a culture of learning",
            "struggling": "- Overcommits emotional energy\n- Avoids sharp feedback to spare feelings\n- Discouraged when others don't grow\n- Burnout",
            "interventions": "Teach them to give 'Radical Candor'. Remind them they can't grow *for* other people. Set boundaries on their time.",
            "integrated_questions": ["Who are you working harder than right now?", "How can you give feedback that helps them grow?", "Are you enabling or empowering?", "What is one hard truth they need to hear?"]
        },
        "Encourager-Purpose": {
            "summary": "This staff member is fueled by connection and meaning. They are the 'Heart of the Mission.' They keep the emotional flame alive. They are deeply impacted by youth suffering and need help with emotional boundaries.\n\nThey are the soul of the unit but can be crushed by the weight of the trauma they witness.",
            "support": "Regular debriefs to process emotional load. Use values-based language for accountability. Connect their daily care to the big picture.",
            "thriving": "- Catches when people feel unseen\n- Translates clinical concepts into human terms\n- Safe harbor for staff\n- High empathy",
            "struggling": "- Carries heavy emotional weight\n- Struggles to enforce consequences on 'sad' cases\n- Heartbroken by outcomes\n- Enmeshment",
            "interventions": "Focus on 'Boundaries as Care'. Help them release what they cannot control. Validate their heart but reinforce structure.",
            "integrated_questions": ["What emotional weight are you carrying that isn't yours?", "How does holding this boundary actually help the youth?", "Are you taking care of yourself?", "Where is your empathy causing burnout?"]
        },
        "Encourager-Connection": {
            "summary": "This staff member is a community builder. They are the ultimate 'Team Builder.' They prioritize harmony above all else. They create a safe culture but may avoid conflict to a fault.\n\nThey are terrified of breaking the bond, so they may tolerate bad behavior from staff or youth rather than risk an uncomfortable interaction.",
            "support": "Practice scripts that connect and correct simultaneously. Plan for hard conversations in advance. check in on *them* personally.",
            "thriving": "- Makes staff feel safe\n- De-escalates through relationship\n- Repairs team conflict\n- Strong sense of 'family'",
            "struggling": "- Avoids addressing harm to keep the peace\n- Takes tension personally\n- Prioritizes harmony over safety\n- Cliques",
            "interventions": "Challenge them: 'Is avoiding this conflict actually helping the team, or hurting safety?' Push for brave conversations.",
            "integrated_questions": ["Are you prioritizing peace or safety?", "How can you lean into conflict to build stronger connection?", "What is the cost of avoiding this issue?", "Who is being hurt by the lack of boundaries?"]
        },
        "Facilitator-Achievement": {
            "summary": "This staff member is steady and gentle, but wants to get things done. They want to reach goals without leaving anyone behind. They move slowly but steadily. They are annoyed by inefficiency but won't voice it loudly.\n\nThey are the 'Quiet Mover.' They don't make a lot of noise, but they want progress. They can become passive-aggressive if others block that progress.",
            "support": "Practice: 'I care about you, and this expectation is important.' Use clear follow-ups. Validate their methodical approach.",
            "thriving": "- Paces goals well\n- Helps staff understand improvement is a journey\n- Calm approach to metrics\n- Steady progress",
            "struggling": "- Apologizes for having expectations\n- Quietly frustrated when others fail\n- Under-communicates urgency\n- Passive-aggressive",
            "interventions": "Teach them that clear expectations reduce anxiety. Ambiguity is not kindness. Give them permission to lead.",
            "integrated_questions": ["How can you be clearer about what you need?", "Are you apologizing for having standards?", "What needs to move faster?", "Where are you holding back your authority?"]
        },
        "Facilitator-Growth": {
            "summary": "This staff member creates calm space for growth. They facilitate learning. They create safe spaces for staff to make mistakes and learn. They are patient teachers but need to ensure they don't tolerate incompetence too long.\n\nThey are the 'Patient Gardener.' They believe things grow in their own time, but in a crisis, they may need to prune faster than they are comfortable with.",
            "support": "Practice naming care and expectations in the same sentence. Break growth steps into small actions. Validate their patience.",
            "thriving": "- Excellent reflective supervisor\n- Safe for youth to open up to\n- Paces change sustainably\n- Deep listener",
            "struggling": "- Avoids sharp expectations\n- Underestimates need for structure\n- Overthinks instead of acting\n- Paralysis",
            "interventions": "Push for the 'Decisive Moment'. Help them value their authority as a tool for growth. Set deadlines for decisions.",
            "integrated_questions": ["Where are you hesitating to lead?", "How can you be kind and firm at the same time?", "Are you waiting too long to act?", "What is the risk of doing nothing?"]
        },
        "Facilitator-Purpose": {
            "summary": "This staff member is a steady presence with a deep sense of right. They are the 'Moral Compass.' They ensure decisions are fair and just. They will slow down a process to ensure it aligns with values.\n\nThey are the conscience of the team. They won't shout, but they will stubbornly refuse to move if something feels unethical.",
            "support": "Use supervision to talk about moral tension. Encourage them to voice concerns early. validate their ethical lens.",
            "thriving": "- Maintains respectful climate\n- Holds space for hard feelings\n- Strong moral anchor\n- Fairness advocate",
            "struggling": "- Quietly carries moral distress\n- Stays neutral too long\n- Stuck when leadership disagrees with values\n- Withdrawal",
            "interventions": "Encourage them to be the 'Voice of Conscience' loudly, not just quietly. Help them navigate grey areas.",
            "integrated_questions": ["What moral tension are you holding right now?", "How can you speak up for your values effectively?", "Are you staying neutral when you should take a stand?", "How does your silence impact the team?"]
        },
        "Facilitator-Connection": {
            "summary": "This staff member is the calm, relational glue. They are the 'Peacemaker.' They ensure the team stays cohesive. They absorb a lot of emotional toxicity to keep the peace and risk burnout.\n\nThey are the shock absorber for the unit. Everyone feels better after talking to them, but they often feel worse.",
            "support": "Script accountability conversations. Set boundaries on how much emotional processing they do for others. Protect their peace.",
            "thriving": "- Helps peers feel understood\n- De-escalates steady\n- Fosters help-seeking culture\n- Low drama",
            "struggling": "- Absorbs emotional labor\n- Struggles to set limits\n- Listens when they should be deciding\n- Compassion fatigue",
            "interventions": "Validate their role as 'Stabilizer' but require them to also be 'Director' when safety is at risk. Mandate self-care.",
            "integrated_questions": ["What boundaries do you need to set to protect your energy?", "Are you listening too much and leading too little?", "Who is taking care of you?", "Is your silence creating confusion?"]
        },
        "Tracker-Achievement": {
            "summary": "This staff member wants strong results via good systems. They are the 'Architect.' They build systems to ensure success. They love data and dislike chaos. They effectively turn vague goals into concrete plans.\n\nThey believe that if you follow the process, you get the result. They get very frustrated when people improvise and break the system.",
            "support": "Pair data shares with appreciation. Contextualize metrics so they aren't personal verdicts. Give them ownership of the 'How'.",
            "thriving": "- Strong at tracking metrics\n- Clear sense of 'good'\n- Insists on consistent routines\n- Reliable results",
            "struggling": "- Impatient with struggle\n- Focuses on reporting over empathy\n- Ties self-worth to numbers\n- Rigid",
            "interventions": "Humanize the data. 'The chart is just a tool, not the goal.' Focus on effort. Encourage flexibility.",
            "integrated_questions": ["How can you measure effort, not just outcome?", "Are you valuing the data more than the person?", "Where is flexibility needed right now?", "How can you support the person, not just the process?"]
        },
        "Tracker-Growth": {
            "summary": "This staff member loves accurate info and improvement. They are the 'Technical Expert.' They master the details and expect others to study the craft. They improve the unit by refining processes.\n\nThey are the master craftsman. They want everyone to take the work as seriously as they do.",
            "support": "Pick a few key processes to improve. Pair process changes with relational steps. Validate their expertise.",
            "thriving": "- Notices patterns in incidents\n- Keeps documentation tight\n- Helps peers improve process\n- Subject matter expert",
            "struggling": "- Frustrated by details others miss\n- Over-focuses on systems over people\n- Hesitates in crisis\n- Perfectionism",
            "interventions": "Help them zoom out. 'Perfection is the enemy of good'. Focus on 'Good Enough' for now. Delegate the mess.",
            "integrated_questions": ["Are you focusing on the system or the person?", "What is 'good enough' for today?", "Are you correcting or coaching?", "How can you make it safe to make mistakes?"]
        },
        "Tracker-Purpose": {
            "summary": "This staff member wants things done right because it matters for kids. They are the 'Guardian.' They use rules to protect the mission. They believe safety is the highest form of care. They can be rigid about compliance.\n\nThey see rules as sacred vows to the clients. Breaking a rule isn't just an error; it's a betrayal.",
            "support": "Process the heavy sense of responsibility. Share the 'Why' behind standards with staff. Connect rules to safety.",
            "thriving": "- Protects youth via safety checks\n- Notices small risks\n- Translates values into concrete practice\n- Safe environment",
            "struggling": "- Intolerant of carelessness\n- Distressed by shortcuts\n- Leans on rules when anxious\n- Policing others",
            "interventions": "Remind them: 'You are responsible for the process, not the outcome.' Release the weight. Focus on intent.",
            "integrated_questions": ["How can you protect the mission without being rigid?", "Are you using rules to manage your anxiety?", "Is this rule serving the child right now?", "How can you explain the 'why' behind the rule?"]
        },
        "Tracker-Connection": {
            "summary": "This staff member cares about getting it right and caring for people. They are the 'Reliable Rock.' They show care by being consistent. They aren't warm and fuzzy, but they are always there. They build trust through stability.\n\nThey show love by doing the paperwork correctly so you don't have to. They feel unloved when you don't notice.",
            "support": "Add relational check-ins before details. Share tasks instead of hoarding them. Notice their quiet reliability.",
            "thriving": "- Gives grounded, specific support\n- Consistency feels safe to youth\n- Safe person for technical questions\n- Steady",
            "struggling": "- Assumes people know they care (they don't)\n- Becomes the 'Do-Everything' person\n- Burnout risk\n- Resentment",
            "interventions": "Force delegation. 'If you do it for them, you rob them of the learning'. Encourage verbalizing care.",
            "integrated_questions": ["How can you show care in a way they understand?", "Are you doing too much for others?", "Do they know you care?", "Where do you need help carrying the load?"]
        }
    }

    key = f"{comm}-{motiv}"
    data = profiles.get(key, profiles["Director-Achievement"])

    # 10 Coaching Questions Assembly
    questions = []
    
    # 3 from Comm Style
    if comm in FULL_COMM_PROFILES:
        questions += FULL_COMM_PROFILES[comm]["questions"]
    
    # 3 from Motivation
    if motiv in FULL_MOTIV_PROFILES:
        questions += FULL_MOTIV_PROFILES[motiv]["questions"]

    # 4 from Integrated (defined above)
    if "integrated_questions" in data:
        questions += data["integrated_questions"]
    
    # Fallback if missing
    while len(questions) < 10:
        questions.append("What support do you need right now?")

    return {
        "s1": FULL_COMM_PROFILES.get(comm, {}).get("description", ""),
        "s2": FULL_COMM_PROFILES.get(comm, {}).get("supervising", ""),
        "s3": FULL_MOTIV_PROFILES.get(motiv, {}).get("description", ""),
        "s4": FULL_MOTIV_PROFILES.get(motiv, {}).get("strategies", ""),
        "s5": data['summary'],
        "s6": data['support'],
        "s7": data['thriving'],
        "s8": data['struggling'],
        "s9": data['interventions'],
        "s10": FULL_MOTIV_PROFILES.get(motiv, {}).get("celebrate", ""),
        "coaching": questions,
        # Bullet lists
        "comm_bullets": FULL_COMM_PROFILES.get(comm, {}).get("desc_bullets", []),
        "sup_bullets": FULL_COMM_PROFILES.get(comm, {}).get("supervising_bullets", []),
        "motiv_bullets": FULL_MOTIV_PROFILES.get(motiv, {}).get("desc_bullets", []),
        "strat_bullets": FULL_MOTIV_PROFILES.get(motiv, {}).get("strategies_bullets", []),
        "cel_bullets": FULL_MOTIV_PROFILES.get(motiv, {}).get("celebrate_bullets", [])
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
                pdf.multi_cell(0, 5, clean_text(b))
        
        # Handle embedded bullets in summary strings
        if "\n-" in body:
            pass 
             
        pdf.ln(4)

    # 1. Communication Profile
    add_section(f"1. Communication Profile: {p_comm}", data['s1'], data['comm_bullets'])
    
    # 2. Supervising Their Communication
    add_section("2. Supervising Their Communication", data['s2'], data['sup_bullets'])
    
    # 3. Motivation Profile
    add_section(f"3. Motivation Profile: {p_mot}", data['s3'], data['motiv_bullets'])
    
    # 4. Motivating This Staff Member
    add_section("4. Motivating This Staff Member", data['s4'], data['strat_bullets'])
    
    # 5. Integrated Leadership Profile
    add_section("5. Integrated Leadership Profile", data['s5'])
    
    # 6. How You Can Best Support Them
    add_section("6. How You Can Best Support Them", data['s6'])
    
    # 7. Thriving Signs
    add_section("7. What They Look Like When Thriving", data['s7'])
    
    # 8. Struggling Signs
    add_section("8. What They Look Like When Struggling", data['s8'])
    
    # 9. Interventions
    add_section("9. Supervisory Interventions", data['s9'])
    
    # 10. Celebrate
    add_section("10. What You Should Celebrate", data['s10'], data['cel_bullets'])

    # 11. Coaching Questions
    if 'coaching' in data:
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, "11. Coaching Questions", ln=True, fill=True); pdf.ln(2)
        pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
        for i, q in enumerate(data['coaching']):
            pdf.multi_cell(0, 5, clean_text(f"{i+1}. {q}"))
        pdf.ln(4)

    # 12. Advancement
    adv_text = "Help them master the operational side. Challenge them to see clarity and accountability as kindness."
    if p_comm == "Director": adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn."
    elif p_comm == "Encourager": adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness."
    elif p_comm == "Facilitator": adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible."
    elif p_comm == "Tracker": adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance."
    
    add_section("12. Helping Them Prepare for Advancement", adv_text)

    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---"); st.markdown(f"### 📘 Supervisory Guide: {name}"); st.divider()
    
    st.subheader(f"1. Communication Profile: {p_comm}")
    st.write(data['s1'])
    for b in data['comm_bullets']: st.markdown(f"- {b}")
    
    st.subheader("2. Supervising Their Communication")
    st.write(data['s2'])
    for b in data['sup_bullets']: st.markdown(f"- {b}")
    
    st.subheader(f"3. Motivation Profile: {p_mot}")
    st.write(data['s3'])
    for b in data['motiv_bullets']: st.markdown(f"- {b}")
    
    st.subheader("4. Motivating This Staff Member")
    st.write(data['s4'])
    for b in data['strat_bullets']: st.markdown(f"- {b}")
    
    st.subheader("5. Integrated Leadership Profile")
    st.info(data['s5'])
    
    st.subheader("6. How You Can Best Support Them")
    st.write(data['s6'])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("7. Thriving")
        st.success(data['s7']) 
    with c2:
        st.subheader("8. Struggling")
        st.error(data['s8']) 
    
    st.subheader("9. Supervisory Interventions")
    st.write(data['s9'])
    
    st.subheader("10. What You Should Celebrate")
    st.write(data['s10'])
    for b in data['cel_bullets']: st.markdown(f"- {b}")
    
    st.subheader("11. Coaching Questions")
    for i, q in enumerate(data['coaching']):
        st.write(f"{i+1}. {q}")
            
    st.subheader("12. Helping Them Prepare for Advancement")
    adv_text = "Help them master the operational side. Challenge them to see clarity and accountability as kindness."
    if p_comm == "Director": adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn."
    elif p_comm == "Encourager": adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness."
    elif p_comm == "Facilitator": adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible."
    elif p_comm == "Tracker": adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance."
    st.write(adv_text)

# --- 7. MAIN APP LOGIC ---
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
