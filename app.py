import streamlit as st
import random
import requests
import time
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components  # Required for scrolling

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Elmcrest Compass", page_icon="🧭", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS STYLING (Modern Glassmorphism) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --primary: #015bad;
            --secondary: #51c3c5;
            --accent: #b9dca4;
            --bg-gradient-light: radial-gradient(circle at top left, #e0f2fe 0%, #ffffff 40%, #dcfce7 100%);
            --bg-gradient-dark: radial-gradient(circle at top left, #0f172a 0%, #1e293b 40%, #064e3b 100%);
            --text-main: #0f172a;
            --text-sub: #475569;
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(255, 255, 255, 0.6);
            --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
            --input-bg: #f8fafc;
        }

        /* HIDE STREAMLIT SIDEBAR NAVIGATION */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}

        @media (prefers-color-scheme: dark) {
            :root {
                --text-main: #f1f5f9;
                --text-sub: #94a3b8;
                --card-bg: rgba(30, 41, 59, 0.85);
                --card-border: rgba(255, 255, 255, 0.1);
                --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.3);
                --input-bg: #0f172a;
            }
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* Main App Background */
        .stApp {
            background-image: var(--bg-gradient-light);
            background-attachment: fixed;
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-image: var(--bg-gradient-dark); }
        }

        /* Headers */
        h1, h2, h3 {
            color: var(--primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        p, label, li, .stMarkdown {
            color: var(--text-main) !important;
            line-height: 1.6;
        }

        /* Glassmorphism Container */
        .block-container {
            padding: 3rem 2rem;
            max-width: 800px;
            background-color: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            margin-top: 2rem;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            width: 100%;
            box-shadow: 0 4px 12px rgba(1, 91, 173, 0.2);
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(1, 91, 173, 0.3);
            opacity: 0.95;
        }

        /* Inputs */
        .stTextInput input, .stSelectbox [data-baseweb="select"] {
            background-color: var(--input-bg);
            border-radius: 12px;
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.5rem;
        }

        /* Centered Radio Buttons */
        .stRadio {
            background-color: transparent;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .stRadio [role="radiogroup"] {
            justify-content: space-between;
            width: 100%;
            margin-top: 4px;
        }
        div[role="radiogroup"] > label > div:first-of-type {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }
        
        /* Assessment Question Styling */
        .question-text {
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-main);
            line-height: 1.4;
        }
        
        /* Labels for Scale */
        .scale-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.7rem;
            color: var(--text-sub);
            margin-bottom: -8px;
            padding-left: 4px;
            padding-right: 4px;
            font-weight: 500;
        }

        /* Custom Cards & Bars */
        .info-card {
            background-color: var(--input-bg);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--card-border);
        }
        .score-container {
            background-color: var(--input-bg);
            border-radius: 8px;
            height: 12px;
            width: 100%;
            margin-top: 5px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .score-fill {
            height: 100%;
            border-radius: 8px;
            background: linear-gradient(90deg, var(--secondary), var(--primary));
            transition: width 1s ease-in-out;
        }
        
        hr {
            margin: 2rem 0;
            border: 0;
            border-top: 1px solid var(--card-border);
            opacity: 0.5;
        }
        
        /* Alerts */
        .stAlert { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTS & DATA ---

ROLE_RELATIONSHIP_LABELS = {
    "Program Supervisor": {"directReportsLabel": "Shift Supervisors", "youthLabel": "youth on your units", "supervisorLabel": "Residential Programs Manager", "leadershipLabel": "agency leadership"},
    "Shift Supervisor": {"directReportsLabel": "YDPs", "youthLabel": "youth you support", "supervisorLabel": "Program Supervisor", "leadershipLabel": "agency leadership"},
    "YDP": {"directReportsLabel": "peers", "youthLabel": "youth in your care", "supervisorLabel": "Shift Supervisor", "leadershipLabel": "Program Supervisor"}
}

COMM_QUESTIONS = [
    {"id": "comm1", "text": "When a situation becomes chaotic, I naturally step in and start directing people toward a plan.", "style": "Director"},
    {"id": "comm2", "text": "I feel most effective when I can make quick decisions and move the team forward.", "style": "Director"},
    {"id": "comm3", "text": "In a crisis, I’d rather take charge and apologize later than wait too long for consensus.", "style": "Director"},
    {"id": "comm4", "text": "If expectations are unclear, I tend to define them myself and communicate them to others.", "style": "Director"},
    {"id": "comm5", "text": "I’m comfortable giving direct feedback, even when it may be hard for someone to hear.", "style": "Director"},
    {"id": "comm6", "text": "I pay close attention to the emotional tone of the team and lift people up when morale is low.", "style": "Encourager"},
    {"id": "comm7", "text": "I often use encouragement, humor, or positive energy to help staff get through hard shifts.", "style": "Encourager"},
    {"id": "comm8", "text": "I notice small wins and like to name them out loud so people know they’re seen.", "style": "Encourager"},
    {"id": "comm9", "text": "I tend to talk things through with people rather than just giving short instructions.", "style": "Encourager"},
    {"id": "comm10", "text": "I’m often the one coworkers come to when they need to vent or feel understood.", "style": "Encourager"},
    {"id": "comm11", "text": "I’m good at slowing conversations down so that different perspectives can be heard.", "style": "Facilitator"},
    {"id": "comm12", "text": "I try to stay calm and balanced when others are escalated or upset.", "style": "Facilitator"},
    {"id": "comm13", "text": "I often find myself summarizing what others are saying to move toward shared understanding.", "style": "Facilitator"},
    {"id": "comm14", "text": "I prefer to build agreement and buy-in rather than rely only on authority.", "style": "Facilitator"},
    {"id": "comm15", "text": "I pay attention to process (how we talk to each other) as much as the final decision.", "style": "Facilitator"},
    {"id": "comm16", "text": "I naturally notice details in documentation, routines, or schedules others overlook.", "style": "Tracker"},
    {"id": "comm17", "text": "I feel responsible for keeping procedures on track, even when others get distracted.", "style": "Tracker"},
    {"id": "comm18", "text": "I tend to ask clarifying questions when expectations or instructions feel vague.", "style": "Tracker"},
    {"id": "comm19", "text": "I’m more comfortable when I know exactly who is doing what and when it needs to be done.", "style": "Tracker"},
    {"id": "comm20", "text": "If something seems out of compliance, it really sticks with me until it’s addressed.", "style": "Tracker"},
]

MOTIVATION_QUESTIONS = [
    {"id": "mot1", "text": "I feel energized when I’m learning new skills or being stretched in healthy ways.", "style": "Growth"},
    {"id": "mot2", "text": "It’s important to me that I can look back and see I’m becoming more effective over time.", "style": "Growth"},
    {"id": "mot3", "text": "When I feel stuck in the same patterns with no development, my motivation drops.", "style": "Growth"},
    {"id": "mot4", "text": "I appreciate feedback that helps me improve, even if it’s uncomfortable in the moment.", "style": "Growth"},
    {"id": "mot5", "text": "Access to training, coaching, or new responsibilities matters a lot for my commitment.", "style": "Growth"},
    {"id": "mot6", "text": "I need to feel that what I’m doing connects to a bigger purpose for youth and families.", "style": "Purpose"},
    {"id": "mot7", "text": "I feel strongest when my work lines up with my values about dignity, justice, and safety.", "style": "Purpose"},
    {"id": "mot8", "text": "It’s hard for me to stay engaged when policies don’t make sense for the youth we serve.", "style": "Purpose"},
    {"id": "mot9", "text": "I’m often the one raising questions about whether a decision is really best for kids.", "style": "Purpose"},
    {"id": "mot10", "text": "I feel proudest when I can see real positive impact, not just tasks checked off.", "style": "Purpose"},
    {"id": "mot11", "text": "Having strong relationships with coworkers makes a big difference in my energy.", "style": "Connection"},
    {"id": "mot12", "text": "When the team feels disconnected, I feel it in my body and it’s harder to stay motivated.", "style": "Connection"},
    {"id": "mot13", "text": "I value feeling known and supported by my team and supervisor, not just evaluated.", "style": "Connection"},
    {"id": "mot14", "text": "I’m often thinking about the emotional climate of the unit and how people are relating.", "style": "Connection"},
    {"id": "mot15", "text": "I’m more likely to go above and beyond when I feel a sense of belonging.", "style": "Connection"},
    {"id": "mot16", "text": "I like having clear goals and being able to see, in concrete ways, when we’ve met them.", "style": "Achievement"},
    {"id": "mot17", "text": "I feel satisfied when I can see that that my effort led to specific improvements.", "style": "Achievement"},
    {"id": "mot18", "text": "It’s frustrating when expectations keep shifting and I’m not sure what success looks like.", "style": "Achievement"},
    {"id": "mot19", "text": "I appreciate data, tracking tools, or simple dashboards that help show progress.", "style": "Achievement"},
    {"id": "mot20", "text": "I’m motivated by being trusted with projects where outcomes are clearly defined.", "style": "Achievement"},
]

# --- DATA DICTIONARIES ---

COMM_PROFILES = {
    "Director": {
        "name": "Director Communicator",
        "tagline": "The Decisive Driver",
        "overview": "<strong>Core Style:</strong> You blend decisive, crisis-ready leadership with a bias for action. You are likely to set direction quickly and then rally people to move with you. You prioritize efficiency and competence, often serving as the 'adult in the room' who keeps things calm while making necessary calls.<br><br><strong>Your Superpower:</strong> In high-pressure moments, you step in and organize. Staff see you as fair and decisive—they know you will act, so they aren't stuck in limbo.",
        "conflictImpact": "Under stress, you may move faster than staff can realistically integrate, making them feel like they are always 'behind'. You might default to control before curiosity.",
        "traumaStrategy": "Your consistency and clear boundaries can be regulating for youth who need predictability, though some may find your intensity intimidating.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Before finalizing a decision, ask Shift Supervisors: 'What are we not seeing from the floor?' and genuinely pause to listen.",
                "youth": "Balance your big energy with moments of quiet, one-to-one check-ins where they get more room to talk.",
                "supervisor": "Name the operational risk of moving fast: 'We can do this quickly if we also build in these guardrails.'.",
                "leadership": "Highlight where strict standards are helping kids AND where they might be creating burnout for staff."
            },
            "Shift Supervisor": {
                "directReports": "Create space for early-warning conversations: 'You don't have to have all the answers before you tell me something is off.'.",
                "youth": "Try naming the 'why' behind structure in simple, human language: 'This schedule is here so you know what to expect. Surprises can be scary.'.",
                "supervisor": "Be honest about any emotional load you are carrying from trying to smooth everything out for everyone.",
                "leadership": "Be candid about how much time it takes to bring people along and where you need backing."
            },
            "YDP": {
                "directReports": "With peers, name explicitly when you are shifting from listening mode to decision mode: 'I've heard the input; here is the decision.'.",
                "youth": "Hold steady when they test your limits. Remind yourself that pushback is a sign you are holding needed structure.",
                "supervisor": "Periodically highlight where strict standards are helping kids and where they might be driving stress.",
                "leadership": "Show that learning is expected: 'Getting it wrong the first few times is part of learning.'."
            }
        }
    },
    "Encourager": {
        "name": "Encourager Communicator",
        "tagline": "The Relational Energizer",
        "overview": "<strong>Core Style:</strong> You lead with enthusiasm, vision, and warmth. You act as the emotional glue of the team, paying attention to how people feel and ensuring they feel seen and supported. You help change feel both human and organized.<br><br><strong>Your Superpower:</strong> You keep the 'why' of the work alive when others are exhausted. You are often the one who notices and names growth in youth or staff.",
        "conflictImpact": "You may avoid giving sharp feedback because you don't want to discourage someone. You might also overcommit your emotional energy when many people need you.",
        "traumaStrategy": "Your ability to foster belonging helps youth feel that adults are approachable, kind, and on their side.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Create explicit space for them to say no or negotiate capacity: 'If this feels like too much right now, tell me and we'll prioritize.'.",
                "youth": "Use your warmth first, then your firmness: 'I care about you, and that's why this boundary is still a hard no.'.",
                "supervisor": "Share not just the enthusiasm around initiatives but also the realistic limits of your team's bandwidth.",
                "leadership": "Clearly state your own needs and boundaries instead of silently absorbing more emotional labor."
            },
            "Shift Supervisor": {
                "directReports": "Be explicit about what is truly flexible vs. what is not to avoid confusion between 'nice to have' and 'must do'.",
                "youth": "Maintain structure while being caring: 'I understand why you are angry, and I still can't allow X. Here is what we can do.'.",
                "supervisor": "Share not just how others feel but also what concrete support you need to keep carrying this emotional work.",
                "leadership": "Name where staff need more time or training to realistically meet the standards you are reinforcing."
            },
            "YDP": {
                "directReports": "Avoid cushioning feedback so much that the message becomes unclear—name the behavior change you need.",
                "youth": "You can be kind and clear: 'I'm not going anywhere, and that behavior is still not okay here.'.",
                "supervisor": "Ask your supervisor to help you script accountability conversations that still feel kind.",
                "leadership": "Don't hide your standards behind niceness—being clear is an act of support."
            }
        }
    },
    "Facilitator": {
        "name": "Facilitator Communicator",
        "tagline": "The Calm Bridge",
        "overview": "<strong>Core Style:</strong> You prefer to listen first and build consensus. You blend a calm, listening posture with a genuine desire to keep relationships steady. You create calmer, more predictable environments.<br><br><strong>Your Superpower:</strong> You de-escalate tension by staying steady and non-threatening. People feel safe bringing mistakes or worries to you without fear of shame.",
        "conflictImpact": "You might stay neutral too long when a strong stance is needed. You may quietly carry moral distress or frustration without voicing it.",
        "traumaStrategy": "Your steady presence helps youth feel safe enough to open up, especially when they aren't ready for intensity.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Name explicitly when you are shifting from listening mode to decision mode: 'I've heard the input; here's the decision.'.",
                "youth": "Hold steady when they test limits. Remind yourself that pushback is a sign you are holding needed structure.",
                "supervisor": "Be candid about how much time it takes to bring people along and where you need their backing.",
                "leadership": "Don't over-own the team's reactions; you can care without carrying all of their feelings."
            },
            "Shift Supervisor": {
                "directReports": "Practice being more direct when standards aren't met: 'I care about you, and this still has to be corrected by Friday.'.",
                "youth": "Remember that some flexibility can be regulating too—look for safe places to say yes when you can.",
                "supervisor": "Don't undersell your impact—your quiet consistency keeps a lot from falling apart.",
                "leadership": "Watch for signs you are quietly absorbing tasks your team should own; invite them into problem-solving instead."
            },
            "YDP": {
                "directReports": "Resist taking on everyone's emotional load—offer support, but help peers connect to other resources (EAP, debriefs).",
                "youth": "Maintain structure while being caring: 'I understand why you're angry, and I still can't allow X.'.",
                "supervisor": "Ask your supervisor for clarity on non-negotiables so you feel confident enforcing them.",
                "leadership": "Break growth steps into very small, concrete actions so they feel manageable."
            }
        }
    },
    "Tracker": {
        "name": "Tracker Communicator",
        "tagline": "The Structured Guardian",
        "overview": "<strong>Core Style:</strong> You lead with structure, detail, and a strong respect for procedure. You want plans to be sound and aligned before you move. You believe the path to success is through good systems and accurate work.<br><br><strong>Your Superpower:</strong> You protect youth and staff by ensuring documentation and procedures support ethical, safe care. You notice small patterns that could become big risks.",
        "conflictImpact": "You may feel intolerant of what looks like carelessness in others. You can focus so much on accurate reporting that you under-communicate empathy.",
        "traumaStrategy": "Your consistency creates a predictable environment that feels safe for youth with trauma histories.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Occasionally invite rough drafts: 'Bring me your early thoughts, not just the final proposal.'.",
                "youth": "Try small moments of flexibility inside your structure so they experience you as human, not just rule-enforcing.",
                "supervisor": "Highlight how much relational work you are doing in addition to the procedural work, so it is seen and valued.",
                "leadership": "Name where your high standards are working and where they may be driving staff stress beyond what's sustainable."
            },
            "Shift Supervisor": {
                "directReports": "Clarify where they truly own decisions vs. where you need to be consulted, so they don't become over-dependent.",
                "youth": "Explain why structure exists in terms of safety and success, not just 'because that's the rule.'.",
                "supervisor": "Ask your supervisor to help you prioritize what truly needs perfection and what can be 'good enough.'.",
                "leadership": "Share tasks and expertise with peers instead of quietly doing things for them."
            },
            "YDP": {
                "directReports": "Pair data shares with appreciation ('Here's what improved, here's who helped make that happen').",
                "youth": "Check in with peers about what support they need to meet expectations before tightening accountability.",
                "supervisor": "Ask your supervisor to help you contextualize metrics so you don't carry them as a personal verdict.",
                "leadership": "Occasionally invite rough drafts from peers: 'Bring me your early thoughts, not just the final proposal.'."
            }
        }
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "name": "Growth Motivation",
        "tagline": "The Learner/Builder",
        "summary": "You are fueled by learning and development that clearly connects to the mission. You're hungry to improve and want to keep leveling up how you and your team support youth.",
        "boosters": [
            "**Focused Projects:** Ask for a small number of focused growth projects rather than trying to improve everything at once.",
            "**Peer Learning:** You light up when sharing strategies with peers rather than learning alone from a manual.",
            "**Concrete Changes:** You are energized by turning new learning into concrete changes on the floor."
        ],
        "killers": [
            "**Disconnected Training:** You feel drained learning skills that feel disconnected from the realities of Elmcrest.",
            "**Lack of Adoption:** You feel discouraged when youth or staff don't 'take up' the growth you see for them.",
            "**Isolation:** Being left to figure everything out alone without peers to process with."
        ],
        "roleSupport": {
            "Program Supervisor": "Connect goals to youth outcomes (e.g., fewer incidents) rather than just compliance.",
            "Shift Supervisor": "Co-design one development goal with each direct report that feels stretching but achievable.",
            "YDP": "Ask for development goals that explicitly tie to youth outcomes like better transitions or family engagement."
        }
    },
    "Purpose": {
        "name": "Purpose Motivation",
        "tagline": "The Mission Keeper",
        "summary": "You are driven to make decisions that align with your values and with what's right for youth and staff. You care not just about order, but about justice and integrity.",
        "boosters": [
            "**Value Alignment:** You are motivated when goals align with safety, healing, and justice for youth.",
            "**Advocacy:** You thrive when advocating for youth or staff when something is not in their best interest.",
            "**Meaningful Metrics:** You need to know that numbers reflect real, meaningful change for youth."
        ],
        "killers": [
            "**Performative Goals:** You emotionally disengage from goals that feel performative or disconnected from kids' real needs.",
            "**Moral Distress:** You feel intense frustration when the system feels misaligned with your values.",
            "**Bureaucracy:** Tasks that feel like 'checking boxes' without real impact."
        ],
        "roleSupport": {
            "Program Supervisor": "Share your top core values with your team so they understand what guides your decisions.",
            "Shift Supervisor": "Ask your supervisor to connect new initiatives explicitly to how they support youth well-being.",
            "YDP": "When you run into system limits, ask: 'What is one small thing I can still do here that reflects my values?'."
        }
    },
    "Connection": {
        "name": "Connection Motivation",
        "tagline": "The Community Builder",
        "summary": "You are fueled by strong relationships and a sense of 'we're in this together'. You make staff feel less alone in the hard work and foster a climate where it's okay to ask for help.",
        "boosters": [
            "**Reflective Space:** You need regular reflective space, not just task-focused check-ins.",
            "**Shared Wins:** You are motivated by seeing the whole team succeed, not just being the 'star'.",
            "**Belonging:** You thrive in spaces where people are honest and curious together."
        ],
        "killers": [
            "**Interpersonal Tension:** You take tension very personally and it drains you.",
            "**Isolation:** Lack of relational support quickly drains your motivation to try new things.",
            "**Sole Responsibility:** Feeling like you have to carry things yourself without the team."
        ],
        "roleSupport": {
            "Program Supervisor": "Schedule short relational touchpoints with staff on tough weeks, even just 2 minutes.",
            "Shift Supervisor": "Turn unit challenges into shared learning projects: 'How can we improve transitions together?'.",
            "YDP": "Identify one peer who can be a thought-partner and commit to a monthly check-in."
        }
    },
    "Achievement": {
        "name": "Achievement Motivation",
        "tagline": "The Results Architect",
        "summary": "You are results-focused and decisive. You want to see tangible improvements in safety, documentation, and outcomes. You believe the path to success is through good systems and accurate work.",
        "boosters": [
            "**Clear Goals:** You like clear indicators that your effort is making a difference.",
            "**Data & Progress:** You are strong at tracking metrics and helping the team adjust based on data.",
            "**Incremental Gains:** Celebrating small wins helps you avoid feeling like the work is endless pressure."
        ],
        "killers": [
            "**Vague Expectations:** You get frustrated if you don't see clear movement or progress.",
            "**Incompetence:** You feel impatient with staff who struggle to meet standards.",
            "**Slow Progress:** You judge yourself harshly when progress is slower than you'd like."
        ],
        "roleSupport": {
            "Program Supervisor": "Set process goals (e.g., 'We debriefed every incident') not just outcome goals (e.g., 'Fewer incidents').",
            "Shift Supervisor": "Partner with clinicians to define realistic pacing for youth progress so you don't burn out.",
            "YDP": "Ask your supervisor to help you differentiate between what is in your control and what is system-level."
        }
    }
}

