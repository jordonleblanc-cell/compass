import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- 3. CONTENT DICTIONARIES ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# --- SUPERVISOR CLASH MATRIX (New Directional Logic) ---
# Key = Supervisor Style, Value = Dict of Staff Styles
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "dynamic": "The Steamroller vs. The Turtle. Your speed and directness likely intimidates them. When you push hard, they retreat to protect the relationship, which you interpret as weakness or lack of focus.",
            "self_check": "Am I skipping the 'Human Connection' step just to get to the task? If I win the logic argument but hurt their feelings, I lose their engagement.",
            "script": "I know I move fast and can be direct. I don't want that to shut you down. Your focus on the team's morale is data I need. When I push for results, please tell me if I'm missing a human cost."
        },
        "Facilitator": {
            "dynamic": "Gas vs. Brake. You want to decide *now* ('Ready, Fire, Aim'). They want to process ('Ready, Aim, Aim...'). You feel slowed down; they feel steamrolled and unsafe.",
            "self_check": "Am I mistaking their 'processing time' for 'resistance'? If I force a decision before they are heard, I get compliance, not buy-in.",
            "script": "I feel urgency to move this forward, but I know you need to ensure we aren't missing perspectives. I can't wait forever, but I can wait 24 hours. What specific input do you need before we decide tomorrow?"
        },
        "Tracker": {
            "dynamic": "Vision vs. Obstacles. You say 'Make it happen.' They say 'But Regulation 14.B says...' You feel they are blocking you; they feel you are being reckless.",
            "self_check": "Am I dismissing their details because they are annoying, or because they are irrelevant? They are trying to keep me out of trouble.",
            "script": "I appreciate you watching the compliance side. I feel frustrated when I hear 'No' without a 'How'. Instead of telling me why we can't do it, can you map out the safest path to get to 'Yes'?"
        },
        "Director": {
            "dynamic": "Power Struggle. Two alphas in a room. You both want to lead. The conversation becomes a debate about who is right rather than what is best.",
            "self_check": "Am I fighting to be 'The Boss' or to solve the problem? I need to give them a lane to lead.",
            "script": "We both have strong opinions and want to move fast. I'm going to define the 'What' (the Goal), and I'm going to trust you with the 'How'. I won't micromanage it."
        }
    },
    "Encourager": {
        "Director": {
            "dynamic": "Soft vs. Hard. They want the bottom line; you want the story. They may interrupt you or tune out, which hurts your feelings. You may perceive them as 'mean'.",
            "self_check": "Am I taking their directness personally? Am I burying the headline? I need to speak their language (Results) to be heard.",
            "script": "I know you value efficiency. I'm going to give you the bottom line first. [State Goal]. Now, to get there, I need you to soften your delivery with the team, or we will lose them."
        },
        "Facilitator": {
            "dynamic": "The Nice-Off. You want to protect the individual's feelings; they want to be fair to the group. You both avoid conflict, so decisions stall indefinitely.",
            "self_check": "Am I prioritizing being liked over being effective? Are we circling the issue to avoid upsetting someone?",
            "script": "We are both trying to be kind here, but the lack of a decision is hurting the team. I'm going to make the call to move forward, even though it might be uncomfortable."
        },
        "Tracker": {
            "dynamic": "Chaos vs. Order. You bend rules to help people. They enforce rules to protect people. They think you are unsafe; you think they are cold.",
            "self_check": "Am I undermining their authority by being inconsistent? Structure is a form of care.",
            "script": "I know my flexibility stresses you out because you value consistency. I value it too. Help me build a structure that still allows room for human judgment, and I promise to stick to it."
        },
        "Encourager": {
            "dynamic": "The Therapy Session. You connect deeply, but may struggle to hold each other accountable. Meetings feel good but produce few action items.",
            "self_check": "Are we just venting? I need to pivot this connection into action.",
            "script": "I love that we support each other. But to protect the program, I need to put my 'Boss Hat' on for a second. We have to fix [Issue], even if it feels hard."
        }
    },
    "Facilitator": {
        "Director": {
            "dynamic": "The Steamroll. They demand a decision. You freeze because you haven't heard from everyone. They interpret your silence as agreement or incompetence.",
            "self_check": "Am I hiding behind 'the team's opinion' to avoid taking a stand? I need to be decisive.",
            "script": "I know you want an answer now. I am not stalling; I am risk-managing. If we decide without [Person]'s input, it will fail. I will have the answer for you by [Time]."
        },
        "Encourager": {
            "dynamic": "Fairness vs. Feelings. You are looking at the system; they are looking at the person. You might struggle to rein them in when they over-function for a client.",
            "self_check": "Am I being too clinical? I need to validate the heart behind their actions before correcting the process.",
            "script": "I see how much you care about [Youth]. However, if we make a special exception for him, it creates unfairness for the other 10 kids. We need a solution that scales."
        },
        "Tracker": {
            "dynamic": "Analysis Paralysis. You want consensus; they want data. You both wait. The program stagnates.",
            "self_check": "Am I waiting for perfect agreement? It doesn't exist. I need to declare a direction.",
            "script": "We have analyzed this enough. We are never going to be 100% sure. I am making the decision to go with Plan A. I need you to help me track the data to see if it works."
        },
        "Facilitator": {
            "dynamic": "The Committee. Endless meetings. Great process, low output. You both defer to each other.",
            "self_check": "Who is driving the bus? If I don't set the destination, no one will.",
            "script": "We are spinning. I'm going to step out of 'listening mode' and into 'directing mode'. Here is the plan we are going with."
        }
    },
    "Tracker": {
        "Director": {
            "dynamic": "The Micromanagement Trap. You see their broad strokes as reckless. You ask 10 questions; they get annoyed. You feel disrespected.",
            "self_check": "Am I trying to control them? I need to trust their intent and only block on true safety issues.",
            "script": "I'm not trying to slow you down; I'm trying to ensure this sticks. I don't need to control the whole project, but I do need veto power on these two specific safety compliance items."
        },
        "Encourager": {
            "dynamic": "Rules vs. Relationship. You see their exceptions as chaos. They feel judged by your clipboard. You risk becoming the 'Principal' to their 'Cool Teacher'.",
            "self_check": "Am I valuing the paperwork over the person? I need to explain the 'Why' (Safety) not just the 'What' (Rule).",
            "script": "When you bend the rule for that youth, it makes the shift unsafe for the rest of us because we don't know what to expect. I need you to follow the protocol, not to be mean, but to keep us safe."
        },
        "Facilitator": {
            "dynamic": "Details vs. Concepts. You want a checklist; they want a conversation. You get frustrated when meetings end without a clear 'To-Do' list.",
            "self_check": "Am I being too rigid? Sometimes the 'deliverable' is just alignment, not a spreadsheet.",
            "script": "I appreciate the discussion. To help me execute this, can we spend the last 5 minutes defining exactly who is doing what by when?"
        },
        "Tracker": {
            "dynamic": "The Audit. You both love details. You might argue over *which* rule applies. You risk missing the forest for the trees.",
            "self_check": "Are we rearranging deck chairs on the Titanic? We need to zoom out.",
            "script": "We are getting stuck in the weeds. Let's pause the detail work. What is the actual outcome we need for the client today?"
        }
    }
}

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "conversation": "You have high capacity and speed, which is a gift. To succeed as a Shift Supervisor, you have to resist the urge to 'rescue' the shift by doing everything yourself. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless safety dictates otherwise).",
            "assignment_task": "They must run the shift entirely through verbal direction and delegation to peers. They cannot touch paperwork or intervene in minor conflicts.",
            "success_indicators": "Did they let a staff member struggle through a task without jumping in? Did they give clear verbal instructions?",
            "red_flags": "They ran out of the office to 'just do it quick'. They complain that their team is 'too slow'.",
            "supervisor_focus": "Watch for 'Hero Mode'. If you see them jumping in to fix a crisis that their staff could handle, intervene. Pull them back and say, 'Let your team handle this. Coach them, don't save them.'"
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "conversation": "You are excellent at execution within your unit. However, program leadership requires getting buy-in from people you don't supervise (School, Clinical, other cottages). You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment_setup": "Identify a peer in another department (School/Clinical) they have friction with.",
            "assignment_task": "Task them with a cross-departmental project (e.g., improving school transitions). They must interview stakeholders and present a plan that incorporates *their* feedback.",
            "success_indicators": "The plan includes ideas that clearly didn't come from the Director. The peer reports feeling heard.",
            "red_flags": "They present a plan that is 100% their own idea and complain that the other dept is 'difficult'.",
            "supervisor_focus": "Monitor their patience. If they complain about 'meetings' or 'politics', reframe it: 'That isn't politics; that is relationship building. That is the job now.'"
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
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
            "conversation": "Your empathy is your superpower, but if you avoid hard conversations to keep the peace, you create an unsafe environment. The team needs you to be a 'Guardian' of the standard. Holding people accountable is actually the kindest thing you can do, because it ensures clarity and safety for everyone.",
            "assignment_setup": "Identify a staff member who is consistently late or missing protocols.",
            "assignment_task": "Lead a policy reinforcement meeting with that staff member. You (Supervisor) observe but do not speak.",
            "success_indicators": "They state the expectation clearly without apologizing. They don't use 'The boss wants...' language.",
            "red_flags": "They apologize for the rule ('Sorry I have to tell you this...'). They make a joke to deflect the tension.",
            "supervisor_focus": "Watch for 'Apology Language'. If they give a directive and then apologize for it, correct them immediately. 'Do not apologize for leading.'"
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "conversation": "You create an amazing emotional climate. To lead a program, that climate must be backed by unshakeable structure. You need to master the 'boring' parts of leadership—budgets, schedules, audits—because those are the tools that protect your team from burnout.",
            "assignment_setup": "Assign ownership of a compliance audit or a complex schedule overhaul.",
            "assignment_task": "They must present the data and the rationale to the team, standing on the facts rather than just their relationship.",
            "success_indicators": "The audit is accurate. They can explain the 'why' without appealing to emotion.",
            "red_flags": "They ask a Tracker to do it for them. They procrastinate the paperwork to hang out with staff.",
            "supervisor_focus": "Inspect what you expect. Encouragers can be disorganized. Help them build a personal organization system so their administrative balls don't drop."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "conversation": "You naturally carry the emotions of your people. At the manager level, the weight is too heavy to carry alone. Your growth edge is learning to set emotional boundaries—caring deeply about the person without taking responsibility for their feelings.",
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
            "conversation": "You are gifted at ensuring everyone feels heard. As a Shift Sup, there will be moments where consensus is impossible and safety requires speed. You need to get comfortable making the '51% decision'—listening to input, but making the call even if 49% disagree.",
            "assignment_setup": "Put them in charge of a time-sensitive crisis drill or transition.",
            "assignment_task": "They must make immediate calls on staff positioning. Debrief afterwards: 'Where did you hesitate?'",
            "success_indicators": "They gave direct commands. They didn't ask 'What do you guys think?' during the crisis.",
            "red_flags": "They stood back and let a Director take over. They tried to have a meeting in the middle of a transition.",
            "supervisor_focus": "Push for speed. When they ask 'What do you think?', throw it back: 'You tell me. You're the leader.' Force them to exercise their judgment muscle."
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "conversation": "You are a great stabilizer. But a Program Supervisor must also be a driver. Instead of just mediating the team's ideas, we need you to inject your own vision. Don't just wait to see what the group wants; tell us where you think the group needs to go.",
            "assignment_setup": "Ask them to propose a new initiative for the program culture.",
            "assignment_task": "Present it to the team as a direction, not a discussion topic. 'This is where we are going.'",
            "success_indicators": "They use declarative statements ('We will...'). They handle pushback without folding.",
            "red_flags": "They frame it as a question ('How would you guys feel about...?'). They retreat at the first sign of resistance.",
            "supervisor_focus": "Watch for 'The Buffer'. Are they just passing messages between staff and admin? Challenge them to take a stand on issues."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
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
            "conversation": "You are brilliant at the details. But you cannot track every detail personally at this level without burning out or micromanaging. Your growth is trusting your team. You have to let them do the checklist, even if they do it differently than you would.",
            "assignment_setup": "The 'Hands-Off' Day. Assign them to supervise a complex task (intake/search).",
            "assignment_task": "Strictly prohibited from touching paperwork. Must guide a peer to do it verbally.",
            "success_indicators": "They kept their hands in their pockets. They gave clear corrections without taking over.",
            "red_flags": "They grabbed the pen. They sighed and said 'I'll just do it'.",
            "supervisor_focus": "Watch for micromanagement. If they are re-doing someone else's work, stop them. 'If it is 80% right, it is right enough. Move on.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "conversation": "You excel when the rules are clear. Program leadership is full of gray areas where the policy manual doesn't have an answer. You need to develop your intuition and judgment to navigate complex family or youth dynamics that don't fit the spreadsheet.",
            "assignment_setup": "Handle a complex parent/youth complaint where standard rules don't apply.",
            "assignment_task": "Make a principle-based decision (fairness/safety) rather than a rule-based one.",
            "success_indicators": "They made a decision that wasn't in the handbook but made sense. They can explain the 'spirit' of the rule.",
            "red_flags": "They froze because 'there's no policy'. They applied a rule rigidly that made no sense in context.",
            "supervisor_focus": "Challenge their rigidity. If they say 'We can't do that, it's not the rule', ask 'What is the *intent* of the rule? Can we meet the intent a different way?'"
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "conversation": "Culture eats strategy (and checklists) for breakfast. If you prioritize efficiency over connection, you will have a compliant but brittle organization. You need to invest as much energy in 'how people feel' as 'what people do'.",
            "assignment_setup": "Task them with a retention or morale initiative.",
            "assignment_task": "Spend one week focusing solely on staff development/relationships. Delegate metrics to a deputy.",
            "success_indicators": "They had non-work conversations. Staff report feeling seen.",
            "red_flags": "They turned the morale initiative into a checklist ('Did you have fun? Check yes').",
            "supervisor_focus": "Look for the 'Human Element'. In every supervision, ask them a question about people, not tasks. 'How is [Staff Name] doing really?'"
        }
    }
}

