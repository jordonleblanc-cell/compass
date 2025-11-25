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

# --- SUPERVISOR CLASH MATRIX ---
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "The 'Bulldozer vs. Doormat' Dynamic. You push for results; they withdraw to protect the relationship.",
            "root_cause": "Value Mismatch: Utility vs. Affirmation. You value usefulness; they value being valued.",
            "watch_fors": [
                "The Encourager stops contributing in meetings (silent withdrawal).",
                "You start interrupting or finishing their sentences.",
                "They complain to peers that you are 'mean' or 'don't care'."
            ],
            "intervention_steps": [
                "**Step 1: Pre-Frame.** 'Efficiency without Empathy is Inefficiency.'",
                "**Step 2: The Translate.** Translate feelings into data.",
                "**Step 3: The Deal.** Listen for 5 minutes before solving."
            ],
            "scripts": {
                "To Director": "You are trying to fix the problem, but right now, the *relationship* is the problem.",
                "To Encourager": "My brevity is not anger; it is urgency. I need you to tell me: 'I can help you win, but I need you to lower your volume.'",
                "Joint": "We are speaking two different languages. I will validate your concern before we move to the next step."
            }
        },
        "Facilitator": {
            "tension": "The 'Gas vs. Brake' Dynamic. You want to decide now; they want to ensure the process is fair.",
            "root_cause": "Risk Perception: Stagnation vs. Error. You fear doing nothing; they fear doing the wrong thing.",
            "watch_fors": [
                "You issue commands via email to avoid a meeting.",
                "They keep saying 'We need to talk about this' but never decide.",
                "You visibly roll your eyes when they ask for 'thoughts'."
            ],
            "intervention_steps": [
                "**Step 1: Define the Clock.** Negotiate a deadline.",
                "**Step 2: Define the Veto.** Give them a 'Red Flag' right.",
                "**Step 3: The Debrief.** Review if you moved too fast or too slow."
            ],
            "scripts": {
                "To Director": "If I force this decision now, I get compliance, not buy-in.",
                "To Facilitator": "Silence looks like agreement. If you disagree, you must say 'Stop'.",
                "Joint": "We have a pace mismatch. We are going to set a timer for discussion, then we decide."
            }
        },
        "Tracker": {
            "tension": "The 'Vision vs. Obstacle' Dynamic. You act on gut; they act on data.",
            "root_cause": "Authority Source: Intuition vs. The Handbook.",
            "watch_fors": [
                "They quote policy numbers in arguments.",
                "You say 'Ask for forgiveness, not permission.'",
                "You bypass them to get things done."
            ],
            "intervention_steps": [
                "**Step 1: Clarify Roles.** You own 'What'; they own 'How'.",
                "**Step 2: The 'Yes, If' Rule.** Coach them to say 'Yes, if we do X...'.",
                "**Step 3: Risk Acceptance.** You must explicitly accept the risk."
            ],
            "scripts": {
                "To Director": "They aren't annoying; they are protecting me. Ask: 'How do we do this legally?'",
                "To Tracker": "Start with the solution. Say: 'I can get you there, but we have to take this side road.'",
                "Joint": "I set the destination. You check the brakes. We need both."
            }
        },
        "Director": {
            "tension": "The 'King vs. King' Dynamic. Two alphas. High conflict, high volume.",
            "root_cause": "Dominance: Both define safety as Control.",
            "watch_fors": [
                "Interruptions and public debates.",
                "Refusal to implement the other's idea.",
                "Team looks awkward during conflict."
            ],
            "intervention_steps": [
                "**Step 1: Separate Lanes.** Give distinct domains of authority.",
                "**Step 2: The Truce.** Acknowledge the power struggle.",
                "**Step 3: Disagree and Commit.**"
            ],
            "scripts": {
                "To Director A": "I am fighting to be right, not effective. Is this the hill I want to die on?",
                "To Director B": "Strip away the tone. Is their idea actually wrong?",
                "Joint": "We have two strong leaders. Stop fighting for the same wheel."
            }
        }
    },
    "Encourager": {
        "Director": {
            "tension": "The 'Sensitivity Gap'. You feel attacked by brevity; they feel annoyed by 'fluff'.",
            "root_cause": "Validation Style: External vs. Internal.",
            "watch_fors": [
                "You apologizing before asking for something.",
                "You feeling exhausted/crying after supervision."
            ],
            "intervention_steps": [
                "**Step 1: The Headline.** Start with the conclusion.",
                "**Step 2: The 'Why'.** Ask them to explain the reason for speed.",
                "**Step 3: Scheduled Venting.** 5 mins for feelings, then work."
            ],
            "scripts": {
                "To Encourager": "I need to translate intuition into business risks. Don't say 'I feel bad', say 'Morale will drop'.",
                "To Director": "You are crushing me. 'Please' and 'Thank you' buy you speed.",
                "Joint": "You own the timeline. I own the communication plan."
            }
        },
        "Facilitator": {
            "tension": "The 'Polite Stagnation'. Both want harmony. Decisions stall.",
            "root_cause": "Conflict Avoidance: Fear of Rejection vs. Fear of Unfairness.",
            "watch_fors": [
                "Endless meetings with no change.",
                "Passive language ('It would be nice if...')."
            ],
            "intervention_steps": [
                "**Step 1: Name the Fear.** 'We are scared to upset them.'",
                "**Step 2: Assign Bad Guy.** Supervisor acts as the heavy.",
                "**Step 3: Script it.** Write the hard conversation together."
            ],
            "scripts": {
                "To Encourager": "I am protecting feelings at the expense of the program.",
                "To Facilitator": "The search for consensus is now procrastination.",
                "Joint": "We are being too nice. Who is going to deliver the news?"
            }
        },
        "Tracker": {
            "tension": "The 'Rigidity vs. Flow' Dynamic. You bend rules; they enforce them.",
            "root_cause": "Safety Source: Connection vs. Consistency.",
            "watch_fors": [
                "You making secret deals.",
                "They police you publicly."
            ],
            "intervention_steps": [
                "**Step 1: Why of Rules.** Rules protect vulnerable youth.",
                "**Step 2: Why of Exceptions.** Rigid rules break rapport.",
                "**Step 3: The Hybrid.** Follow rule, deliver with empathy."
            ],
            "scripts": {
                "To Encourager": "When I bend the rule, I make you the 'bad guy'. We must be united.",
                "To Tracker": "You are right about the policy, but your delivery is cold."
            }
        },
        "Encourager": {
            "tension": "The 'Echo Chamber'. High warmth, low accountability.",
            "root_cause": "Emotional Contagion.",
            "watch_fors": [
                "Supervision is just venting.",
                "Us vs. Them narratives."
            ],
            "intervention_steps": [
                "**Step 1: 5-Minute Rule.** Limit venting.",
                "**Step 2: The Pivot.** 'What is the first step to fixing it?'",
                "**Step 3: External Data.** Force reality check."
            ],
            "scripts": {
                "To Encourager A": "We are spinning. Let's solve the logistics.",
                "Joint": "We support each other well. Now we need to challenge each other."
            }
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "The 'Steamroll'. They demand decision; you freeze.",
            "root_cause": "Processing: External vs. Internal.",
            "watch_fors": [
                "You staying silent in meetings.",
                "They assume agreement."
            ],
            "intervention_steps": [
                "**Step 1: Interrupt.** Learn to say 'Hold on'.",
                "**Step 2: Pre-Meeting.** Brief them beforehand.",
                "**Step 3: The Frame.** Frame process as risk management."
            ],
            "scripts": {
                "To Director": "You are moving too fast. Let me get the team on board.",
                "To Facilitator": "I am giving away power. I must speak up."
            }
        },
        "Tracker": {
            "tension": "The 'Details Loop'. You want concept; they want form.",
            "root_cause": "Scope: Horizontal vs. Vertical.",
            "watch_fors": [
                "Long email chains.",
                "Meetings run over."
            ],
            "intervention_steps": [
                "**Step 1: Concept First.** Agree on goal.",
                "**Step 2: Detail Second.** Build checklist.",
                "**Step 3: Parking Lot.** Park details till end."
            ],
            "scripts": {
                "To Tracker": "We are at 30,000 feet. Fly with me for 5 mins.",
                "To Facilitator": "Tracker isn't killing the idea; they are testing it."
            }
        }
    },
    "Tracker": {
        "Director": {
            "tension": "The 'Micromanagement Trap'. You ask questions; they feel distrusted.",
            "root_cause": "Trust: Verification vs. Competence.",
            "watch_fors": [
                "You sending correction emails.",
                "They avoid you."
            ],
            "intervention_steps": [
                "**Step 1: Pick Battles.** Safety vs. Preference.",
                "**Step 2: The Sandbox.** Safe space to break things.",
                "**Step 3: Solution-First.** 'We can, IF...'"
            ],
            "scripts": {
                "To Director": "I'm ensuring you don't get fired for compliance.",
                "To Tracker": "I must stop correcting spelling. Focus on liability risks."
            }
        }
    }
}
# Robustness for missing keys
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {
                "tension": "Differing perspectives on work and communication.",
                "root_cause": "Different priorities.",
                "watch_fors": ["Miscommunication", "Frustration"],
                "intervention_steps": ["Listen first", "Clarify goals"],
                "scripts": {"To Director": "Let's align.", "To Encourager": "Let's align.", "Joint": "Let's align."}
            }

