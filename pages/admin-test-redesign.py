import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, clean look
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #2C3E50;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e9ecef;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA CONSTANTS ---

STYLES = ["Director", "Encourager", "Facilitator", "Tracker"]
DRIVERS = ["Achievement", "Growth", "Purpose", "Connection"]

ARCHETYPES = {
    ("Director", "Achievement"): {"name": "The Executive General", "synergy": "Operational Velocity", "intervention": "The Pause Button", "desc": "They don't just lead; they want to win."},
    ("Director", "Growth"): {"name": "The Restless Improver", "synergy": "Transformational Leadership", "intervention": "Stakeholder Analysis", "desc": "They want to upgrade the shift, not just manage it."},
    ("Director", "Purpose"): {"name": "The Mission Defender", "synergy": "Ethical Courage", "intervention": "The Gray Zone", "desc": "They speak truth to power and fight for the underdog."},
    ("Director", "Connection"): {"name": "The Protective Captain", "synergy": "Safe Enclosure", "intervention": "Delegation of Care", "desc": "They are the 'Mama/Papa Bear' who shields the team."},
    ("Encourager", "Achievement"): {"name": "The Coach", "synergy": "Inspirational Performance", "intervention": "Data Discipline", "desc": "They make hard work feel like a game."},
    ("Encourager", "Growth"): {"name": "The Mentor", "synergy": "Developmental Charisma", "intervention": "Closing the Loop", "desc": "They see gold in people and talk it out of them."},
    ("Encourager", "Purpose"): {"name": "The Heart of the Mission", "synergy": "Passionate Advocacy", "intervention": "Boundaries", "desc": "They keep the emotional flame alive."},
    ("Encourager", "Connection"): {"name": "The Team Builder", "synergy": "Social Cohesion", "intervention": "Professionalism", "desc": "The 'cruise director' of the unit."},
    ("Facilitator", "Achievement"): {"name": "The Steady Mover", "synergy": "Methodical Progress", "intervention": "Imperfect Action", "desc": "They march with precision."},
    ("Facilitator", "Growth"): {"name": "The Patient Gardener", "synergy": "Organic Development", "intervention": "Timelines", "desc": "They nurture difficult staff rather than firing them."},
    ("Facilitator", "Purpose"): {"name": "The Moral Compass", "synergy": "Principled Consensus", "intervention": "The 51% Decision", "desc": "The quiet conscience of the team."},
    ("Facilitator", "Connection"): {"name": "The Peacemaker", "synergy": "Harmonious Inclusion", "intervention": "Disappointing Others", "desc": "They create psychological safety."},
    ("Tracker", "Achievement"): {"name": "The Architect", "synergy": "Systematic Perfection", "intervention": "Flexibility", "desc": "They build the infrastructure."},
    ("Tracker", "Growth"): {"name": "The Technical Expert", "synergy": "Knowledge Mastery", "intervention": "Simplification", "desc": "The walking encyclopedia."},
    ("Tracker", "Purpose"): {"name": "The Guardian", "synergy": "Protective Compliance", "intervention": "Risk Assessment", "desc": "Following rules is their form of caring."},
    ("Tracker", "Connection"): {"name": "The Reliable Rock", "synergy": "Servant Consistency", "intervention": "Saying No", "desc": "They show love by doing the work perfectly."},
}

STYLE_DETAILS = {
    "Director": {"focus": "Task", "pace": "Fast", "motto": "Be Concise. Focus on Outcomes.", "risk": "Steamrolling others"},
    "Encourager": {"focus": "People", "pace": "Fast", "motto": "Allow Discussion. Follow up in writing.", "risk": "Toxic Tolerance"},
    "Facilitator": {"focus": "People", "pace": "Slow", "motto": "Advance Notice. Solicit Opinion.", "risk": "Analysis Paralysis"},
    "Tracker": {"focus": "Task", "pace": "Slow", "motto": "Be Specific. Provide Data.", "risk": "Stagnation/Bureaucracy"},
}

