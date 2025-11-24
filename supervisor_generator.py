import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- Configuration ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- Constants ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- Expanded Content Dictionaries for PDF & Tools ---

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# Detailed Conflict Scripts
CONFLICT_SCRIPTS = {
    "Director-Encourager": {
        "tension": "The Director feels the Encourager is 'too soft' or wasting time on feelings. The Encourager feels the Director is 'mean' or steamrolling the team.",
        "advice_a": "Your drive for efficiency is hurting the relationship. If you crush their morale, they will disengage. Stop interrupting and acknowledge the *feeling* before you fix the *problem*.",
        "advice_b": "The Director isn't trying to be mean; they are stressed by the lack of progress. Be direct. Say, 'I can move faster, but I need you to listen to my concern about the team's morale first.'"
    },
    "Director-Facilitator": {
        "tension": "The Speed vs. Process Clash. The Director wants to decide *now*; the Facilitator wants to hear from everyone first.",
        "advice_a": "You are moving too fast for them. If you force a decision now, you get compliance, not buy-in. Ask: 'What specific perspective are we missing?' then set a deadline.",
        "advice_b": "Silence looks like agreement to a Director. You must speak up. Say: 'I am not stalling, I am preventing a mistake. Give me 10 minutes to outline the risk.'"
    },
    "Director-Tracker": {
        "tension": "The Big Picture vs. The Weeds. The Director says 'Just get it done.' The Tracker asks 'But how? What about regulation X?'",
        "advice_a": "They aren't being difficult; they are protecting you from liability. Stop dismissing the details. Ask: 'What is the critical blocker preventing us from moving?'",
        "advice_b": "The Director doesn't need every detail. Start with the solution, not the problem. Say: 'We can hit that deadline, but we have to skip step B. Do you agree?'"
    },
    "Encourager-Tracker": {
        "tension": "Heart vs. Head. The Encourager bends rules to help the kid. The Tracker cites the policy manual.",
        "advice_a": "Rules aren't just red tape; they create the safety container for your relationship. If you are inconsistent, you aren't being kind, you're being confusing.",
        "advice_b": "You are right about the rule, but you are losing the relationship. Validate the intent ('I know you want to help the kid') before correcting the method."
    },
    "Encourager-Facilitator": {
        "tension": "The Nice-Off. Both want harmony, but the Facilitator focuses on fairness while the Encourager focuses on feelings. Decisions can stall indefinitely.",
        "advice_a": "You are prioritizing the person in front of you over the fairness of the whole group. Step back.",
        "advice_b": "You are prioritizing the process over the immediate emotional need. Step in."
    },
    "Facilitator-Tracker": {
        "tension": "Analysis Paralysis. Both are cautious. The Facilitator waits for consensus; the Tracker waits for data. Nothing happens.",
        "advice_a": "Consensus doesn't mean unanimity. You have enough votes. Move.",
        "advice_b": "You have enough data. Perfection is the enemy of done. Move."
    }
}

