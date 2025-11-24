import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- 3. DEEP-DIVE CONTENT DICTIONARIES ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# --- CONFLICT SCRIPTS (Expanded for Teaching Supervisors) ---
CONFLICT_SCRIPTS = {
    "Director-Encourager": {
        "tension": "The 'Head vs. Heart' Battle. The Director wants to solve the problem efficiently; the Encourager wants to heal the relationship. The Director thinks the Encourager is 'soft' or emotional; the Encourager thinks the Director is 'cold' or mean.",
        "prep": [
            "Tell the Director: 'If you win the logic argument but hurt their feelings, you lose the war. You must validate their emotion.'",
            "Tell the Encourager: 'The Director isn't attacking you personally; they are attacking the inefficiency. Don't withdraw.'"
        ],
        "protocol": [
            "1. Open by stating the shared goal (e.g., 'We both want a smooth shift').",
            "2. Let the Encourager speak first about the *impact* of the friction. The Director must listen without interrupting.",
            "3. Ask the Director to restate what they heard (Validation Check).",
            "4. Let the Director define the *task* or *standard* that isn't being met.",
            "5. Ask the Encourager to agree to the standard, provided the delivery is respectful."
        ],
        "script_a": "Director: 'I need to know you have my back on enforcing rules, even when it's uncomfortable.'",
        "script_b": "Encourager: 'I can enforce the rules, but I need you to stop correcting me in front of the kids.'"
    },
    "Director-Facilitator": {
        "tension": "The 'Gas vs. Brake' Battle. The Director operates on 'Ready, Fire, Aim.' The Facilitator operates on 'Ready, Aim, Aim, Aim.' The Director feels held back; the Facilitator feels steamrolled.",
        "prep": [
            "Tell the Director: 'Silence does not mean agreement. If you push too fast, they will shut down.'",
            "Tell the Facilitator: 'You cannot wait for 100% consensus. You need to articulate your specific risk, not just a vague feeling.'"
        ],
        "protocol": [
            "1. Acknowledge the pace difference immediately.",
            "2. Ask the Director to propose their plan.",
            "3. Ask the Facilitator: 'What is the ONE major risk you see with this speed?' (Force specificity).",
            "4. Negotiate a timeline. Not 'Now' (Director) and not 'Next Month' (Facilitator). Pick a date.",
            "5. Director commits to waiting until the date; Facilitator commits to deciding on that date."
        ],
        "script_a": "Director: 'I am frustrated because every delay feels like we are paralyzed.'",
        "script_b": "Facilitator: 'I am frustrated because we keep making the same mistakes by rushing.'"
    },
    "Director-Tracker": {
        "tension": "The 'Vision vs. Reality' Battle. The Director says 'Just make it happen.' The Tracker asks 'But what about Regulation 14.B?'. The Director feels blocked by details; the Tracker feels their expertise is being ignored.",
        "prep": [
            "Tell the Director: 'They are not trying to be difficult; they are trying to keep you out of jail/trouble. Listen to the risk.'",
            "Tell the Tracker: 'Start with 'Yes, if...' instead of 'No'. Show them the path to the goal, don't just put up a wall.'"
        ],
        "protocol": [
            "1. Director states the desired outcome.",
            "2. Tracker outlines the specific compliance/safety blockers.",
            "3. Supervisor asks Tracker: 'Is this a preference or a policy?'",
            "4. If Policy: Director must adapt. If Preference: Tracker must adapt.",
            "5. Agree on the 'Minimum Viable Compliant Plan'."
        ],
        "script_a": "Director: 'I value your eye for detail, but I need solutions, not just problems.'",
        "script_b": "Tracker: 'I want to get there too, but I cannot sign off on a plan that violates safety protocols.'"
    },
    "Encourager-Tracker": {
        "tension": "The 'Empathy vs. Policy' Battle. The Encourager bends rules to build rapport. The Tracker enforces rules to build safety. The Tracker sees the Encourager as chaotic/unsafe; the Encourager sees the Tracker as robotic/uncaring.",
        "prep": [
            "Tell the Encourager: 'Structure is a form of care. Inconsistency creates anxiety for traumatized youth.'",
            "Tell the Tracker: 'Rules without relationship breeds rebellion. You need the Encourager's rapport to get the youth to comply.'"
        ],
        "protocol": [
            "1. Frame the conflict around 'Safety'.",
            "2. Ask Tracker to explain *why* the rule exists (the safety rationale).",
            "3. Ask Encourager to explain *why* they bent it (the relational need).",
            "4. Compromise: The Rule remains firm (Tracker wins), but the Delivery changes (Encourager wins).",
            "5. Script the exact language to use with the youth next time."
        ],
        "script_a": "Encourager: 'I felt like enforcing that consequence would have caused a restrain, so I let it slide.'",
        "script_b": "Tracker: 'When you let it slide, you made me the bad guy for the next shift. We have to be consistent.'"
    },
    "Encourager-Facilitator": {
        "tension": "The 'Nice-Off' (Stagnation). Both want harmony. The Facilitator focuses on fairness to the group; the Encourager focuses on the feelings of the individual. They will circle an issue for hours to avoid upsetting anyone.",
        "prep": [
            "Supervisor Role: You must be the 'Bad Guy' who forces the conflict into the open.",
            "Warning: Watch out for them agreeing just to end the meeting. You need to dig for the disagreement."
        ],
        "protocol": [
            "1. Call out the elephant: 'We are being too nice. What is the actual problem?'",
            "2. Force a choice: 'If we prioritize the individual (Encourager), is it fair to the group (Facilitator)?'",
            "3. If they can't decide, you (Supervisor) make the call.",
            "4. Assign specific communication roles so they don't have to feel 'mean' delivering the news."
        ],
        "script_a": "Encourager: 'I just don't want [Staff Member] to feel singled out.'",
        "script_b": "Facilitator: 'But if we don't address it, the rest of the team feels it's unfair.'"
    },
    "Facilitator-Tracker": {
        "tension": "The 'Analysis Paralysis' Loop. The Facilitator waits for consensus. The Tracker waits for more data. Nothing happens. The risk is total stagnation.",
        "prep": [
            "Supervisor Role: You must set a hard deadline.",
            "Tell both: 'A good decision today is better than a perfect decision next week.'"
        ],
        "protocol": [
            "1. Identify the decision that is stuck.",
            "2. Ask Tracker: 'Do we have enough data to be 80% sure?' (They will never be 100% sure).",
            "3. Ask Facilitator: 'Does anyone have a major objection that endangers the program?'",
            "4. Supervisor declares: 'We are moving forward. I take responsibility for the risk.'",
            "5. Set a review date to adjust the plan later (this lowers their anxiety)."
        ],
        "script_a": "Facilitator: 'I want to make sure everyone is comfortable with the new schedule.'",
        "script_b": "Tracker: 'I'm just worried we haven't accounted for the Tuesday transport logistics yet.'"
    }
}

