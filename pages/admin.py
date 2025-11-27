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

# --- 5. EXTENDED CONTENT DICTIONARIES ---

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

# --- EXTENDED DICTIONARIES ---

TEAM_CULTURE_GUIDE = {
    "Director": {
        "title": "The Command Center",
        "impact_analysis": "This team moves fast and breaks things. They are highly efficient but likely suffering from low psychological safety. Quiet voices are being steamrolled.",
        "management_strategy": "**Slow Down.** Force them to pause and debate. Protect the dissenters. Assign a 'Devil's Advocate' in every meeting.",
        "meeting_protocol": "No interruptions allowed. 2-minute silence after a proposal to think before speaking.",
        "team_building": "Empathy maps or vulnerability exercises (which they will hate, but need)."
    },
    "Encourager": {
        "title": "The Social Hub",
        "impact_analysis": "This team has high morale but low accountability. They avoid hard conversations and tolerate underperformance to keep the peace.",
        "management_strategy": "**Tighten Up.** Focus on results and deadlines. Normalize 'healthy conflict' as a tool for growth, not a threat to safety.",
        "meeting_protocol": "Start with 'Where are we failing?' to break the toxic positivity.",
        "team_building": "Debate club or competitive goal-setting."
    },
    "Facilitator": {
        "title": "The United Nations",
        "impact_analysis": "This team is fair and inclusive but suffers from analysis paralysis. Decisions take forever because they wait for consensus.",
        "management_strategy": "**Speed Up.** Set hard deadlines for decisions. Teach 'Disagreement and Commitment'.",
        "meeting_protocol": "The '51% Rule': If we are 51% sure, we move. No revisiting decisions.",
        "team_building": "Escape rooms (forcing time-bound decisions)."
    },
    "Tracker": {
        "title": "The Audit Team",
        "impact_analysis": "This team is safe and compliant but rigid. They fear change and will quote policy to stop innovation. They lack flexibility.",
        "management_strategy": "**Loosen Up.** Focus on the 'spirit of the law', not just the letter. Reward creative problem solving.",
        "meeting_protocol": "Ban the phrase 'We've always done it this way'.",
        "team_building": "Improv games (forcing adaptability)."
    },
    "Balanced": {
        "title": "The Balanced Team",
        "impact_analysis": "No single style dominates.",
        "management_strategy": "Act as a translator between styles.",
        "meeting_protocol": "Round robin input.",
        "team_building": "Role swapping."
    }
}

MISSING_VOICE_GUIDE = {
    "Director": {"risk": "No one is driving the bus. Decisions linger and urgency is low.", "fix": "You must be the bad guy. Set shorter deadlines and demand 'bottom lines'."},
    "Encourager": {"risk": "The team is cold and transactional. Burnout is high because no one feels cared for.", "fix": "Start every meeting with a personal check-in. Celebrate birthdays and wins aggressively."},
    "Facilitator": {"risk": "Steamrolling. The loudest voices win, and quiet dissenters check out.", "fix": "Use round-robin speaking. Don't let anyone speak twice until everyone speaks once."},
    "Tracker": {"risk": "Chaos. Details are dropped, and safety issues are missed.", "fix": "Create checklists. Assign a 'Safety Captain' to review plans for risks."}
}

SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "Efficiency vs. Empathy (Safety as Control vs. Safety as Connection)",
            "psychology": "This is the classic 'Oil and Water' dynamic. You (Director) find safety in speed, competence, and checking boxes. You view 'feelings' as variables that slow down the mission. \n\nThe Encourager finds safety in connection and harmony. When you push for speed or deliver blunt feedback, they don't just hear 'work instructions'—they feel an existential threat to the group's safety. They retreat because they feel steamrolled; you push harder because you think they are incompetent.",
            "watch_fors": [
                "**The 'Shut Down':** If they go silent, they aren't agreeing with you. They are protecting themselves from your intensity.",
                "**The 'Smile & Nod':** They may agree to a deadline they know they can't meet just to end the uncomfortable interaction.",
                "**Venting:** They will likely process their hurt feelings with peers, creating a 'shadow culture' you aren't part of."
            ],
            "intervention_steps": [
                "**1. Disarm the Threat (Why: They are in fight/flight):** Lower your volume and physical pace. Sit down. Do not start with the task; start with the person. 'How are you feeling about the shift today?'",
                "**2. Translate the Intent (Why: They think you are angry):** Explicitly state that your intensity is about the *problem*, not them. 'I am frustrated with the schedule, not with you. I value you.'",
                "**3. The 'Sandwich' Reframe (Why: They need safety to hear truth):** You hate feedback sandwiches, but they need them. Affirm the relationship, give the correction, affirm the future. It is not 'fluff'; it is the toll you pay to get on the bridge."
            ],
            "scripts": {
                "Opening": "I want to talk about [Task], but first I want to check in. I've been moving fast today—how is the team feeling?",
                "Validation": "I know my communication style can feel intense or abrupt. I validate that you prioritize the team's morale, and I don't want to damage that.",
                "The Pivot": "However, we do need to solve [Problem]. My concern is that if we don't fix this, the team will suffer in the long run.",
                "Crisis": "I need to be very direct right now because of the safety risk. This isn't personal, but I need you to do X immediately.",
                "Feedback": "I value how much the team loves you. To grow, I need you to be able to hear hard news without feeling like I'm attacking your character."
            }
        },
        "Facilitator": {
            "tension": "Speed vs. Process (Urgency vs. Fairness)",
            "psychology": "You (Director) value 'Done'. They (Facilitator) value 'Fair'. You see their desire for meetings and consensus as 'Analysis Paralysis' and a waste of time. They see your desire for quick decisions as reckless and exclusive.\n\nThey are terrified of leaving someone behind. You are terrified of missing the opportunity. You are fighting for results; they are fighting for legitimacy.",
            "watch_fors": [
                "**The 'We Need to Talk':** They will try to schedule meetings to delay decisions they feel were made too fast.",
                "**Passive Resistance:** They won't argue, but they won't implement the plan because they feel 'the team wasn't consulted'.",
                "**Moral High Ground:** They may subtly frame your speed as 'uncaring' or 'undemocratic'."
            ],
            "intervention_steps": [
                "**1. Define the Sandbox (Why: They need parameters):** Give them a clear deadline. 'We need to decide this by 3:00 PM.'",
                "**2. Assign the 'Who' (Why: They fear exclusion):** Ask them specifically: 'Who are the critical 3 people we need to ask?' Limit it to 3.",
                "**3. The 'Good Enough' Agreement (Why: They want perfection):** Remind them that a good decision today is better than a perfect decision next week. Ask: 'Is this safe enough to try?'"
            ],
            "scripts": {
                "Opening": "I know this decision feels rushed. I want to respect the process, but we have a tight timeline.",
                "Validation": "I value that you want everyone to be heard. You are the moral compass of the team.",
                "The Pivot": "The risk we face is that if we don't decide by noon, we lose the option entirely. We have to move.",
                "Crisis": "In this specific moment, I have to make the call. We can debrief the process later, but right now, follow my lead.",
                "Feedback": "Your desire for consensus is a strength, but sometimes it becomes a bottleneck. I need you to be willing to make the '51% decision'."
            }
        }
    },
    "Encourager": {
        "Director": {
            "tension": "Warmth vs. Competence (Being Liked vs. Being Effective)",
            "psychology": "You (Encourager) value harmony and feeling connected. You interpret their (Director) lack of small talk and directness as dislike or anger. You feel unsafe around them.\n\nThey interpret your focus on feelings as incompetence or lack of focus. When you try to 'nice' them into compliance, they lose respect for you. They don't want a friend; they want a leader who can remove obstacles.",
            "watch_fors": [
                "**Apologizing:** You apologizing for giving them work to do.",
                "**Taking it Personally:** You going home feeling hurt because they didn't say 'good morning' enthusiastically.",
                "**Avoidance:** You emailing them instead of talking to them because you fear the conflict."
            ],
            "intervention_steps": [
                "**1. Cut the Fluff (Why: They value time):** Do not ask about their weekend for 10 minutes. Start with the headline. 'I need your help with X.'",
                "**2. Stand Your Ground (Why: They respect strength):** If they push back, do not fold. State your reasoning calmly. 'I hear you, but the policy is X, and that's what we are doing.'",
                "**3. Ask for Input (Why: They want to solve problems):** Frame the relationship issue as a problem. 'I feel like we are missing each other. How can I communicate better with you?'"
            ],
            "scripts": {
                "Opening": "I'm going to get straight to the point because I know you value your time.",
                "Validation": "I know you are focused on getting this done, and I appreciate your efficiency.",
                "The Pivot": "However, the way you spoke to the team caused a shutdown. We can't be efficient if no one wants to work for you.",
                "Crisis": "Stop. I need you to listen to me right now. This is a safety issue.",
                "Feedback": "You are excellent at tasks, but your delivery is costing you relationship capital. You are right on the facts, but wrong on the approach."
            }
        }
    },
    "Facilitator": {
        "Tracker": {
            "tension": "Consensus vs. Compliance (People vs. Policy)",
            "psychology": "You (Facilitator) want the team to agree on a solution that feels fair. They (Tracker) want the team to follow the written rule because that is safe.\n\nYou feel they are being rigid and uncaring 'robots'. They feel you are being reckless and treating safety rules as 'suggestions'. You prioritize the human element; they prioritize the systemic element.",
            "watch_fors": [
                "**The Policy War:** They quote the handbook; you quote the 'vibe' or the 'context'.",
                "**Ignoring:** You ignoring their emails about compliance because it feels like nagging.",
                "**Anxiety:** They getting visibly anxious when you say 'let's just see how it goes'."
            ],
            "intervention_steps": [
                "**1. Validate the Rule (Why: They need to know you aren't reckless):** Start by acknowledging the policy. 'I know the rule is X.'",
                "**2. Contextualize the Exception (Why: They need a reason):** Explain *why* this specific human situation requires a bend. 'Because of [Client's] history, we need to adapt.'",
                "**3. Define the New Boundary (Why: They fear chaos):** Create a new, temporary rule for this situation so they feel there is still a plan."
            ],
            "scripts": {
                "Opening": "I know this plan deviates from our standard SOP, and I want to explain why.",
                "Validation": "I appreciate you keeping us compliant. You protect the agency's license.",
                "The Pivot": "In this specific case, following the rule to the letter will cause a behavioral escalation. We need to flex here to maintain safety.",
                "Crisis": "I am taking responsibility for this exception. Please document that I made this call.",
                "Feedback": "I need you to see the gray areas. The rulebook is a map, but the territory is real people."
            }
        }
    }
}

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Delegating'",
            "why": "Directors are great individual contributors because they are fast. They struggle to let go of control because they think they can do it better/faster themselves.",
            "conversation": "You are the quarterback, not the receiver. If you are holding the ball, you aren't leading.",
            "assignment_setup": "Run a shift from the office chair.",
            "assignment_task": "Do not intervene on the floor for 2 hours unless there is imminent danger. Direct others to solve the problems.",
            "success_indicators": "The team solved problems without them physically stepping in.",
            "red_flags": "They ran out to 'save' the shift the moment it got loud.",
            "supervisor_focus": "Watch for them getting frustrated with how slow others are."
        },
        "Program Supervisor": {
            "shift": "From 'Delegating' to 'Developing'",
            "why": "They prioritize efficiency over people development.",
            "conversation": "Efficiency is not the only metric. You need to build a bench.",
            "assignment_setup": "Mentor a struggling staff member.",
            "assignment_task": "Coach a peer through a task rather than doing it for them.",
            "success_indicators": "The peer learned a new skill.",
            "red_flags": "They just gave the peer the answer."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Boss'",
            "why": "They value harmony and relationships. Correcting peers feels like a betrayal of friendship.",
            "conversation": "Being liked is not the goal. Being respected and safe is the goal.",
            "assignment_setup": "Audit a friend's documentation.",
            "assignment_task": "Deliver corrective feedback to a peer regarding a documentation error.",
            "success_indicators": "They delivered the hard news clearly without apologizing for doing their job.",
            "red_flags": "They softened the message so much the point was lost.",
            "supervisor_focus": "Watch for them apologizing for having authority."
        },
        "Program Supervisor": {
            "shift": "From 'Harmony' to 'Standards'",
            "why": "They tolerate mediocrity to keep the peace.",
            "conversation": "To lead the program, you must set the standard.",
            "assignment_setup": "Lead a team meeting.",
            "assignment_task": "Address a team-wide performance issue (e.g., lateness).",
            "success_indicators": "They spoke directly about the issue.",
            "red_flags": "They turned it into a 'suggestion' rather than an expectation."
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Input' to 'Decision'",
            "why": "They get stuck in 'Analysis Paralysis' trying to make everyone happy.",
            "conversation": "Consensus is a luxury we don't always have in a crisis.",
            "assignment_setup": "Crisis simulation / Tabletop exercise.",
            "assignment_task": "Make a safety decision in under 1 minute with incomplete information.",
            "success_indicators": "They made a call effectively and stood by it.",
            "red_flags": "They froze or asked 'what do you guys think?' repeatedly.",
            "supervisor_focus": "Watch for them hesitating to be the final authority."
        },
        "Program Supervisor": {
            "shift": "From 'Peacemaker' to 'Driver'",
            "why": "They struggle to push the team toward uncomfortable change.",
            "conversation": "You need to drive the bus, not just make sure the passengers are happy.",
            "assignment_setup": "Implement a new protocol.",
            "assignment_task": "Roll out a change that the team might not like.",
            "success_indicators": "They focused on the 'why' and held firm.",
            "red_flags": "They caved when the team complained."
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Rule' to 'Reason'",
            "why": "They view the rulebook as a shield. They struggle when unique situations require flexibility.",
            "conversation": "Safety over compliance. The rule is the map, not the territory.",
            "assignment_setup": "Manage a schedule change/crisis.",
            "assignment_task": "Adapt the routine for a crisis (e.g., staff call-out) without panicking.",
            "success_indicators": "They flexed the rules safely to meet the need.",
            "red_flags": "They refused to deviate from the schedule despite the crisis.",
            "supervisor_focus": "Watch for them quoting policy instead of solving the problem."
        },
        "Program Supervisor": {
            "shift": "From 'Guardian' to 'Architect'",
            "why": "They are great at maintaining systems, but struggle to build new ones.",
            "conversation": "We need you to build a better way, not just protect the old way.",
            "assignment_setup": "Revise a workflow.",
            "assignment_task": "Identify a broken process and design a fix.",
            "success_indicators": "They created a system that improved efficiency.",
            "red_flags": "They created a system that was just more bureaucracy."
        }
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
        thriving_bullets.append("**Decisive Action:** You will see them moving the team forward with clarity and speed, removing obstacles quickly.")
        struggling_bullets.append("**Steamrolling:** You will see them bypassing others' input to get results quickly, leaving staff feeling unheard.")
    elif comm == "Encourager":
        thriving_bullets.append("**High Morale:** You will see them keeping the team's energy and hope alive, even during difficult shifts.")
        struggling_bullets.append("**Conflict Avoidance:** You will see them hiding hard truths or delaying feedback to keep the peace.")
    elif comm == "Facilitator":
        thriving_bullets.append("**Inclusive Decisions:** You will see them ensuring everyone is heard and on board before moving forward.")
        struggling_bullets.append("**Indecision:** You will see them stalling out, waiting for total consensus that may never come.")
    elif comm == "Tracker":
        thriving_bullets.append("**Reliable Systems:** You will see them creating safety through order, consistency, and impeccable follow-through.")
        struggling_bullets.append("**Rigidity:** You will see them quoting the rulebook instead of solving the human problem in front of them.")
        
    if motiv == "Achievement":
        thriving_bullets.append("**Goal Crushing:** You will see them consistently hitting targets and improving metrics week over week.")
        struggling_bullets.append("**Burnout:** You will see them pushing themselves and others past reasonable limits to hit a number.")
    elif motiv == "Growth":
        thriving_bullets.append("**Continuous Improvement:** You will see them constantly learning, upgrading skills, and asking 'why'.")
        struggling_bullets.append("**Boredom:** You will see them checking out or becoming cynical if the work feels repetitive or stagnant.")
    elif motiv == "Purpose":
        thriving_bullets.append("**Mission Alignment:** You will see them acting as a moral compass, reminding the team why the work matters.")
        struggling_bullets.append("**Moral Outrage:** You will see them becoming resentful or defiant if asked to do 'meaningless' tasks.")
    elif motiv == "Connection":
        thriving_bullets.append("**Team Cohesion:** You will see them fostering a deep sense of belonging and mutual support on the unit.")
        struggling_bullets.append("**Personalization:** You will see them taking general feedback or team friction as a personal attack.")

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
                # Handle bolding in bullets manually for PDF
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
    adv_bullets = ["**Master Operations:** Ensure they can handle the boring parts of the job.", "**See Accountability as Kindness:** Reframe tough conversations as care.", "**Expand Range:** Practice communication styles that aren't natural to them."]
    
    if p_comm == "Director": 
        adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn. They need to move from being the hero to being the guide.\n\nTheir natural instinct is to take over when things get slow or messy. Advancement requires them to tolerate the messiness of other people's learning curves."
        adv_bullets = ["**Delegate Effectively:** Give away tasks they are good at.", "**Allow Safe Failure:** Let the team struggle so they can learn.", "**Focus on Strategy:** Move from the 'how' to the 'why'."]
    elif p_comm == "Encourager": 
        adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness. They need to learn that being 'nice' isn't always being 'kind'.\n\nThey naturally lean into relationships. Advancement requires them to lean into the structural and operational pillars of leadership without losing their heart."
        adv_bullets = ["**Master Structure:** Become proficient in audits and schedules.", "**Hold Boundaries:** Practice saying 'no' without apologizing.", "**Separate Niceness from Kindness:** Delivering hard news is a leadership duty."]
    elif p_comm == "Facilitator": 
        adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible. They need to get comfortable with not everyone agreeing.\n\nThey naturally seek harmony and input. Advancement requires them to become comfortable with the loneliness of making the final call when the team is divided."
        adv_bullets = ["**Executive Presence:** Speak first in meetings sometimes.", "**Decisive Action:** Make calls without 100% consensus.", "**Limit Consensus-Seeking:** Know when to stop voting and start doing."]
    elif p_comm == "Tracker": 
        adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance. They need to learn to read the room, not just the rulebook.\n\nThey naturally lean into safety and rules. Advancement requires them to understand the 'spirit of the law' and to build relational capital that allows them to lead people, not just processes."
        adv_bullets = ["**Develop Intuition:** Trust their gut in gray areas.", "**Prioritize Relationships:** Spend time connecting without an agenda.", "**Flexibility:** Know which glass balls cannot drop and which rubber balls can bounce."]
    
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
    show_section("5. Integrated Leadership Profile", data['s5'])
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
    adv_text = "Help them master the operational side. Challenge them to see clarity and accountability as kindness.\n\nTo advance, they must move beyond their natural strengths and develop their blind spots. This requires intentional coaching and 'safe failure' opportunities."
    adv_bullets = ["**Master Operations:** Ensure they can handle the boring parts of the job.", "**See Accountability as Kindness:** Reframe tough conversations as care.", "**Expand Range:** Practice communication styles that aren't natural to them."]
    
    if p_comm == "Director": 
        adv_text = "Shift from doing to enabling. Challenge them to sit on their hands and let the team fail safely to learn. They need to move from being the hero to being the guide.\n\nTheir natural instinct is to take over when things get slow or messy. Advancement requires them to tolerate the messiness of other people's learning curves."
        adv_bullets = ["**Delegate Effectively:** Give away tasks they are good at.", "**Allow Safe Failure:** Let the team struggle so they can learn.", "**Focus on Strategy:** Move from the 'how' to the 'why'."]
    elif p_comm == "Encourager": 
        adv_text = "Master structure and operations. Challenge them to see that holding a boundary is a form of kindness. They need to learn that being 'nice' isn't always being 'kind'.\n\nThey naturally lean into relationships. Advancement requires them to lean into the structural and operational pillars of leadership without losing their heart."
        adv_bullets = ["**Master Structure:** Become proficient in audits and schedules.", "**Hold Boundaries:** Practice saying 'no' without apologizing.", "**Separate Niceness from Kindness:** Delivering hard news is a leadership duty."]
    elif p_comm == "Facilitator": 
        adv_text = "Develop executive presence. Challenge them to make the 51% decision when consensus isn't possible. They need to get comfortable with not everyone agreeing.\n\nThey naturally seek harmony and input. Advancement requires them to become comfortable with the loneliness of making the final call when the team is divided."
        adv_bullets = ["**Executive Presence:** Speak first in meetings sometimes.", "**Decisive Action:** Make calls without 100% consensus.", "**Limit Consensus-Seeking:** Know when to stop voting and start doing."]
    elif p_comm == "Tracker": 
        adv_text = "Develop intuition and flexibility. Challenge them to prioritize relationships over rigid compliance. They need to learn to read the room, not just the rulebook.\n\nThey naturally lean into safety and rules. Advancement requires them to understand the 'spirit of the law' and to build relational capital that allows them to lead people, not just processes."
        adv_bullets = ["**Develop Intuition:** Trust their gut in gray areas.", "**Prioritize Relationships:** Spend time connecting without an agenda.", "**Flexibility:** Know which glass balls cannot drop and which rubber balls can bounce."]

    show_section("12. Helping Them Prepare for Advancement", adv_text, adv_bullets)