INTEGRATED_PROFILES = {
    "Director-Growth": {"title": "Director + Growth – The Driven Developer", "summary": "You lean into leadership and action, and you want to keep getting better at it.", "strengths": ["Decisive action", "Rapid learning", "Ambitious"], "watchouts": ["Impatience", "Burnout"]},
    "Director-Purpose": {"title": "Director + Purpose – The Ethical Guardian", "summary": "You make firm decisions through a values lens.", "strengths": ["Advocacy", "Clarity", "Integrity"], "watchouts": ["Rigidity", "Righteous anger"]},
    "Director-Connection": {"title": "Director + Connection – The Relational Driver", "summary": "You lead with energy and care about how the team is doing together.", "strengths": ["Mobilizing", "Protective", "Direct"], "watchouts": ["Overpowering", "Taking conflict personally"]},
    "Director-Achievement": {"title": "Director + Achievement – The Results Leader", "summary": "You want clear goals and you’re willing to lead the way to reach them.", "strengths": ["Execution", "Focus", "Speed"], "watchouts": ["Steamrolling", "Ignoring feelings"]},
    # Note: If other combinations are needed, add them here. The app handles missing combos gracefully.
}

# --- 4. FUNCTIONS ---

def normalize_role_key(role):
    if not role: return "YDP"
    r = role.lower()
    if "program" in r: return "Program Supervisor"
    if "shift" in r: return "Shift Supervisor"
    return "YDP"