# --- CAREER PATHWAYS (Expanded for Teaching Supervisors) ---
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "why": "Directors act fast. They see a problem and fix it. As a Shift Sup, if they fix everything, their team learns nothing. They become the bottleneck.",
            "conversation": "You have high capacity and speed. But to succeed now, you have to sit on your hands. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless absolute safety dictates otherwise).",
            "assignment_task": "They must run the shift entirely through verbal direction and delegation to peers. They cannot touch paperwork or intervene in minor conflicts.",
            "success_indicators": "Did they let a staff member struggle through a task without jumping in? Did they give clear verbal instructions?",
            "red_flags": "They ran out of the office to 'just do it quick'. They complain that their team is 'too slow'."
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "why": "Program Sups need buy-in from people they don't supervise (School, Clinical). Directors tend to order people around, which alienates peers.",
            "conversation": "You are excellent at execution. But you can't order the Clinical team to do things. You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment_setup": "Identify a peer in another department (School/Clinical) they have friction with.",
            "assignment_task": "Task them with a cross-departmental project (e.g., improving school transitions). They must interview stakeholders and present a plan that incorporates *their* feedback.",
            "success_indicators": "The plan includes ideas that clearly didn't come from the Director. The peer reports feeling heard.",
            "red_flags": "They present a plan that is 100% their own idea and complain that the other dept is 'difficult'."
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
            "why": "Directors love fighting fires. Managers need to prevent fires. Directors often struggle to sit still long enough to plan.",
            "conversation": "You react beautifully to problems. The next level requires you to prevent them 6 months in advance. You need to shift from reliance on your force of will to reliance on sustainable systems.",
            "assignment_setup": "Assign a long-term strategic plan for a recurring seasonal issue (e.g., Summer Break Structure).",
            "assignment_task": "They must submit a plan with data projections, budget needs, and staffing models 3 months in advance.",
            "success_indicators": "The plan relies on systems, not just 'working harder'. They anticipate risks.",
            "red_flags": "They delay the planning until the last minute. The plan is just 'we will figure it out'."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Guardian'.",
            "why": "Encouragers want to be liked. Shift Sups must be respected. If they can't hold a boundary, the shift becomes unsafe.",
            "conversation": "Your empathy is your superpower, but if you avoid hard conversations, you create an unsafe environment. The team needs you to be a 'Guardian' of the standard. Accountability is kindness.",
            "assignment_setup": "Identify a staff member who is consistently late or missing protocols.",
            "assignment_task": "Lead a policy reinforcement meeting with that staff member. You (Supervisor) observe but do not speak.",
            "success_indicators": "They state the expectation clearly without apologizing. They don't use 'The boss wants...' language.",
            "red_flags": "They apologize for the rule ('Sorry I have to tell you this...'). They make a joke to deflect the tension."
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "why": "Encouragers run on personality. Programs run on structure. They need to master the boring parts (budgets, audits) to protect the team.",
            "conversation": "You create an amazing climate. To lead a program, that climate must be backed by unshakeable structure. You need to master the unsexy parts of leadership so your team is protected.",
            "assignment_setup": "Assign ownership of a compliance audit or a complex schedule overhaul.",
            "assignment_task": "They must present the data and the rationale to the team, standing on the facts rather than just their relationship.",
            "success_indicators": "The audit is accurate. They can explain the 'why' without appealing to emotion.",
            "red_flags": "They ask a Tracker to do it for them. They procrastinate the paperwork to hang out with staff."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "why": "Managers deal with resource scarcity. Encouragers take 'No' personally and burn out trying to save everyone.",
            "conversation": "You carry the emotions of your people. At the manager level, that weight is too heavy. Your growth edge is caring deeply about the person without taking responsibility for their feelings.",
            "assignment_setup": "Have them manage a resource allocation conflict (e.g., denying a budget request).",
            "assignment_task": "Deliver a 'No' to a request, explain the business reason, and withstand the disappointment of the staff member.",
            "success_indicators": "They hold the line. They don't promise to 'fix it later' just to stop the person from being sad.",
            "red_flags": "They cave to the request. They vent to the staff member about 'Upper Management' making them do it."
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Peer' to 'Decider'.",
            "why": "Facilitators freeze when the team is split. Safety requires immediate direction without consensus.",
            "conversation": "You ensure everyone is heard. But as a Shift Sup, there will be moments where consensus is impossible. You need to get comfortable making the '51% decision'.",
            "assignment_setup": "Put them in charge of a time-sensitive crisis drill or transition.",
            "assignment_task": "They must make immediate calls on staff positioning. Debrief afterwards: 'Where did you hesitate?'",
            "success_indicators": "They gave direct commands. They didn't ask 'What do you guys think?' during the crisis.",
            "red_flags": "They stood back and let a Director take over. They tried to have a meeting in the middle of a transition."
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "why": "Facilitators lead from the middle. Program Sups must lead from the front and set the vision.",
            "conversation": "You act as a great buffer. But we need you to inject your own vision. Don't just wait to see what the group wants; tell us where you think the group needs to go.",
            "assignment_setup": "Ask them to propose a new initiative for the program culture.",
            "assignment_task": "Present it to the team as a direction, not a discussion topic. 'This is where we are going.'",
            "success_indicators": "They use declarative statements ('We will...'). They handle pushback without folding.",
            "red_flags": "They frame it as a question ('How would you guys feel about...?'). They retreat at the first sign of resistance."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
            "why": "Facilitators get bogged down in fairness and stall critical changes.",
            "conversation": "Fair process is vital, but sometimes it yields poor results. You need to be willing to disrupt the harmony to achieve the mission.",
            "assignment_setup": "Task them with implementing a necessary but unpopular policy change.",
            "assignment_task": "Listen to complaints, validate feelings, but do NOT change the decision.",
            "success_indicators": "The policy gets implemented on time. They survive the team being unhappy with them.",
            "red_flags": "They delay implementation to 'get more feedback'. They water down the policy to make it nicer."
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Executor' to 'Overseer'.",
            "why": "Trackers don't trust others to do it right, so they micromanage. They burn out trying to do 5 jobs.",
            "conversation": "You are brilliant at details. But you cannot track every detail personally. You have to let the team do the checklist, even if they do it differently than you would.",
            "assignment_setup": "The 'Hands-Off' Day. Assign them to supervise a complex task (intake/search).",
            "assignment_task": "Strictly prohibited from touching paperwork. Must guide a peer to do it verbally.",
            "success_indicators": "They kept their hands in their pockets. They gave clear corrections without taking over.",
            "red_flags": "They grabbed the pen. They sighed and said 'I'll just do it'."
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "why": "Trackers want a rule for everything. Leadership involves judgment calls where no rule exists.",
            "conversation": "You excel when rules are clear. Leadership is full of gray areas. You need to develop your intuition to navigate dynamics that don't fit the spreadsheet.",
            "assignment_setup": "Handle a complex parent/youth complaint where standard rules don't apply.",
            "assignment_task": "Make a principle-based decision (fairness/safety) rather than a rule-based one.",
            "success_indicators": "They made a decision that wasn't in the handbook but made sense. They can explain the 'spirit' of the rule.",
            "red_flags": "They froze because 'there's no policy'. They applied a rule rigidly that made no sense in context."
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "why": "Trackers value efficiency over connection, risking a sterile, unhappy culture.",
            "conversation": "Culture eats strategy for breakfast. If you prioritize efficiency over connection, you will have a compliant but brittle organization.",
            "assignment_setup": "Task them with a retention or morale initiative.",
            "assignment_task": "Spend one week focusing solely on staff development/relationships. Delegate metrics to a deputy.",
            "success_indicators": "They had non-work conversations. Staff report feeling seen.",
            "red_flags": "They turned the morale initiative into a checklist ('Did you have fun? Check yes')."
        }
    }
}

