import streamlit as st
from fpdf import FPDF

# --- Configuration ---
st.set_page_config(page_title="Supervisor Guide Generator", page_icon="📑", layout="centered")

# --- Data (Shared with main app, plus specific supervisor content) ---
COMM_PROFILES = {
    "Director": {
        "overview": "Moves quickly toward action. In high-pressure moments, steps in, organizes people, and pushes for clear decisions.",
        "supervising": "Be direct and concise. They respect competence and decisiveness. Don't micromanage; give them the 'what' and let them figure out the 'how'.",
        "struggle": "May become blunt, controlling, or impatient. Might talk over others or rush decisions without building consensus.",
        "coaching": ["What is the risk of moving this fast?", "Who haven't we heard from yet?", "How can you frame this directive so the team feels supported rather than controlled?"],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience and consensus-building."
    },
    "Encourager": {
        "overview": "Brings warmth, optimism, and emotional presence. Notices when people need encouragement and acts as the team's emotional glue.",
        "supervising": "Connect relationally before diving into tasks. Validate their feelings and impact. Criticism can feel personal, so frame it around growth.",
        "struggle": "May avoid hard truths to keep the peace. Might talk too much or become disorganized under stress.",
        "coaching": ["How can you deliver this hard news while staying kind?", "What boundaries do you need to set to protect your energy?", "Are we prioritizing popularity over effectiveness here?"],
        "advancement": "Help them master the operational/administrative side of leadership so their high EQ is backed by reliability."
    },
    "Facilitator": {
        "overview": "Listens deeply, notices perspectives, and helps people stay at the table. Cares about process and fairness.",
        "supervising": "Give them time to process. Ask for their observations—they see things you miss. Encourage them to take a stand.",
        "struggle": "May delay decisions or absorb tension silently. Might say 'it's fine' when it isn't to avoid conflict.",
        "coaching": ["If you had to decide right now, what would you do?", "What is the cost of waiting for total consensus?", "Where are you holding tension for the team?"],
        "advancement": "Encourage them to be more vocal and decisive in crises. Help them see that clarity is a form of kindness."
    },
    "Tracker": {
        "overview": "Notices patterns, details, and gaps. Keeps routines and documentation on track to protect the team from risk.",
        "supervising": "Provide clear expectations and structure. They need to know the 'why' and the specific 'how'. respecting their systems builds trust.",
        "struggle": "May become rigid, critical, or get stuck in the weeds. Can come across as inflexible when stressed.",
        "coaching": ["Does this detail change the outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the big picture goal here?"],
        "advancement": "Help them delegate details so they can focus on strategy. Teach them to tolerate 'good enough' in non-critical areas."
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "summary": "Energized by developing new skills and stretch assignments. Stagnation is draining.",
        "motivating": "Give them problems to solve, not just tasks to do. Provide regular feedback on their development.",
        "support": "Connect their daily work to their career trajectory. Sponsor them for training or special projects.",
        "killers": "Repetitive tasks with no learning curve. Being ignored.",
        "thriving": "Proactive, asking questions, seeking feedback, mentoring others.",
    },
    "Purpose": {
        "summary": "Driven by meaning and alignment with values. Wants work to match beliefs about justice and care.",
        "motivating": "Connect every directive to the mission. Explain the 'why' behind policies.",
        "support": "Create space for ethical questions. Validate their passion for the youth.",
        "killers": "Cynicism, bureaucratic red tape, feeling like 'just a number'.",
        "thriving": "Passionate advocate, high integrity, deeply committed to youth outcomes.",
    },
    "Connection": {
        "summary": "Energized by strong relationships and community. Belonging fuels resilience.",
        "motivating": "Prioritize team cohesion. Recognize shared wins. Check in on them personally.",
        "support": "Ensure they aren't isolated. facilitate team bonding moments.",
        "killers": "Isolation, unresolved team conflict, cold leadership.",
        "thriving": "Collaborative, morale-booster, highly empathetic and supportive.",
    },
    "Achievement": {
        "summary": "Cares about clear goals and concrete progress. Wants to see the score.",
        "motivating": "Set clear, measurable goals. Celebrate milestones visibly.",
        "support": "Remove blockers. Give them autonomy to reach the target.",
        "killers": "Vague expectations, shifting goalposts, lack of recognition.",
        "thriving": "Efficient, goal-oriented, reliable, high output.",
    }
}