def get_top_two(scores):
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary = sorted_scores[0][0] if len(sorted_scores) > 0 else None
    secondary = sorted_scores[1][0] if len(sorted_scores) > 1 else None
    return primary, secondary

def clean_text(text):
    if not text: return ""
    return text.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '-').replace('—', '-').encode('latin-1', 'replace').decode('latin-1')

def submit_to_google_sheets(data, action="save"):
    # Sends data to Google Scripts
    url = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"
    data["action"] = action
    try:
        requests.post(url, json=data)
        return True
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

def send_email_via_smtp(to_email, subject, body):
    try:
        # Requires secrets.toml setup
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

def generate_text_report(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    lines = [f"ELMCREST COMPASS PROFILE FOR {user_info['name'].upper()}", "="*40, ""]
    
    # Comm
    lines.append(f"COMMUNICATION STYLE: {comm_prof['name']}")
    lines.append(f"Tagline: {comm_prof['tagline']}")
    lines.append(f"Overview: {comm_prof['overview']}")
    lines.append(f"Under Stress: {comm_prof['conflictImpact']}")
    lines.append("")
    lines.append("ROLE TIPS:")
    tips = comm_prof['roleTips'][role_key]
    lines.append(f"* With {role_labels['directReportsLabel']}: {tips['directReports']}")
    lines.append(f"* With {role_labels['youthLabel']}: {tips['youth']}")
    lines.append(f"* With {role_labels['supervisorLabel']}: {tips['supervisor']}")
    lines.append(f"* With {role_labels['leadershipLabel']}: {tips['leadership']}")
    lines.append("")
    
    # Motiv
    lines.append(f"MOTIVATION DRIVER: {mot_prof['name']}")
    lines.append(f"Tagline: {mot_prof['tagline']}")
    lines.append(f"Summary: {mot_prof['summary']}")
    lines.append("Boosters (Energizers):")
    for b in mot_prof['boosters']: lines.append(f"* {b}")
    lines.append("Drainers (De-energizers):")
    for k in mot_prof['killers']: lines.append(f"* {k}")
    lines.append(f"Support Needed: {mot_prof['roleSupport'][role_key]}")
    lines.append("")
    
    # Integrated
    if int_prof:
        lines.append(f"INTEGRATED PROFILE: {int_prof['title']}")
        lines.append(int_prof['summary'])
        lines.append("Strengths: " + ", ".join(int_prof['strengths']))
        lines.append("Watch-outs: " + ", ".join(int_prof['watchouts']))
        
    return "\n".join(lines)

def create_pdf(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (1, 91, 173)
    black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Compass Profile", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"Prepared for: {user_info['name']} | Role: {user_info['role']}"), ln=True, align='C')
    pdf.ln(5)
    
    # Comm
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, clean_text(f"Communication: {comm_prof['name']}"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*black)
    
    # Fix for bolding: Replace HTML strong tags with plain text or custom formatting if needed
    overview_text = comm_prof['overview'].replace("<strong>", "").replace("</strong>", "").replace("<br><br>", "\n\n")
    pdf.multi_cell(0, 6, clean_text(overview_text))
    pdf.ln(3)
    
    # Role Tips
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "Role-Specific Tips:", ln=True, fill=True)
    tips = comm_prof['roleTips'][role_key]
    pdf.set_font("Arial", '', 11)
    pdf.ln(2)
    pdf.multi_cell(0, 6, clean_text(f"- Direct Reports: {tips['directReports']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Youth: {tips['youth']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Supervisor: {tips['supervisor']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Leadership: {tips['leadership']}"))
    pdf.ln(5)

    # Motiv
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, clean_text(f"Motivation: {mot_prof['name']}"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*black)
    pdf.multi_cell(0, 6, clean_text(mot_prof['summary']))
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Boosters (Energizers):", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    for b in mot_prof['boosters']: 
        clean_b = b.replace("**", "")
        pdf.multi_cell(0, 6, clean_text(f"- {clean_b}"))
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Drainers (De-energizers):", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    for k in mot_prof['killers']: 
        clean_k = k.replace("**", "")
        pdf.multi_cell(0, 6, clean_text(f"- {clean_k}"))
    pdf.ln(5)
    
    # Integrated
    if int_prof:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(*blue)
        pdf.cell(0, 10, clean_text(f"Integrated: {int_prof['title']}"), ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        pdf.multi_cell(0, 6, clean_text(int_prof['summary']))
        pdf.ln(2)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Strengths:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for s in int_prof['strengths']: pdf.multi_cell(0, 6, clean_text(f"- {s}"))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI HELPERS ---
def show_brand_header(subtitle):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.markdown("<div style='width:60px;height:60px;background:linear-gradient(135deg,#015bad,#51c3c5);border-radius:14px;color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.4rem;box-shadow:0 4px 10px rgba(1,91,173,0.3);'>EC</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 60px;">
            <div style="color: #015bad; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.03em;">ELMCREST COMPASS</div>
            <div style="color: #64748b; font-size: 0.95rem; font-weight: 500;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def draw_score_bar(label, value, max_value=25):
    pct = (value / max_value) * 100
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.85rem; font-weight: 600; color: #475569;">
            <span>{label}</span>
            <span>{value}</span>
        </div>
        <div class="score-container">
            <div class="score-fill" style="width: {pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. APP LOGIC ---

# Function to scroll to top
def scroll_to_top():
    js = """
    <script>
        var body = window.parent.document.body;
        var doc = window.parent.document.documentElement;
        doc.scrollTop = 0;
        body.scrollTop = 0;
    </script>
    """
    components.html(js, height=0)

if 'step' not in st.session_state:
    st.session_state.step = 'intro'
    comm_q, motiv_q = COMM_QUESTIONS.copy(), MOTIVATION_QUESTIONS.copy()
    random.shuffle(comm_q); random.shuffle(motiv_q)
    st.session_state.shuffled_comm = comm_q
    st.session_state.shuffled_motiv = motiv_q
    st.session_state.answers_comm = {}
    st.session_state.answers_motiv = {}
    st.session_state.user_info = {}

# --- INTRO ---
if st.session_state.step == 'intro':
    show_brand_header("Communication & Motivation Snapshot")
    st.markdown("#### 👋 Welcome")
    st.info("This assessment helps you understand your natural patterns at work. Your insights will shape a personalized profile built to support your growth.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("intro_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name", placeholder="e.g. Jane Doe")
        email = c2.text_input("Email Address", placeholder="e.g. jane@elmcrest.org")
        
        c3, c4 = st.columns(2)
        role = c3.selectbox("Current Role", ["Program Supervisor", "Shift Supervisor", "YDP"], index=None, placeholder="Select your role...")
        cottage = c4.selectbox("Home Program", ["Cottage 2", "Cottage 3", "Cottage 8", "Cottage 9", "Cottage 11", "Overnight"], index=None, placeholder="Select your program...")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Start Assessment →"):
            if not name or not email or not role or not cottage: 
                st.error("Please complete all fields.")
            else:
                st.session_state.user_info = {"name": name, "email": email, "role": role, "cottage": cottage}
                st.session_state.step = 'comm'
                scroll_to_top()
                st.rerun()

    # JS to force scroll to top if we just landed here (optional)
    scroll_to_top()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    # Discrete Admin Access Button
    col_spacer, col_admin = st.columns([0.8, 0.2])
    with col_admin:
        if st.button("🔒 Supervisor Portal"):
            st.switch_page("pages/admin.py")

# --- COMM ---
elif st.session_state.step == 'comm':
    scroll_to_top()
    show_brand_header("Part 1: Communication")
    st.progress(33)
    st.markdown("**Instructions:** Choose how strongly each statement fits you most days.")
    
    with st.form("comm_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_comm):
            # Card-like container for each question
            with st.container(border=True):
                col_q, col_a = st.columns([0.6, 0.4], gap="medium")
                
                with col_q:
                    st.markdown(f"<div class='question-text' style='display:flex;align-items:center;height:100%;'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
                
                with col_a:
                    st.markdown("""
                    <div class="scale-labels">
                        <span>Disagree</span>
                        <span>Agree</span>
                    </div>
                    """, unsafe_allow_html=True)
                    answers[q['id']] = st.radio(
                        f"q_{i}", 
                        options=[1, 2, 3, 4, 5], 
                        horizontal=True, 
                        index=None, 
                        key=f"c_{q['id']}", 
                        label_visibility="collapsed"
                    )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation Logic
        if st.form_submit_button("Continue to Motivation →"):
            missed = [q['id'] for q in st.session_state.shuffled_comm if answers.get(q['id']) is None]
            if missed:
                st.error(f"Please answer all questions. You missed {len(missed)} questions.")
            else:
                st.session_state.answers_comm = answers
                st.session_state.step = 'motiv'
                scroll_to_top()
                st.rerun()

# --- MOTIV ---
elif st.session_state.step == 'motiv':
    scroll_to_top()
    show_brand_header("Part 2: Motivation")
    st.progress(66)
    st.markdown("**Instructions:** Focus on what keeps you engaged or drains you.")

    with st.form("motiv_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_motiv):
            # Card-like container for each question
            with st.container(border=True):
                col_q, col_a = st.columns([0.6, 0.4], gap="medium")
                
                with col_q:
                    st.markdown(f"<div class='question-text' style='display:flex;align-items:center;height:100%;'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
                
                with col_a:
                    st.markdown("""
                    <div class="scale-labels">
                        <span>Disagree</span>
                        <span>Agree</span>
                    </div>
                    """, unsafe_allow_html=True)
                    answers[q['id']] = st.radio(
                        f"mq_{i}", 
                        options=[1, 2, 3, 4, 5], 
                        horizontal=True, 
                        index=None, 
                        key=f"m_{q['id']}", 
                        label_visibility="collapsed"
                    )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation Logic
        if st.form_submit_button("Complete & View Profile →"):
            missed = [q['id'] for q in st.session_state.shuffled_motiv if answers.get(q['id']) is None]
            if missed:
                st.error(f"Please answer all questions. You missed {len(missed)} questions.")
            else:
                st.session_state.answers_motiv = answers
                st.session_state.step = 'processing'
                scroll_to_top()
                st.rerun()

# --- PROCESSING ---
elif st.session_state.step == 'processing':
    scroll_to_top()
    c_scores = {k:0 for k in COMM_PROFILES}
    m_scores = {k:0 for k in MOTIVATION_PROFILES}
    for q in COMM_QUESTIONS: c_scores[q['style']] += st.session_state.answers_comm[q['id']]
    for q in MOTIVATION_QUESTIONS: m_scores[q['style']] += st.session_state.answers_motiv[q['id']]
    
    p_comm, s_comm = get_top_two(c_scores)
    p_mot, s_mot = get_top_two(m_scores)
    
    st.session_state.results = {
        "primaryComm": p_comm, "secondaryComm": s_comm,
        "primaryMotiv": p_mot, "secondaryMotiv": s_mot,
        "commScores": c_scores, "motivScores": m_scores
    }
    
    # Logic to clean cottage name (remove "Cottage " prefix)
    raw_cottage = st.session_state.user_info['cottage']
    clean_cottage = raw_cottage.replace("Cottage ", "")
    
    payload = {
        "name": st.session_state.user_info['name'],
        "email": st.session_state.user_info['email'],
        "role": st.session_state.user_info['role'],
        "cottage": clean_cottage, # Use cleaned version
        "scores": st.session_state.results
    }
    
    with st.spinner("Analyzing results..."):
        submit_to_google_sheets(payload, action="save")
        time.sleep(1.0)
    
    st.session_state.step = 'results'
    st.rerun()

# --- RESULTS ---
elif st.session_state.step == 'results':
    scroll_to_top()
    st.progress(100)
    res = st.session_state.results
    user = st.session_state.user_info
    role_key = normalize_role_key(user['role'])
    role_labels = ROLE_RELATIONSHIP_LABELS[role_key]
    
    show_brand_header(f"Profile for {user['name']}")
    
    comm_prof = COMM_PROFILES[res['primaryComm']]
    mot_prof = MOTIVATION_PROFILES[res['primaryMotiv']]
    int_key = f"{res['primaryComm']}-{res['primaryMotiv']}"
    int_prof = INTEGRATED_PROFILES.get(int_key)

    # --- ACTION BAR ---
    c1, c2 = st.columns(2)
    with c1:
        pdf_bytes = create_pdf(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="Elmcrest_Profile.pdf", mime="application/pdf")
    with c2:
        if st.button("📧 Email Me Full Report"):
            full_text = generate_text_report(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
            with st.spinner("Sending..."):
                if send_email_via_smtp(user['email'], "Your Elmcrest Compass Profile", full_text):
                    st.success("Sent!")

    st.markdown("---")

    # --- COMM SECTION ---
    st.markdown(f"### 🗣️ {comm_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#015bad;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{comm_prof['tagline']}</div>
        <div style="line-height:1.6;">{comm_prof['overview']}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        with st.expander("Detailed Role Tips", expanded=True):
            tips = comm_prof['roleTips'][role_key]
            st.markdown(f"**With {role_labels['directReportsLabel']}:** {tips['directReports']}")
            st.markdown(f"**With Youth:** {tips['youth']}")
            st.markdown(f"**With Supervisor:** {tips['supervisor']}")
            st.markdown(f"**With Leadership:** {tips['leadership']}")
        st.warning(f"**Under Stress:** {comm_prof['conflictImpact']}")
        st.success(f"**Trauma Strategy:** {comm_prof['traumaStrategy']}")

    with col2:
        st.markdown("**Score Breakdown**")
        for style, score in res['commScores'].items():
            draw_score_bar(style, score)

    st.markdown("---")

    # --- MOTIV SECTION ---
    st.markdown(f"### 🔋 {mot_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#015bad;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{mot_prof['tagline']}</div>
        <div style="line-height:1.6;">{mot_prof['summary']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    c_a, c_b = st.columns(2)
    with c_a: 
        st.markdown("#### ✅ Boosters")
        for b in mot_prof['boosters']: st.write(f"• {b}")
    with c_b:
        st.markdown("#### 🔻 Drainers")
        for k in mot_prof['killers']: st.write(f"• {k}")
    
    st.info(f"**Support Needed:** {mot_prof['roleSupport'][role_key]}")

    # --- INTEGRATED SECTION ---
    if int_prof:
        st.markdown("---")
        st.markdown(f"### 🔗 Integrated: {int_prof['title']}")
        st.write(int_prof['summary'])
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("**Key Strengths**")
            for s in int_prof['strengths']: st.write(f"• {s}")
        with ic2:
            st.markdown("**Watch-outs**")
            for w in int_prof['watchouts']: st.write(f"• {w}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
