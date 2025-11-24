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

CONFLICT_SCRIPTS = {
    "Director-Encourager": {
        "tension": "The Efficiency vs. Humanity Gap. The Director feels the Encourager is 'too soft' or wasting time on feelings. The Encourager feels the Director is 'mean' or steamrolling the team.",
        "advice_a": "Your drive for efficiency is hurting the relationship. If you crush their morale, they will disengage. Stop interrupting and acknowledge the *feeling* before you fix the *problem*.",
        "advice_b": "The Director isn't trying to be mean; they are stressed by the lack of progress. Be direct. Say, 'I can move faster, but I need you to listen to my concern about the team's morale first.'",
        "mediator_guide": "You must act as the Translator. The Director speaks 'Task'; the Encourager speaks 'Relationship'. Frame the Encourager's feelings as 'data' the Director needs to solve the problem. Frame the Director's speed as a way to reduce the team's stress (by solving the issue). Warn the Director: 'If you win the argument but lose the relationship, you fail.'"
    },
    "Director-Facilitator": {
        "tension": "The Speed vs. Process Clash. The Director wants to decide *now* ('Ready, Fire, Aim'); the Facilitator wants to hear from everyone first ('Ready, Aim, Aim, Aim').",
        "advice_a": "You are moving too fast for them. If you force a decision now, you get compliance, not buy-in. Ask: 'What specific perspective are we missing?' then set a deadline.",
        "advice_b": "Silence looks like agreement to a Director. You must speak up. Say: 'I am not stalling, I am preventing a mistake. Give me 10 minutes to outline the risk.'",
        "mediator_guide": "You must manage the Clock. The Director hits the gas; the Facilitator hits the brakes. Your job is to set the speed limit. Give the Facilitator a specific deadline for processing (e.g., 'You have 24 hours to gather input'). Tell the Director: 'We will move at [Time], but not before.' This gives the Facilitator safety and the Director certainty."
    },
    "Director-Tracker": {
        "tension": "The Big Picture vs. The Weeds. The Director says 'Just get it done.' The Tracker asks 'But how? What about regulation X?'. The Director feels blocked; the Tracker feels ignored.",
        "advice_a": "They aren't being difficult; they are protecting you from liability. Stop dismissing the details. Ask: 'What is the critical blocker preventing us from moving?'",
        "advice_b": "The Director doesn't need every detail. Start with the solution, not the problem. Say: 'We can hit that deadline, but we have to skip step B. Do you agree?'",
        "mediator_guide": "Align on the 'Why' vs 'How'. Affirm that the Director owns the vision (Why) and the Tracker owns the execution (How). Ensure the Director respects the Tracker's reality check ('Is this legal/safe?'). Ensure the Tracker isn't using details to passively block the vision. Ask the Tracker: 'How can we get to 'Yes' safely?'"
    },
    "Encourager-Tracker": {
        "tension": "Heart vs. Head. The Encourager bends rules to help the kid/staff. The Tracker cites the policy manual. The Tracker thinks the Encourager is chaotic; the Encourager thinks the Tracker is cold.",
        "advice_a": "Rules aren't just red tape; they create the safety container for your relationship. If you are inconsistent, you aren't being kind, you're being confusing.",
        "advice_b": "You are right about the rule, but you are losing the relationship. Validate the intent ('I know you want to help the kid') before correcting the method.",
        "mediator_guide": "Connect Structure to Safety. Show the Encourager that 'Structure (Tracker) protects the Relationship.' Show the Tracker that 'Rapport (Encourager) buys the influence to enforce the rules.' Challenge them to co-lead: The Tracker builds the plan; the Encourager sells it to the team."
    },
    "Encourager-Facilitator": {
        "tension": "The Nice-Off. Both want harmony, but the Facilitator focuses on fairness while the Encourager focuses on feelings. Decisions can stall indefinitely because neither wants to upset anyone.",
        "advice_a": "You are prioritizing the person in front of you over the fairness of the whole group. Step back.",
        "advice_b": "You are prioritizing the process over the immediate emotional need. Step in.",
        "mediator_guide": "Force the Friction. Both parties are conflict-avoidant. As the supervisor, you must put the elephant in the room. Ask: 'What are we *not* saying right now because we want to be nice?' Push them to prioritize 'Respect' over 'Harmony.' Respect means telling the truth even when it's uncomfortable."
    },
    "Facilitator-Tracker": {
        "tension": "Analysis Paralysis. Both are cautious. The Facilitator waits for consensus; the Tracker waits for data. Nothing happens. The risk is stagnation.",
        "advice_a": "Consensus doesn't mean unanimity. You have enough votes. Move.",
        "advice_b": "You have enough data. Perfection is the enemy of done. Move.",
        "mediator_guide": "Break the Stall. Both act out of a fear of making a mistake (social mistake for Facilitator, technical mistake for Tracker). Absolve them of that fear. Say: 'I am authorizing this decision. If it goes wrong, it is on me.' Then set a hard deadline for action."
    }
}

CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "conversation": "You have high capacity and speed, which is a gift. To succeed as a Shift Supervisor, you have to resist the urge to 'rescue' the shift by doing everything yourself. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless safety dictates otherwise). Their goal is to run the shift entirely through verbal direction and delegation to peers, forcing them to build trust.",
            "supervisor_focus": "Watch for 'Hero Mode'. If you see them jumping in to fix a crisis that their staff could handle, intervene. Pull them back and say, 'Let your team handle this. Coach them, don't save them.'"
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "conversation": "You are excellent at execution within your unit. However, program leadership requires getting buy-in from people you don't supervise (School, Clinical, other cottages). You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment": "Task them with a cross-departmental project (e.g., improving school transitions). Their goal is to interview stakeholders in the School and Clinical teams and present a plan that incorporates *their* feedback, not just the Director's own ideas.",
            "supervisor_focus": "Monitor their patience. If they complain about 'meetings' or 'politics', reframe it: 'That isn't politics; that is relationship building. That is the job now.'"
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
            "conversation": "You react beautifully to problems. The next level requires you to prevent them 6 months in advance. You need to shift from reliance on your force of will to reliance on sustainable systems.",
            "assignment": "Have them write a strategic plan for a recurring seasonal issue (e.g., summer break structure). It must rely on data and systems, not just 'working harder'.",
            "supervisor_focus": "Check their horizon. Are they talking about today's crisis or next month's risk? Push them to think longer term."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Guardian'.",
            "conversation": "Your empathy is your superpower, but if you avoid hard conversations to keep the peace, you create an unsafe environment. The team needs you to be a 'Guardian' of the standard. Holding people accountable is actually the kindest thing you can do, because it ensures clarity and safety for everyone.",
            "assignment": "Have them lead a policy refresher or 'reset' meeting with the team regarding a specific routine that has slipped. Coach them beforehand on how to be firm about the standard while remaining warm in their tone.",
            "supervisor_focus": "Watch for 'Apology Language'. If they give a directive and then apologize for it ('Sorry guys, I have to ask you to do this...'), correct them immediately. 'Do not apologize for leading.'"
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "conversation": "You create an amazing emotional climate. To lead a program, that climate must be backed by unshakeable structure. You need to master the 'boring' parts of leadership—budgets, schedules, audits—because those are the tools that protect your team from burnout.",
            "assignment": "Assign them ownership of a compliance audit or a schedule overhaul. Challenge them to present the data and the rationale, ensuring they don't just rely on personality to sell the change.",
            "supervisor_focus": "Inspect what you expect. Encouragers can be disorganized. Help them build a personal organization system so their administrative balls don't drop."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "conversation": "You naturally carry the emotions of your people. At the manager level, the weight is too heavy to carry alone. Your growth edge is learning to set emotional boundaries—caring deeply about the person without taking responsibility for their feelings.",
            "assignment": "Have them manage a resource allocation conflict (e.g., denying a budget request or staffing request) where they have to say 'No' clearly, explain the business reason, and withstand the disappointment of the staff member.",
            "supervisor_focus": "Watch for burnout. If they look exhausted, they are likely over-functioning emotionally. Ask: 'Who are you trying to save right now?'"
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Peer' to 'Decider'.",
            "conversation": "You are gifted at ensuring everyone feels heard. As a Shift Sup, there will be moments where consensus is impossible and safety requires speed. You need to get comfortable making the '51% decision'—listening to input, but making the call even if 49% disagree.",
            "assignment": "Put them in charge of a time-sensitive crisis drill or transition. Debrief afterwards: 'Where did you hesitate? How did it feel to give a direct command?' Affirm their authority.",
            "supervisor_focus": "Push for speed. When they ask 'What do you think?', throw it back: 'You tell me. You're the leader.' Force them to exercise their judgment muscle."
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "conversation": "You are a great stabilizer. But a Program Supervisor must also be a driver. Instead of just mediating the team's ideas, we need you to inject your own vision. Don't just wait to see what the group wants; tell us where you think the group needs to go.",
            "assignment": "Ask them to propose a new initiative for the program culture. They must present it to the team not as a 'discussion' but as a direction, practicing assertive leadership.",
            "supervisor_focus": "Watch for 'The Buffer'. Are they just passing messages between staff and admin? Challenge them to take a stand on issues."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
            "conversation": "Fair process is vital, but sometimes it yields poor results. At this level, you must prioritize the outcome over the comfort of the process. You need to be willing to disrupt the harmony to achieve the mission.",
            "assignment": "Task them with implementing a necessary but unpopular policy change. Coach them on how to listen to complaints without backtracking on the decision.",
            "supervisor_focus": "Monitor their tolerance for conflict. If they start delaying a necessary change to avoid upset, step in. 'The upset is inevitable; the delay is optional.'"
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Executor' to 'Overseer'.",
            "conversation": "You are brilliant at the details. But you cannot track every detail personally at this level without burning out or micromanaging. Your growth is trusting your team. You have to let them do the checklist, even if they do it differently than you would.",
            "assignment": "The 'Hands-Off' Day. Assign them to supervise a complex task (like an intake or a room search) where they are strictly prohibited from touching any paperwork themselves. They must guide a peer to do it.",
            "supervisor_focus": "Watch for micromanagement. If they are re-doing someone else's work, stop them. 'If it is 80% right, it is right enough. Move on.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "conversation": "You excel when the rules are clear. Program leadership is full of gray areas where the policy manual doesn't have an answer. You need to develop your intuition and judgment to navigate complex family or youth dynamics that don't fit the spreadsheet.",
            "assignment": "Have them handle a complex parent complaint or a unique youth restriction plan where standard rules don't apply. Guide them to make a principle-based decision rather than a rule-based one.",
            "supervisor_focus": "Challenge their rigidity. If they say 'We can't do that, it's not the rule', ask 'What is the *intent* of the rule? Can we meet the intent a different way?'"
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "conversation": "Culture eats strategy (and checklists) for breakfast. If you prioritize efficiency over connection, you will have a compliant but brittle organization. You need to invest as much energy in 'how people feel' as 'what people do'.",
            "assignment": "Task them with a retention or morale initiative. Success is measured not by a completed task list, but by staff feedback and engagement scores.",
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
    
    # Retrieve Data
    c_data = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m_data = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    # --- Content Sections ---

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

    # 1. Communication Profile
    add_heading(f"1. Communication Profile: {p_comm}")
    add_body(c_data['overview'])

    # 2. Supervising Their Communication
    add_heading("2. Supervising Their Communication")
    add_body(c_data['supervising'])

    # 3. Motivation Profile
    add_heading(f"3. Motivation Profile: {p_mot}")
    add_body(m_data['overview'])

    # 4. Motivating This Program Supervisor
    add_heading("4. Motivating This Staff Member")
    add_body(m_data['motivating'])

    # 5. Integrated Leadership Profile
    integrated_text = (
        f"This staff member leads with {p_comm} energy (focused on {c_data['overview'].split('leads with')[0] if 'leads with' in c_data['overview'] else 'their style'}) "
        f"and is fueled by a drive for {p_mot}. "
        f"They are at their best when they can communicate via {p_comm} channels to achieve {p_mot}-aligned outcomes."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    # 6. How You Can Best Support Them
    add_heading("6. How You Can Best Support Them")
    add_body(m_data['support'])

    # 7. What They Look Like When Thriving
    add_heading("7. What They Look Like When Thriving")
    add_bullets(m_data['thriving_bullets'])

    # 8. What They Look Like When Struggling
    add_heading("8. What They Look Like When Struggling")
    add_bullets(c_data['struggle_bullets'])

    # 9. Supervisory Interventions
    add_heading("9. Supervisory Interventions")
    intervention_text = (
        f"• Increase structure or flexibility depending on their {p_comm} style.\n"
        f"• Re-establish expectations or reclarify priorities to satisfy their {p_mot} drive.\n"
        f"• {m_data['intervention']}\n"
        f"• Provide emotional support without enabling overextension."
    )
    add_body(intervention_text)

    # 10. What You Should Celebrate
    add_heading("10. What You Should Celebrate")
    celebrate_intro = (
        f"• Their unique {p_comm} leadership strengths\n"
        f"• Their contributions to climate, safety, or structure\n"
        f"• {m_data['celebrate']}"
    )
    add_body(celebrate_intro)

    # 11. Coaching Questions
    add_heading("11. Coaching Questions")
    add_bullets(c_data['coaching'])

    # 12. Helping Them Prepare for Advancement
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
                        if dominant_style == "Director": st.write("Risk: Moving too fast, steamrolling quieter voices. **Correction:** Intentionally invite dissent.")
                        elif dominant_style == "Encourager": st.write("Risk: 'Nice' culture that avoids hard accountability. **Correction:** Standardize review processes.")
                        elif dominant_style == "Facilitator": st.write("Risk: Slow decision making, endless meetings. **Correction:** Set hard deadlines.")
                        elif dominant_style == "Tracker": st.write("Risk: Rigid adherence to rules over relationships. **Correction:** Schedule team bonding time.")
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
                
                # Supervisor Strategy
                if 'mediator_guide' in script:
                    st.markdown(f"#### 🛡️ Supervisor Strategy:\n{script['mediator_guide']}")
                
                st.markdown("#### 🗣️ What to say to them individually:")
                
                if style1 < style2:
                    advice1 = script['advice_a']
                    advice2 = script['advice_b']
                else:
                    advice1 = script['advice_b']
                    advice2 = script['advice_a']
                
                col_x, col_y = st.columns(2)
                with col_x:
                    st.markdown(f"**To {p1_name} ({style1}):**")
                    st.success(f"\"{advice1}\"")
                with col_y:
                    st.markdown(f"**To {p2_name} ({style2}):**")
                    st.success(f"\"{advice2}\"")
            
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
                # Supervisor Focus (New)
                if 'supervisor_focus' in path_data:
                    st.warning(f"👀 **Supervisor Focus (What to Watch):** {path_data['supervisor_focus']}")
                
                st.info(f"💡 **The Core Shift:** {path_data['shift']}")
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                with c2:
                    st.markdown("#### ✅ The Developmental Assignment")
                    st.success(path_data['assignment'])
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