# --- SESSION STATE ---
if 'staff_db' not in st.session_state:
    st.session_state.staff_db = [
        {"name": "Sarah Connor", "style": "Director", "driver": "Purpose", "role": "Supervisor"},
        {"name": "John Smith", "style": "Facilitator", "driver": "Connection", "role": "Staff"},
        {"name": "Emily Chen", "style": "Tracker", "driver": "Achievement", "role": "Manager"},
        {"name": "Mike Ross", "style": "Encourager", "driver": "Growth", "role": "Staff"},
    ]

# --- HELPER FUNCTIONS ---
def get_archetype(style, driver):
    return ARCHETYPES.get((style, driver), {"name": "Unknown", "synergy": "N/A", "intervention": "N/A", "desc": "N/A"})

def render_header():
    st.title("🛡️ Elmcrest Supervisor Platform")
    st.markdown("**Leadership Intelligence & Staff Development System**")
    st.divider()

# --- MODULES ---

def module_supervisor_guide():
    st.header("1. Supervisor's Guide (HUD)")
    st.info("Translate abstract personality traits into a concrete operational manual.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Profile Input")
        name = st.text_input("Staff Name")
        style = st.selectbox("Communication Style", STYLES)
        driver = st.selectbox("Motivation Driver", DRIVERS)
        
        if st.button("Generate Guide"):
            st.session_state.current_profile = {"name": name, "style": style, "driver": driver}

    with col2:
        if 'current_profile' in st.session_state:
            p = st.session_state.current_profile
            arch = get_archetype(p['style'], p['driver'])
            details = STYLE_DETAILS[p['style']]

            st.markdown(f"### 👤 {p['name'] or 'Staff Member'}")
            st.markdown(f"**Archetype:** `{arch['name']}`")
            
            # The HUD
            st.markdown("#### 📟 The Heads-Up Display")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Focus", details['focus'])
            c2.metric("Pace", details['pace'])
            c3.metric("Synergy", arch['synergy'])

            with st.expander("📖 Operating Manual", expanded=True):
                st.write(f"**Core Identity:** {arch['desc']}")
                st.write(f"**How to Supervise:** {details['motto']}")
                st.markdown(f"""
                <div class='highlight-box'>
                <b>⚠️ Required Intervention: {arch['intervention']}</b><br>
                {details['risk']} is the primary risk factor.
                </div>
                """, unsafe_allow_html=True)

            with st.expander("🚀 Motivation Strategy"):
                st.write(f"This staff member is driven by **{p['driver']}**.")
                if p['driver'] == "Achievement":
                    st.write("Need visible scoreboards, task completion, and efficiency.")
                elif p['driver'] == "Growth":
                    st.write("Need curiosity, future potential, and feedback.")
                elif p['driver'] == "Purpose":
                    st.write("Need values, advocacy, and meaning.")
                elif p['driver'] == "Connection":
                    st.write("Need belonging, harmony, and team support.")

            # Save to DB option
            if st.button("Save to Team Database"):
                new_entry = {"name": p['name'] or "Unnamed", "style": p['style'], "driver": p['driver'], "role": "Staff"}
                st.session_state.staff_db.append(new_entry)
                st.success(f"Added {p['name']} to the team database.")

def module_team_dna():
    st.header("2. Team DNA")
    st.info("Analyze unit culture and blind spots based on the staff database.")

    if not st.session_state.staff_db:
        st.warning("No staff in database. Go to Supervisor's Guide to add staff.")
        return

    df = pd.DataFrame(st.session_state.staff_db)
    
    st.subheader("Current Roster")
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dominant Culture")
        style_counts = df['style'].value_counts()
        st.bar_chart(style_counts)
        
        dominant = style_counts.idxmax()
        st.markdown(f"**Dominant Style:** `{dominant}`")
        
        if dominant == "Director":
            st.warning("**Risk: The Efficiency Trap.** Burn and Turn. Quiet voices are steamrolled.")
        elif dominant == "Encourager":
            st.warning("**Risk: The Nice Trap.** Toxic Tolerance. Issues go underground.")
        elif dominant == "Facilitator":
            st.warning("**Risk: The Consensus Trap.** Analysis Paralysis. Solutions watered down.")
        elif dominant == "Tracker":
            st.warning("**Risk: The Bureaucracy Trap.** Stagnation. Rules over relationships.")

    with col2:
        st.subheader("Missing Voices")
        present_styles = set(df['style'].unique())
        all_styles = set(STYLES)
        missing = list(all_styles - present_styles)

        if missing:
            for m in missing:
                st.error(f"❌ Missing: **{m}**")
                if m == "Director": st.write("Risk: Decisions drift; accountability feels optional.")
                if m == "Encourager": st.write("Risk: Morale sags; feedback feels cold.")
                if m == "Facilitator": st.write("Risk: Conflict escalates; perspectives missed.")
                if m == "Tracker": st.write("Risk: Documentation slips; inconsistent follow-through.")
        else:
            st.success("✅ Balanced Team: All styles represented.")

