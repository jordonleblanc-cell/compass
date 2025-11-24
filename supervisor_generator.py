import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- Configuration ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- Constants ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- Content Dictionaries (Shortened for logic use, Full text in PDF generator) ---
COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture"}
}

MOTIV_DRIVERS = {
    "Growth": "New Skills & Challenges",
    "Purpose": "Mission & Impact",
    "Connection": "Belonging & Team",
    "Achievement": "Goals & Progress"
}

# --- Expanded Content Dictionaries for PDF ---
COMM_PROFILES = {
    "Director": {
        "overview": "This staff member communicates primarily as a Director, meaning they lead with the core traits associated with this style—such as clarity, structure, and urgency.",
        "supervising": "Be direct, concise, and outcome-focused. They respect leaders who get to the point. Do not micromanage; define the 'what' (the goal) clearly, but give them autonomy on the 'how'.",
        "struggle_bullets": ["Decreased patience", "Over-assertiveness", "Fatigue/Irritability", "Rigid enforcement"],
        "coaching": ["What are the risks of moving this fast?", "Who haven't we heard from yet?", "How can you frame this directive so the team feels supported?"],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience and consensus-building."
    },
    "Encourager": {
        "overview": "This staff member communicates primarily as an Encourager, meaning they lead with warmth, optimism, and high emotional intelligence.",
        "supervising": "Connect relationally before diving into tasks. Validate their emotional labor. Criticism can feel personal, so frame it around professional growth.",
        "struggle_bullets": ["Avoidance of conflict", "Disorganization", "Prioritizing being liked", "Emotional exhaustion"],
        "coaching": ["How can you deliver this hard news while remaining kind?", "Are we prioritizing popularity over effectiveness?", "What boundaries do you need to set?"],
        "advancement": "Help them master the operational side of leadership. Challenge them to see clarity and accountability as forms of kindness."
    },
    "Facilitator": {
        "overview": "This staff member communicates primarily as a Facilitator, meaning they lead by listening, gathering perspectives, and seeking fairness.",
        "supervising": "Give them time to process. Ask for their observations explicitly. Validate their desire for fairness but push for decisions.",
        "struggle_bullets": ["Analysis paralysis", "Passive-aggressiveness", "Saying 'it's fine' when it isn't", "Getting stuck in the middle"],
        "coaching": ["If you had to decide right now, what would you do?", "What is the cost of waiting for consensus?", "Where are you holding tension for the team?"],
        "advancement": "Encourage them to be more vocal and decisive. Help them see that they can be assertive without being aggressive."
    },
    "Tracker": {
        "overview": "This staff member communicates primarily as a Tracker, meaning they lead with details, data, and systems.",
        "supervising": "Provide clear expectations and structure. Respecting their systems builds trust. Explain the 'why' behind changes.",
        "struggle_bullets": ["Rigidity/Perfectionism", "Getting stuck in weeds", "Coming across as cold", "Prioritizing policy over people"],
        "coaching": ["Does this detail change the outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the big picture goal?"],
        "advancement": "Help them delegate details to focus on strategy. Teach them to distinguish between 'mission-critical' and 'preference'."
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "overview": "Their primary motivator is Growth. They thrive on progress, new skills, and developmental challenges.",
        "motivating": "Give them problems to solve. Provide feedback on skill development. Connect work to career trajectory.",
        "support": "Sponsor them for training. Ask 'What are you learning?'. Ensure they don't feel boxed in.",
        "thriving_bullets": ["Proactive questions", "Volunteering", "Mentoring peers", "High engagement"],
        "intervention": "Realign tasks to include learning. Ask: 'Do you feel challenged right now?'",
        "celebrate": "Celebrate acquisition of new skills and adaptability."
    },
    "Purpose": {
        "overview": "Their primary motivator is Purpose. They thrive on meaning, alignment, and values-driven action.",
        "motivating": "Connect directives to the mission. Be transparent about the 'why'. Invite input on ethical decisions.",
        "support": "Create space for ethical concerns. Validate their passion. Remind them of human impact.",
        "thriving_bullets": ["Passionate advocacy", "High integrity", "Going the extra mile", "Commitment to outcomes"],
        "intervention": "Reconnect to mission. Ask: 'Does this feel misaligned with why you are here?'",
        "celebrate": "Celebrate moments where their work directly impacted a youth's life."
    },
    "Connection": {
        "overview": "Their primary motivator is Connection. They thrive on belonging, team cohesion, and relationships.",
        "motivating": "Prioritize team cohesion. Recognize shared wins. Check in personally.",
        "support": "Ensure they aren't isolated. Facilitate team bonding. Be accessible.",
        "thriving_bullets": ["Collaborative", "High morale", "Family atmosphere", "Strong rapport"],
        "intervention": "Repair relationships. Ask: 'How are you feeling about the team dynamic?'",
        "celebrate": "Celebrate their contributions to culture and supporting peers."
    },
    "Achievement": {
        "overview": "Their primary motivator is Achievement. They thrive on progress, results, and concrete accomplishment.",
        "motivating": "Set clear goals. Use checklists/metrics. Give autonomy to reach targets.",
        "support": "Remove blockers. Protect their time. Be definitive about 'success'.",
        "thriving_bullets": ["High follow-through", "Efficiency", "Reliability", "Goal-oriented"],
        "intervention": "Clarify expectations. Ask: 'Is it clear what success looks like here?'",
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
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Supervisory Guide", ln=True, align='C')
    
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

    # 12-Point Structure
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

    killer_hint = "disengagement" 
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

# --- TAB 1: GUIDE GENERATOR (Original) ---
with tab1:
    st.markdown("### Generate Individual Supervisory Guides")
    
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🔄 Refresh Database"):
            st.cache_data.clear()
            st.rerun()
            
    if not df.empty:
        staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
        selected_staff_name = st.selectbox("Select Staff Member", options=list(staff_options.keys()))
        
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
                st.download_button(
                    label="Download PDF Guide",
                    data=pdf_bytes,
                    file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Database is empty or loading...")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    st.write("Select multiple staff members to analyze the culture of a specific unit or team.")
    
    if not df.empty:
        team_selection = st.multiselect("Build your Team", df['name'].tolist())
        
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            
            st.divider()
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Communication Mix")
                comm_counts = team_selection_counts = team_df['p_comm'].value_counts()
                fig_team_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4)
                st.plotly_chart(fig_team_comm, use_container_width=True)
                
                # Comm Analysis
                dominant_comm = comm_counts.idxmax()
                if comm_counts.max() / len(team_df) > 0.6:
                    st.warning(f"⚠️ **Echo Chamber Risk:** This team is dominated by **{dominant_comm}s**.")
                    if dominant_comm == "Director":
                        st.write("Risk: Moving too fast, steamrolling quieter voices. **Correction:** Intentionally invite dissent.")
                    elif dominant_comm == "Encourager":
                        st.write("Risk: 'Nice' culture that avoids hard accountability. **Correction:** Standardize review processes.")
                    elif dominant_comm == "Facilitator":
                        st.write("Risk: Slow decision making, endless meetings. **Correction:** Set hard deadlines.")
                    elif dominant_comm == "Tracker":
                        st.write("Risk: Rigid adherence to rules over relationships. **Correction:** Schedule team bonding time.")
            
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                fig_team_mot = px.bar(x=mot_counts.index, y=mot_counts.values)
                st.plotly_chart(fig_team_mot, use_container_width=True)
                
                # Motivation Analysis
                if "Growth" in mot_counts and mot_counts["Growth"] > 1:
                    st.success("💡 **High Growth Energy:** This team will love pilots and new initiatives.")
                if "Connection" in mot_counts and mot_counts["Connection"] > 1:
                    st.info("💡 **High Connection Energy:** This team needs time to process emotions together.")

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    st.write("Select two staff members who are struggling to collaborate.")
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Staff Member A", df['name'].unique(), key="p1")
        with c2:
            p2_name = st.selectbox("Staff Member B", df['name'].unique(), key="p2")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            
            st.divider()
            st.subheader(f"The Clash: {p1['p_comm']} vs. {p2['p_comm']}")
            
            # Logic for Conflict
            style1 = p1['p_comm']
            style2 = p2['p_comm']
            
            clash_map = {
                "Director": {"Encourager": "Efficiency vs. Harmony", "Facilitator": "Speed vs. Process", "Tracker": "Big Picture vs. Details", "Director": "Power Struggle"},
                "Encourager": {"Director": "Harmony vs. Efficiency", "Facilitator": "Feelings vs. Fairness", "Tracker": "Relationships vs. Rules", "Encourager": "Lack of Structure"},
                "Facilitator": {"Director": "Process vs. Speed", "Encourager": "Fairness vs. Feelings", "Tracker": "Consensus vs. Policy", "Facilitator": "Analysis Paralysis"},
                "Tracker": {"Director": "Details vs. Big Picture", "Encourager": "Rules vs. Relationships", "Facilitator": "Policy vs. Consensus", "Tracker": "Rigidity"}
            }
            
            core_tension = clash_map.get(style1, {}).get(style2, "Differing Perspectives")
            st.info(f"**Core Tension:** {core_tension}")
            
            st.markdown("#### 🗣️ Mediation Script")
            st.markdown(f"**To {p1_name} ({style1}):**")
            st.write(f"\"{p2_name} isn't trying to be difficult. Their {style2} style focuses on {COMM_TRAITS[style2]['focus']}. When you push for {COMM_TRAITS[style1]['focus']}, they feel you are ignoring {COMM_TRAITS[style2]['focus']}. Try asking for their input first before deciding.\"")
            
            st.markdown(f"**To {p2_name} ({style2}):**")
            st.write(f"\"{p1_name} values {COMM_TRAITS[style1]['focus']}. When they push hard, it's not personal; they are trying to solve the problem. Be direct with them about what you need rather than waiting for them to guess.\"")

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    st.write("Analyze readiness for promotion.")
    
    if not df.empty:
        candidate_name = st.selectbox("Select Candidate", df['name'].unique(), key="career")
        target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"])
        
        if candidate_name:
            cand = df[df['name'] == candidate_name].iloc[0]
            
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({cand['p_comm']} / {cand['p_mot']})")
            
            # Simple Logic for "Gap"
            st.subheader("The Growth Gap")
            
            if cand['p_comm'] == "Director":
                st.write("⚠️ **Challenge:** Moving up requires leading leaders, not just followers. You cannot command a Shift Supervisor the way you command a YDP.")
                st.write("✅ **Action Plan:** Delegate a project entirely. If you intervene to 'fix it', you fail the assignment.")
            
            elif cand['p_comm'] == "Encourager":
                st.write("⚠️ **Challenge:** Higher roles require delivering unpopular news without wavering. Your desire to be liked will be tested.")
                st.write("✅ **Action Plan:** Lead a disciplinary conversation or a policy reinforcement meeting without apologizing for the rule.")
                
            elif cand['p_comm'] == "Tracker":
                st.write("⚠️ **Challenge:** Senior roles are ambiguous. You won't always have a checklist. You need to get comfortable with 'gray areas'.")
                st.write("✅ **Action Plan:** Manage a situation where two policies conflict and a judgment call is required.")
                
            elif cand['p_comm'] == "Facilitator":
                st.write("⚠️ **Challenge:** The higher you go, the less time you have for consensus. You will need to make unpopular calls quickly.")
                st.write("✅ **Action Plan:** Make a time-sensitive decision for the team without calling a meeting first.")

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Communication Styles")
            fig_org_comm = px.pie(df, names='p_comm', color='p_comm', 
                                 color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'})
            st.plotly_chart(fig_org_comm, use_container_width=True)
        
        with c2:
            st.subheader("Motivation Drivers")
            fig_org_mot = px.bar(df, x='p_mot', color='p_mot')
            st.plotly_chart(fig_org_mot, use_container_width=True)
            
        st.divider()
        st.subheader("Role Breakdown")
        
        # Pivot table for Role vs Comm Style
        if 'role' in df.columns:
            role_breakdown = pd.crosstab(df['role'], df['p_comm'])
            st.dataframe(role_breakdown, use_container_width=True)
            
            st.info("Tip: If 'Shift Supervisors' are mostly 'Encouragers' but 'Program Supervisors' are mostly 'Directors', expect friction during hand-offs.")
    else:
        st.warning("No data available.")
