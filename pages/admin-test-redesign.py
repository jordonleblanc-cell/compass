import streamlit as st
import pandas as pd
import random
import time

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
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .highlight-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 20px;
    }
    .gray-zone-box {
        background-color: #fcf8e3;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f39c12;
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

def module_home():
    st.markdown("### Welcome to the Leadership Intelligence Hub")
    st.write("Select a module from the sidebar to begin. Below is a snapshot of the system capabilities.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>1️⃣ Supervisor's Guide</h3>
            <p><strong>Input:</strong> Individual Profiles<br>
            <strong>Output:</strong> 12-point HUD Manual<br>
            <strong>Use for:</strong> Generating stress prescriptions and coaching moves.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>3️⃣ Conflict Mediator</h3>
            <p><strong>Input:</strong> Two Staff Profiles<br>
            <strong>Output:</strong> Clash Matrix & Scripts<br>
            <strong>Use for:</strong> Resolving interpersonal friction.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>5️⃣ Organization Pulse</h3>
            <p><strong>Input:</strong> Full Database<br>
            <strong>Output:</strong> Cloning Bias Detection<br>
            <strong>Use for:</strong> Leadership pipeline health.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>2️⃣ Team DNA</h3>
            <p><strong>Input:</strong> CSV Roster Upload<br>
            <strong>Output:</strong> Culture Analysis & Missing Voices<br>
            <strong>Use for:</strong> Analyzing cottages, shifts, or programs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <h3>4️⃣ Career Pathfinder</h3>
            <p><strong>Input:</strong> Candidate & Target Role<br>
            <strong>Output:</strong> Gray Zone Assignments<br>
            <strong>Use for:</strong> Preventing Peter Principle promotions.</p>
        </div>
        """, unsafe_allow_html=True)

def module_supervisor_guide():
    st.header("1. Supervisor's Guide (HUD)")
    st.markdown("Generate individualized coaching manuals.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Staff Profile Input")
        name = st.text_input("Staff Name")
        style = st.selectbox("Communication Style", STYLES)
        driver = st.selectbox("Motivation Driver", DRIVERS)
        role = st.selectbox("Current Role", ["Staff", "Supervisor", "Manager", "Director"])
        
        if st.button("Generate HUD Guide", type="primary"):
            st.session_state.current_profile = {"name": name, "style": style, "driver": driver, "role": role}

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
                <b>⚠️ Prescription & Intervention: {arch['intervention']}</b><br>
                <strong>Stress Signature:</strong> {details['risk']} is the primary risk factor.
                </div>
                """, unsafe_allow_html=True)

            with st.expander("🚀 Motivation Strategy"):
                st.write(f"This staff member is driven by **{p['driver']}**.")
                if p['driver'] == "Achievement":
                    st.write("• **Needs:** Visible scoreboards, task completion, efficiency.")
                    st.write("• **De-motivator:** Wasted time, incompetent peers.")
                elif p['driver'] == "Growth":
                    st.write("• **Needs:** Curiosity, future potential, feedback.")
                    st.write("• **De-motivator:** Stagnation, repetitive tasks.")
                elif p['driver'] == "Purpose":
                    st.write("• **Needs:** Values, advocacy, meaning.")
                    st.write("• **De-motivator:** Ethical compromises, 'just for the money'.")
                elif p['driver'] == "Connection":
                    st.write("• **Needs:** Belonging, harmony, team support.")
                    st.write("• **De-motivator:** Conflict, isolation, cold feedback.")

            # Save to DB option
            if st.button("Add to Roster Database"):
                new_entry = {"name": p['name'] or "Unnamed", "style": p['style'], "driver": p['driver'], "role": p['role']}
                st.session_state.staff_db.append(new_entry)
                st.success(f"Added {p['name']} to the team database.")

def module_team_dna():
    st.header("2. Team DNA")
    st.markdown("Analyze unit culture and blind spots.")

    tab1, tab2 = st.tabs(["📊 Analysis Dashboard", "📂 Data Management"])

    with tab2:
        st.subheader("Roster Management")
        
        # CSV Upload
        st.write("Upload a CSV with columns: `name`, `style`, `driver`, `role`")
        uploaded_file = st.file_uploader("Upload Unit Roster", type=["csv"])
        
        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
                # Normalize headers
                df_upload.columns = [c.lower() for c in df_upload.columns]
                
                required_cols = {'name', 'style', 'driver', 'role'}
                if not required_cols.issubset(df_upload.columns):
                    st.error(f"CSV missing columns. Required: {required_cols}")
                else:
                    if st.button("Import CSV Data"):
                        # Convert to list of dicts and extend session state
                        new_data = df_upload.to_dict('records')
                        # Title case values just in case
                        for d in new_data:
                            d['style'] = d['style'].title()
                            d['driver'] = d['driver'].title()
                            d['role'] = d['role'].title()
                        st.session_state.staff_db = new_data
                        st.success(f"Successfully imported {len(new_data)} staff members!")
                        time.sleep(1)
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

        st.divider()
        st.subheader("Current Database")
        df = pd.DataFrame(st.session_state.staff_db)
        st.dataframe(df, use_container_width=True)
        
        if st.button("Clear Database"):
            st.session_state.staff_db = []
            st.rerun()

    with tab1:
        if not st.session_state.staff_db:
            st.warning("No staff in database. Upload CSV or add staff in Supervisor's Guide.")
            return

        df = pd.DataFrame(st.session_state.staff_db)
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dominant Culture Analysis")
            style_counts = df['style'].value_counts()
            st.bar_chart(style_counts, color="#3498db")
            
            dominant = style_counts.idxmax()
            st.markdown(f"**Dominant Style:** `{dominant}`")
            
            st.markdown("<div class='highlight-box'>", unsafe_allow_html=True)
            if dominant == "Director":
                st.write("🔥 **Risk: The Efficiency Trap.**")
                st.write("Staff feel management doesn't care, only numbers matter. Quiet voices are steamrolled.")
                st.write("**Strategy:** Mandate 'Cooling Off' periods for decisions.")
            elif dominant == "Encourager":
                st.write("😊 **Risk: The 'Nice' Trap.**")
                st.write("Toxic Tolerance. Poor performance is tolerated to keep peace. Issues go underground.")
                st.write("**Strategy:** Redefine kindness as accountability.")
            elif dominant == "Facilitator":
                st.write("🤔 **Risk: The Consensus Trap.**")
                st.write("Analysis Paralysis. Urgent problems fester while waiting for agreement.")
                st.write("**Strategy:** The '51% Rule' (move with partial certainty).")
            elif dominant == "Tracker":
                st.write("📜 **Risk: The Bureaucracy Trap.**")
                st.write("Stagnation. Rules are enforced over relationships.")
                st.write("**Strategy:** Create 'Safe to Fail' zones.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.subheader("Missing Voice Analysis")
            present_styles = set(df['style'].unique())
            all_styles = set(STYLES)
            missing = list(all_styles - present_styles)

            if missing:
                for m in missing:
                    st.error(f"⚠️ Missing Voice: **{m}**")
                    if m == "Director": st.write("• **Consequence:** Decisions drift; accountability feels optional.")
                    if m == "Encourager": st.write("• **Consequence:** Morale sags; feedback feels cold.")
                    if m == "Facilitator": st.write("• **Consequence:** Conflict escalates quickly; perspectives missed.")
                    if m == "Tracker": st.write("• **Consequence:** Documentation slips; follow-through is inconsistent.")
            else:
                st.success("✅ **Balanced Team:** All 4 voices are present.")

def module_conflict_mediator():
    st.header("3. Conflict Mediator")
    st.markdown("Style-to-style clash detection & scripts.")

    staff_names = [s['name'] for s in st.session_state.staff_db]
    if len(staff_names) < 2:
        st.warning("Need at least 2 staff members in the database to mediate.")
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
            st.info(f"**{p1['name']}**\n\nStyle: {p1['style']}\n\nFocus: {p1_details['focus']}")
            
        with c2:
            st.info(f"**{p2['name']}**\n\nStyle: {p2['style']}\n\nFocus: {p2_details['focus']}")

        with c3:
            st.subheader("⚔️ The Clash Matrix")
            
            # Logic for clash
            clash_type = "Minor Friction"
            reasons = []
            
            # Pace Clash
            if p1_details['pace'] != p2_details['pace']:
                clash_type = "Major Tension (Pace)"
                reasons.append(f"**Pace Mismatch:** {p1['name']} wants {p1_details['pace']} decisions, {p2['name']} wants {p2_details['pace']} process.")
            
            # Focus Clash
            if p1_details['focus'] != p2_details['focus']:
                if clash_type == "Major Tension (Pace)": clash_type = "Total Opposite (Polarized)"
                else: clash_type = "Major Tension (Focus)"
                reasons.append(f"**Focus Mismatch:** {p1['name']} prioritizes {p1_details['focus']}, {p2['name']} prioritizes {p2_details['focus']}.")
            
            st.markdown(f"**Severity:** `{clash_type}`")
            for r in reasons:
                st.write(r)

        st.markdown("### 🗣️ Prebuilt Intervention Script")
        
        st.markdown(f"""
        <div class="highlight-box">
        <strong>1. Name the Mismatch:</strong><br>
        "I want to stop us for a second. I think we are reacting differently to the stress of this situation. 
        {p1['name']}, you are pushing for <u>{p1_details['focus']} and speed</u>. 
        {p2['name']}, you are prioritizing <u>{p2_details['focus']} and caution</u>."
        <br><br>
        <strong>2. Align on Goal:</strong><br>
        "We can't do both perfectly right now. What does 'safe and good enough' look like for this specific issue?"
        <br><br>
        <strong>3. Choose a Lane (The Deal):</strong><br>
        "For the next 24 hours, we are going to adopt {p1['name']}'s timeline (Speed), but we will use {p2['name']}'s checklist (Accuracy) to get there. Agreed?"
        </div>
        """, unsafe_allow_html=True)

def module_career_pathfinder():
    st.header("4. Career Pathfinder")
    st.markdown("Readiness assessment & Gray Zone assignments.")

    staff_names = [s['name'] for s in st.session_state.staff_db]
    if not staff_names:
        st.write("No staff available.")
        return

    col1, col2 = st.columns(2)
    with col1:
        person_name = st.selectbox("Select Candidate", staff_names)
        person = next(p for p in st.session_state.staff_db if p['name'] == person_name)
    
    with col2:
        target_role = st.selectbox("Target Promotion", ["Shift Supervisor", "Program Supervisor", "Manager", "Director"])

    st.subheader(f"Path: {person['style']} ➔ {target_role}")

    # Shift Logic
    shifts = {
        "Shift Supervisor": {"shift": "From Deciding to Stabilizing.", "desc": "The shift is from personal competence to regulating the tone of the floor."},
        "Program Supervisor": {"shift": "From Command to Systems.", "desc": "The shift is from being the hero to building the system."},
        "Manager": {"shift": "From Unit Outcomes to People Outcomes.", "desc": "The shift is managing capacity and developing other leaders."},
        "Director": {"shift": "From Execution to Strategy.", "desc": "The shift is aligning stakeholders and managing organizational risk."}
    }
    
    shift_data = shifts[target_role]
    st.info(f"**The Psychological Shift:** {shift_data['shift']}\n\n{shift_data['desc']}")

    # Specific Advice
    st.markdown("#### 🚧 Profile-Specific Hurdles")
    if person['style'] == "Director":
        st.write("• **The Hurdle:** Steamrolling stakeholders.")
        st.write("• **The Lesson:** Must learn to slow down and build coalitions before acting.")
    elif person['style'] == "Encourager":
        st.write("• **The Hurdle:** Avoiding hard calls.")
        st.write("• **The Lesson:** Must learn to hold warm accountability without fearing loss of friendship.")
    elif person['style'] == "Facilitator":
        st.write("• **The Hurdle:** Indecision / Analysis Paralysis.")
        st.write("• **The Lesson:** Must learn to make decisions with incomplete data (The 51% Rule).")
    elif person['style'] == "Tracker":
        st.write("• **The Hurdle:** Bureaucratic Stagnation.")
        st.write("• **The Lesson:** Must learn to prioritize risks (Tier 1 vs Tier 3) rather than treating all rules as equal.")

    st.markdown("#### 📝 Gray Zone Assignment Generator")
    st.markdown("To test readiness, assign a task where policy provides discretion, not certainty.")
    
    # Dynamic Gray Zone Text
    gz_task = "Create a plan for a hypothetical crisis."
    if target_role == "Shift Supervisor":
        gz_task = "A staff member is technically following policy but has a toxic attitude. Policy doesn't explicitly forbid 'attitude'. How do you address it?"
    elif target_role == "Program Supervisor":
        gz_task = "We need to cut the budget for the summer trip by 20%. Design a new itinerary that keeps the 'spirit' of the trip but costs less. You cannot ask for more money."
    elif target_role == "Manager":
        gz_task = "Two of your best Shift Supervisors hate each other and refuse to work the same shift. It is affecting the schedule. Resolve this without firing either."
    
    st.markdown(f"""
    <div class='gray-zone-box'>
    <strong>The Assignment:</strong> {gz_task}<br><br>
    <strong>Success Indicator:</strong> They must quantify risk and propose a solution. If they ask 'What is the rule for this?', they are not ready.
    </div>
    """, unsafe_allow_html=True)

def module_org_pulse():
    st.header("5. Organization Pulse")
    st.markdown("Macro-level culture metrics & Leadership Pipeline Health.")
    
    if not st.session_state.staff_db:
        st.warning("No data found.")
        return

    df = pd.DataFrame(st.session_state.staff_db)
    
    col1, col2, col3 = st.columns(3)
    
    total_staff = len(df)
    dom_style = df['style'].mode()[0] if not df.empty else "N/A"
    dom_driver = df['driver'].mode()[0] if not df.empty else "N/A"
    
    col1.metric("Total Headcount", total_staff)
    col2.metric("Agency Dominant Style", dom_style)
    col3.metric("Top Motivation Driver", dom_driver)

    st.divider()
    
    st.subheader("🧬 Cloning Bias Detector")
    st.write("The system compares the **General Staff Mix** to the **Leadership Team Mix** to detect if leaders are hiring people who think exactly like them.")
    
    # Analyze Leadership
    leaders = df[df['role'].isin(['Supervisor', 'Manager', 'Director'])]
    
    if len(leaders) < 1:
        st.warning("Not enough leadership roles defined in database to calculate cloning bias. Ensure roles are set to Supervisor, Manager, or Director.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**General Staff Mix**")
            st.bar_chart(df['style'].value_counts(normalize=True))
        with c2:
            st.write("**Leadership Team Mix**")
            leader_counts = leaders['style'].value_counts(normalize=True)
            st.bar_chart(leader_counts, color="#ff4b4b")
        
        # Check for bias
        bias_found = False
        for style, pct in leader_counts.items():
            if pct > 0.60:
                st.error(f"⚠️ **CLONING BIAS ALERT:** Leadership is {pct*100:.1f}% {style}.")
                st.write(f"**Risk:** The leadership team has a massive blind spot regarding {style} weaknesses. They are promoting people who 'look like them'.")
                bias_found = True
        
        if not bias_found:
            st.success("✅ Leadership pipeline appears balanced (No style > 60%).")

# --- MAIN APP LAYOUT ---

render_header()

# Sidebar Navigation
with st.sidebar:
    st.header("Navigation")
    module = st.radio("Go to:", [
        "Home",
        "1. Supervisor's Guide", 
        "2. Team DNA", 
        "3. Conflict Mediator", 
        "4. Career Pathfinder", 
        "5. Organization Pulse"
    ])
    
    st.divider()
    st.info("💡 **Tip:** Use the 'Team DNA' module to upload your full unit roster CSV.")
    st.caption("Elmcrest Supervisor Platform v1.1")

# Routing
if module == "Home":
    module_home()
elif module == "1. Supervisor's Guide":
    module_supervisor_guide()
elif module == "2. Team DNA":
    module_team_dna()
elif module == "3. Conflict Mediator":
    module_conflict_mediator()
elif module == "4. Career Pathfinder":
    module_career_pathfinder()
elif module == "5. Organization Pulse":
    module_org_pulse()
