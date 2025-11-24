import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF

# --- Configuration ---
st.set_page_config(page_title="Elmcrest Supervisor Dashboard", page_icon="📊", layout="wide")

# --- Constants ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- Expanded Content Dictionaries ---

COMM_PROFILES = {
    "Director": {
        "overview": "The Director communicates with brevity, speed, and a focus on action. In high-pressure moments, they naturally step in to fill leadership vacuums, organizing people and pushing for clear decisions. They value competence and results over process or feelings.",
        "supervising": "Be direct, concise, and outcome-focused. They respect leaders who get to the point. Do not micromanage; define the 'what' (the goal) clearly, but give them autonomy on the 'how'. When giving feedback, don't 'sandwich' it—give it straight. They often view debate as a healthy way to get to the best answer, not as conflict.",
        "struggle": "Under stress, Directors may become blunt, controlling, or impatient. They might talk over others, ignore dissenting opinions, or rush decisions without building necessary consensus. They may perceive legitimate questions as resistance or incompetence.",
        "coaching": [
            "I noticed we moved very fast on that decision. What are the risks of not hearing from the rest of the team first?",
            "How can you frame this directive so the team feels supported rather than just commanded?",
            "Who haven't we heard from yet? What might they be seeing that we are missing?"
        ],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience and consensus-building. Their next level of growth is learning to bring the team along with them, rather than just dragging them across the finish line."
    },
    "Encourager": {
        "overview": "The Encourager brings warmth, optimism, and high emotional intelligence to the team. They communicate through stories and relationships, often acting as the 'glue' that holds the unit together during tough shifts. They prioritize morale and harmony.",
        "supervising": "Connect relationally before diving into tasks; ask 'How are you?' and mean it. Validate their emotional labor—they often carry the weight of the team's feelings. Criticism can feel intensely personal to them, so frame feedback clearly around professional growth and specific behaviors, reassuring them of their value to the team.",
        "struggle": "Under stress, they may avoid hard truths or delay necessary conflict to keep the peace. They might talk excessively when nervous or become disorganized. They may prioritize being liked over being effective, or struggle to enforce boundaries with staff or youth.",
        "coaching": [
            "How can you deliver this difficult message clearly while still remaining kind?",
            "Are we prioritizing popularity over effectiveness in this situation?",
            "What boundaries do you need to set right now to protect your own energy and focus?"
        ],
        "advancement": "Help them master the operational and administrative sides of leadership so their high EQ is backed by unshakable reliability. Challenge them to see 'clarity' and 'accountability' as forms of kindness, not opposition to it."
    },
    "Facilitator": {
        "overview": "The Facilitator is a deep listener who seeks to understand all perspectives before acting. They care deeply about process, fairness, and ensuring everyone has a voice. They are calm, steady, and excellent at de-escalating tense interpersonal dynamics.",
        "supervising": "Give them time to process information before demanding a decision. Ask for their observations explicitly—they often see team dynamics that others miss but won't share unless invited. Validate their desire for fairness, but help them distinguish between 'consensus' and 'unanimity'.",
        "struggle": "Under stress, they may fall into 'analysis paralysis,' delaying decisions while trying to accommodate everyone. They might absorb team tension silently until they burn out. They may say 'it's fine' when it isn't to avoid immediate conflict, letting issues fester.",
        "coaching": [
            "If you had to make a decision right now with only 80% of the information, what would it be?",
            "What is the cost to the team of waiting for total consensus on this?",
            "Where are you holding tension for the team that you need to release or address directly?"
        ],
        "advancement": "Encourage them to be more vocal and decisive during crises. Help them see that they can be assertive without being aggressive. Their growth lies in becoming a leader who can make the tough call even when not everyone agrees."
    },
    "Tracker": {
        "overview": "The Tracker communicates through details, data, and systems. They notice gaps, patterns, and risks that others overlook. They view rules and routines not as constraints, but as the safety net that protects staff and youth from chaos and liability.",
        "supervising": "Provide clear expectations, structure, and written follow-up. They need to know the 'why' (logic) and the specific 'how' (process). Respecting their systems builds trust; disregarding details erodes it. When changing things, give them time to map out the new workflow.",
        "struggle": "Under stress, they may become rigid, critical, or perfectionistic. They might get 'stuck in the weeds,' focusing on minor compliance details while missing the bigger emotional picture. They can come across as cold or inflexible to youth in crisis.",
        "coaching": [
            "Does this specific detail change the safety or outcome of the situation?",
            "How can we meet the standard here while keeping the relationship with the youth warm?",
            "What is the big picture goal, and are we sacrificing it for a minor procedural win?"
        ],
        "advancement": "Help them delegate the details so they can focus on strategy and people development. Teach them to distinguish between 'mission-critical' compliance and 'preference,' helping them tolerate 'good enough' in non-essential areas."
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "overview": "The Learner/Builder. This person is energized by progress—both their own and others'. They view the role not as a job, but as a classroom.",
        "motivating": "Feed their curiosity. Give them problems to solve, not just tasks to execute. Provide regular, specific feedback on their skill development. Frame new initiatives as 'pilots' or 'learning opportunities.'",
        "support": "Connect their daily work to their long-term career trajectory. Sponsor them for training, certifications, or special projects. Ask: 'What are you learning right now?'",
        "killers": "Repetitive tasks with no learning curve. Being micromanaged in a way that prevents experimentation. Feeling stagnant or that there is 'nowhere to go.'",
        "thriving": "Proactive, asking 'why' and 'how,' seeking feedback, mentoring others, volunteering for new responsibilities.",
        "celebrate": "Celebrate their acquisition of new skills. Acknowledge when they take a risk to try something new, even if it isn't perfect. Praise their adaptability."
    },
    "Purpose": {
        "overview": "The Mission Keeper. This person is driven by meaning, values, and alignment. They need to know that their work makes a tangible difference in the lives of youth.",
        "motivating": "Connect every directive back to the mission: 'We are doing X because it helps the youth achieve Y.' Be transparent about the 'why' behind policies. Invite their input on ethical or care-related decisions.",
        "support": "Create space for them to voice ethical concerns or advocacy. Validate their passion for the youth, even when you have to say no to a request. Ensure they see the 'human' impact of their work.",
        "killers": "Cynicism, excessive bureaucratic red tape, feeling like 'just a number,' or perceiving leadership decisions as uncaring or unjust.",
        "thriving": "Passionate advocate for youth, high integrity, deeply committed to outcomes, willing to go the extra mile for a kid.",
        "celebrate": "Celebrate moments where their work directly impacted a youth's life. Share specific stories of their impact. Publicly acknowledge their integrity and advocacy."
    },
    "Connection": {
        "overview": "The Community Builder. This person is energized by strong relationships, team cohesion, and a sense of belonging. They work for the 'who,' not just the 'what.'",
        "motivating": "Prioritize team cohesion. Recognize shared wins rather than just individual ones. Check in on them personally before talking business. Allow time for team processing.",
        "support": "Ensure they aren't working in isolation. Facilitate team bonding moments. Be a warm, accessible presence. When the team is splintered, they will feel it most; support them by addressing team conflict quickly.",
        "killers": "Isolation, working alone for long stretches, unresolved team conflict, or cold/impersonal interactions with leadership.",
        "thriving": "Collaborative, morale-booster, highly empathetic, supportive of peers, creates a 'family' atmosphere on the unit.",
        "celebrate": "Celebrate their contributions to team culture. Acknowledge when they support a struggling peer. Praise them for holding the team together during hard times."
    },
    "Achievement": {
        "overview": "The Results Architect. This person cares about clarity, goals, and concrete progress. They want to know the score and feel satisfied when they win.",
        "motivating": "Set clear, measurable goals. Use checklists, dashboards, or metrics to show progress. Be definitive about what 'success' looks like. Give them autonomy to reach the target once it's set.",
        "support": "Remove blockers that prevent them from finishing tasks. Protect their time from unnecessary meetings. Give them the resources to be efficient.",
        "killers": "Vague expectations, constantly shifting goalposts, lack of recognition for completed work, or inefficiency that wastes their time.",
        "thriving": "Efficient, goal-oriented, reliable, high output, organized, drives projects to completion.",
        "celebrate": "Celebrate the completion of projects and the hitting of metrics. Give public recognition for reliability and high standards. 'You said you'd do it, and you did it.'"
    }
}