# --- PDF Content Dictionaries (Full Text) ---
COMM_PROFILES = {
    "Director": {
        "overview": "This staff member communicates primarily as a Director, meaning they lead with clarity, structure, and urgency.",
        "supervising": "Be direct, concise, and outcome-focused. They respect leaders who get to the point. Define the 'what' clearly, but give autonomy on the 'how'.",
        "struggle_bullets": ["Decreased patience", "Over-assertiveness", "Fatigue/Irritability", "Rigid enforcement"],
        "coaching": ["What are the risks of moving this fast?", "Who haven't we heard from yet?", "How can you frame this so the team feels supported?", "What is the difference between being 'right' and being 'effective'?", "If you had to achieve this result without giving a single order, how would you do it?"],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience."
    },
    "Encourager": {
        "overview": "This staff member communicates primarily as an Encourager, leading with warmth, optimism, and emotional intelligence.",
        "supervising": "Connect relationally before diving into tasks. Validate their emotional labor. Frame criticism around professional growth.",
        "struggle_bullets": ["Avoidance of conflict", "Disorganization", "Prioritizing being liked", "Emotional exhaustion"],
        "coaching": ["How can you deliver this hard news while remaining kind?", "Are we prioritizing popularity over effectiveness?", "What boundaries do you need to set?", "If you avoid this conflict today, what is the cost to the team next week?", "How does holding this standard actually create safety for the youth?"],
        "advancement": "Help them master the operational side. Challenge them to see clarity and accountability as kindness."
    },
    "Facilitator": {
        "overview": "This staff member communicates primarily as a Facilitator, leading by listening, gathering perspectives, and seeking fairness.",
        "supervising": "Give them time to process. Ask for observations explicitly. Validate fairness but push for decisions.",
        "struggle_bullets": ["Analysis paralysis", "Passive-aggressiveness", "Saying 'it's fine' when it isn't", "Getting stuck in the middle"],
        "coaching": ["If you had to decide right now, what would you do?", "What is the cost of waiting?", "Where are you holding tension?", "Who specifically are you trying not to upset with this decision?", "How can you support the team's direction even if you don't fully agree?"],
        "advancement": "Encourage them to be more vocal and decisive. Help them be assertive without being aggressive."
    },
    "Tracker": {
        "overview": "This staff member communicates primarily as a Tracker, leading with details, data, and systems.",
        "supervising": "Provide clear expectations. Respecting their systems builds trust. Explain the 'why' behind changes.",
        "struggle_bullets": ["Rigidity/Perfectionism", "Getting stuck in weeds", "Coming across as cold", "Prioritizing policy over people"],
        "coaching": ["Does this detail change the outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the big picture goal?", "If we follow the rule perfectly but lose the kid's trust, did we succeed?", "What is the 'Good Enough' version of this task?"],
        "advancement": "Help them delegate details. Teach them to distinguish between 'mission-critical' and 'preference'."
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "overview": "Primary motivator: Growth. Thrives on progress, new skills, and challenges.",
        "motivating": "Give problems to solve. Provide skill feedback. Connect work to career.",
        "support": "Sponsor for training. Ask 'What are you learning?'. Don't box them in.",
        "thriving_bullets": ["Proactive questions", "Volunteering", "Mentoring", "High engagement"],
        "intervention": "Realign tasks to include learning. Ask: 'Do you feel challenged?'",
        "celebrate": "Celebrate acquisition of new skills and adaptability."
    },
    "Purpose": {
        "overview": "Primary motivator: Purpose. Thrives on meaning, alignment, and values.",
        "motivating": "Connect directives to mission. Be transparent about the 'why'. Invite ethical input.",
        "support": "Create space for ethical concerns. Validate passion. Remind of human impact.",
        "thriving_bullets": ["Passionate advocacy", "High integrity", "Going the extra mile", "Commitment"],
        "intervention": "Reconnect to mission. Ask: 'Does this feel misaligned?'",
        "celebrate": "Celebrate moments where their work directly impacted a youth's life."
    },
    "Connection": {
        "overview": "Primary motivator: Connection. Thrives on belonging, cohesion, and relationships.",
        "motivating": "Prioritize team cohesion. Recognize shared wins. Check in personally.",
        "support": "Ensure no isolation. Facilitate bonding. Be accessible.",
        "thriving_bullets": ["Collaborative", "High morale", "Family atmosphere", "Strong rapport"],
        "intervention": "Repair relationships. Ask: 'How is the team dynamic?'",
        "celebrate": "Celebrate contributions to culture and supporting peers."
    },
    "Achievement": {
        "overview": "Primary motivator: Achievement. Thrives on progress, results, and completion.",
        "motivating": "Set clear goals. Use checklists. Give autonomy to reach targets.",
        "support": "Remove blockers. Protect time. Be definitive about 'success'.",
        "thriving_bullets": ["High follow-through", "Efficiency", "Reliability", "Goal-oriented"],
        "intervention": "Clarify expectations. Ask: 'Is success clear here?'",
        "celebrate": "Celebrate completion of projects and reliability."
    }
}