# --- 6. MAIN APP LOGIC ---
staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

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
        # Sidebar for API Key
        with st.sidebar:
            gemini_key = st.text_input("🔑 Gemini API Key (Optional)", type="password", help="Get a key at aistudio.google.com to enable the smart chatbot.")
            if not gemini_key:
                # Try to get from secrets if not input
                gemini_key = st.secrets.get("GEMINI_API_KEY", "")

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
                if gemini_key:
                    st.caption(f"Powered by Gemini 2.5 Flash | Ask specific questions about managing **{p2}** ({s2} x {m2}).")
                else:
                    st.caption("Basic Mode | Add an API Key in the sidebar to unlock full AI capabilities.")
                
                st.info("⬇️ **Type your question in the chat bar at the bottom of the screen.**")
                
                # Initialize history specifically for this view if not present
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                # Display messages
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # -------------------------------------------
                # LOGIC ENGINE: HYBRID (Rule-Based + Gemini)
                # -------------------------------------------
                def get_smart_response(query, comm_style, motiv_driver, key):
                    # Prepare Context Data
                    comm_data = FULL_COMM_PROFILES.get(comm_style, {})
                    mot_data = FULL_MOTIV_PROFILES.get(motiv_driver, {})
                    
                    # If API Key exists, use Gemini
                    if key:
                        try:
                            # Context Prompt Construction
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
                            
                            # API Call to Gemini 2.5 Flash (Standard Endpoint)
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

                    # FALLBACK: Rule-Based Logic (No API Key)
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
                        response = f"I can help you manage {p2}. Try asking about:\n- How to give **feedback**\n- How to **motivate** them\n- How to handle **conflict**\n\n*Note: Add a Gemini API Key in the sidebar for smarter, custom answers.*"
                    
                    return response

                # Input
                if prompt := st.chat_input(f"Ask about {p2}..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Consulting the Compass Database..."):
                            # bot_reply = get_smart_response(prompt, s2, m2, gemini_key) # Fixed variable scope
                            bot_reply = get_smart_response(prompt, s2, m2, gemini_key)
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
        c1, c2, c3 = st.columns(3)
        top_comm = df['p_comm'].mode()[0]; top_mot = df['p_mot'].mode()[0]
        c1.metric("Dominant Style", top_comm); c2.metric("Top Driver", top_mot); c3.metric("Total Staff", len(df))
        st.divider()
        c_a, c_b = st.columns(2)
        with c_a: st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']]), use_container_width=True)
        with c_b: 
            if 'role' in df.columns: st.plotly_chart(px.histogram(df, x="role", color="p_comm", title="Leadership Pipeline", color_discrete_map={'Director':BRAND_COLORS['blue'], 'Encourager':BRAND_COLORS['green'], 'Facilitator':BRAND_COLORS['teal'], 'Tracker':BRAND_COLORS['gray']}), use_container_width=True)
    else: st.warning("No data available.")
