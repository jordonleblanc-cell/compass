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
        div[data-testid="stForm"], .info-card, div[data-testid="stExpander"] {
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

ROLE_RELATIONSHIP_LABELS = {
    "Program Supervisor": {"directReportsLabel": "Shift Supervisors", "youthLabel": "youth on your units", "supervisorLabel": "Residential Programs Manager", "leadershipLabel": "agency leadership"},
    "Shift Supervisor": {"directReportsLabel": "YDPs", "youthLabel": "youth you support", "supervisorLabel": "Program Supervisor", "leadershipLabel": "agency leadership"},
    "YDP": {"directReportsLabel": "peers", "youthLabel": "youth in your care", "supervisorLabel": "Shift Supervisor", "leadershipLabel": "Program Supervisor"}
}

# Updated Communication Questions (24 Total, with Reverse Keying)
COMM_QUESTIONS = [
    # Director
    {"id": "c1", "text": "When a situation becomes chaotic, I naturally step in and start directing people toward a plan.", "style": "Director"},
    {"id": "c2", "text": "I feel most effective when I can make quick decisions and move the team forward.", "style": "Director"},
    {"id": "c3", "text": "In a crisis, I’d rather take charge and apologize later than wait too long for consensus.", "style": "Director"},
    {"id": "c4", "text": "If expectations are unclear, I tend to define them myself and communicate them to others.", "style": "Director"},
    {"id": "c5", "text": "I’m comfortable giving direct feedback, even when it may be hard for someone to hear.", "style": "Director"},
    {"id": "c6", "text": "I hesitate to take the lead until I’m confident everyone agrees.", "style": "Director", "reverse": True},
    
    # Encourager
    {"id": "c7", "text": "I pay close attention to the emotional tone of the team and lift people up when morale is low.", "style": "Encourager"},
    {"id": "c8", "text": "I often use encouragement, humor, or positive energy to help staff get through hard shifts.", "style": "Encourager"},
    {"id": "c9", "text": "I notice small wins and like to name them out loud so people know they’re seen.", "style": "Encourager"},
    {"id": "c10", "text": "I tend to talk things through with people rather than just giving short instructions.", "style": "Encourager"},
    {"id": "c11", "text": "I’m often the one coworkers come to when they need to vent or feel understood.", "style": "Encourager"},
    {"id": "c12", "text": "I tend to focus on tasks and outcomes more than how people are feeling.", "style": "Encourager", "reverse": True},
    
    # Facilitator
    {"id": "c13", "text": "I’m good at slowing conversations down so that different perspectives can be heard.", "style": "Facilitator"},
    {"id": "c14", "text": "I try to stay calm and balanced when others are escalated or upset.", "style": "Facilitator"},
    {"id": "c15", "text": "I often find myself summarizing what others are saying to move toward shared understanding.", "style": "Facilitator"},
    {"id": "c16", "text": "I prefer to build agreement and buy-in rather than rely only on authority.", "style": "Facilitator"},
    {"id": "c17", "text": "I pay attention to process (how we talk to each other) as much as the final decision.", "style": "Facilitator"},
    {"id": "c18", "text": "I get impatient with long discussions and prefer to move to action quickly.", "style": "Facilitator", "reverse": True},
    
    # Tracker
    {"id": "c19", "text": "I naturally notice details in documentation, routines, or schedules others overlook.", "style": "Tracker"},
    {"id": "c20", "text": "I feel responsible for keeping procedures on track, even when others get distracted.", "style": "Tracker"},
    {"id": "c21", "text": "I tend to ask clarifying questions when expectations or instructions feel vague.", "style": "Tracker"},
    {"id": "c22", "text": "I’m more comfortable when I know exactly who is doing what and when it needs to be done.", "style": "Tracker"},
    {"id": "c23", "text": "If something seems out of compliance, it really sticks with me until it’s addressed.", "style": "Tracker"},
    {"id": "c24", "text": "I’m comfortable proceeding even when processes or expectations feel loosely defined.", "style": "Tracker", "reverse": True},
]

# Updated Motivation Questions (25 Total, with Reverse Keying & Context Item)
MOTIVATION_QUESTIONS = [
    # Growth
    {"id": "m1", "text": "I feel energized when I’m learning new skills or being stretched in healthy ways.", "style": "Growth"},
    {"id": "m2", "text": "It’s important to me that I can look back and see I’m becoming more effective over time.", "style": "Growth"},
    {"id": "m3", "text": "When I feel stuck in the same patterns with no development, my motivation drops.", "style": "Growth"},
    {"id": "m4", "text": "I appreciate feedback that helps me improve, even if it’s uncomfortable in the moment.", "style": "Growth"},
    {"id": "m5", "text": "Access to training, coaching, or new responsibilities matters a lot for my commitment.", "style": "Growth"},
    {"id": "m6", "text": "I’m generally satisfied doing the same work as long as things feel stable.", "style": "Growth", "reverse": True},
    
    # Purpose
    {"id": "m7", "text": "I need to feel that what I’m doing connects to a bigger purpose for youth and families.", "style": "Purpose"},
    {"id": "m8", "text": "I feel strongest when my work lines up with my values about dignity, justice, and safety.", "style": "Purpose"},
    {"id": "m9", "text": "It’s hard for me to stay engaged when policies don’t make sense for the youth we serve.", "style": "Purpose"},
    {"id": "m10", "text": "I’m often the one raising questions about whether a decision is really best for kids.", "style": "Purpose"},
    {"id": "m11", "text": "I feel proudest when I can see real positive impact, not just tasks checked off.", "style": "Purpose"},
    {"id": "m12", "text": "As long as the job gets done, the deeper meaning doesn't affect my motivation much.", "style": "Purpose", "reverse": True},
    
    # Connection
    {"id": "m13", "text": "Having strong relationships with coworkers makes a big difference in my energy.", "style": "Connection"},
    {"id": "m14", "text": "When the team feels disconnected, I feel it in my body and it’s harder to stay motivated.", "style": "Connection"},
    {"id": "m15", "text": "I value feeling known and supported by my team and supervisor, not just evaluated.", "style": "Connection"},
    {"id": "m16", "text": "I’m often thinking about the emotional climate of the unit and how people are relating.", "style": "Connection"},
    {"id": "m17", "text": "I’m more likely to go above and beyond when I feel a sense of belonging.", "style": "Connection"},
    {"id": "m18", "text": "I’m able to stay motivated even when I feel disconnected from the team.", "style": "Connection", "reverse": True},
    
    # Achievement
    {"id": "m19", "text": "I like having clear goals and being able to see, in concrete ways, when we’ve met them.", "style": "Achievement"},
    {"id": "m20", "text": "I feel satisfied when I can see that my effort led to specific improvements.", "style": "Achievement"},
    {"id": "m21", "text": "It’s frustrating when expectations keep shifting and I’m not sure what success looks like.", "style": "Achievement"},
    {"id": "m22", "text": "I appreciate data, tracking tools, or simple dashboards that help show progress.", "style": "Achievement"},
    {"id": "m23", "text": "Clear goals help me feel calmer and more effective in my work with youth.", "style": "Achievement"},
    {"id": "m24", "text": "I’m comfortable doing my best work even when success isn’t clearly defined.", "style": "Achievement", "reverse": True},
    
    # Context (Burnout)
    {"id": "m25", "text": "When I feel emotionally exhausted, even meaningful work becomes hard to stay engaged with.", "style": "Context"}
]

# --- DATA DICTIONARIES (Updated with new content) ---

COMM_PROFILES = {
    "Director": {
        "name": "Director Communicator",
        "tagline": "The Decisive Driver",
        "overview": "<strong>Core Style:</strong> You blend decisive, crisis-ready leadership with a bias for action. You are likely to set direction quickly and then rally people to move with you. You prioritize efficiency and competence, often serving as the 'adult in the room' who keeps things calm while making necessary calls. You rarely suffer from 'analysis paralysis,' preferring to make a wrong decision that can be fixed rather than no decision at all.<br><br><strong>Your Superpower:</strong> In high-pressure moments, you step in and organize. Staff see you as fair and decisive—they know you will act, so they aren't stuck in limbo. When everyone else is panicking, your clarity acts as an anchor.",
        "conflictImpact": "Under stress, you may move faster than staff can realistically integrate, making them feel like they are always 'behind' or incompetent. You might default to control before curiosity, issuing orders rather than asking questions.",
        "traumaStrategy": "Your consistency and clear boundaries can be regulating for youth who need predictability, though some may find your intensity intimidating. Traumatized brains often crave structure to feel safe.",
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
            "Program Supervisor": "Set process goals (e.g., 'We debriefed every incident') not just outcome goals (e.g., 'Fewer incidents').",
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
    lines = [f"Elmcrest Leadership Compass PROFILE FOR {user_info['name'].upper()}", "="*40, ""]
    
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
        lines.append("\nSTRENGTHS:")
        for s in int_prof['strengths']: lines.append(f"- {s}")
        lines.append("\nWEAKNESSES:")
        for w in int_prof['weaknesses']: lines.append(f"- {w}")
        lines.append("\nCOMMUNICATION ARCHITECTURE:")
        for ca in int_prof['comm_arch']: lines.append(f"- {ca}")
        lines.append("\nSTRATEGIC DEVELOPMENT ROADMAP:")
        for r in int_prof['roadmap']: lines.append(f"- {r}")
        
    return "\n".join(lines)

def create_pdf(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (0, 122, 255) # iOS Blue
    black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Leadership Compass Profile", ln=True, align='C')
    
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
    
    # Fix for bolding: Replace HTML strong tags
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
    comm_q, motiv_q = COMM_QUESTIONS.copy(), MOTIVATION_QUESTIONS.copy()
    random.shuffle(comm_q); random.shuffle(motiv_q)
    st.session_state.shuffled_comm = comm_q
    st.session_state.shuffled_motiv = motiv_q
    st.session_state.answers_comm = {}
    st.session_state.answers_motiv = {}
    st.session_state.user_info = {}

# --- INTRO ---
if st.session_state.step == 'intro':
    # Force scroll to top on load (optional, but good practice)
    scroll_to_top()
    
    show_brand_header("Communication & Motivation Snapshot")
    st.markdown("#### 👋 Welcome")
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
                st.session_state.step = 'comm'
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
                col_q, col_a = st.columns([0.45, 0.55], gap="medium") # Adjusted ratio to give radios more space
                
                with col_q:
                    # Append (reverse) text only if debugging, otherwise keep clean
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
                col_q, col_a = st.columns([0.45, 0.55], gap="medium") # Adjusted ratio
                
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
                st.rerun()

# --- PROCESSING ---
elif st.session_state.step == 'processing':
    scroll_to_top()
    
    # Calculate Scores with Reverse Keying Logic
    def calculate_points(raw_score, is_reverse):
        if is_reverse:
            return 6 - raw_score
        return raw_score

    c_scores = {k:0 for k in COMM_PROFILES}
    m_scores = {k:0 for k in MOTIVATION_PROFILES}
    context_score = 0
    
    # Process Comm
    for q in COMM_QUESTIONS:
        raw_val = st.session_state.answers_comm[q['id']]
        points = calculate_points(raw_val, q.get('reverse', False))
        c_scores[q['style']] += points
        
    # Process Motiv
    for q in MOTIVATION_QUESTIONS:
        raw_val = st.session_state.answers_motiv[q['id']]
        if q['style'] == "Context":
            context_score = raw_val # Just store raw val
        else:
            points = calculate_points(raw_val, q.get('reverse', False))
            m_scores[q['style']] += points
    
    p_comm, s_comm = get_top_two(c_scores)
    p_mot, s_mot = get_top_two(m_scores)
    
    st.session_state.results = {
        "primaryComm": p_comm, "secondaryComm": s_comm,
        "primaryMotiv": p_mot, "secondaryMotiv": s_mot,
        "commScores": c_scores, "motivScores": m_scores,
        "burnoutScore": context_score
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
        
        # Create dynamic filename
        clean_name = user['name'].strip().replace(" ", "_").lower()
        file_name_str = f"{clean_name}_compass.pdf"
        
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=file_name_str, mime="application/pdf")
    with c2:
        if st.button("📧 Email Me Full Report"):
            full_text = generate_text_report(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
            with st.spinner("Sending..."):
                if send_email_via_smtp(user['email'], "Your Elmcrest Leadership Compass Profile", full_text):
                    st.success("Sent!")

    st.markdown("---")

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