# --- Helper Function: Clean Text for PDF ---
def clean_text(text):
    if not text: return ""
    text = str(text)
    # Replace common windows-1252 chars with ascii equivalents or latin-1 safe chars
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', 
        '\u2013': '-', '\u2014': '-', '\u2026': '...',
        '—': '-', '–': '-', '“': '"', '”': '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    
    # Final safety net: encode to latin-1, replacing errors with ?
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
    
    # Colors
    blue = (1, 91, 173)
    black = (0, 0, 0)
    gray = (100, 100, 100)
    
    # HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
    # Helper for content blocks
    def add_section(title, content):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*blue)
        pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        
        if isinstance(content, list):
            for item in content:
                pdf.multi_cell(0, 6, clean_text(f"- {item}"))
        else:
            pdf.multi_cell(0, 6, clean_text(content))
        pdf.ln(4)

    # Retrieve Data
    c_data = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m_data = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    # 1. Communication Profile
    add_section(f"1. Communication Profile: {p_comm}", c_data['overview'])

    # 2. Supervising Their Communication
    add_section("2. Supervising Their Communication", c_data['supervising'])

    # 3. Motivation Profile
    add_section(f"3. Motivation Profile: {p_mot}", m_data['overview'])

    # 4. Motivating This Program Supervisor
    add_section("4. Motivating This Staff Member", m_data['motivating'])

    # 5. Integrated Leadership Profile
    # Dynamic synthesis of Comm + Motiv
    integrated_text = (
        f"This staff member leads with {p_comm} energy (focused on {c_data['overview'].split('.')[0].lower()}) "
        f"and is fueled by a drive for {p_mot} (seeking {m_data['overview'].split('.')[0].lower()}). "
        f"They are at their best when they can communicate via {p_comm} channels to achieve {p_mot} outcomes."
    )
    add_section("5. Integrated Leadership Profile", integrated_text)

    # 6. How You Can Best Support Them
    add_section("6. How You Can Best Support Them", m_data['support'])

    # 7. What They Look Like When Thriving
    add_section("7. What They Look Like When Thriving", m_data['thriving'])

    # 8. What They Look Like When Struggling
    add_section("8. What They Look Like When Struggling", c_data['struggle'])

    # 9. Supervisory Interventions
    # Dynamic synthesis of Stress (Comm) + Killers (Motiv)
    killer_hint = m_data['killers'].split('.')[0]
    intervention_text = (
        f"When struggling, they likely need you to validate their need for {p_mot} first (addressing feelings of {killer_hint.lower()}), "
        f"and then coach them on the impact of their {p_comm} style under stress. "
        f"Connect the feedback to their desire for {p_mot} to get buy-in."
    )
    add_section("9. Supervisory Interventions", intervention_text)

    # 10. What You Should Celebrate
    add_section("10. What You Should Celebrate", m_data['celebrate'])

    # 11. Coaching Questions
    add_section("11. Coaching Questions", c_data['coaching'])

    # 12. Helping Them Prepare for Advancement
    add_section("12. Helping Them Prepare for Advancement", c_data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

# --- Main UI ---

st.title("Supervisor & Admin Dashboard")
st.markdown("View staff assessments and generate comprehensive supervisory guides.")

# Tabs for Manual Entry vs Database
tab1, tab2 = st.tabs(["📚 Database (Auto-Fill)", "✏️ Manual Entry"])

with tab1:
    col_a, col_b = st.columns([0.8, 0.2])
    with col_a:
        st.write("Select a staff member from the database to auto-generate their guide.")
    with col_b:
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
    staff_list = fetch_staff_data()
    
    if staff_list:
        # Create a nice display string for the dropdown
        # We use a dictionary to map the display string back to the full data object
        staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
        
        selected_staff_name = st.selectbox("Select Staff Member", options=list(staff_options.keys()))
        
        if selected_staff_name:
            data = staff_options[selected_staff_name]
            
            # Display Quick Stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Role", data['role'])
            col2.metric("Primary Comm", data['p_comm'])
            col3.metric("Primary Motiv", data['p_mot'])
            
            if data['s_comm'] and data['s_comm'] != 'None':
                st.caption(f"Secondary Traits: {data['s_comm']} (Comm) / {data['s_mot']} (Motiv)")
            
            st.markdown("###")
            if st.button("Generate Guide for " + data['name'], type="primary"):
                pdf_bytes = create_supervisor_guide(
                    data['name'], data['role'], 
                    data['p_comm'], data['s_comm'], 
                    data['p_mot'], data['s_mot']
                )
                st.success("Guide Generated Successfully!")
                st.download_button(
                    label="Download PDF Guide",
                    data=pdf_bytes,
                    file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("No data found in database yet. Ensure the Google Script is deployed correctly.")

with tab2:
    st.write("Manually enter profile details to generate a guide.")
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
            st.download_button(
                label="Download PDF Guide",
                data=pdf_bytes,
                file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
