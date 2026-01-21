import streamlit as st
import random
import copy
import requests
import time
from fpdf import FPDF
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components  # Required for scrolling
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Leadership Compass", 
    page_icon="🧭", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLING (Pixel / Material Inspired + Compact) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

        /* --- LIGHT MODE VARIABLES --- */
        :root {
            --primary: #1a73e8;       /* Google Blue */
            --primary-hover: #1557b0;
            --background: #f0f2f5;
            --card-bg: #ffffff;
            --text-main: #202124;
            --text-sub: #5f6368;
            --border-color: #dadce0;
            --input-bg: #f1f3f4;
            --shadow: 0 1px 3px rgba(0,0,0,0.12);
            --score-track: #e8eaed;
        }

        /* --- DARK MODE VARIABLES --- */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary: #8ab4f8;
                --primary-hover: #aecbfa;
                --background: #1C1C1E;    /* Dark Gray */
                --card-bg: #2C2C2E;       /* Lighter Dark Gray */
                --text-main: #e8eaed;
                --text-sub: #9aa0a6;
                --border-color: #38383A;
                --input-bg: #3A3A3C;
                --shadow: 0 4px 8px rgba(0,0,0,0.3);
                --score-track: #5f6368;
            }
        }

        /* HIDE DEFAULT UI */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* GLOBAL */
        html, body, [class*="css"] {
            font-family: 'Google Sans', 'Roboto', sans-serif;
            background-color: var(--background);
            color: var(--text-main);
        }
        .stApp { background-color: var(--background); }

        /* TYPOGRAPHY */
        h1, h2, h3, h4 {
            font-family: 'Google Sans', sans-serif;
            color: var(--text-main) !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        p, label, .stMarkdown {
            color: var(--text-main) !important;
            line-height: 1.5;
            font-size: 0.95rem;
        }

        /* COMPACT CONTAINER */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 850px; /* Widened for radio buttons */
        }

        /* CARDS */
        div[data-testid="stForm"], .info-card, div[data-testid="stExpander"], div[data-testid="stContainer"] {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            box-shadow: var(--shadow);
            margin-bottom: 16px;
        }

        /* BUTTONS */
        .stButton button {
            background-color: var(--primary);
            color: var(--background) !important;
            border: none;
            border-radius: 20px;
            padding: 0.5rem 1.5rem;
            font-family: 'Google Sans', sans-serif;
            font-weight: 500;
            text-transform: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
            width: 100%;
        }
        .stButton button:hover {
            background-color: var(--primary-hover);
            transform: translateY(-1px);
        }

        /* INPUTS */
        .stTextInput input, .stSelectbox [data-baseweb="select"] {
            background-color: var(--input-bg);
            border: 1px solid transparent;
            border-radius: 8px;
            color: var(--text-main);
            padding: 8px 12px;
            font-size: 0.95rem;
            min-height: 40px;
        }
        
        /* RADIO */
        .stRadio { background-color: transparent; }
        div[role="radiogroup"] > label > div:first-of-type {
            background-color: var(--card-bg) !important;
            border: 2px solid var(--text-sub) !important;
            width: 18px; height: 18px;
        }
        div[role="radiogroup"] > label[data-checked="true"] > div:first-of-type {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }

        /* PROGRESS BAR */
        .stProgress > div > div > div > div {
            background-color: var(--primary);
            border-radius: 10px;
        }

        /* UTILS */
        .question-text {
            font-size: 1rem;
            font-weight: 400;
            color: var(--text-main);
            margin-bottom: 4px;
        }
        .scale-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.7rem;
            color: var(--text-sub);
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 2px;
        }
        .score-container {
            background-color: var(--score-track);
            border-radius: 6px;
            height: 8px;
            width: 100%;
            margin-top: 4px;
            margin-bottom: 12px;
            overflow: hidden;
        }
        .score-fill {
            height: 100%;
            border-radius: 6px;
            background-color: var(--primary);
        }
        hr {
            border: 0;
            height: 1px;
            background-color: var(--border-color);
            margin: 16px 0;
        }
        .info-card { border-left: 5px solid var(--primary); }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTS & DATA ---

BRAND_COLORS = {
    "blue": "#1a73e8",
    "green": "#34a853",
    "teal": "#12b5cb",
    "gray": "#5f6368",
    "red": "#ea4335",
    "yellow": "#fbbc04"
}

ROLE_RELATIONSHIP_LABELS = {
    "Program Supervisor": {"directReportsLabel": "Shift Supervisors", "youthLabel": "youth on your units", "supervisorLabel": "Residential Programs Manager", "leadershipLabel": "agency leadership"},
    "Shift Supervisor": {"directReportsLabel": "YDPs", "youthLabel": "youth you support", "supervisorLabel": "Program Supervisor", "leadershipLabel": "agency leadership"},
    "YDP": {"directReportsLabel": "peers", "youthLabel": "youth in your care", "supervisorLabel": "Shift Supervisor", "leadershipLabel": "Program Supervisor"}
}


# --- ASSESSMENT QUESTIONS (IPSATIVE / FORCED-CHOICE BLOCKS) ---
# Methodology:
# - 24 blocks total
# - For each block, participant selects:
#     * MOST like me  -> +3 points to that style/driver
#     * LEAST like me -> -1 point (penalty) to that style/driver
# - Blocks are randomized, and the order of statements within each block is randomized once per session.
#
# Section 1 (Blocks 1–12): Communication Style
#   - Director, Encourager, Facilitator, Tracker
# Section 2 (Blocks 13–24): Motivation Drivers
#   - Growth, Purpose, Connection, Achievement

MOST_POINTS = 3
LEAST_POINTS = -1

IPSATIVE_BLOCKS = [
    # --- SECTION 1: COMMUNICATION (1–12) ---
    {"id":"B01","section":"comm","title":"Crisis Response","intro":"In a crisis, my natural response is to...","statements":[
        {"code":"Director","text":"I naturally take charge and issue clear directives to stabilize the situation."},
        {"code":"Encourager","text":"I focus on keeping the emotional energy of the team positive and calm."},
        {"code":"Facilitator","text":"I pause to ensure we are hearing all perspectives before acting."},
        {"code":"Tracker","text":"I immediately check the protocols to ensure we are following the correct procedure."},
    ]},
    {"id":"B02","section":"comm","title":"Feedback Style","intro":"When giving feedback, I'm most likely to...","statements":[
        {"code":"Encourager","text":"I frame feedback with encouragement so the person feels supported."},
        {"code":"Tracker","text":"I refer to the specific rule or standard that was missed."},
        {"code":"Director","text":"I give direct, blunt feedback to correct the behavior quickly."},
        {"code":"Facilitator","text":"I ask questions to understand their perspective before giving my opinion."},
    ]},
    {"id":"B03","section":"comm","title":"Decision Making","intro":"When a decision needs to be made, I tend to...","statements":[
        {"code":"Facilitator","text":"I prefer to wait until the group has reached a consensus."},
        {"code":"Director","text":"I prefer to make the decision myself to ensure it happens fast."},
        {"code":"Tracker","text":"I rely on data and past records to guide my choice."},
        {"code":"Encourager","text":"I consider how the decision will impact the team’s morale first."},
    ]},
    {"id":"B04","section":"comm","title":"Managing Conflict","intro":"When conflict shows up, I usually...","statements":[
        {"code":"Director","text":"I step in and define the solution to stop the argument."},
        {"code":"Facilitator","text":"I try to mediate and help both sides understand each other."},
        {"code":"Encourager","text":"I listen to vent emotions and help them feel better."},
        {"code":"Tracker","text":"I look for the policy that clarifies who is right."},
    ]},
    {"id":"B05","section":"comm","title":"Team Meetings","intro":"In team meetings, I typically focus on...","statements":[
        {"code":"Tracker","text":"I ensure there is an agenda and we stick to the timeline."},
        {"code":"Director","text":"I focus on the goals and action items we need to hit."},
        {"code":"Facilitator","text":"I ensure everyone has a chance to speak and contribute."},
        {"code":"Encourager","text":"I start or end with something fun to build connection."},
    ]},
    {"id":"B06","section":"comm","title":"Under Stress","intro":"When I'm under stress, I'm most likely to...","statements":[
        {"code":"Director","text":"I become impatient if things are moving too slowly."},
        {"code":"Encourager","text":"I worry that I might have offended someone."},
        {"code":"Facilitator","text":"I struggle to make a decision because I want to be fair."},
        {"code":"Tracker","text":"I get anxious if the plan changes at the last minute."},
    ]},
    {"id":"B07","section":"comm","title":"Communication Preference","intro":"I prefer communication that is...","statements":[
        {"code":"Director","text":"Brief, bulleted points. Tell me the bottom line."},
        {"code":"Tracker","text":"Detailed, written instructions so I don’t miss anything."},
        {"code":"Facilitator","text":"A conversation where we can explore ideas together."},
        {"code":"Encourager","text":"A warm, personal interaction where we connect first."},
    ]},
    {"id":"B08","section":"comm","title":"Leadership Superpower","intro":"At my best, my leadership strength is that...","statements":[
        {"code":"Tracker","text":"People trust me to notice the details they missed."},
        {"code":"Director","text":"People look to me when a hard call needs to be made."},
        {"code":"Facilitator","text":"People feel safe and heard when they talk to me."},
        {"code":"Encourager","text":"People feel energized and appreciated around me."},
    ]},
    {"id":"B09","section":"comm","title":"Handling Change","intro":"When things change, I usually...","statements":[
        {"code":"Encourager","text":"I help the team process how they feel about the change."},
        {"code":"Tracker","text":"I ask, “Does this change align with our established processes?”"},
        {"code":"Director","text":"I drive the change forward and overcome resistance."},
        {"code":"Facilitator","text":"I facilitate a discussion on how to implement it fairly."},
    ]},
    {"id":"B10","section":"comm","title":"Prioritization","intro":"When priorities compete, I default toward...","statements":[
        {"code":"Director","text":"Efficiency and results are my top priorities."},
        {"code":"Encourager","text":"Harmony and team cohesion are my top priorities."},
        {"code":"Tracker","text":"Accuracy and compliance are my top priorities."},
        {"code":"Facilitator","text":"Inclusion and consensus are my top priorities."},
    ]},
    {"id":"B11","section":"comm","title":"The “Shadow” Side (What trips you up?)","intro":"If I'm not careful, I can trip myself up by...","statements":[
        {"code":"Director","text":"I can be too blunt and hurt feelings."},
        {"code":"Encourager","text":"I can be too lenient and avoid hard conversations."},
        {"code":"Tracker","text":"I can be too rigid and resist necessary changes."},
        {"code":"Facilitator","text":"I can be too indecisive and delay action."},
    ]},
    {"id":"B12","section":"comm","title":"Final Communication Check","intro":"In a team, I most naturally function as...","statements":[
        {"code":"Director","text":"I am the accelerator; I make things go."},
        {"code":"Tracker","text":"I am the brake; I ensure we are safe."},
        {"code":"Encourager","text":"I am the glue; I hold us together."},
        {"code":"Facilitator","text":"I am the bridge; I connect the sides."},
    ]},

    # --- SECTION 2: MOTIVATION (13–24) ---
    {"id":"B13","section":"motiv","title":"What Energizes You?","intro":"I feel most energized at work when...","statements":[
        {"code":"Growth","text":"Learning a new skill or mastering a complex task."},
        {"code":"Purpose","text":"Knowing my work aligns with my deep personal values."},
        {"code":"Connection","text":"Feeling a deep sense of belonging with my team."},
        {"code":"Achievement","text":"Checking items off a list and seeing concrete progress."},
    ]},
    {"id":"B14","section":"motiv","title":"What Drains You?","intro":"Work drains me most when...","statements":[
        {"code":"Growth","text":"Stagnation; doing the same thing without improving."},
        {"code":"Purpose","text":"Moral distress; doing something that feels unethical."},
        {"code":"Connection","text":"Isolation; working alone or in a toxic team environment."},
        {"code":"Achievement","text":"Ambiguity; not knowing if I am succeeding or failing."},
    ]},
    {"id":"B15","section":"motiv","title":"Ideal Recognition","intro":"The kind of recognition that lands best for me is...","statements":[
        {"code":"Achievement","text":"“You did a great job hitting that goal on time.”"},
        {"code":"Connection","text":"“I really value you as a person and a friend.”"},
        {"code":"Growth","text":"“You have grown so much in your leadership skills.”"},
        {"code":"Purpose","text":"“Your work made a real difference in that child’s life.”"},
    ]},
    {"id":"B16","section":"motiv","title":"Definition of Success","intro":"To me, success looks like...","statements":[
        {"code":"Growth","text":"Success is becoming the best version of myself."},
        {"code":"Purpose","text":"Success is making the world a more just place."},
        {"code":"Connection","text":"Success is having a team that loves working together."},
        {"code":"Achievement","text":"Success is hitting the target numbers efficiently."},
    ]},
    {"id":"B17","section":"motiv","title":"Project Preference","intro":"Given a choice, I'd rather work on...","statements":[
        {"code":"Growth","text":"A project where I can design a new system or strategy."},
        {"code":"Purpose","text":"A project that directly advocates for the youth."},
        {"code":"Connection","text":"A project where we collaborate closely as a group."},
        {"code":"Achievement","text":"A project with a clear deadline and measurable outcome."},
    ]},
    {"id":"B18","section":"motiv","title":"Dealing with Failure","intro":"When something goes wrong, my first instinct is to...","statements":[
        {"code":"Achievement","text":"I analyze the data to see where the process broke down."},
        {"code":"Connection","text":"I worry I let the team down relationally."},
        {"code":"Growth","text":"I treat it as a learning opportunity to get better."},
        {"code":"Purpose","text":"I question if we lost sight of the mission."},
    ]},
    {"id":"B19","section":"motiv","title":"Coaching Needs","intro":"The coaching/support that helps me most is...","statements":[
        {"code":"Growth","text":"Challenge me to reach the next level of my career."},
        {"code":"Purpose","text":"Remind me why this work matters in the big picture."},
        {"code":"Connection","text":"Check in on me personally and how I am doing."},
        {"code":"Achievement","text":"Give me clear metrics on where I stand."},
    ]},
    {"id":"B20","section":"motiv","title":"Values Check","intro":"The value I tend to prioritize most is...","statements":[
        {"code":"Growth","text":"Competence: Being highly skilled at what I do."},
        {"code":"Purpose","text":"Integrity: Doing what is right, even when it is hard."},
        {"code":"Connection","text":"Community: Being part of a supportive tribe."},
        {"code":"Achievement","text":"Excellence: Delivering high-quality results."},
    ]},
    {"id":"B21","section":"motiv","title":"Burnout Trigger","intro":"Under stress, I am more likely to burn out if...","statements":[
        {"code":"Purpose","text":"Feeling like a cog in a machine with no meaning."},
        {"code":"Growth","text":"Feeling incompetent or undertrained for the task."},
        {"code":"Connection","text":"Feeling lonely or excluded by my peers."},
        {"code":"Achievement","text":"Feeling like we are spinning our wheels with no results."},
    ]},
    {"id":"B22","section":"motiv","title":"Motivation in Crisis","intro":"In a crisis, I'm most motivated by...","statements":[
        {"code":"Achievement","text":"I am motivated to solve the problem and fix the mess."},
        {"code":"Connection","text":"I am motivated to protect the people involved."},
        {"code":"Growth","text":"I am motivated to learn from this so it doesn’t happen again."},
        {"code":"Purpose","text":"I am motivated to ensure justice is done."},
    ]},
    {"id":"B23","section":"motiv","title":"The “Why”","intro":"My deeper reason for doing this work is...","statements":[
        {"code":"Growth","text":"I work here to build a career and skills."},
        {"code":"Purpose","text":"I work here because I believe in the cause."},
        {"code":"Connection","text":"I work here because I love the team culture."},
        {"code":"Achievement","text":"I work here to get things done and achieve goals."},
    ]},
    {"id":"B24","section":"motiv","title":"Final Motivation Check","intro":"I most want to be known as...","statements":[
        {"code":"Growth","text":"I want to be known as an Expert."},
        {"code":"Purpose","text":"I want to be known as an Advocate."},
        {"code":"Connection","text":"I want to be known as a Friend."},
        {"code":"Achievement","text":"I want to be known as a High-Performer."},
    ]},
]