# (D) CAREER PATHWAYS ---
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "why": "Directors act fast. They see a problem and fix it. As a Shift Sup, if they fix everything, their team learns nothing.",
            "conversation": "You have high capacity. But to succeed now, you have to sit on your hands. Your success is defined by how confident your team feels, not how much you do.",
            "assignment_setup": "Lead a shift physically restricted to the office.",
            "assignment_task": "Run the shift entirely through verbal direction. No touching paperwork.",
            "success_indicators": "Did they let staff struggle without jumping in? Clear verbal instructions?",
            "red_flags": "Running out of the office to 'just do it quick'.",
            "supervisor_focus": "Watch for 'Hero Mode'. Pull them back if they jump in to fix a crisis their team could handle."
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "why": "Program Sups need buy-in from people they don't supervise (School, Clinical).",
            "conversation": "You execute well. But you can't order Clinical to do things. 'Slowing down' to build relationships speeds up results.",
            "assignment_setup": "Identify a peer in another department they have friction with.",
            "assignment_task": "Task them with a cross-departmental project. They must interview stakeholders and incorporate feedback.",
            "success_indicators": "The plan includes ideas that didn't come from them.",
            "red_flags": "They present a plan that is 100% their own idea.",
            "supervisor_focus": "Monitor patience. Reframe 'politics' as 'relationship building'."
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
            "why": "Managers prevent fires. Directors love fighting them.",
            "conversation": "You react beautifully to problems. The next level requires you to prevent them 6 months in advance.",
            "assignment_setup": "Assign a strategic plan for a recurring seasonal issue.",
            "assignment_task": "Submit a plan with data projections and budget needs 3 months early.",
            "success_indicators": "The plan relies on systems, not force of will.",
            "red_flags": "Delaying planning until the last minute.",
            "supervisor_focus": "Check their horizon. Are they talking about today or next month?"
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Guardian'.",
            "why": "Encouragers want to be liked. Shift Sups must be respected.",
            "conversation": "Your empathy is key, but avoiding hard conversations creates an unsafe environment. Accountability is kindness.",
            "assignment_setup": "Identify a staff member who is consistently late.",
            "assignment_task": "Lead a policy reinforcement meeting. Supervisor observes.",
            "success_indicators": "States expectation without apologizing.",
            "red_flags": "Apologizing for the rule. Making a joke to deflect.",
            "supervisor_focus": "Watch for 'Apology Language'. Correct immediately."
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "why": "Programs run on structure, not just personality.",
            "conversation": "You create an amazing climate. Now back it with structure. Master the boring parts (budgets, audits) to protect the team.",
            "assignment_setup": "Assign ownership of a compliance audit.",
            "assignment_task": "Present data and rationale to the team, standing on facts.",
            "success_indicators": "Accurate audit. Explained 'why' without emotion.",
            "red_flags": "Asking a Tracker to do it. Procrastinating.",
            "supervisor_focus": "Inspect what you expect. Help them organize."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "why": "Encouragers take 'No' personally and burn out.",
            "conversation": "You carry everyone's emotions. At manager level, that weight is too heavy. Learn to set emotional boundaries.",
            "assignment_setup": "Manage a resource allocation conflict (deny a budget request).",
            "assignment_task": "Deliver a 'No', explain the business reason, withstand disappointment.",
            "success_indicators": "Holding the line without promising to 'fix it later'.",
            "red_flags": "Caving to the request. Venting about 'Upper Management'.",
            "supervisor_focus": "Watch for burnout. Ask: 'Who are you trying to save?'"
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Peer' to 'Decider'.",
            "why": "Facilitators freeze when the team is split.",
            "conversation": "You ensure everyone is heard. But sometimes consensus is impossible. Get comfortable making the '51% decision'.",
            "assignment_setup": "Put them in charge of a time-sensitive transition.",
            "assignment_task": "Make immediate calls on positioning. Debrief: 'Where did you hesitate?'",
            "success_indicators": "Gave direct commands. Didn't ask 'What do you guys think?' during crisis.",
            "red_flags": "Stood back. Tried to have a meeting during transition.",
            "supervisor_focus": "Push for speed. Throw questions back: 'You tell me.'"
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "why": "Program Sups must set the vision, not just mediate.",
            "conversation": "You act as a buffer. Now inject your own vision. Don't wait to see what the group wants; tell us where to go.",
            "assignment_setup": "Propose a new initiative for program culture.",
            "assignment_task": "Present it as a direction, not a discussion.",
            "success_indicators": "Uses declarative statements ('We will...'). Handles pushback.",
            "red_flags": "Frames it as a question. Retreats at resistance.",
            "supervisor_focus": "Watch for 'The Buffer'. Challenge them to take a stand."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
            "why": "Facilitators stall critical changes for fairness.",
            "conversation": "Fair process is vital, but sometimes yields poor results. Prioritize outcome over comfort. Disrupt harmony to achieve mission.",
            "assignment_setup": "Implement a necessary but unpopular policy change.",
            "assignment_task": "Listen, validate, but do NOT change the decision.",
            "success_indicators": "Policy implemented on time. They survive the unhappiness.",
            "red_flags": "Delays to 'get more feedback'. Waters down policy.",
            "supervisor_focus": "Monitor tolerance for conflict. 'The upset is inevitable.'"
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Executor' to 'Overseer'.",
            "why": "Trackers micromanage because they don't trust others' accuracy.",
            "conversation": "You are brilliant at details. But you can't track everything personally. You have to trust the team.",
            "assignment_setup": "The 'Hands-Off' Day. Supervise a complex task.",
            "assignment_task": "Strictly prohibited from touching paperwork. Guide verbally.",
            "success_indicators": "Kept hands in pockets. Gave clear corrections.",
            "red_flags": "Grabbed the pen. Sighed and did it themselves.",
            "supervisor_focus": "Watch for micromanagement. 'If it is 80% right, it is right enough.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "why": "Leadership involves judgment calls where no rule exists.",
            "conversation": "You excel when rules are clear. Leadership is full of gray areas. Develop intuition to navigate dynamics that don't fit the spreadsheet.",
            "assignment_setup": "Handle a complex parent complaint where standard rules don't apply.",
            "assignment_task": "Make a principle-based decision rather than rule-based.",
            "success_indicators": "Made a sensible decision not in the handbook.",
            "red_flags": "Froze because 'there's no policy'. Applied a rule rigidly.",
            "supervisor_focus": "Challenge rigidity. Ask 'What is the intent of the rule?'"
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "why": "Efficiency over connection creates a brittle organization.",
            "conversation": "Culture eats strategy for breakfast. Invest as much energy in 'how people feel' as 'what people do'.",
            "assignment_setup": "Task them with a retention initiative.",
            "assignment_task": "Focus solely on relationships for a week. Delegate metrics.",
            "success_indicators": "Had non-work conversations. Staff feel seen.",
            "red_flags": "Turned morale into a checklist.",
            "supervisor_focus": "Look for the 'Human Element'. Ask about people, not tasks."
        }
    }
}