# --- PDF Content Dictionaries (Full Text) ---
COMM_PROFILES = {
    "Director": {
        "overview": "This staff member communicates primarily as a Director, meaning they lead with clarity, structure, and urgency.",
        "supervising": "Be direct, concise, and outcome-focused. They respect leaders who get to the point. Define the 'what' clearly, but give autonomy on the 'how'.",
        "struggle_bullets": ["Decreased patience", "Over-assertiveness", "Fatigue/Irritability", "Rigid enforcement"],
        "coaching": ["What are the risks of moving this fast?", "Who haven't we heard from yet?", "How can you frame this so the team feels supported?"],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience."
    },
    "Encourager": {
        "overview": "This staff member communicates primarily as an Encourager, leading with warmth, optimism, and emotional intelligence.",
        "supervising": "Connect relationally before diving into tasks. Validate their emotional labor. Frame criticism around professional growth.",
        "struggle_bullets": ["Avoidance of conflict", "Disorganization", "Prioritizing being liked", "Emotional exhaustion"],
        "coaching": ["How can you deliver this hard news while remaining kind?", "Are we prioritizing popularity over effectiveness?", "What boundaries do you need to set?"],
        "advancement": "Help them master the operational side. Challenge them to see clarity and accountability as kindness."
    },
    "Facilitator": {
        "overview": "This staff member communicates primarily as a Facilitator, leading by listening, gathering perspectives, and seeking fairness.",
        "supervising": "Give them time to process. Ask for observations explicitly. Validate fairness but push for decisions.",
        "struggle_bullets": ["Analysis paralysis", "Passive-aggressiveness", "Saying 'it's fine' when it isn't", "Getting stuck in the middle"],
        "coaching": ["If you had to decide right now, what would you do?", "What is the cost of waiting?", "Where are you holding tension?"],
        "advancement": "Encourage them to be more vocal and decisive. Help them be assertive without being aggressive."
    },
    "Tracker": {
        "overview": "This staff member communicates primarily as a Tracker, leading with details, data, and systems.",
        "supervising": "Provide clear expectations. Respecting their systems builds trust. Explain the 'why' behind changes.",
        "struggle_bullets": ["Rigidity/Perfectionism", "Getting stuck in weeds", "Coming across as cold", "Prioritizing policy over people"],
        "coaching": ["Does this detail change the outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the big picture goal?"],
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

# Fetch data once
staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# TABS
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
            def reset_t1():
                st.session_state.t1_staff_select = None

            staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            selected_staff_name = st.selectbox(
                "Select Staff Member", 
                options=list(staff_options.keys()), 
                index=None, 
                key="t1_staff_select",
                placeholder="Choose a staff member..."
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
                st.success(f"Guide generated for {m_name}")
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    st.write("Select multiple staff members to analyze the culture of a specific unit or team.")
    
    def reset_t2():
        st.session_state.t2_team_select = []

    if not df.empty:
        team_selection = st.multiselect("Build your Team", df['name'].tolist(), key="t2_team_select")
        
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Communication Mix")
                comm_counts = team_df['p_comm'].value_counts()
                fig_team_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4)
                st.plotly_chart(fig_team_comm, use_container_width=True)
                
                if not comm_counts.empty:
                    dominant_style = comm_counts.idxmax()
                    dom_pct = comm_counts.max() / len(team_df)
                    if dom_pct > 0.5:
                        st.warning(f"⚠️ **Echo Chamber Risk:** {int(dom_pct*100)}% of this team are **{dominant_style}s**.")
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                fig_team_mot = px.bar(x=mot_counts.index, y=mot_counts.values)
                st.plotly_chart(fig_team_mot, use_container_width=True)
                if "Growth" in mot_counts and mot_counts["Growth"] > 1: st.success("💡 **High Growth Energy:** This team will love pilots and new initiatives.")
                if "Connection" in mot_counts and mot_counts["Connection"] > 1: st.info("💡 **High Connection Energy:** This team needs time to process emotions together.")
            
            st.markdown("---")
            st.button("Clear Team Selection", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    st.write("Select two staff members who are struggling to collaborate.")
    
    def reset_t3():
        st.session_state.p1 = None
        st.session_state.p2 = None

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Staff Member A", df['name'].unique(), index=None, key="p1", placeholder="Select first person...")
        with c2:
            p2_name = st.selectbox("Staff Member B", df['name'].unique(), index=None, key="p2", placeholder="Select second person...")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            st.divider()
            st.subheader(f"The Clash: {p1['p_comm']} vs. {p2['p_comm']}")
            
            style1 = p1['p_comm']
            style2 = p2['p_comm']
            key = "-".join(sorted([style1, style2]))
            
            if style1 == style2:
                st.warning("Same-Style Conflict: These two are likely clashing because they are too similar (fighting for airtime) or amplifying each other's weaknesses.")
            elif key in CONFLICT_SCRIPTS:
                script = CONFLICT_SCRIPTS[key]
                st.info(f"**Root Tension:** {script['tension']}")
                
                if 'mediator_guide' in script:
                    with st.expander("🛡️ Supervisor Strategy (How to run this meeting)", expanded=True):
                        st.write(script['mediator_guide'])
                        
                        st.markdown("**✅ Pre-Meeting Checklist:**")
                        for item in script['prep']:
                            st.markdown(f"- {item}")
                        
                        st.markdown("**📋 Meeting Protocol:**")
                        for item in script['protocol']:
                            st.markdown(f"- {item}")
                
                st.divider()
                st.markdown("#### 🗣️ What to say to them individually:")
                
                if style1 < style2:
                    advice1 = script['advice_a']
                    advice2 = script['advice_b']
                    script1 = script['script_a']
                    script2 = script['script_b']
                else:
                    advice1 = script['advice_b']
                    advice2 = script['advice_a']
                    script1 = script['script_b']
                    script2 = script['script_a']
                
                col_x, col_y = st.columns(2)
                with col_x:
                    st.markdown(f"**To {p1_name} ({style1}):**")
                    st.info(f"\"{advice1}\"")
                    st.markdown(f"*Sample Line:* \"{script1.split(': ', 1)[1]}\"")
                with col_y:
                    st.markdown(f"**To {p2_name} ({style2}):**")
                    st.info(f"\"{advice2}\"")
                    st.markdown(f"*Sample Line:* \"{script2.split(': ', 1)[1]}\"")
            
            st.markdown("---")
            st.button("Reset Conflict Tool", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    st.write("Analyze readiness for promotion.")
    
    def reset_t4():
        st.session_state.career = None
        st.session_state.career_target = None

    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select candidate...")
        with col_b:
            target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select target role...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({style})")
            st.markdown(f"**Target:** {target_role}")
            
            path_data = CAREER_PATHWAYS.get(style, {}).get(target_role)
            
            if path_data:
                st.info(f"💡 **The Core Shift:** {path_data['shift']}")
                st.markdown(f"**Why it's hard for a {style}:** {path_data['why']}")
                
                st.divider()
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                    
                    if 'supervisor_focus' in path_data:
                        st.warning(f"👀 **What to Watch For:** {path_data['supervisor_focus']}")
                        
                with c2:
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
            fig_org_comm = px.pie(df, names='p_comm', color='p_comm', color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'})
            st.plotly_chart(fig_org_comm, use_container_width=True)
        with c2:
            st.subheader("Motivation Drivers")
            fig_org_mot = px.bar(df, x='p_mot', color='p_mot')
            st.plotly_chart(fig_org_mot, use_container_width=True)
        
        st.divider()
        if 'role' in df.columns:
            role_breakdown = pd.crosstab(df['role'], df['p_comm'])
            st.dataframe(role_breakdown.style.background_gradient(cmap="Blues"), use_container_width=True)
    else:
        st.warning("No data available.")