# --- Helper Function: Clean Text for PDF ---
def clean_text(text):
    if not text: return ""
    text = str(text)
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', 
        '\u2013': '-', '\u2014': '-', '\u2026': '...',
        '—': '-', '–': '-', '“': '"', '”': '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- Data Fetching ---
@st.cache_data(ttl=60)
def fetch_staff_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return []

# --- PDF Generator ---
def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (1, 91, 173)
    black = (0, 0, 0)
    
    # HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
    c_data = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m_data = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    def add_heading(title):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*blue)
        pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(2)

    def add_body(content):
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        pdf.multi_cell(0, 6, clean_text(content))
        pdf.ln(3)

    def add_bullets(items):
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        for item in items:
            pdf.multi_cell(0, 6, clean_text(f"- {item}"))
        pdf.ln(3)

    add_heading(f"1. Communication Profile: {p_comm}")
    add_body(c_data['overview'])

    add_heading("2. Supervising Their Communication")
    add_body(c_data['supervising'])

    add_heading(f"3. Motivation Profile: {p_mot}")
    add_body(m_data['overview'])

    add_heading("4. Motivating This Staff Member")
    add_body(m_data['motivating'])

    integrated_text = (
        f"This staff member leads with {p_comm} energy (focused on {c_data['overview'].split('leads with')[0] if 'leads with' in c_data['overview'] else 'their style'}) "
        f"and is fueled by a drive for {p_mot}. "
        f"They are at their best when they can communicate via {p_comm} channels to achieve {p_mot}-aligned outcomes."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    add_heading("6. How You Can Best Support Them")
    add_body(m_data['support'])

    add_heading("7. What They Look Like When Thriving")
    add_bullets(m_data['thriving_bullets'])

    add_heading("8. What They Look Like When Struggling")
    add_bullets(c_data['struggle_bullets'])

    intervention_text = (
        f"• Increase structure or flexibility depending on their {p_comm} style.\n"
        f"• Re-establish expectations or reclarify priorities to satisfy their {p_mot} drive.\n"
        f"• {m_data['intervention']}\n"
        f"• Provide emotional support without enabling overextension."
    )
    add_heading("9. Supervisory Interventions")
    add_body(intervention_text)

    add_heading("10. What You Should Celebrate")
    add_body(f"• Their unique {p_comm} leadership strengths\n• {m_data['celebrate']}")

    add_heading("11. Coaching Questions")
    add_bullets(c_data['coaching'])

    add_heading("12. Helping Them Prepare for Advancement")
    add_body(c_data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP LOGIC ---

staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Guide Generator", 
    "🧬 Team DNA", 
    "⚖️ Conflict Mediator", 
    "🚀 Career Pathfinder",
    "📈 Org Pulse"
])