# (E) PDF Content Dictionaries (Full Text)
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
    gray = (100, 100, 100)
    
    # HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

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
    add_body(c['overview'])

    add_heading("2. Supervising Their Communication")
    add_body(c['supervising'])

    add_heading(f"3. Motivation Profile: {p_mot}")
    add_body(m['overview'])

    add_heading("4. Motivating This Staff Member")
    add_body(m['motivating'])

    integrated_text = (
        f"This staff member leads with {p_comm} energy (focused on {c['overview'].split('leads with')[0] if 'leads with' in c['overview'] else 'their style'}) "
        f"and is fueled by a drive for {p_mot}. "
        f"They are at their best when they can communicate via {p_comm} channels to achieve {p_mot}-aligned outcomes."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    add_heading("6. How You Can Best Support Them")
    add_body(m['support'])

    add_heading("7. What They Look Like When Thriving")
    add_bullets(m['thriving_bullets'])

    add_heading("8. What They Look Like When Struggling")
    add_bullets(c['struggle_bullets'])

    intervention_text = (
        f"• Increase structure or flexibility depending on their {p_comm} style.\n"
        f"• Re-establish expectations or reclarify priorities to satisfy their {p_mot} drive.\n"
        f"• {m['intervention']}\n"
        f"• Provide emotional support without enabling overextension."
    )
    add_heading("9. Supervisory Interventions")
    add_body(intervention_text)

    add_heading("10. What You Should Celebrate")
    add_body(f"• Their unique {p_comm} leadership strengths\n• {m['celebrate']}")

    add_heading("11. Coaching Questions")
    add_bullets(c['coaching'])

    add_heading("12. Helping Them Prepare for Advancement")
    add_body(c['advancement'])

    return pdf.output(dest='S').encode('latin-1')

# --- DISPLAY GUIDE ON SCREEN ---
def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])
    
    st.markdown(f"## 📑 Supervisory Guide: {name}")
    st.markdown(f"**Role:** {role} | **Profile:** {p_comm} × {p_mot}")
    st.divider()
    
    st.subheader(f"1. Communication Profile: {p_comm}")
    st.write(c['overview'])
    
    st.subheader("2. Supervising Their Communication")
    st.write(c['supervising'])
    
    st.subheader(f"3. Motivation Profile: {p_mot}")
    st.write(m['overview'])
    
    st.subheader("4. Motivating This Staff Member")
    st.write(m['motivating'])
    
    st.subheader("5. Integrated Leadership Profile")
    integrated_text = (
        f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. "
        f"They lead with {p_comm} traits while seeking {p_mot} outcomes. "
        "When these align, they are unstoppable. When they conflict, frustration mounts quickly."
    )
    st.write(integrated_text)
    
    st.subheader("6. How You Can Best Support Them")
    st.write(m['support'])
    
    st.subheader("7. What They Look Like When Thriving")
    for b in m['thriving_bullets']: st.markdown(f"- {b}")
    
    st.subheader("8. What They Look Like When Struggling")
    for b in c['struggle_bullets']: st.markdown(f"- {b}")
    
    st.subheader("9. Supervisory Interventions")
    st.write("When this staff member is struggling, use these targeted interventions:")
    interventions = [
        f"Validate their Motivation ({p_mot}) before correcting behavior.",
        f"Re-align Expectations: Ensure they know exactly what success looks like in this specific situation.",
        f"{m['intervention']}"
    ]
    for i in interventions: st.markdown(f"- {i}")
    
    st.subheader("10. What You Should Celebrate")
    st.write(m['celebrate'])
    
    st.subheader("11. Coaching Questions")
    for q in c['coaching']: st.markdown(f"- {q}")
    
    st.subheader("12. Helping Them Prepare for Advancement")
    st.write(c['advancement'])