# --- DATA DICTIONARIES (Updated with new content) ---

COMM_PROFILES = {
    "Director": {
        "name": "Director Communicator",
        "tagline": "The Decisive Driver",
        "overview": "<strong>Core Style:</strong> You blend decisive, crisis-ready leadership with a bias for action. You are likely to set direction quickly and then rally people to move with you. You prioritize efficiency and competence, often serving as the 'adult in the room' who keeps things calm while making necessary calls. You rarely suffer from 'analysis paralysis,' preferring to make a wrong decision that can be fixed rather than no decision at all.<br><br><strong>Your Superpower:</strong> In high-pressure moments, you step in and organize. Staff see you as fair and decisive—they know you will act, so they aren't stuck in limbo. When everyone else is panicking, your clarity acts as an anchor.",
        "conflictImpact": "Under stress, you may move faster than staff can realistically integrate, making them feel like they are always 'behind' or incompetent. You might default to control before curiosity, issuing orders rather than asking questions.",
        "traumaStrategy": "Your consistency and clear boundaries can be regulating for youth who need predictability, though some may find your intensity intimidating. Traumatized brains often crave structure to feel safe.",
        "supervising_bullets": [
            "**Be Concise:** Get to the point immediately.",
            "**Focus on Outcomes:** Tell them what needs to be achieved, leave the how to them.",
            "**Respect Autonomy:** Give them space to operate independently."
        ],
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Before finalizing a decision, ask Shift Supervisors: 'What are we not seeing from the floor?' and genuinely pause to listen. Your speed can sometimes silence their hesitation.",
                "youth": "Balance your big energy with moments of quiet, one-to-one check-ins where they get more room to talk. Since you take up a lot of space energetically, consciously shrinking your presence allows withdrawn youth to step forward.",
                "supervisor": "Name the operational risk of moving fast: 'We can do this quickly if we also build in these guardrails.' This shows you aren't just rushing, but calculating the cost of speed.",
                "leadership": "Highlight where strict standards are helping kids AND where they might be creating burnout for staff. You are the best person to identify when the 'ask' has exceeded the 'capacity.'"
            },
            "Shift Supervisor": {
                "directReports": "Create space for early-warning conversations: 'You don't have to have all the answers before you tell me something is off.' Your staff may hide problems until they have a solution to impress you.",
                "youth": "Try naming the 'why' behind structure in simple, human language: 'This schedule is here so you know what to expect. Surprises can be scary.' This softens your directives.",
                "supervisor": "Be honest about any emotional load you are carrying from trying to smooth everything out for everyone. You often look like you have it all together, so you must explicitly voice when you are nearing capacity.",
                "leadership": "Be candid about how much time it takes to bring people along and where you need backing. Don't just report that the task is done; report what it *took* to get it done."
            },
            "YDP": {
                "directReports": "With peers, name explicitly when you are shifting from listening mode to decision mode: 'I've heard the input; here is the decision.' This helps peers understand that the brainstorming phase is over.",
                "youth": "Hold steady when they test your limits. Remind yourself that pushback is a sign you are holding needed structure. They are shaking the fence to see if it holds; your job is to be the fence.",
                "supervisor": "Periodically highlight where strict standards are helping kids and where they might be driving stress. Your eye for efficiency is a gift—use it to point out policies that are getting in the way of care.",
                "leadership": "Show that learning is expected: 'Getting it wrong the first few times is part of learning.' This signals that while you have high standards, you are safe enough to fail with."
            }
        }
    },
    "Encourager": {
        "name": "Encourager Communicator",
        "tagline": "The Relational Energizer",
        "overview": "<strong>Core Style:</strong> You lead with enthusiasm, vision, and warmth. You act as the emotional glue of the team, paying attention to how people feel and ensuring they feel seen and supported. You help change feel both human and organized. You are likely the person others come to when they are discouraged.<br><br><strong>Your Superpower:</strong> You keep the 'why' of the work alive when others are exhausted. You are often the one who notices and names growth in youth or staff.",
        "conflictImpact": "You may avoid giving sharp feedback because you don't want to discourage someone or damage the relationship. You might also overcommit your emotional energy when many people need you, leading to 'empathy fatigue'.",
        "traumaStrategy": "Your ability to foster belonging helps youth feel that adults are approachable, kind, and on their side. For youth who expect rejection or harshness, your consistent warmth disrupts their negative worldview.",
        "supervising_bullets": [
            "**Allow Discussion:** Need the relational runway to take off.",
            "**Ask for Specifics:** Drill down to find the reality beneath the enthusiasm.",
            "**Follow Up in Writing:** Document the boring parts for them."
        ],
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Create explicit space for them to say no or negotiate capacity: 'If this feels like too much right now, tell me and we'll prioritize.' Your enthusiasm can sometimes feel like pressure.",
                "youth": "Use your warmth first, then your firmness: 'I care about you, and that's why this boundary is still a hard no.' This technique helps detach the 'No' from rejection.",
                "supervisor": "Share not just the enthusiasm around initiatives but also the realistic limits of your team's bandwidth. You are the advocate for the team's heart; make sure leadership knows when that heart is tired.",
                "leadership": "Clearly state your own needs and boundaries instead of silently absorbing more emotional labor. You are at high risk for martyrdom; vocalizing your limits is a professional responsibility."
            },
            "Shift Supervisor": {
                "directReports": "Be explicit about what is truly flexible vs. what is not to avoid confusion between 'nice to have' and 'must do'. Your kindness can sometimes blur the lines; clear is kind.",
                "youth": "Maintain structure while being caring: 'I understand why you are angry, and I still can't allow X. Here is what we can do.' Validate the emotion completely, but hold the behavioral line firm.",
                "supervisor": "Share not just how others feel but also what concrete support you need to keep carrying this emotional work. Don't just vent; ask for the resources required to sustain the morale.",
                "leadership": "Name where staff need more time or training to realistically meet the standards you are reinforcing. Connect the dots between staff well-being and youth outcomes."
            },
            "YDP": {
                "directReports": "With peers, avoid cushioning feedback so much that the message becomes unclear—name the behavior change you need. Trust that your relationship is strong enough to handle the truth.",
                "youth": "You can be kind and clear: 'I'm not going anywhere, and that behavior is still not okay here.' This reassurance combats abandonment fears while maintaining safety.",
                "supervisor": "Ask your supervisor to help you script accountability conversations that still feel kind. Role-playing these moments can lower your anxiety about 'being mean'.",
                "leadership": "Don't hide your standards behind niceness—being clear is an act of support. When you let standards slide to be nice, you set the next shift up for failure."
            }
        }
    },
    "Facilitator": {
        "name": "Facilitator Communicator",
        "tagline": "The Calm Bridge",
        "overview": "<strong>Core Style:</strong> You prefer to listen first and build consensus. You blend a calm, listening posture with a genuine desire to keep relationships steady. You create calmer, more predictable environments. You operate on the belief that the collective wisdom of the group is stronger than any single directive.<br><br><strong>Your Superpower:</strong> You de-escalate tension by staying steady and non-threatening. People feel safe bringing mistakes or worries to you without fear of shame.",
        "conflictImpact": "You might stay neutral too long when a strong stance is needed, hoping the group will self-correct. You may quietly carry moral distress or frustration without voicing it.",
        "traumaStrategy": "Your steady presence helps youth feel safe enough to open up, especially when they aren't ready for intensity. Hyper-vigilant youth often scan for aggression; your low-affect, calm demeanor signals 'no threat'.",
        "supervising_bullets": [
            "**Advance Notice:** Give them time to think before asking for a decision.",
            "**Deadlines:** Set clear 'decision dates' to prevent endless deliberation.",
            "**Solicit Opinion:** Ask them explicitly what they think during meetings."
        ],
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Name explicitly when you are shifting from listening mode to decision mode: 'I've heard the input; here's the decision.' Staff may assume the decision is still up for debate unless you clearly mark the transition.",
                "youth": "Hold steady when they test limits. Remind yourself that pushback is a sign you are holding needed structure. You don't need to be loud to be firm; your consistency is your strength.",
                "supervisor": "Be candid about how much time it takes to bring people along and where you need backing. Ensure your supervisor understands that your 'slowness' is actually an investment in long-term buy-in.",
                "leadership": "Don't over-own the team's reactions; you can care without carrying all of their feelings. Differentiate between 'listening to' their frustration and 'solving' their frustration."
            },
            "Shift Supervisor": {
                "directReports": "Practice being more direct when standards aren't met: 'I care about you, and this still has to be corrected by Friday.' Frame accountability as a form of support—you are helping them succeed in their role.",
                "youth": "Remember that some flexibility can be regulating too—look for safe places to say yes when you can. Finding small 'Yeses' builds the relational capital needed for the big 'Nos'.",
                "supervisor": "Don't undersell your impact—your quiet consistency keeps a lot from falling apart. Make sure your wins are visible, as prevention is often invisible.",
                "leadership": "Watch for signs you are quietly absorbing tasks your team should own; invite them into problem-solving instead. Don't be the martyr who cleans up the mess to keep the peace."
            },
            "YDP": {
                "directReports": "With peers, resist taking on everyone's emotional load—offer support, but help peers connect to other resources (EAP, debriefs). You are a peer, not a therapist.",
                "youth": "Maintain structure while being caring: 'I understand why you're angry, and I still can't allow X.' You can validate their feelings 100% while validating their behavior 0%.",
                "supervisor": "Ask your supervisor for clarity on non-negotiables so you feel confident enforcing them. Knowing exactly where the 'hard line' is allows you to be flexible everywhere else.",
                "leadership": "Break growth steps into very small, concrete actions so they feel manageable. Help leadership see the small steps needed to get to the big goal."
            }
        }
    },
    "Tracker": {
        "name": "Tracker Communicator",
        "tagline": "The Structured Guardian",
        "overview": "<strong>Core Style:</strong> You lead with structure, detail, and a strong respect for procedure. You want plans to be sound and aligned before you move. You believe the path to success is through good systems and accurate work.<br><br><strong>Your Superpower:</strong> You protect youth and staff by ensuring documentation and procedures support ethical, safe care. You notice small patterns that could become big risks. You check the smoke detectors to ensure the fire doesn't happen.",
        "conflictImpact": "You may feel intolerant of what looks like carelessness in others, interpreting a missed checkbox as a lack of care. You can focus so much on accurate reporting that you under-communicate empathy.",
        "traumaStrategy": "Your consistency creates a predictable environment that feels safe for youth with trauma histories. Chaos is a trigger for trauma; your ability to create order acts as a soothing balm for dysregulated nervous systems.",
        "supervising_bullets": [
            "**Be Specific:** Give the metric, not vague encouragement.",
            "**Provide Data:** Bring the numbers and the facts to persuade.",
            "**Written Instructions:** Follow up verbal conversation with an email."
        ],
        "roleTips": {
            "Program Supervisor": {
                "directReports": "Occasionally invite rough drafts: 'Bring me your early thoughts, not just the final proposal.' Perfectionism can silence your team; show them you value their raw ideas too.",
                "youth": "Try small moments of flexibility inside your structure so they experience you as human, not just rule-enforcing. A rigid rule followed by a moment of unexpected grace can be a powerful therapeutic tool.",
                "supervisor": "Highlight how much relational work you are doing in addition to the procedural work, so it is seen and valued. Don't let yourself get pigeonholed as just 'the admin person'.",
                "leadership": "Name where your high standards are working and where they may be driving staff stress beyond what's sustainable. Use your data to advocate for realistic workloads."
            },
            "Shift Supervisor": {
                "directReports": "Clarify where they truly own decisions vs. where you need to be consulted, so they don't become over-dependent. If you fix every error, they will stop checking their own work.",
                "youth": "Explain why structure exists in terms of safety and success, not just 'because that's the rule.' 'We lock this door so that everyone sleeps safe tonight' lands better than 'It's policy.'",
                "supervisor": "Ask your supervisor to help you prioritize what truly needs perfection and what can be 'good enough.' Not every email needs to be a dissertation; save your energy for the critical safety logs.",
                "leadership": "Share tasks and expertise with peers instead of quietly doing things for them. Teaching someone to fish is messier than fishing for them, but it builds a stronger team."
            },
            "YDP": {
                "directReports": "With peers, pair data shares with appreciation ('Here's what improved, here's who helped make that happen'). People receive data better when it is wrapped in recognition.",
                "youth": "Check in with peers about what support they need to meet expectations before tightening accountability. Ensure the youth *can* do what you are asking before you penalize them.",
                "supervisor": "Ask your supervisor to help you contextualize metrics so you don't carry them as a personal verdict. A bad number doesn't mean you are a bad worker; it means the strategy needs adjusting.",
                "leadership": "Occasionally invite rough drafts from peers: 'Bring me your early thoughts, not just the final proposal.' Encourage a culture where it is safe to be in-process."
            }
        }
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "name": "Growth Motivation",
        "tagline": "The Learner/Builder",
        "summary": "You are fueled by learning and development that clearly connects to the mission. You're hungry to improve and want to keep leveling up how you and your team support youth. You view every shift as a classroom and every challenge as a curriculum; stagnation is your enemy, and competence is your currency.",
        "strategies_bullets": [
            "**Stretch Assignments:** Tasks slightly above current skill level.",
            "**Career Pathing:** Regular discussion of professional future.",
            "**Mentorship:** Connection with leaders they admire."
        ],
        "boosters": [
            "**Focused Projects:** Ask for a small number of focused growth projects rather than trying to improve everything at once. You thrive on depth.",
            "**Peer Learning:** You light up when sharing strategies with peers rather than learning alone from a manual. The social aspect validates your expertise.",
            "**Concrete Changes:** You are energized by turning new learning into concrete changes on the floor. Theory is boring to you until it becomes practice."
        ],
        "killers": [
            "**Disconnected Training:** You feel drained learning skills that feel disconnected from the realities of Elmcrest.",
            "**Lack of Adoption:** You feel discouraged when youth or staff don't 'take up' the growth you see for them. It is painful for you to watch potential go unrealized.",
            "**Isolation:** Being left to figure everything out alone without peers to process with. You need a sounding board to refine your ideas."
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
        "summary": "You are driven to make decisions that align with your values and with what's right for youth and staff. You care not just about order, but about justice and integrity. You need to know that your work matters in a cosmic sense; you can endure difficult shifts if you believe the work is meaningful.",
        "strategies_bullets": [
            "**The Why:** Explain the mission behind every mandate.",
            "**Storytelling:** Share narratives of redemption and impact.",
            "**Ethics:** Allow space to voice moral concerns."
        ],
        "boosters": [
            "**Value Alignment:** You are motivated when goals align with safety, healing, and justice for youth. When you can see a direct line between a task and a youth's dignity, you have infinite energy.",
            "**Advocacy:** You thrive when advocating for youth or staff when something is not in their best interest. Being the 'voice for the voiceless' gives you a rush of purpose.",
            "**Meaningful Metrics:** You need to know that numbers reflect real, meaningful change for youth. You don't care about compliance; you care about outcomes."
        ],
        "killers": [
            "**Performative Goals:** You emotionally disengage from goals that feel performative or disconnected from kids' real needs.",
            "**Moral Distress:** You feel intense frustration when the system feels misaligned with your values. Being forced to enforce a rule you don't believe in is physically painful.",
            "**Bureaucracy:** Tasks that feel like 'checking boxes' without real impact. If you can't see the 'why', you will struggle to do the 'what'."
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
        "summary": "You are fueled by strong relationships and a sense of 'we're in this together'. You make staff feel less alone in the hard work and foster a climate where it's okay to ask for help. For you, the *people* are the work. You believe that a healthy team can handle any crisis.",
        "strategies_bullets": [
            "**Face Time:** Prioritize in-person check-ins.",
            "**Team Rituals:** Encourage meals, huddles, and traditions.",
            "**Personal Care:** Ask about life outside work."
        ],
        "boosters": [
            "**Reflective Space:** You need regular reflective space, not just task-focused check-ins. You need time to process the 'emotional residue' of the shift.",
            "**Shared Wins:** You are motivated by seeing the whole team succeed, not just being the 'star'. A high-five after a successful group intervention means more to you than an award.",
            "**Belonging:** You thrive in spaces where people are honest and curious together. Feeling 'known' by your colleagues makes the hard parts of the job bearable."
        ],
        "killers": [
            "**Interpersonal Tension:** You take tension very personally and it drains you. Walking into a room where people are angry at each other feels like walking into a wall of heat.",
            "**Isolation:** Lack of relational support quickly drains your motivation to try new things. If you feel like you are out on a limb alone, you will retreat to safety.",
            "**Sole Responsibility:** Feeling like you have to carry things yourself without the team. You are a pack animal; being forced to hunt alone induces anxiety."
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
        "summary": "You are results-focused and decisive. You want to see tangible improvements in safety, documentation, and outcomes. You believe the path to success is through good systems and accurate work. You treat the unit like a puzzle to be solved.",
        "strategies_bullets": [
            "**Visual Goals:** Use charts, dashboards, or checklists.",
            "**Public Wins:** Acknowledge success in front of peers.",
            "**Autonomy:** Give them the goal and let them design the strategy."
        ],
        "boosters": [
            "**Clear Goals:** You like clear indicators that your effort is making a difference. 'Reduce incidents by 10%' is motivating because it has a finish line.",
            "**Data & Progress:** You are strong at tracking metrics and helping the team adjust based on data. Seeing a graph go in the right direction gives you a dopamine hit.",
            "**Incremental Gains:** Celebrating small wins helps you avoid feeling like the work is endless pressure. You need to win the small games (a clean shift) to stay hungry."
        ],
        "killers": [
            "**Vague Expectations:** You get frustrated if you don't see clear movement or progress. Working hard without knowing where the goalposts are feels like running on a treadmill.",
            "**Incompetence:** You feel impatient with staff who struggle to meet standards. Watching the same mistake happen three times feels like a personal insult to your efficiency.",
            "**Slow Progress:** You judge yourself harshly when progress is slower than you'd like. You tend to take systemic failures as personal failures."
        ],
        "roleSupport": {
            "Program Supervisor": "Set process goals (e.g., 'We debrief every incident') not just outcome goals (e.g., 'Fewer incidents').",
            "Shift Supervisor": "Partner with clinicians to define realistic pacing for youth progress so you don't burn out.",
            "YDP": "Ask your supervisor to help you differentiate between what is in your control and what is system-level."
        }
    }
}

INTEGRATED_PROFILES = {
    "Director-Achievement": {
        "title": "THE EXECUTIVE GENERAL",
        "summary": "You are a high-velocity leader who combines the ability to set clear direction with a relentless drive for tangible outcomes. You don't just want to lead; you want to win. The synergy here is **Operational Velocity**.",
        "strengths": [
            "**Rapid Decision Architecture:** You process risk vs. reward faster than most. You are comfortable making calls with 70% of the information because you trust your ability to course-correct.",
            "**Objective Focus:** You separate the story from the fact. You focus on behaviors and outcomes rather than getting lost in emotional narratives.",
            "**High-Bar Accountability:** You do not walk past a mistake. You believe that correcting small errors prevents big failures."
        ],
        "weaknesses": [
            "**The Steamroller Effect:** A valuing of speed over consensus. You may announce decisions without checking if the team is emotionally ready to follow.",
            "**Burnout by Intensity:** Your engine runs hotter than others. You accidentally burn out your team by pushing for result after result.",
            "**Dismissing 'Soft' Data:** A preference for tangible metrics over feelings. You might ignore a staff member's 'bad feeling', missing an early warning sign."
        ],
        "comm_arch": [
            "**Listening Style:** Action-Oriented. You listen for the problem so you can solve it.",
            "**Persuasion Trigger:** Efficiency + Results. Show you how this plan saves time or improves safety.",
            "**Feedback Preference:** Blunt & Immediate. You respect people who look you in the eye and say it straight.",
            "**Meeting Mode:** Briefing Style. You want an agenda, clear action items, and a hard stop time."
        ],
        "roadmap": [
            "**Phase 1: The Pause Button (0–6 Months):** Force a delay between your thought and your action. Practice asking three questions before giving one order.",
            "**Phase 2: Narrative Leadership (6–12 Months):** Learn to explain the 'Why' behind your directives. Connect your commands to the larger mission.",
            "**Phase 3: Multiplier Effect (12–18 Months):** Stop being the hero who fixes everything. Train two deputies to think like you."
        ]
    },
    "Director-Growth": {
        "title": "THE RESTLESS IMPROVER",
        "summary": "You are a visionary builder who is never satisfied with 'good enough.' You combine the authority to make changes with a hunger to learn and improve. The synergy here is **Transformational Leadership**.",
        "strengths": [
            "**Diagnostic Speed:** You quickly identify skill gaps or process failures. You don't just see a bad shift; you see why it happened.",
            "**Fearless Innovation:** You aren't afraid to try a new schedule or a new intervention if the old one isn't working. You treat the floor like a lab.",
            "**High-Impact Coaching:** You give direct, developmental feedback that accelerates the growth of their peers. You don't coddle staff; you challenge them because you believe they can be better."
        ],
        "weaknesses": [
            "**The Pace Mismatch:** Your brain moves faster than the system changes. You get frustrated with staff who learn slowly.",
            "**'Fix-It' Fatigue:** Seeing everything as a problem to be solved. Staff feel they can never please you because you always find the one thing that could be better.",
            "**Leaving People Behind:** Focusing on the idea rather than the adoption. You launch a great new initiative, but nobody follows it."
        ],
        "comm_arch": [
            "**Listening Style:** Diagnostic. You listen for gaps in logic or skills. You are constantly thinking, 'How do we fix this?'",
            "**Persuasion Trigger:** Innovation + Logic. Show you how a new method is smarter, faster, or more effective than the 'old way'.",
            "**Feedback Preference:** Specific & Developmental. You want to know exactly what you did wrong and how to fix it.",
            "**Meeting Mode:** Workshop Style. You want to brainstorm, problem-solve, and leave with a new plan."
        ],
        "roadmap": [
            "**Phase 1: Validation (0–6 Months):** Learn to validate the current effort before suggesting a future improvement. Practice saying, 'This is working well.'",
            "**Phase 2: Change Management (6–12 Months):** Study how people process change. Learn that resistance isn't stubbornness; it's often fear.",
            "**Phase 3: Capacity Building (12–18 Months):** Shift from being the one who comes up with ideas to the one who facilitates others' ideas."
        ]
    },
    "Director-Purpose": {
        "title": "THE MISSION DEFENDER",
        "summary": "You are a warrior for the cause. You combine the strength of a commander with the heart of an advocate. The synergy here is **Ethical Courage**. You provide the moral backbone for your team.",
        "strengths": [
            "**Unshakeable Advocacy:** When you see something unjust or unsafe, you act immediately. You are not intimidated by titles or difficulty.",
            "**Clarity of 'Why':** You can draw a straight line between a boring task and the mission (keeping kids safe). You inspire purpose.",
            "**Crisis Ethics:** In a chaotic restraint or incident, you keep your moral compass. You ensure safety is never compromised for convenience."
        ],
        "weaknesses": [
            "**Righteous Rigidity:** Seeing the world in black and white. You may view a difference of opinion as a moral failing in the other person.",
            "**The Martyr Complex:** Believing that if you stop fighting, the mission fails. You overwork yourself to the point of collapse.",
            "**Judgmental Tone:** High internal standards applied externally. You may come across as 'preachy' or superior to staff."
        ],
        "comm_arch": [
            "**Listening Style:** Evaluative. You are listening to see if the speaker's values align with yours.",
            "**Persuasion Trigger:** Values + Impact. Don't talk about the budget; talk about how this decision affects the youth's dignity.",
            "**Feedback Preference:** Honest & Principled. You can handle harsh truth if it comes from a place of integrity.",
            "**Meeting Mode:** Mission-Driven. You want meetings to stay focused on the 'Main Thing'—the youth."
        ],
        "roadmap": [
            "**Phase 1: The Gray Zone (0–6 Months):** Practice identifying the validity in opposing viewpoints. Learn that two people can have different strategies and both care about the kids.",
            "**Phase 2: Sustainable Advocacy (6–12 Months):** Learn to pick your battles. Not every hill is worth dying on.",
            "**Phase 3: Cultural Architecture (12–18 Months):** Move from fighting individual fires to building fire-proof systems. Help write policies that institutionalize values."
        ]
    },
    "Director-Connection": {
        "title": "THE PROTECTIVE CAPTAIN",
        "summary": "You are the 'Papa Bear' or 'Mama Bear' of the unit. You combine decisive authority with a deep tribal loyalty to your people. The synergy here is **Safe Enclosure**. You lead from the front, taking the hits so your team doesn't have to.",
        "strengths": [
            "**Decisive Care:** You don't just sympathize; you fix. If a staff member is overwhelmed, you send them on break and take their post.",
            "**Crisis Stabilization:** When things get scary, you get calm and protective. Your presence signals 'I've got this'.",
            "**Team Loyalty:** You build a cohesive unit. You define 'Us' clearly and ensure everyone on the shift feels included."
        ],
        "weaknesses": [
            "**Us vs. Them Mentality:** Intense loyalty to your specific shift. You may become hostile toward other shifts or administration.",
            "**Over-Functioning:** A desire to protect your team from stress. You do everyone's job for them, and staff never learn to handle the load.",
            "**Taking Conflict Personally:** Conflating professional disagreement with personal betrayal. If a staff member questions you, you feel hurt."
        ],
        "comm_arch": [
            "**Listening Style:** Protective. You listen for threats to your team's well-being.",
            "**Persuasion Trigger:** Team Benefit. Show you how this change will help your people suffer less or succeed more.",
            "**Feedback Preference:** Respectful & Private. Never correct this person in front of their 'troops'. Do it one-on-one.",
            "**Meeting Mode:** Family Dinner. You want business done, but you also want to check in on everyone's life."
        ],
        "roadmap": [
            "**Phase 1: Delegation of Care (0–6 Months):** Stop being the only one who fixes things. Assign 'care tasks' to others to build their muscles.",
            "**Phase 2: Organizational Citizenship (6–12 Months):** Expand your circle of loyalty. Start viewing the whole agency as 'your team'.",
            "**Phase 3: Mentorship (12–18 Months):** Transition from being the Captain to being the Admiral. Teach other leaders how to build the loyalty you generate."
        ]
    },
    "Encourager-Achievement": {
        "title": "THE COACH",
        "summary": "You are the ultimate morale booster who loves to win. You combine high relational warmth with a drive for results. The synergy here is **Performance Positivity**. You make hard work feel like a game that we are winning together.",
        "strengths": [
            "**Motivational Framing:** You can reframe a boring Tuesday cleaning task into a team challenge. You inject energy into static situations.",
            "**Celebrating the Wins:** You notice the small victories and make noise about them. You build a 'Winning Culture'.",
            "**Resilience:** When the plan fails, you don't sulk. You bounce back, find the silver lining, and rally the team for Plan B."
        ],
        "weaknesses": [
            "**The 'Nice' Trap:** Fear that giving negative feedback will kill the vibe. You let underperformance slide, hoping it will fix itself.",
            "**Hiding Failure:** Desire to present a winning image. You might downplay serious incidents or 'spin' bad data.",
            "**Exhaustion:** Maintaining high energy is physically draining. You crash hard at home or become resentful that no one is cheering for you."
        ],
        "comm_arch": [
            "**Listening Style:** Appreciative. You listen for the good news and the potential. You might miss the red flags.",
            "**Persuasion Trigger:** Vision + Success. Paint a picture of how great it will feel when we achieve this goal.",
            "**Feedback Preference:** Encouraging Sandwich. Start with the positive, give the growth area, end with belief in them.",
            "**Meeting Mode:** Pep Rally. You want energy, interaction, and to leave feeling pumped up."
        ],
        "roadmap": [
            "**Phase 1: The Hard Conversations (0–6 Months):** Commit to giving one piece of constructive/negative feedback per week. Get comfortable with the awkwardness.",
            "**Phase 2: Data Reality (6–12 Months):** Learn to love the 'bad' data. Use your optimism to fix the bad numbers, not to hide them.",
            "**Phase 3: Culture Carrier (12–18 Months):** Teach other supervisors how to bring the energy. Systematize your celebration rituals."
        ]
    },
    "Encourager-Growth": {
        "title": "THE MENTOR",
        "summary": "You are a developer of people. You combine warmth with a deep belief in human potential. The synergy here is **Psychological Safety**. You create an environment where it is safe to make mistakes, which is the only environment where true learning happens.",
        "strengths": [
            "**Talent Spotting:** You see gifts in people that they don't see in themselves. You build the bench.",
            "**Developmental Feedback:** You give feedback that feels like a gift, not a punishment. Staff get better faster because they aren't defensive.",
            "**Patience:** You understand that behavior change takes time. You hold the hope when others have lost it."
        ],
        "weaknesses": [
            "**Tolerating Mediocrity:** Confusing 'potential' with 'performance.' You keep waiting for a staff member to improve, ignoring the fact that they haven't changed.",
            "**Over-Investment:** Taking responsibility for others' growth. You work harder on their growth than they do.",
            "**Softening the Blow:** Empathy for the struggle of learning. You hint at a problem rather than naming it."
        ],
        "comm_arch": [
            "**Listening Style:** Deep & Reflective. You listen to understand the person's internal world and motivation.",
            "**Persuasion Trigger:** Growth + Potential. Show how this task will help them learn a new skill or reach their career goals.",
            "**Feedback Preference:** Dialogue. You want a conversation about growth, not a one-way directive.",
            "**Meeting Mode:** Seminar Style. You want to learn something new or discuss a case study."
        ],
        "roadmap": [
            "**Phase 1: Assessment (0–6 Months):** Learn to objectively assess skill vs. will. You can teach skill; you cannot force will.",
            "**Phase 2: The Exit Ramp (6–12 Months):** Learn how to help people transition out of roles that aren't a fit. This is also a form of mentorship.",
            "**Phase 3: Train the Trainer (12–18 Months):** Build a curriculum. Take your intuitive teaching style and write it down so others can use it."
        ]
    },
    "Encourager-Purpose": {
        "title": "THE HEART OF THE MISSION",
        "summary": "You are the soul of the unit. You combine deep empathy with unshakeable values. The synergy here is **Emotional Resonance**. You feel the pain of the youth and the stress of the staff, and you transmute that into a call to action.",
        "strengths": [
            "**Cultural Compass:** You instinctively know when the culture is turning toxic or cold. You are the canary in the coal mine.",
            "**Inspiring Communication:** You speak from the heart. When you talk about the kids, people listen because your care is authentic.",
            "**Intuitive Connection:** You can reach the kid no one else can reach because you lead with vulnerability, not authority."
        ],
        "weaknesses": [
            "**Compassion Fatigue:** No emotional skin. You absorb everyone's trauma. You crash into depression or numbness.",
            "**Boundary Drift:** Wanting to help so badly that rules feel like barriers. You might share too much personal info or make special exceptions.",
            "**Difficulty with Punitive Measures:** Empathy for the youth's trauma history. You struggle to enforce consequences because 'they've been through so much'."
        ],
        "comm_arch": [
            "**Listening Style:** Empathetic. You listen with your whole body. You validate feelings before facts.",
            "**Persuasion Trigger:** Human Story. Don't show a spreadsheet; tell the story of one kid whose life will change.",
            "**Feedback Preference:** Kind & Gentle. You bruise easily. You need to know you are still valued even if you messed up.",
            "**Meeting Mode:** Connection First. You need to clear the emotional air before diving into business."
        ],
        "roadmap": [
            "**Phase 1: Emotional Armor (0–6 Months):** Learn the difference between empathy (feeling *with* them) and compassion (feeling *for* them). Keep one foot on the bank.",
            "**Phase 2: Structural Care (6–12 Months):** Learn how rules and boundaries are actually tools of love for traumatized kids.",
            "**Phase 3: The Storyteller (12–18 Months):** Use your voice to advocate for systemic change. Write the impact stories that get funding or change policy."
        ]
    },
    "Encourager-Connection": {
        "title": "THE TEAM BUILDER",
        "summary": "You are the glue. You combine warmth with a deep need for group cohesion. The synergy here is **Social Capital**. You ensure that the team likes each other, trusts each other, and wants to work together.",
        "strengths": [
            "**Conflict Diffusion:** You sense tension before it explodes and smooth it over with humor, food, or a kind word.",
            "**Retention Mastery:** You make people feel like they belong. You remember birthdays, ask about kids, and create fun.",
            "**Inclusive Leadership:** You notice the person sitting alone in the cafeteria. You ensure everyone has a voice."
        ],
        "weaknesses": [
            "**Ruinous Empathy:** Valuing harmony over truth. You don't fire the toxic employee because 'they're going through a hard time'.",
            "**Clique Formation:** Naturally bonding with those who reciprocate your warmth. You accidentally create an 'in-group' of favorites.",
            "**Difficulty with Unpopularity:** Need for connection. You struggle to make necessary unpopular decisions (like denying time off)."
        ],
        "comm_arch": [
            "**Listening Style:** Relational. You listen to connect. You interrupt to share 'me too' stories.",
            "**Persuasion Trigger:** Social Proof. Show you that 'everyone else is on board' and it will be fun.",
            "**Feedback Preference:** Warm & Reassuring. Reaffirm the relationship ('We're cool') before and after the critique.",
            "**Meeting Mode:** Roundtable. You want everyone to speak. You hate lectures."
        ],
        "roadmap": [
            "**Phase 1: Boundaries (0–6 Months):** Learn to say 'No' without over-explaining or apologizing.",
            "**Phase 2: Professional Distance (6–12 Months):** Differentiate between being 'Friendly' and being 'Friends.'",
            "**Phase 3: Culture Architect (12–18 Months):** Move from planning potlucks to planning culture. How do we institutionalize belonging?"
        ]
    },
    "Facilitator-Achievement": {
        "title": "THE STEADY MOVER",
        "summary": "You are the tortoise who beats the hare. You combine a calm, listening approach with a quiet but relentless drive for results. The synergy here is **Sustainable Progress**. You build consensus for changes that actually stick.",
        "strengths": [
            "**Broad Buy-In:** You don't move until the key players agree. You do the pre-work of aligning people.",
            "**Calm Execution:** You don't panic when the numbers are down. You just adjust the plan and keep working.",
            "**Listening as Strategy:** You listen to the complaints to find the operational bottlenecks. You use feedback to sharpen the spear."
        ],
        "weaknesses": [
            "**Analysis Paralysis:** Wanting 100% consensus and 100% data confidence. You study the problem for too long while the unit is burning.",
            "**Frustration with 'Director' Types:** You value process; they value speed. You view fast movers as reckless; they view you as an obstructionist.",
            "**Under-Selling Success:** Modesty and focus on the 'we.' You don't claim credit for your wins, so leadership doesn't know how effective you are."
        ],
        "comm_arch": [
            "**Listening Style:** Synthesizing. You listen to multiple points of view and try to find the middle ground.",
            "**Persuasion Trigger:** Logic + Consensus. Show you that the data supports it AND the team supports it.",
            "**Feedback Preference:** Thoughtful & Balanced. You want time to process the feedback. Don't demand an immediate reaction.",
            "**Meeting Mode:** Structured Dialogue. You want a facilitator, a clear process, and equal air time."
        ],
        "roadmap": [
            "**Phase 1: Speed Drills (0–6 Months):** Practice making low-stakes decisions instantly. Train your gut.",
            "**Phase 2: Directive Voice (6–12 Months):** Practice saying 'I have decided' instead of 'What do we think?' in appropriate moments.",
            "**Phase 3: Strategic Alignment (12–18 Months):** Use your ability to bridge groups to solve agency-wide silos."
        ]
    },
    "Facilitator-Growth": {
        "title": "THE PATIENT GARDENER",
        "summary": "You cultivate an ecosystem of learning. You combine a listening posture with a desire for deep rooted growth. The synergy here is **Organic Development**. You don't force growth; you create the conditions where growth is inevitable.",
        "strengths": [
            "**Psychological Safety:** Your non-judgmental presence makes people feel safe to confess mistakes and ask for help.",
            "**Facilitated Learning:** You don't lecture; you ask questions. You teach staff *how* to think, not just what to do.",
            "**Long-Game Perspective:** You aren't rattled by a bad day. You help the team ride out the storms without losing hope."
        ],
        "weaknesses": [
            "**Lack of Urgency:** Viewing everything as a process. You tolerate safety violations or acute failure as 'part of the learning curve'.",
            "**The 'Drift':** Dislike of rigid structures. Standards slowly slip over time because you haven't reinforced the hard lines.",
            "**Over-Processing:** Love of deep understanding. You spend 2 hours debriefing a minor incident, exhausting the staff."
        ],
        "comm_arch": [
            "**Listening Style:** Curious. You ask 'Tell me more' and 'Why do you think that is?'",
            "**Persuasion Trigger:** Developmental Story. Show how this path leads to wisdom or maturity.",
            "**Feedback Preference:** Socratic. Ask them self-reflection questions rather than just telling them the answer.",
            "**Meeting Mode:** Retrospective. Looking back to learn for the future."
        ],
        "roadmap": [
            "**Phase 1: The Pruning Shears (0–6 Months):** Learn that cutting back dead branches (bad behaviors/tasks) is an act of growth.",
            "**Phase 2: Operational Cadence (6–12 Months):** Add rhythm to your growth. Weekly checks, monthly goals. Structure helps the garden grow straight.",
            "**Phase 3: Scalable Wisdom (12–18 Months):** Create learning modules. How do we take your wisdom and put it in a video or a guide?"
        ]
    },
    "Facilitator-Purpose": {
        "title": "THE MORAL COMPASS",
        "summary": "You are the conscience of the group. You combine a need for consensus with a fierce ethical drive. The synergy here is **Inclusive Justice**. You want to make sure the decision is right, AND that everyone was heard in the process.",
        "strengths": [
            "**Ethical Vetting:** You look at every decision through the lens of fairness and values. You spot the unintended consequences.",
            "**Voice for the Margins:** You notice who hasn't spoken in the meeting. You ask, 'What does the night shift think? What does the quiet kid think?'",
            "**Trust Building:** People trust you because they know you have no hidden agenda. Your agenda is fairness."
        ],
        "weaknesses": [
            "**Decision Fatigue:** Trying to weigh every single ethical variable. You can't choose a lunch spot because you don't want to exclude anyone.",
            "**Perceived as 'Slow':** The need for process. In a crisis, you want to discuss; the team needs you to act.",
            "**Process over Outcome:** Believing a fair process guarantees a good result. You hold a perfect meeting, but no decision is made."
        ],
        "comm_arch": [
            "**Listening Style:** Judicial. You are weighing the evidence and looking for fairness.",
            "**Persuasion Trigger:** Fairness + Inclusion. Show how this decision respects everyone's rights and input.",
            "**Feedback Preference:** Respectful Dialogue. Approach as peers. Don't pull rank.",
            "**Meeting Mode:** Town Hall. Open forum, democratic process."
        ],
        "roadmap": [
            "**Phase 1: Bias for Action (0–6 Months):** Practice making decisions with only 80% of the voices heard. Realize the world didn't end.",
            "**Phase 2: Conflict Confidence (6–12 Months):** Move from mediating to directing. Sometimes fairness requires a judge, not a mediator.",
            "**Phase 3: Systemic Ethics (12–18 Months):** Help design the systems (hiring, intake) so they are fair by default."
        ]
    },
    "Facilitator-Connection": {
        "title": "THE PEACEMAKER",
        "summary": "You are the harmonizer. You combine a listening style with a deep need for relationship. The synergy here is **Relational Stability**. You absorb the shocks of the system. You keep the team from fracturing under pressure.",
        "strengths": [
            "**De-Escalation Mastery:** Your non-threatening posture and genuine listening bring the temperature down instantly.",
            "**Bridge Building:** You connect people. You help the morning shift understand the night shift. You translate anger into need.",
            "**Emotional Intelligence:** You read the room perfectly. You know when to push and when to back off."
        ],
        "weaknesses": [
            "**Conflict Avoidance:** Fear that conflict will break the relationship. You let passive-aggressive behavior slide.",
            "**The Emotional Sponge:** Porous boundaries. You go home exhausted because you are carrying everyone's feelings.",
            "**Passive Resistance:** Inability to say 'No' to a face. You say 'Yes' in the meeting to be nice, but then don't do the task because you disagree with it."
        ],
        "comm_arch": [
            "**Listening Style:** Supportive. You nod, you validate, you make them feel heard.",
            "**Persuasion Trigger:** Harmony + Relationship. Show how this will make us closer or reduce tension.",
            "**Feedback Preference:** Gentle & Private. Please don't raise your voice.",
            "**Meeting Mode:** Check-In. How are we doing? How are we feeling?"
        ],
        "roadmap": [
            "**Phase 1: Assertiveness (0–6 Months):** Practice stating your own needs. 'I need [X].'",
            "**Phase 2: The Bad Cop (6–12 Months):** Role-play being the enforcer. Realize that people still like you even when you say no.",
            "**Phase 3: Facilitating Conflict (12–18 Months):** Move from *stopping* the fight to *refereeing* the fight. Help people argue productively."
        ]
    },
    "Tracker-Achievement": {
        "title": "THE ARCHITECT",
        "summary": "You are the builder of systems. You combine a love for detail with a drive for results. The synergy here is **Scalable Efficiency**. You don't just want to win today; you want to build a machine that wins every day.",
        "strengths": [
            "**Process Optimization:** You see the wasted steps in a workflow. You know how to streamline the intake process or the med pass.",
            "**Reliability:** If you say it's done, it's done. Your paperwork is flawless. Leadership never has to double-check your work.",
            "**Data-Driven Decisions:** You don't guess; you look at the logs. 'Incidents happen at 4pm, so we need staff at 4pm.'"
        ],
        "weaknesses": [
            "**Rigidity:** Finding safety in structure. You panic when the plan changes. You might prioritize filling out the form over helping the crying kid.",
            "**Valuing Process over People:** Focus on the 'What,' not the 'Who.' You treat people like widgets in your machine.",
            "**Inability to Pivot:** Sunk cost fallacy in your plan. You keep pushing the system even when it's clearly failing because you built it."
        ],
        "comm_arch": [
            "**Listening Style:** Sorting. You are categorizing information as you hear it.",
            "**Persuasion Trigger:** Data + Order. Show me the numbers. Show me the plan.",
            "**Feedback Preference:** Written & Specific. Send me an email with the details so I can reference it.",
            "**Meeting Mode:** Agenda-Driven. Start on time, end on time."
        ],
        "roadmap": [
            "**Phase 1: Human Variables (0–6 Months):** Accept that humans are messy variables. You cannot spreadsheet feelings.",
            "**Phase 2: User Experience (6–12 Months):** Ask 'How does this form *feel* to the person filling it out?' Design for the user, not just the data.",
            "**Phase 3: Systems Thinking (12–18 Months):** Move from fixing the unit to fixing the agency workflow."
        ]
    },
    "Tracker-Growth": {
        "title": "THE TECHNICAL EXPERT",
        "summary": "You are the master craftsman. You combine a love for detail with a hunger to learn. The synergy here is **Expertise**. You want to know the *right* way to do everything, and you want to teach others to do it right.",
        "strengths": [
            "**Precision Training:** You know the handbook inside and out. You teach the technique perfectly.",
            "**Best Practice Adoption:** You read the research. You bring outside knowledge in to upgrade the unit.",
            "**Problem Solving:** You troubleshoot. If a process is broken, you take it apart and fix it."
        ],
        "weaknesses": [
            "**Micromanagement:** Belief that there is only one 'Right Way' (yours). You hover over staff correcting minor details, driving them crazy.",
            "**Frustration with 'Sloppy' Work:** High standards. You become critical and condescending to staff who aren't as detailed as you.",
            "**Missing the Human Element:** Focus on technique. You evaluate a restraint based on hand placement, ignoring that the staff member was mocking the kid."
        ],
        "comm_arch": [
            "**Listening Style:** Analytical. You are checking for accuracy and consistency.",
            "**Persuasion Trigger:** Competence + Logic. Teach me something new. Show me the manual.",
            "**Feedback Preference:** Objective. Show me the scorecard. Don't fluff it up.",
            "**Meeting Mode:** Training. I want to leave knowing more than when I arrived."
        ],
        "roadmap": [
            "**Phase 1: Delegation (0–6 Months):** Let someone else do it, even if they do it 80% as well as you.",
            "**Phase 2: Soft Skills (6–12 Months):** Study leadership and empathy as 'technical skills' to be mastered.",
            "**Phase 3: Knowledge Management (12–18 Months):** Build the wiki. Create the resource library so your brain exists outside your head."
        ]
    },
    "Tracker-Purpose": {
        "title": "THE GUARDIAN",
        "summary": "You are the protector of the mission through the rigorous application of standards. The synergy here is **Compliance as Care**. You don't check boxes for fun; you check them because a missed box could mean a hurt child.",
        "strengths": [
            "**Risk Mitigation:** You see the accident before it happens. 'That door is unlocked. That knife count is off.'",
            "**Ethical Documentation:** You ensure the story is told accurately in the record. You protect the agency and the client with the truth.",
            "**Stability:** You are the anchor. In chaos, you fall back on protocol, which calms everyone down."
        ],
        "weaknesses": [
            "**Bureaucracy:** Risk aversion. You create so many rules and forms that staff can't do their job. You stifle connection with paperwork.",
            "**Seeing Rules as Absolute:** Conflating rules with morals. You struggle to make therapeutic exceptions.",
            "**Conflict with Flexible Thinkers:** You view flexibility as danger. You clash with 'Encourager' or 'Director' types who play fast and loose."
        ],
        "comm_arch": [
            "**Listening Style:** Audit. You are listening for compliance and risk.",
            "**Persuasion Trigger:** Safety + Duty. Show how this protects the mission and the kids.",
            "**Feedback Preference:** Formal. I prefer a scheduled supervision with documentation.",
            "**Meeting Mode:** Governance. Reviewing policies and incidents."
        ],
        "roadmap": [
            "**Phase 1: The 'Why' (0–6 Months):** Practice explaining *why* the rule exists every time you enforce it.",
            "**Phase 2: Risk Tolerance (6–12 Months):** Differentiate between 'Red Risks' (Life safety) and 'Yellow Risks' (Procedural error). Don't treat a typo like a fire.",
            "**Phase 3: Policy Architect (12–18 Months):** Help rewrite the rules so they are easier to follow. Good policy makes compliance easy."
        ]
    },
    "Tracker-Connection": {
        "title": "THE RELIABLE ROCK",
        "summary": "You show love through consistency. You combine a need for order with a deep loyalty to the team. The synergy here is **Operational Support**. You take care of the team by taking care of the environment.",
        "strengths": [
            "**Logistical Care:** You anticipate needs. You remove the physical friction from the day so staff can focus on kids.",
            "**Trustworthiness:** You are consistent. Your 'Yes' means 'Yes'. Staff know that if you are on shift, the tasks will get done.",
            "**Creating Order:** You organize the chaos. You create a calm, clean environment which helps traumatized brains regulate."
        ],
        "weaknesses": [
            "**Inflexibility:** Anxiety when the routine breaks. You get grumpy when the schedule changes last minute.",
            "**Appearing Cold:** Focusing on tasks to show care. You are cleaning the kitchen while a staff member is crying on the couch.",
            "**Struggle with Emotional Expression:** Preferring concrete actions over abstract feelings. You struggle to verbally praise or comfort people."
        ],
        "comm_arch": [
            "**Listening Style:** Practical. What do you need me to *do*?",
            "**Persuasion Trigger:** Stability + Helpfulness. Show me how this helps the team function better.",
            "**Feedback Preference:** Clear & Private. Tell me what to fix, don't make it a big emotional scene.",
            "**Meeting Mode:** Logistics. Who is doing what, and when?"
        ],
        "roadmap": [
            "**Phase 1: Verbalizing Care (0–6 Months):** Practice saying 'I did this *because* I care about you.' Connect the dot for them.",
            "**Phase 2: Delegation (6–12 Months):** Allow others to help you. Doing everything yourself isn't sustainable.",
            "**Phase 3: Operational Leadership (12–18 Months):** Teach the team the value of order. Create systems that run without you."
        ]
    }
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

def fetch_user_data(email):
    # Attempts to fetch data from Google Scripts
    # NOTE: Your Google Script must handle the 'retrieve' action for this to work.
    url = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"
    try:
        response = requests.post(url, json={"action": "retrieve", "email": email})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def generate_html_report(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    """
    Generates a rich HTML report for email body, mirroring the online dashboard style.
    """
    
    # Generate Cheat Sheet Data
    cheat_data = generate_profile_content_user(results['primaryComm'], results['primaryMotiv'])

    # CSS for Email (Inline styles are safest for email clients)
    style_card = "background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
    style_header = "background-color: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;"
    style_h2 = "color: #1a73e8; margin-top: 0;"
    style_h3 = "color: #202124; margin-bottom: 5px; font-size: 16px;"
    style_list = "margin: 0; padding-left: 20px; color: #5f6368;"
    
    # Construct HTML
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; color: #202124;">
        
        <!-- HEADER -->
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden;">
            <div style="{style_header}">
                <h1 style="margin: 0; font-size: 24px;">Elmcrest Leadership Compass</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Profile Report for {user_info['name']}</p>
            </div>
            
            <div style="padding: 30px;">
            
                <!-- SUMMARY CARD -->
                <div style="{style_card} border-left: 5px solid #1a73e8;">
                    <h2 style="{style_h2}">Your Profile Snapshot</h2>
                    <p><strong>Communication Style:</strong> {comm_prof['name']}</p>
                    <p><strong>Motivation Driver:</strong> {mot_prof['name']}</p>
                    <p><strong>Leadership Archetype:</strong> {int_prof['title'] if int_prof else 'N/A'}</p>
                </div>

                <!-- CHEAT SHEET -->
                <div style="{style_card} background-color: #f8f9fa;">
                    <h2 style="{style_h2}">⚡ Rapid Interaction Cheat Sheet</h2>
                    <p style="font-size: 12px; color: #666;">How you operate best:</p>
                    
                    <h3 style="color: #34a853;">✅ Your Core Strengths</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{item}</li>" for item in cheat_data['cheat_strengths']])}
                    </ul>
                    
                    <h3 style="color: #ea4335; margin-top: 15px;">⛔ Potential Blindspots</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{item}</li>" for item in cheat_data['cheat_blindspots']])}
                    </ul>

                     <h3 style="color: #1a73e8; margin-top: 15px;">🔋 What Fuels You</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{item}</li>" for item in cheat_data['cheat_fuel']])}
                    </ul>
                </div>

                <!-- COMM DETAILED -->
                <div style="{style_card}">
                    <h2 style="{style_h2}">🗣️ Communication: {comm_prof['name']}</h2>
                    <p>{comm_prof['overview']}</p>
                    <div style="background-color: #e8f0fe; padding: 10px; border-radius: 4px; margin-top: 10px;">
                        <strong>Under Stress:</strong> {comm_prof['conflictImpact']}
                    </div>
                </div>

                <!-- MOTIV DETAILED -->
                <div style="{style_card}">
                    <h2 style="{style_h2}">🔋 Motivation: {mot_prof['name']}</h2>
                    <p>{mot_prof['summary']}</p>
                    
                    <h3 style="{style_h3}">Boosters (Energizers)</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{b}</li>" for b in mot_prof['boosters']])}
                    </ul>
                    
                    <h3 style="{style_h3}; margin-top: 10px;">Drainers (De-energizers)</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{k}</li>" for k in mot_prof['killers']])}
                    </ul>
                </div>
                
                <!-- INTEGRATED -->
                <div style="{style_card}">
                    <h2 style="{style_h2}">🔗 Integrated Leadership</h2>
                    <p><strong>{int_prof['title'] if int_prof else ''}</strong></p>
                    <p>{int_prof['summary'] if int_prof else ''}</p>
                    
                    <h3 style="{style_h3}">Strategic Development Roadmap</h3>
                    <ul style="{style_list}">
                        {''.join([f"<li>{r}</li>" for r in int_prof.get('roadmap', [])]) if int_prof else ''}
                    </ul>
                </div>

                <div style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
                    <p>Generated by Elmcrest Leadership Compass</p>
                </div>
            
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email_via_smtp(to_email, subject, html_content):
    try:
        # Requires secrets.toml setup
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# [CHANGE] Updated Generator Helper for PDF and UI consistency
def generate_profile_content_user(comm, motiv):
    m_data = MOTIVATION_PROFILES.get(motiv, {})
    
    # Self-Coaching Blindspots (Internal View)
    blindspot_map = {
        "Director": [
            "**Pace Mismatch:** You likely process faster than your team. Pause to let them catch up.",
            "**Steamrolling:** You may accidentally silence quiet voices. Explicitly ask for input.",
            "**Intensity:** Your directness can feel like aggression. Soften your approach."
        ],
        "Encourager": [
            "**The 'Nice' Trap:** You might avoid hard feedback to keep the peace. Remember: Clarity is kind.",
            "**Over-Promising:** Your optimism can lead to committing to things you can't deliver.",
            "**Taking it Personally:** You tend to view professional critique as personal rejection."
        ],
        "Facilitator": [
            "**Analysis Paralysis:** You wait for 100% consensus. Sometimes a 51% decision is needed.",
            "**Conflict Avoidance:** You may delay necessary conflict, letting issues fester.",
            "**Indecision:** In a crisis, the team needs a command, not a committee."
        ],
        "Tracker": [
            "**Rigidity:** You may prioritize the rule over the relationship. Context matters.",
            "**The Weeds:** You get lost in details and miss the big picture or the human element.",
            "**Risk Aversion:** Your fear of mistakes can stifle necessary innovation."
        ]
    }

    # Strengths Map (Internal View)
    strength_map = {
        "Director": [
            "**Decisive Action:** You provide clarity and direction when things feel chaotic.",
            "**Momentum:** You keep things moving and prevent stagnation.",
            "**Problem Solving:** You view obstacles as challenges to be overcome, not dead ends."
        ],
        "Encourager": [
            "**Morale Building:** You are the emotional glue that holds the team together.",
            "**Optimism:** You see potential in people and situations where others see failure.",
            "**Connection:** You make people feel seen, valued, and safe."
        ],
        "Facilitator": [
            "**Consensus Building:** You ensure everyone feels heard, increasing long-term buy-in.",
            "**De-escalation:** Your calm presence lowers the temperature in the room.",
            "**Fairness:** You look at decisions from all angles to ensure equity."
        ],
        "Tracker": [
            "**Accuracy:** You ensure we don't make sloppy mistakes that hurt the agency.",
            "**Consistency:** You provide the stability and routine that traumatized youth need.",
            "**Process:** You build the systems that allow the work to happen smoothly."
        ]
    }

    return {
        "cheat_strengths": strength_map.get(comm, []),
        "cheat_blindspots": blindspot_map.get(comm, []),
        "cheat_fuel": m_data.get('boosters', [])
    }

def create_pdf(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (26, 115, 232)
    green = (52, 168, 83)
    red = (234, 67, 53)
    black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Leadership Compass Profile", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"Prepared for: {user_info['name']} | Role: {user_info['role']}"), ln=True, align='C')
    pdf.ln(5)
    
    # --- [CHANGE] Cheat Sheet Section Added ---
    data = generate_profile_content_user(results['primaryComm'], results['primaryMotiv'])
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Personal Leadership Cheat Sheet", ln=True, fill=True, align='C')
    pdf.ln(2)

    def print_cheat_column(title, items, color_rgb):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*color_rgb)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        for item in items:
            clean_item = item.replace("**", "")
            pdf.multi_cell(0, 5, clean_text(f"- {clean_item}"))
        pdf.ln(2)

    print_cheat_column("YOUR CORE STRENGTHS:", data['cheat_strengths'], green)
    print_cheat_column("YOUR BLINDSPOTS:", data['cheat_blindspots'], red)
    print_cheat_column("WHAT FUELS YOU:", data['cheat_fuel'], blue)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Horizontal line
    pdf.ln(5)
    
    # --- Original Content Resumes ---
    # Comm
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, clean_text(f"Communication: {comm_prof['name']}"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*black)
    
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
        
        # Strengths
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Strengths:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for s in int_prof['strengths']: pdf.multi_cell(0, 6, clean_text(f"- {s.replace('**', '')}"))
        pdf.ln(2)

        # Weaknesses
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Weaknesses:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for w in int_prof['weaknesses']: pdf.multi_cell(0, 6, clean_text(f"- {w.replace('**', '')}"))
        pdf.ln(2)

        # Comm Arch
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Communication Architecture:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for c in int_prof['comm_arch']: pdf.multi_cell(0, 6, clean_text(f"- {c.replace('**', '')}"))
        pdf.ln(2)

        # Roadmap
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Strategic Development Roadmap:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for r in int_prof['roadmap']: pdf.multi_cell(0, 6, clean_text(f"- {r.replace('**', '')}"))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI HELPERS ---
def show_brand_header(subtitle):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.image("https://raw.githubusercontent.com/jordonleblanc-cell/compass/main/elmcrest-icon.png", width=60)
    with col2:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 60px;">
            <div style="color: #007AFF; font-weight: 700; font-size: 1.5rem; letter-spacing: -0.02em;">Elmcrest Leadership Compass</div>
            <div style="color: #8E8E93; font-size: 0.9rem; font-weight: 500;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def draw_score_bar(label, value, max_value=30):
    pct = (value / max_value) * 100
    st.markdown(f"""
    <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.9rem; font-weight: 500; color: #8E8E93;">
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
        
        var main = window.parent.document.querySelector(".main");
        if (main) main.scrollTop = 0;
        
        var stApp = window.parent.document.querySelector(".stApp");
        if (stApp) stApp.scrollTop = 0;
    </script>
    """
    components.html(js, height=0)

if 'step' not in st.session_state:
    st.session_state.step = 'intro'

    # Randomize blocks and the order of statements within each block ONCE per session
    blocks = copy.deepcopy(IPSATIVE_BLOCKS)
    random.shuffle(blocks)
    for b in blocks:
        random.shuffle(b["statements"])

    st.session_state.blocks = blocks
    st.session_state.answers_ipsative = {}
    st.session_state.user_info = {}

# --- INTRO ---
if st.session_state.step == 'intro':
    # Force scroll to top on load (optional, but good practice)
    scroll_to_top()
    
    show_brand_header("Communication & Motivation Snapshot")
    st.markdown("#### Welcome!")
    # Tighter welcome message
    st.markdown("This assessment helps you understand your natural patterns at work. Your insights will shape a personalized profile built to support your growth.")
    
    # NEW INSTRUCTIONS ADDED HERE
    st.info("""
    **Important:**
    This assessment looks at patterns, not perfection.
    
    Most people show strong tendencies in more than one area. There is no “right” profile—only information that helps you work more effectively and sustainably.
    
    **How to answer:**
    Please answer based on how you usually show up at work on most days, not how you wish you showed up or how you are on your very best day.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("intro_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name", placeholder="e.g. Jane Doe")
        email = c2.text_input("Email Address", placeholder="e.g. jane@elmcrest.org")
        
        c3, c4 = st.columns(2)
        
        # Updated Roles with "Other" Logic
        role_options = ["Program Supervisor", "Shift Supervisor", "YDP", "TSS Staff", "Student Advocate", "Other"]
        role = c3.selectbox("Current Role", role_options, index=None, placeholder="Select your role...")
        
        # New text input for 'Other' specification
        role_other = c3.text_input("If 'Other', please specify:", placeholder="e.g. Director, Manager")

        # Updated Program List
        prog_options = ["Building 10", "Cottage 2", "Cottage 3", "Cottage 7", "Cottage 8", "Cottage 9", "Cottage 11", "Euclid", "Overnight", "Skeele Valley", "TSS Staff"]
        cottage = c4.selectbox("Home Program", prog_options, index=None, placeholder="Select your program...")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Start Assessment →"):
            if not name or not email or not role or not cottage: 
                st.error("Please complete all fields.")
            else:
                # Handle 'Other' Role logic
                final_role = role
                if role == "Other":
                    if role_other.strip():
                        final_role = role_other.strip()
                    else:
                        st.error("Please specify your role in the text box provided.")
                        st.stop()

                st.session_state.user_info = {"name": name, "email": email, "role": final_role, "cottage": cottage}
                st.session_state.step = 'assessment'
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- RECOVERY SECTION (NEW) ---
    with st.expander("Already took the assessment? Recover your results"):
        st.info("Enter your email to receive a verification code and retrieve your past results.")
        
        if 'recovery_stage' not in st.session_state:
            st.session_state.recovery_stage = 'email_input'

        if st.session_state.recovery_stage == 'email_input':
            rec_email = st.text_input("Email for recovery", key="rec_email_input")
            if st.button("Send Access Code"):
                if rec_email:
                    code = str(random.randint(100000, 999999))
                    st.session_state.recovery_code = code
                    st.session_state.recovery_email = rec_email
                    
                    if send_email_via_smtp(rec_email, "Your Access Code - Elmcrest Leadership Compass", f"Your access code is: {code}"):
                        st.session_state.recovery_stage = 'code_verify'
                        st.success("Code sent! Check your email.")
                        st.rerun()
                    else:
                        st.error("Could not send email. Please try again.")
                else:
                    st.error("Please enter an email address.")
        
        elif st.session_state.recovery_stage == 'code_verify':
            entered_code = st.text_input("Enter 6-digit code", key="rec_code_input")
            if st.button("Verify & Load"):
                if entered_code == st.session_state.recovery_code:
                    with st.spinner("Fetching your results..."):
                        data = fetch_user_data(st.session_state.recovery_email)
                        if data and data.get("found"):
                            # Hydrate session state with fetched data
                            fetched_user = data.get("user_info")
                            fetched_results = data.get("scores")
                            
                            # [FIX] Handle potential stringified JSON or invalid types
                            if isinstance(fetched_results, str):
                                try:
                                    fetched_results = json.loads(fetched_results)
                                except:
                                    pass
                            
                            # [FIX] Strict type check
                            if not isinstance(fetched_results, dict):
                                st.error(f"Error: Stored data is in an invalid format ({type(fetched_results).__name__}). Please retake the assessment.")
                            elif not fetched_results:
                                st.error("Found user but no scores recorded.")
                            else:
                                st.session_state.user_info = fetched_user
                                st.session_state.results = fetched_results
                                st.session_state.step = 'results'
                                st.success("Results loaded! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("No results found for this email, or database connection failed.")
                else:
                    st.error("Incorrect code.")
            
            if st.button("Cancel / Try Different Email"):
                st.session_state.recovery_stage = 'email_input'
                st.rerun()

    # Discrete Admin Access Button (Tighter spacing)
    col_spacer, col_admin = st.columns([0.7, 0.3])
    with col_admin:
        if st.button("🔒 Supervisor Portal"):
            st.switch_page("pages/admin.py")

# --- COMM ---

elif st.session_state.step == 'assessment':
    scroll_to_top()
    show_brand_header("Ipsative Assessment")
    st.markdown("**Instructions:** For each block, select the statement that is **MOST like you** and the statement that is **LEAST like you**.")

    total_blocks = len(st.session_state.blocks)
    answered = sum(
        1 for b in st.session_state.blocks
        if st.session_state.answers_ipsative.get(b["id"], {}).get("most") is not None
        and st.session_state.answers_ipsative.get(b["id"], {}).get("least") is not None
    )
    st.progress(int((answered / max(total_blocks, 1)) * 100))

    with st.form("ipsative_form"):
        responses = {}

        for i, block in enumerate(st.session_state.blocks):
            bid = block["id"]
            title = block.get("title", f"Block {i+1}")
            intro = block.get("intro")
            statements = block["statements"]

            st.markdown(f"### Block {i+1}: {title}")
            if intro:
                st.markdown(f"*{intro}*")
            with st.container(border=True):

                # Options are indices into the statements list (already randomized for this session)
                opts = list(range(len(statements)))

                def fmt(idx):
                    return statements[idx]["text"]

                most_key = f"{bid}_most"
                least_key = f"{bid}_least"

                most_choice = st.radio(
                    "MOST like me",
                    options=opts,
                    index=None,
                    key=most_key,
                    format_func=fmt,
                )
                least_choice = st.radio(
                    "LEAST like me",
                    options=opts,
                    index=None,
                    key=least_key,
                    format_func=fmt,
                )

                responses[bid] = {"most": most_choice, "least": least_choice}

        st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button("Complete & View Profile →"):
            # Validation
            missing = []
            same = []
            for b in st.session_state.blocks:
                bid = b["id"]
                r = responses.get(bid, {})
                if r.get("most") is None or r.get("least") is None:
                    missing.append(bid)
                elif r.get("most") == r.get("least"):
                    same.append(bid)

            if missing:
                st.error(f"Please answer all blocks. You missed {len(missing)} block(s).")
            elif same:
                st.error(f"In each block, MOST and LEAST must be different. Please fix {len(same)} block(s).")
            else:
                # Persist answers as codes (not indices)
                final_answers = {}
                for b in st.session_state.blocks:
                    bid = b["id"]
                    stmts = b["statements"]
                    most_idx = responses[bid]["most"]
                    least_idx = responses[bid]["least"]
                    final_answers[bid] = {
                        "most": stmts[most_idx]["code"],
                        "least": stmts[least_idx]["code"],
                    }
                st.session_state.answers_ipsative = final_answers
                st.session_state.step = 'processing'
                st.rerun()


# --- PROCESSING ---
elif st.session_state.step == 'processing':
    scroll_to_top()
    
        # Calculate Scores (Ipsative: MOST +3, LEAST -1)
    c_scores = {k: 0.0 for k in COMM_PROFILES}
    m_scores = {k: 0.0 for k in MOTIVATION_PROFILES}

    for bid, resp in st.session_state.answers_ipsative.items():
        most_code = resp.get("most")
        least_code = resp.get("least")

        if most_code in c_scores:
            c_scores[most_code] += MOST_POINTS
        elif most_code in m_scores:
            m_scores[most_code] += MOST_POINTS

        if least_code in c_scores:
            c_scores[least_code] += LEAST_POINTS
        elif least_code in m_scores:
            m_scores[least_code] += LEAST_POINTS

    # This assessment version does not collect extra burnout/context items
    burnout_score = None

    p_comm, s_comm = get_top_two(c_scores)
    p_mot, s_mot = get_top_two(m_scores)

    st.session_state.results = {
        "primaryComm": p_comm,
        "secondaryComm": s_comm,
        "primaryMotiv": p_mot,
        "secondaryMotiv": s_mot,
        "commScores": c_scores,
        "motivScores": m_scores,
        "burnoutScore": burnout_score,
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
    
    # [FIX] Enhanced Guard clause for missing or corrupted data
    if "results" not in st.session_state or not isinstance(st.session_state.results, dict):
        st.error("No valid results found. Please restart the assessment.")
        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    res = st.session_state.results
    user = st.session_state.user_info
    role_key = normalize_role_key(user['role'])
    role_labels = ROLE_RELATIONSHIP_LABELS[role_key]
    
    show_brand_header(f"Profile for {user['name']}")
    
    comm_prof = COMM_PROFILES[res['primaryComm']]
    mot_prof = MOTIVATION_PROFILES[res['primaryMotiv']]
    int_key = f"{res['primaryComm']}-{res['primaryMotiv']}"
    int_prof = INTEGRATED_PROFILES.get(int_key)
    
    # Generate content for cheat sheet
    cheat_data = generate_profile_content_user(res['primaryComm'], res['primaryMotiv'])

    # --- ACTION BAR ---
    c1, c2 = st.columns(2)
    with c1:
        pdf_bytes = create_pdf(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
        
        # Create dynamic filename
        clean_name = user['name'].strip().replace(" ", "_").lower()
        file_name_str = f"{clean_name}_compass.pdf"
        
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=file_name_str, mime="application/pdf")
    with c2:
        if st.button("📧 Email Me Full Report"):
            # [CHANGE] Now calls the HTML generator function
            full_html = generate_html_report(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
            with st.spinner("Sending..."):
                if send_email_via_smtp(user['email'], "Your Elmcrest Leadership Compass Profile", full_html):
                    st.success("Sent!")

    st.markdown("---")
    
    # --- [NEW] VISUALIZATION SECTION ---
    with st.container(border=True):
        st.subheader("📊 Profile At-A-Glance")
        vc1, vc2 = st.columns(2)
        
        with vc1:
            # 1. COMMUNICATION RADAR
            # Use real scores from the assessment results
            radar_df = pd.DataFrame(dict(r=[max(v, 0) for v in res['commScores'].values()], theta=list(res['commScores'].keys())))
            fig_comm = px.line_polar(radar_df, r='r', theta='theta', line_close=True, title="Communication Footprint", range_r=[0,36])
            fig_comm.update_traces(fill='toself', line_color=BRAND_COLORS['blue'])
            fig_comm.update_layout(height=300, margin=dict(t=30, b=30, l=30, r=30))
            st.plotly_chart(fig_comm, use_container_width=True)
            
        with vc2:
            # 2. MOTIVATION BATTERY
            # Use real scores from the assessment results
            sorted_mot = dict(sorted(res['motivScores'].items(), key=lambda item: item[1], reverse=True))
            mot_df = pd.DataFrame(dict(Driver=list(sorted_mot.keys()), Intensity=[max(v, 0) for v in sorted_mot.values()]))
            
            fig_mot = px.bar(mot_df, x="Intensity", y="Driver", orientation='h', title="Motivation Drivers", color="Intensity", color_continuous_scale=[BRAND_COLORS['gray'], BRAND_COLORS['blue']])
            fig_mot.update_layout(height=300, showlegend=False, margin=dict(t=30, b=30, l=30, r=30))
            fig_mot.update_xaxes(visible=False)
            st.plotly_chart(fig_mot, use_container_width=True)

    # --- [NEW] CHEAT SHEET SECTION ---
    with st.expander("⚡ Rapid Interaction Cheat Sheet (How others experience you)", expanded=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown("##### ✅ Your Core Strengths")
            for b in cheat_data['cheat_strengths']: st.success(b)
        with cc2:
            st.markdown("##### ⛔ Potential Blindspots")
            for avoid in cheat_data['cheat_blindspots']: st.error(avoid)
        with cc3:
            st.markdown("##### 🔋 What Fuels You")
            for b in cheat_data['cheat_fuel']: st.info(b)

    # --- COMM SECTION ---
    st.markdown(f"### 🗣️ {comm_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#007AFF;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{comm_prof['tagline']}</div>
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
        # Check if scores exist (handles legacy retrieved data that might be empty)
        if res.get('commScores') and len(res['commScores']) > 0:
            for style, score in res['commScores'].items():
                draw_score_bar(style, score, max_value=30) # Max is now 30 (6 questions * 5)
        else:
            st.caption("Detailed score breakdown is not available for this record.")

    st.markdown("---")

    # --- MOTIV SECTION ---
    st.markdown(f"### 🔋 {mot_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#007AFF;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{mot_prof['tagline']}</div>
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
        
        # New Expanded Section
        with st.expander("✨ View Full Analysis (Strengths, Weaknesses, Roadmap)", expanded=True):
            st.subheader("Key Strengths")
            for s in int_prof['strengths']: st.write(f"- {s}")
            
            st.subheader("Potential Weaknesses")
            for w in int_prof['weaknesses']: st.write(f"- {w}")
            
            st.markdown("---")
            c_comm, c_road = st.columns(2)
            
            with c_comm:
                st.subheader("Communication Architecture")
                for c in int_prof['comm_arch']: st.write(f"- {c}")
                
            with c_road:
                st.subheader("Strategic Development Roadmap")
                for r in int_prof['roadmap']: st.write(f"- {r}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