# Career Growth Maps
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": "You must learn that you can't do it all yourself. Your job is now to direct the *traffic*, not drive every car. Delegate, don't rescue.",
        "Program Supervisor": "You are excellent at execution, but senior leadership requires political capital. You need to build bridges with other departments, not just demand things from them."
    },
    "Encourager": {
        "Shift Supervisor": "You have to be willing to be the 'bad guy.' Holding staff accountable is a form of care. If you let standards slide to be liked, you will fail.",
        "Program Supervisor": "You need to master the data. Your high EQ is an asset, but you need to back it up with budget management, compliance tracking, and strategic planning."
    },
    "Facilitator": {
        "Shift Supervisor": "You need to make calls when the team is split. Waiting for everyone to agree during a crisis is dangerous. Practice 'disagree and commit'.",
        "Program Supervisor": "You act as a great buffer, but you need to set the vision. Don't just mediate the team's ideas; inject your own direction and strategy."
    },
    "Tracker": {
        "Shift Supervisor": "You cannot track everything. You have to trust your team to do their jobs without hovering. Focus on the critical safety items, let the rest go.",
        "Program Supervisor": "You need to tolerate ambiguity. Program leadership involves gray areas where there is no clear policy. Develop your intuition and judgment."
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
        "celebrate": "Celebrate moments where they directly impacted a youth's life."
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
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf", mime="application/pdf")
    else:
        st.info("Database is empty or loading...")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    st.write("Select multiple staff members to analyze unit culture, friction points, and meeting strategies.")
    
    if not df.empty:
        team_selection = st.multiselect("Build your Team (Select at least 2 people)", df['name'].tolist())
        
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            
            st.divider()
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Analysis")
                comm_counts = team_df['p_comm'].value_counts()
                mot_counts = team_df['p_mot'].value_counts()
                
                # Dominance Check
                if not comm_counts.empty:
                    dominant_style = comm_counts.idxmax()
                    dom_pct = comm_counts.max() / len(team_df)
                    
                    if dom_pct > 0.5:
                        st.warning(f"⚠️ **Echo Chamber Risk:** {int(dom_pct*100)}% of this team are **{dominant_style}s**.")
                        if dominant_style == "Director": st.write("• Risk: Moving too fast, steamrolling quieters. **Fix:** Appoint a 'Devil's Advocate'.")
                        elif dominant_style == "Encourager": st.write("• Risk: Avoiding conflict, lack of accountability. **Fix:** Standardize meeting agendas.")
                        elif dominant_style == "Facilitator": st.write("• Risk: Slow decisions, endless meetings. **Fix:** Set strict time limits.")
                        elif dominant_style == "Tracker": st.write("• Risk: Rigid adherence to rules, low warmth. **Fix:** Start meetings with a relational check-in.")
                    else:
                        st.success("✅ **Balanced Communication:** No single style dominates (>50%).")

                # Missing Voices
                all_styles = {"Director", "Encourager", "Facilitator", "Tracker"}
                present_styles = set(team_df['p_comm'].unique())
                missing = all_styles - present_styles
                if missing:
                    st.info(f"**Missing Voices:** This team lacks **{', '.join(missing)}** energy. You (the supervisor) may need to fill this gap.")

            with c2:
                st.subheader("Team Meeting Protocol")
                st.write("Based on this mix, run your meetings like this:")
                
                if "Director" in present_styles and "Facilitator" in present_styles:
                    st.write("👉 **The Speed Trap:** Directors will want to decide fast; Facilitators need time. **Protocol:** Send agenda 24hrs in advance so Facilitators can process.")
                if "Tracker" in present_styles:
                    st.write("👉 **The Data Check:** Trackers need details. **Protocol:** Don't just announce changes; provide a written one-pager.")
                if "Encourager" in present_styles:
                    st.write("👉 **The Vibe Check:** Encouragers need connection. **Protocol:** Spend the first 5 mins on 'wins' or personal updates.")

            st.divider()
            st.subheader("Visual Breakdown")
            vc1, vc2 = st.columns(2)
            with vc1:
                st.caption("Communication Mix")
                st.plotly_chart(px.pie(team_df, names='p_comm', hole=0.4), use_container_width=True)
            with vc2:
                st.caption("Motivation Drivers")
                st.plotly_chart(px.bar(team_df, x='p_mot'), use_container_width=True)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    st.write("Select two staff members who are struggling to collaborate to get a specific mediation script.")
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Staff Member A", df['name'].unique(), key="p1")
        with c2:
            p2_name = st.selectbox("Staff Member B", df['name'].unique(), key="p2")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            
            style1 = p1['p_comm']
            style2 = p2['p_comm']
            
            # Generate Key for Dictionary (alphabetical order to handle A-B or B-A)
            key = "-".join(sorted([style1, style2]))
            
            st.divider()
            st.subheader(f"The Dynamic: {style1} vs. {style2}")
            
            if style1 == style2:
                st.warning("Same-Style Conflict: These two are likely clashing because they are too similar (fighting for airtime) or amplifying each other's weaknesses.")
            elif key in CONFLICT_SCRIPTS:
                script = CONFLICT_SCRIPTS[key]
                st.info(f"**Root Tension:** {script['tension']}")
                
                st.markdown("#### 🗣️ What to say to them individually:")
                
                # Determine which advice goes to whom
                if style1 < style2: # Matches dictionary order
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

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    st.write("Analyze readiness for promotion based on their current style and the demands of the next role.")
    
    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            candidate_name = st.selectbox("Select Candidate", df['name'].unique(), key="career")
        with col_b:
            target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor"])
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({style} / {cand['p_mot']})")
            st.markdown(f"**Target:** {target_role}")
            
            # logic
            advice = CAREER_PATHWAYS.get(style, {}).get(target_role, "Standard advancement path.")
            
            st.info(f"💡 **The Growth Gap:** {advice}")
            
            st.subheader("Assignments to Test Readiness")
            if target_role == "Shift Supervisor":
                st.write("1. **Delegation Test:** Assign them a project where they are NOT allowed to do the work themselves, only organize others.")
                st.write("2. **Conflict Test:** Have them facilitate a shift debrief after a difficult incident.")
            elif target_role == "Program Supervisor":
                st.write("1. **Strategy Test:** Ask them to write a 1-page proposal for changing a cottage routine, including impact on other depts.")
                st.write("2. **Hiring Test:** Have them interview a candidate and defend their recommendation based on team fit.")

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Communication Breakdown")
            fig_org_comm = px.pie(df, names='p_comm', color='p_comm', 
                                 color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'})
            st.plotly_chart(fig_org_comm, use_container_width=True)
        
        with c2:
            st.subheader("Motivation Drivers")
            fig_org_mot = px.bar(df, x='p_mot', color='p_mot')
            st.plotly_chart(fig_org_mot, use_container_width=True)
            
        st.divider()
        st.subheader("Deep Dive: Who sits in which seat?")
        st.write("This heatmap shows you if certain roles are dominated by specific personality types.")
        
        if 'role' in df.columns:
            # Create a heatmap-style pivot table
            role_breakdown = pd.crosstab(df['role'], df['p_comm'])
            
            # Display using dataframe styling for heatmap effect
            st.dataframe(role_breakdown.style.background_gradient(cmap="Blues"), use_container_width=True)
            
            # Automated Insight
            try:
                shift_sups = role_breakdown.loc['Shift Supervisor'] if 'Shift Supervisor' in role_breakdown.index else None
                if shift_sups is not None:
                    max_style = shift_sups.idxmax()
                    if shift_sups[max_style] > shift_sups.sum() * 0.6:
                        st.warning(f"🚨 **Structural Risk:** Over 60% of Shift Supervisors are **{max_style}s**. This creates a very specific culture on the floor that may lack balance.")
            except:
                pass
    else:
        st.warning("No data available.")