# --- MAIN APP LOGIC ---

staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# RESET FUNCTIONS
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

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
                        data['name'], data['role'], 
                        data['p_comm'], data['s_comm'], 
                        data['p_mot'], data['s_mot']
                    )
                    st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf", mime="application/pdf")
                    
                    st.divider()
                    display_guide(data['name'], data['role'], data['p_comm'], data['s_comm'], data['p_mot'], data['s_mot'])

                st.markdown("---")
                st.button("Reset Selection", key="reset_t1_db", on_click=reset_t1)
        else:
            st.info("Database is empty or loading...")

    with subtab2:
        with st.form("manual_form"):
            col1, col2 = st.columns(2)
            with col1:
                m_name = st.text_input("Staff Name")
                m_role = st.selectbox("Role", ["Program Supervisor", "Shift Supervisor", "YDP"])
            with col2:
                m_p_comm = st.selectbox("Primary Communication", ["Director", "Encourager", "Facilitator", "Tracker"])
                m_p_mot = st.selectbox("Primary Motivation", ["Growth", "Purpose", "Connection", "Achievement"])
                
            m_submitted = st.form_submit_button("Generate Guide (Manual)")
            
            if m_submitted and m_name:
                pdf_bytes = create_supervisor_guide(m_name, m_role, m_p_comm, "None", m_p_mot, "None")
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")
                
                st.divider()
                display_guide(m_name, m_role, m_p_comm, "None", m_p_mot, "None")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
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
                    dominant_style = comm_counts.idxmax()
                    dom_pct = comm_counts.max() / len(team_df)
                    if dom_pct > 0.5:
                        st.warning(f"⚠️ **Echo Chamber Risk:** {int(dom_pct*100)}% of this team are **{dominant_style}s**.")
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values), use_container_width=True)
                
                # Missing Voices Analysis
                all_comms = {"Director", "Encourager", "Facilitator", "Tracker"}
                present_comms = set(team_df['p_comm'].unique())
                missing = all_comms - present_comms
                if missing:
                    st.info(f"🔍 **Missing Voices:** This team lacks **{', '.join(missing)}** energy. As the supervisor, you may need to fill this gap.")

            st.markdown("---")
            st.button("Clear Team Selection", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: p1_name = st.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1", placeholder="Select...")
        with c2: p2_name = st.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2", placeholder="Select...")
        
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            sup_style, staff_style = p1['p_comm'], p2['p_comm']
            st.divider()
            st.subheader(f"Dynamic: {sup_style} (You) vs. {staff_style} (Staff)")
            
            if sup_style == staff_style:
                st.warning("⚠️ **Same-Style Blindspot:** You both communicate the same way.")
            elif sup_style in SUPERVISOR_CLASH_MATRIX and staff_style in SUPERVISOR_CLASH_MATRIX[sup_style]:
                data = SUPERVISOR_CLASH_MATRIX[sup_style][staff_style]
                with st.expander("🔥 The Dynamic (Read First)", expanded=True):
                    st.write(data['tension'])
                    st.markdown(f"**Root Cause:** {data['root_cause']}")
                    st.markdown("**👀 Watch For:**")
                    for w in data['watch_fors']: st.markdown(f"- {w}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🛠️ Intervention Plan")
                    for s in data['intervention_steps']: st.markdown(s)
                with c_b:
                    st.markdown("#### 🗣️ Script Library")
                    st.info(f"**To You:** {data['scripts'].get('To Director') or data['scripts'].get('To Encourager') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}")
                    st.warning(f"**To Them:** {data['scripts'].get('To Encourager') or data['scripts'].get('To Director') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}")
                    st.success(f"**Joint:** {data['scripts']['Joint']}")
            st.markdown("---")
            st.button("Reset", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select...")
        with c2: target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({style})")
            path_data = CAREER_PATHWAYS.get(style, {}).get(target_role)
            
            if path_data:
                st.info(f"💡 **The Shift:** {path_data['shift']}")
                st.markdown(f"**The Why:** {path_data['why']}")
                st.divider()
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                    st.warning(f"**👀 Watch For:** {path_data.get('supervisor_focus')}")
                with c_b:
                    st.markdown("#### ✅ The 'Litmus Test' Assignment")
                    with st.container(border=True):
                        st.markdown(f"**Setup:** {path_data['assignment_setup']}")
                        st.markdown(f"**Task:** {path_data['assignment_task']}")
                        st.divider()
                        st.success(f"**🏆 Success:** {path_data['success_indicators']}")
                        st.error(f"**🚩 Red Flag:** {path_data['red_flags']}")
            st.markdown("---")
            st.button("Reset", key="reset_btn_t4", on_click=reset_t4)

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    if not df.empty:
        # Top Level Metrics
        m1, m2, m3, m4 = st.columns(4)
        top_comm = df['p_comm'].mode()[0]
        top_mot = df['p_mot'].mode()[0]
        
        all_comms = ["Director", "Encourager", "Facilitator", "Tracker"]
        comm_counts = df['p_comm'].value_counts()
        missing_comm = [c for c in all_comms if c not in comm_counts.index]
        lowest_comm = missing_comm[0] if missing_comm else comm_counts.idxmin()
        
        m1.metric("Dominant Style", top_comm)
        m2.metric("Top Driver", top_mot)
        m3.metric("Cultural Blindspot", lowest_comm)
        m4.metric("Total Assessments", len(df))
        
        st.divider()
        
        st.subheader("1. The Leadership Pipeline")
        role_order = ["YDP", "Shift Supervisor", "Program Supervisor"]
        fig_pipeline = px.histogram(df, x="role", color="p_comm", 
                                    category_orders={"role": role_order},
                                    color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'},
                                    title="Communication Style by Role")
        st.plotly_chart(fig_pipeline, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("2. Motivation Heatmap")
            if 'role' in df.columns and 'p_mot' in df.columns:
                mot_cross = pd.crosstab(df['role'], df['p_mot'])
                st.dataframe(mot_cross.style.background_gradient(cmap="Greens"), use_container_width=True)
        
        with c2:
            st.subheader("3. The Culture Matrix")
            df['pair'] = df['p_comm'] + " + " + df['p_mot']
            pair_counts = df.groupby(['p_comm', 'p_mot']).size().reset_index(name='counts')
            fig_matrix = px.scatter(pair_counts, x='p_comm', y='p_mot', size='counts', color='p_comm',
                                    color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'},
                                    size_max=60)
            st.plotly_chart(fig_matrix, use_container_width=True)
            
        st.info("💡 **Insight:** " + (f"High Burnout Risk: 'Director + Achievement' culture." if top_comm == "Director" and top_mot == "Achievement" else f"Current dominant culture: {top_comm} driven by {top_mot}."))
        
    else:
        st.warning("No data available.")