INTEGRATED_PROFILES = {
    # Generic fallback generator if specific combo isn't hardcoded
    "Generic": {
        "title": "Integrated Leader",
        "summary": "A leader blending communication style with specific motivational drivers.",
        "strengths": ["Unique perspective", "Balanced approach"],
        "intervention": "Align tasks with their motivation while coaching their communication gaps."
    }
}

# --- Helper Function: Clean Text for PDF ---
def clean_text(text):
    if not text: return ""
    replacements = {'\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2013': '-', '—': '-'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- PDF Generator ---
def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    
    # Colors
    blue = (1, 91, 173)
    grey = (100, 100, 100)
    black = (0, 0, 0)
    
    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} Communicator x {p_mot} Motivation"), ln=True, align='C')
    pdf.ln(10)

    # Data Retrieval
    c_data = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m_data = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])
    
    # ---------------------------------------------------------
    # 12 HEADINGS
    # ---------------------------------------------------------
    
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

    # 1. Communication Profile
    add_section("1. Communication Profile", c_data['overview'])

    # 2. Supervising Their Communication
    add_section("2. Supervising Their Communication", c_data['supervising'])

    # 3. Motivation Profile
    add_section("3. Motivation Profile", m_data['summary'])

    # 4. Motivating This Program Supervisor
    add_section("4. Motivating This Person", m_data['motivating'])

    # 5. Integrated Leadership Profile
    # Constructing a dynamic summary
    integrated_summary = f"This leader leads with {p_comm} energy (focused on {c_data['overview'].split('.')[0].lower()}) and is fueled by {p_mot} (seeking {m_data['summary'].split('.')[0].lower()}). They are at their best when they can communicate via {p_comm} channels to achieve {p_mot} goals."
    add_section("5. Integrated Leadership Profile", integrated_summary)

    # 6. How You Can Best Support Them
    add_section("6. How You Can Best Support Them", m_data['support'])

    # 7. What They Look Like When Thriving
    add_section("7. What They Look Like When Thriving", m_data['thriving'])

    # 8. What They Look Like When Struggling
    add_section("8. What They Look Like When Struggling", c_data['struggle'])

    # 9. Supervisory Interventions
    intervention = f"When struggling, they likely need you to validate their {p_mot} needs first, then coach them on the impact of their {p_comm} style. If they are stuck, check if they are feeling {m_data['killers'].split(',')[0]}."
    add_section("9. Supervisory Interventions", intervention)

    # 10. What You Should Celebrate
    celebrate = f"Celebrate moments where they use their {p_comm} style to drive {p_mot} outcomes. Specifically, acknowledge when they: {m_data['thriving']}."
    add_section("10. What You Should Celebrate", celebrate)

    # 11. Coaching Questions
    add_section("11. Coaching Questions", c_data['coaching'])

    # 12. Helping Them Prepare for Advancement
    add_section("12. Helping Them Prepare for Advancement", c_data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

# --- Main UI ---

st.title("Supervisor Guide Generator")
st.markdown("Generate a comprehensive 12-point PDF guide for supervisors based on assessment results.")

with st.form("generator_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Staff Name")
        role = st.selectbox("Role", ["Program Supervisor", "Shift Supervisor", "YDP"])
    with col2:
        p_comm = st.selectbox("Primary Communication", ["Director", "Encourager", "Facilitator", "Tracker"])
        p_mot = st.selectbox("Primary Motivation", ["Growth", "Purpose", "Connection", "Achievement"])
        
    # Optional Secondaries (for future expansion, currently not used heavily in the 12-point guide to keep it focused)
    with st.expander("Secondary Traits (Optional)"):
        s_comm = st.selectbox("Secondary Communication", ["None", "Director", "Encourager", "Facilitator", "Tracker"])
        s_mot = st.selectbox("Secondary Motivation", ["None", "Growth", "Purpose", "Connection", "Achievement"])

    submitted = st.form_submit_button("Generate Guide PDF")

if submitted:
    if not name:
        st.error("Please enter a name.")
    else:
        pdf_bytes = create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot)
        st.success(f"Guide generated for {name}!")
        st.download_button(
            label="Download PDF Guide",
            data=pdf_bytes,
            file_name=f"Supervisor_Guide_{name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