# --- TAB 1: GUIDE GENERATOR ---
with tab1:
    st.markdown("### Generate Individual Supervisory Guides")
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🔄 Refresh Database"):
            st.cache_data.clear()
            st.rerun()
            
    subtab1, subtab2 = st.tabs(["📚 From Database", "✏️ Manual Entry"])
    
    with subtab1:
        if not df.empty:
            def reset_t1(): st.session_state.t1_staff_select = None
            staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            selected_staff_name = st.selectbox(
                "Select Staff Member", options=list(staff_options.keys()), 
                index=None, key="t1_staff_select", placeholder="Choose a staff member..."
            )
            if selected_staff_name:
                data = staff_options[selected_staff_name]
                col1, col2, col3 = st.columns(3)
                col1.metric("Role", data['role'])
                col2.metric("Communication", data['p_comm'])
                col3.metric("Motivation", data['p_mot'])
                if st.button("Generate Guide for " + data['name'], type="primary"):
                    pdf_bytes = create_supervisor_guide(
                        data['name'], data['role'], data['p_comm'], data['s_comm'], data['p_mot'], data['s_mot']
                    )
                    st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf", mime="application/pdf")
                st.markdown("---")
                st.button("Reset Selection", key="reset_t1_db", on_click=reset_t1)
        else:
            st.info("Database is empty or loading...")

    with subtab2:
        with st.form("manual_form"):
            c1, c2 = st.columns(2)
            with c1:
                m_name = st.text_input("Staff Name")
                m_role = st.selectbox("Role", ["Program Supervisor", "Shift Supervisor", "YDP"])
            with c2:
                m_p_comm = st.selectbox("Primary Communication", ["Director", "Encourager", "Facilitator", "Tracker"])
                m_p_mot = st.selectbox("Primary Motivation", ["Growth", "Purpose", "Connection", "Achievement"])
            m_submitted = st.form_submit_button("Generate Guide (Manual)")
            if m_submitted and m_name:
                pdf_bytes = create_supervisor_guide(m_name, m_role, m_p_comm, "None", m_p_mot, "None")
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    def reset_t2(): st.session_state.t2_team_select = []
    if not df.empty:
        team_selection = st.multiselect("Build your Team", df['name'].tolist(), key="t2_team_select")
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Communication Mix")
                comm_counts = team_df['p_comm'].value_counts()
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4), use_container_width=True)
                if not comm_counts.empty:
                    dom_style = comm_counts.idxmax()
                    if comm_counts.max() / len(team_df) > 0.5:
                        st.warning(f"⚠️ **Echo Chamber Risk:** {int(comm_counts.max()/len(team_df)*100)}% of this team are **{dom_style}s**.")
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values), use_container_width=True)
            st.markdown("---")
            st.button("Clear Team Selection", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: p1_name = st.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1", placeholder="Select first person...")
        with c2: p2_name = st.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2", placeholder="Select second person...")
        
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            
            # Here p1 is Supervisor, p2 is Staff
            sup_style = p1['p_comm']
            staff_style = p2['p_comm']
            
            st.divider()
            st.subheader(f"Dynamic: {sup_style} (You) vs. {staff_style} (Staff)")
            
            if sup_style == staff_style:
                st.warning("⚠️ **Same-Style Blindspot:** You both communicate the same way. This often means you amplify each other's weaknesses (e.g., two Directors moving too fast, or two Facilitators waiting too long).")
                st.info("💡 **Tip:** Consciously adopt the opposite style to create balance.")
            
            elif sup_style in SUPERVISOR_CLASH_MATRIX and staff_style in SUPERVISOR_CLASH_MATRIX[sup_style]:
                data = SUPERVISOR_CLASH_MATRIX[sup_style][staff_style]
                
                st.info(f"**The Tension:** {data['dynamic']}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🛑 Self-Check (Your Blindspot)")
                    st.error(data['self_check'])
                with c_b:
                    st.markdown("#### 🗣️ The 1:1 Script")
                    st.success(f"\"{data['script']}\"")
            
            st.markdown("---")
            st.button("Reset Conflict Tool", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    def reset_t4(): st.session_state.career = None; st.session_state.career_target = None
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select candidate...")
        with c2: target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select target role...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({style})")
            path_data = CAREER_PATHWAYS.get(style, {}).get(target_role)
            
            if path_data:
                st.info(f"💡 **The Core Shift:** {path_data['shift']}")
                st.divider()
                c_a, c_b = st.columns([1, 1])
                with c_a:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                    if 'supervisor_focus' in path_data:
                        st.warning(f"👀 **Supervisor Focus (Watch Item):**\n\n{path_data['supervisor_focus']}")
                with c_b:
                    st.markdown("#### ✅ The Developmental Assignment")
                    with st.container(border=True):
                        st.write(f"**Setup:** {path_data['assignment_setup']}")
                        st.write(f"**The Task:** {path_data['assignment_task']}")
                        st.divider()
                        st.success(f"**🏆 Success looks like:** {path_data['success_indicators']}")
                        st.error(f"**🚩 Red flag:** {path_data['red_flags']}")
            else:
                st.write("Standard advancement path.")
            st.markdown("---")
            st.button("Reset Career Path", key="reset_btn_t4", on_click=reset_t4)

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Communication Styles")
            st.plotly_chart(px.pie(df, names='p_comm', color='p_comm', color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'}), use_container_width=True)
        with c2:
            st.subheader("Motivation Drivers")
            st.plotly_chart(px.bar(df, x='p_mot', color='p_mot'), use_container_width=True)
        st.divider()
        if 'role' in df.columns:
            role_breakdown = pd.crosstab(df['role'], df['p_comm'])
            st.dataframe(role_breakdown.style.background_gradient(cmap="Blues"), use_container_width=True)
    else:
        st.warning("No data available.")