def module_conflict_mediator():
    st.header("3. Conflict Mediator")
    st.info("Resolve friction between two staff members.")

    staff_names = [s['name'] for s in st.session_state.staff_db]
    if len(staff_names) < 2:
        st.warning("Need at least 2 staff members in the database.")
        return

    col1, col2 = st.columns(2)
    with col1:
        p1_name = st.selectbox("Select Person A", staff_names, key="p1")
    with col2:
        p2_name = st.selectbox("Select Person B", staff_names, key="p2")

    if p1_name and p2_name and p1_name != p2_name:
        p1 = next(p for p in st.session_state.staff_db if p['name'] == p1_name)
        p2 = next(p for p in st.session_state.staff_db if p['name'] == p2_name)

        p1_details = STYLE_DETAILS[p1['style']]
        p2_details = STYLE_DETAILS[p2['style']]

        st.divider()
        
        c1, c2, c3 = st.columns([1,1,2])
        
        with c1:
            st.markdown(f"**{p1['name']}**")
            st.write(f"Style: {p1['style']}")
            st.caption(f"{p1_details['pace']} / {p1_details['focus']}")
            
        with c2:
            st.markdown(f"**{p2['name']}**")
            st.write(f"Style: {p2['style']}")
            st.caption(f"{p2_details['pace']} / {p2_details['focus']}")

        with c3:
            st.subheader("⚔️ The Clash Matrix")
            
            # Logic for clash
            clash_reasons = []
            if p1_details['pace'] != p2_details['pace']:
                clash_reasons.append(f"**Pace Mismatch:** One acts fast, the other needs time. (Pressure -> {p1['name']} speeds up, {p2['name']} slows down).")
            if p1_details['focus'] != p2_details['focus']:
                clash_reasons.append(f"**Focus Mismatch:** One prioritizes tasks/logic, the other prioritizes people/feelings.")
            
            if not clash_reasons:
                st.success("Minimal structural friction. Issues likely situational.")
            else:
                for r in clash_reasons:
                    st.markdown(f"- {r}")

        st.subheader("🚑 Intervention Protocol")
        st.markdown(f"""
        1. **Name the Mismatch:** "We are reacting differently to stress. {p1['name']} is pushing for {p1_details['focus']}, {p2['name']} is pushing for {p2_details['focus']}."
        2. **Align on Goal:** "What does 'good enough' look like right now?"
        3. **Choose a Lane:** Decide who leads the next 24 hours.
        """)
        
        with st.expander("🤖 AI Supervisor Assistant (Simulation)"):
            st.write("Generate a script to mediate this specific conflict:")
            st.code(f"""
            [AI Output]: 
            "I'm noticing friction. {p1['name']}, you are feeling held back by the process. {p2['name']}, you are feeling rushed. 
            
            For this specific issue, we are going to adopt {p1['style']}'s timeline but use {p2['style']}'s checklist. Agreed?"
            """)

