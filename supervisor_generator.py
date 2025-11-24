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
        "overview": "This staff member communicates primarily as a Director, meaning they lead with the core traits associated with this style—such as clarity, structure, and urgency. This significantly shapes how they interact with their team, youth, families, and you as their supervisor.\n\nThey influence the emotional tone of the program through their natural decisiveness, while also facing challenges that arise under stress. Their communication tendencies affect how comfortable staff feel approaching them, how effectively they redirect youth, and how well they sustain structure during crises.",
        "supervising": "When supervising someone with a Director communication profile, it is important to adapt your approach so they feel supported, understood, and able to use their style effectively without overusing it.\n\nKey strategies include:\n- Matching their level of directness or warmth appropriately.\n- Giving feedback in ways that reinforce their strengths while addressing blind spots.\n- Helping them adjust communication with youth and staff based on situational needs rather than just command-and-control.",
        "struggle_bullets": [
            "Decreased patience or overcommunication of demands",
            "Avoidance of listening or over-assertiveness",
            "Fatigue, irritability, or becoming overly blunt",
            "Rigid enforcement of structure without empathy"
        ],
        "coaching": [
            "I noticed we moved very fast on that decision. What are the risks of not hearing from the rest of the team first?",
            "How can you frame this directive so the team feels supported rather than just commanded?",
            "Who haven't we heard from yet? What might they be seeing that we are missing?"
        ],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience and consensus-building. Their next level of growth is learning to bring the team along with them, rather than just dragging them across the finish line."
    },
    "Encourager": {
        "overview": "This staff member communicates primarily as an Encourager, meaning they lead with warmth, optimism, and high emotional intelligence. This significantly shapes how they build rapport with their team, youth, and families.\n\nThey influence the emotional tone of the program by acting as the 'glue' that holds the team together. Their communication tendencies affect how well staff feel heard, how they de-escalate youth through connection, and how they maintain morale during difficult shifts.",
        "supervising": "When supervising someone with an Encourager profile, it is important to connect relationally before diving into tasks. They need to feel that their emotional labor is seen and valued.\n\nKey strategies include:\n- Validating their feelings and the impact they have on team culture.\n- Framing feedback around professional growth rather than personal failure, as criticism can hit them hard.\n- Helping them set boundaries so they don't burn out from carrying the team's emotional weight.",
        "struggle_bullets": [
            "Avoidance of hard truths or necessary conflict",
            "Disorganization or lack of follow-through on details",
            "Prioritizing being liked over being effective",
            "Emotional exhaustion or taking youth behaviors personally"
        ],
        "coaching": [
            "How can you deliver this difficult message clearly while still remaining kind?",
            "Are we prioritizing popularity over effectiveness in this situation?",
            "What boundaries do you need to set right now to protect your own energy?"
        ],
        "advancement": "Help them master the operational and administrative sides of leadership so their high EQ is backed by unshakable reliability. Challenge them to see 'clarity' and 'accountability' as forms of kindness, not opposition to it."
    },
    "Facilitator": {
        "overview": "This staff member communicates primarily as a Facilitator, meaning they lead by listening, gathering perspectives, and seeking fairness. This significantly shapes how they navigate team dynamics and conflict.\n\nThey influence the tone of the program by creating a sense of stability and inclusion. Their tendencies affect how slowly or quickly decisions are made, how well all voices are heard, and how conflict is mediated between staff or youth.",
        "supervising": "When supervising a Facilitator, it is crucial to give them time to process information. They often see dynamics you might miss but need an invitation to share them.\n\nKey strategies include:\n- Asking for their observations explicitly during supervision.\n- Validating their desire for fairness while pushing them to make decisions even when consensus isn't possible.\n- Encouraging them to voice their own opinion, not just summarize others.",
        "struggle_bullets": [
            "Analysis paralysis or delaying decisions too long",
            "Passive-aggressiveness or holding tension silently",
            "Saying 'it is fine' when it clearly is not",
            "Getting stuck in the middle of staff conflicts without resolving them"
        ],
        "coaching": [
            "If you had to make a decision right now with only 80% of the information, what would it be?",
            "What is the cost to the team of waiting for total consensus on this?",
            "Where are you holding tension for the team that you need to release?"
        ],
        "advancement": "Encourage them to be more vocal and decisive during crises. Help them see that they can be assertive without being aggressive. Their growth lies in becoming a leader who can make the tough call even when not everyone agrees."
    },
    "Tracker": {
        "overview": "This staff member communicates primarily as a Tracker, meaning they lead with details, data, and systems. This shapes how they view safety, compliance, and routine.\n\nThey influence the program by ensuring nothing falls through the cracks. Their tendencies affect how safe the environment feels physically, how well documentation is maintained, and how consistent the routine is for the youth.",
        "supervising": "When supervising a Tracker, provide clear expectations and structure. They respect competence and reliability. Ambiguity is their enemy.\n\nKey strategies include:\n- Providing the 'why' behind changes and the specific 'how' for implementation.\n- Respecting their systems and organization; disrupting their routine erodes trust.\n- Helping them zoom out from the details to see the human/relational picture.",
        "struggle_bullets": [
            "Becoming rigid, critical, or perfectionistic",
            "Getting 'stuck in the weeds' of minor details",
            "Coming across as cold or inflexible to youth in crisis",
            " prioritizing policy over immediate relational needs"
        ],
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
        "overview": "Their primary motivator is Growth. This means they thrive when their work environment honors their need for progress, new skills, and developmental challenges.\n\nUnderstanding this pattern helps you anticipate what conditions will bring out their best—and what circumstances (like stagnation or repetitive tasks) may cause frustration, burnout, or disengagement.",
        "motivating": "As someone driven by Growth, this staff member responds best to strategies that feed their curiosity and competence. Examples include:\n- Assigning 'stretch' projects that require learning new skills.\n- Framing feedback as coaching for the future, not just critique of the past.\n- Connecting their daily work to their long-term career trajectory.",
        "support": "To support them effectively:\n- Sponsor them for trainings or special certifications.\n- Ask 'What are you learning right now?' during supervision.\n- Ensure they don't feel boxed in; show them the path forward.",
        "thriving_bullets": [
            "Proactive questions about 'why' and 'how'",
            "Volunteering for new responsibilities",
            "Mentoring peers on new skills",
            "High engagement in training and development"
        ],
        "intervention": "Realign their tasks to include a learning component. If they are struggling, they may be bored. Ask: 'Do you feel challenged right now?'",
        "celebrate": "Celebrate their acquisition of new skills and their adaptability. 'I saw how you learned X and applied it—great work.'"
    },
    "Purpose": {
        "overview": "Their primary motivator is Purpose. This means they thrive when their work environment honors their need for meaning, alignment, and values-driven action.\n\nUnderstanding this pattern helps you anticipate what conditions will bring out their best—and what circumstances (like perceived injustice or bureaucracy) may cause frustration, burnout, or disengagement.",
        "motivating": "As someone driven by Purpose, this staff member responds best to strategies that reinforce the mission. Examples include:\n- Connecting every directive back to the impact on youth and families.\n- Being transparent about the 'why' behind difficult policies.\n- Inviting their input on ethical or care-related decisions.",
        "support": "To support them effectively:\n- Create space for them to voice ethical concerns.\n- Validate their passion, even when you have to say no.\n- Remind them of the human impact of their work during hard times.",
        "thriving_bullets": [
            "Passionate advocacy for youth needs",
            "High integrity and ethical standards",
            "Willingness to go the extra mile for a kid",
            "Deep commitment to program outcomes"
        ],
        "intervention": "Reconnect them to the mission. If they are struggling, they may feel cynical. Ask: 'Does this feel misaligned with why you are here?'",
        "celebrate": "Celebrate moments where their work directly impacted a youth's life. Share specific stories of their impact."
    },
    "Connection": {
        "overview": "Their primary motivator is Connection. This means they thrive when their work environment honors their need for belonging, team cohesion, and relationship.\n\nUnderstanding this pattern helps you anticipate what conditions will bring out their best—and what circumstances (like isolation or unresolved conflict) may cause frustration, burnout, or disengagement.",
        "motivating": "As someone driven by Connection, this staff member responds best to strategies that reinforce the team dynamic. Examples include:\n- Prioritizing team cohesion and shared wins.\n- Checking in on them personally before diving into business.\n- Allowing time for team processing and debriefing.",
        "support": "To support them effectively:\n- Ensure they aren't working in isolation for long periods.\n- Facilitate team bonding and repair conflict quickly.\n- Be a warm, accessible presence to them.",
        "thriving_bullets": [
            "Collaborative problem solving",
            "High morale and support of peers",
            "Creating a 'family' atmosphere on the unit",
            "Strong rapport with difficult youth"
        ],
        "intervention": "Repair relationships. If they are struggling, they may feel isolated. Ask: 'How are you feeling about the team dynamic right now?'",
        "celebrate": "Celebrate their contributions to culture. 'You really held the team together today.'"
    },
    "Achievement": {
        "overview": "Their primary motivator is Achievement. This means they thrive when their work environment honors their need for progress, results, and concrete accomplishment.\n\nUnderstanding this pattern helps you anticipate what conditions will bring out their best—and what circumstances (like vague goals or shifting goalposts) may cause frustration, burnout, or disengagement.",
        "motivating": "As someone driven by Achievement, this staff member responds best to strategies that reinforce their intrinsic drive to win. Examples include:\n- Setting clear, measurable goals with defined finish lines.\n- Using checklists or data to visualize progress.\n- Giving them autonomy to reach the target once it is set.",
        "support": "To support them effectively:\n- Remove blockers that prevent them from finishing tasks.\n- Protect their time from unnecessary meetings.\n- Be definitive about what 'success' looks like.",
        "thriving_bullets": [
            "High-quality documentation and follow-through",
            "Efficient management of shift tasks",
            "Reliability and consistency",
            "Goal-oriented leadership"
        ],
        "intervention": "Clarify expectations. If they are struggling, they may feel ineffective. Ask: 'Is it clear what success looks like in this situation?'",
        "celebrate": "Celebrate the completion of projects and reliability. 'You said you'd do it, and you did it.'"
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
    
    # Colors
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
    # This dynamic text mimics the logic of "Director x Achievement"
    integrated_text = (
        f"When their {p_comm} communication style intersects with their {p_mot} motivation, a distinct leadership pattern emerges. "
        f"This integrated style influences how they problem-solve, how they support youth and staff, and how they manage crises.\n\n"
        f"This crossover determines how they carry expectations (often driven by {p_mot}), how they respond to pressure (often reverting to {p_comm} tendencies), "
        f"and how they regulate during emotional intensity. They are at their best when they can communicate via {p_comm} channels "
        f"to achieve {p_mot}-aligned outcomes."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    # 6. How You Can Best Support Them
    add_heading("6. How You Can Best Support Them")
    add_body(f"To support this staff member effectively, tailor your supervision to both their communication ({p_comm}) and motivation ({p_mot}) styles.")
    add_body("Best practices include:")
    # Combine support tips from both
    support_tips = [
        "Reinforcing boundaries, self-regulation, and emotional sustainability.",
        "Helping them navigate youth complexity without becoming overwhelmed or rigid."
    ]
    # Add motivation-specific support tip
    support_tips.insert(0, m_data['support'].split('\n')[0]) # Take the first sentence/line for brevity or use full if preferred
    add_body(m_data['support']) # Using full block for richness

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