def module_career_pathfinder():
    st.header("4. Career Pathfinder")
    st.info("Assess readiness for promotion and identify 'Gray Zone' assignments.")

    staff_names = [s['name'] for s in st.session_state.staff_db]
    if not staff_names:
        st.write("No staff available.")
        return

    person_name = st.selectbox("Select Candidate", staff_names)
    person = next(p for p in st.session_state.staff_db if p['name'] == person_name)
    
    target_role = st.selectbox("Target Promotion", ["Shift Supervisor", "Program Supervisor", "Manager", "Director"])

    st.subheader(f"Path for {person['style']} -> {target_role}")

    # Shift Logic
    shifts = {
        "Shift Supervisor": "From Deciding to Stabilizing.",
        "Program Supervisor": "From Command to Systems.",
        "Manager": "From Unit Outcomes to People Outcomes.",
        "Director": "From Execution to Strategy."
    }
    
    st.markdown(f"#### 🧠 The Psychological Shift: {shifts[target_role]}")

    # Specific Advice
    st.markdown("#### 🚧 Developmental Hurdles")
    if person['style'] == "Director":
        st.write("Must learn to slow down and build coalitions. **Risk:** Steamrolling stakeholders.")
    elif person['style'] == "Encourager":
        st.write("Must learn to hold warm accountability. **Risk:** Avoiding hard calls to keep the peace.")
    elif person['style'] == "Facilitator":
        st.write("Must learn to make decisions with incomplete data. **Risk:** Indecision.")
    elif person['style'] == "Tracker":
        st.write("Must learn to prioritize risks (Tier 1 vs Tier 3). **Risk:** Treating all rules as equal emergencies.")

    st.markdown("""
    <div class='highlight-box'>
    <b>📝 The 'Gray Zone' Assignment</b><br>
    Assign them a task where policy provides discretion, not certainty.<br>
    <i>Example: Design a Risk Mitigation Plan for a marginal-fit referral.</i>
    </div>
    """, unsafe_allow_html=True)

def module_org_pulse():
    st.header("5. Organization Pulse")
    st.info("Macro-level health and leadership pipeline risks.")
    
    if not st.session_state.staff_db:
        return

    df = pd.DataFrame(st.session_state.staff_db)
    
    col1, col2, col3 = st.columns(3)
    
    total_staff = len(df)
    dom_style = df['style'].mode()[0]
    dom_driver = df['driver'].mode()[0]
    
    col1.metric("Total Headcount", total_staff)
    col2.metric("Agency Dominant Style", dom_style)
    col3.metric("Top Motivation Driver", dom_driver)

    st.divider()
    
    st.subheader("🧬 Cloning Bias Detector")
    st.write("Comparing General Staff Mix vs. Leadership Team Mix")
    
    # Mocking leadership data for demonstration if not enough data
    leaders = df[df['role'].isin(['Supervisor', 'Manager', 'Director'])]
    
    if len(leaders) < 1:
        st.warning("Not enough leadership roles defined in database to calculate cloning bias. Go to Supervisor Guide and add people with 'Manager' roles.")
    else:
        leader_counts = leaders['style'].value_counts(normalize=True)
        
        # Check for bias
        bias_found = False
        for style, pct in leader_counts.items():
            st.write(f"Leadership is {pct*100:.1f}% {style}")
            if pct > 0.60:
                st.error(f"⚠️ CLONING BIAS DETECTED: Leadership is over 60% {style}.")
                st.write("Warning: Leaders are promoting people who 'look like them'. Huge blind spot risk.")
                bias_found = True
        
        if not bias_found:
            st.success("Leadership pipeline appears balanced.")

# --- MAIN APP LAYOUT ---

render_header()

# Sidebar Navigation
with st.sidebar:
    st.header("Navigation")
    module = st.radio("Go to:", [
        "Supervisor's Guide", 
        "Team DNA", 
        "Conflict Mediator", 
        "Career Pathfinder", 
        "Organization Pulse"
    ])
    
    st.divider()
    st.caption("Elmcrest Supervisor Platform v1.0")
    st.caption("Based on the Elmcrest Operational Manual")

# Routing
if module == "Supervisor's Guide":
    module_supervisor_guide()
elif module == "Team DNA":
    module_team_dna()
elif module == "Conflict Mediator":
    module_conflict_mediator()
elif module == "Career Pathfinder":
    module_career_pathfinder()
elif module == "Organization Pulse":
    module_org_pulse()
