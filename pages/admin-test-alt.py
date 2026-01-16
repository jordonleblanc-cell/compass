import streamlit as st
import requests
import pandas as pd
import re
from fpdf import FPDF
import plotly.express as px
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Supervisor Platform", 
    page_icon="📊", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- NAVIGATION HELPER ---
if "current_view" not in st.session_state:
    st.session_state.current_view = "Supervisor's Guide"

def set_view(view_name):
    st.session_state.current_view = view_name

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

BRAND_COLORS = {
    "blue": "#1a73e8",
    "green": "#34a853",
    "teal": "#12b5cb",
    "gray": "#5f6368",
    "red": "#ea4335",
    "yellow": "#fbbc04"
}

# --- 3. CSS STYLING (OPTIMIZED) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

        /* --- VARIABLES --- */
        :root {
            --primary: #1a73e8;        
            --primary-hover: #1557b0;
            --background: #f8f9fa;
            --card-bg: #ffffff;
            --text-main: #202124;
            --text-sub: #5f6368;
            --border-color: #e0e0e0;
            --shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            --input-bg: #ffffff;
        }

        /* --- DARK MODE OVERRIDES --- */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary: #8ab4f8;
                --primary-hover: #aecbfa;
                --background: #131314;
                --card-bg: #1e1e1f;
                --text-main: #e8eaed;
                --text-sub: #9aa0a6;
                --border-color: #444746;
                --shadow: 0 4px 8px rgba(0,0,0,0.4);
                --input-bg: #1e1e1f;
            }
        }

        /* --- LAYOUT COMPACTION --- */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 95% !important;
        }
        
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: -15px; 
        }
        
        h1, h2, h3, h4 {
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
            padding-bottom: 0 !important;
            font-family: 'Google Sans', sans-serif !important;
        }
        
        hr { margin: 1.5em 0 !important; }

        /* --- COMPONENT STYLING --- */
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
            color: var(--text-main) !important;
            background-color: var(--background);
        }

        /* Hide Sidebar Nav */
        [data-testid="stSidebarNav"] {display: none;}
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg);
            border-right: 1px solid var(--border-color);
        }

        /* Hero Box */
        .hero-box {
            background: linear-gradient(135deg, var(--primary) 0%, #1557b0 100%);
            padding: 30px;
            border-radius: 12px;
            color: white !important;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .hero-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 !important;
            color: white !important;
        }
        .hero-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 5px;
            color: rgba(255, 255, 255, 0.9) !important;
        }

        /* Big Navigation Tiles */
        div[data-testid="column"] .stButton button {
            background-color: var(--card-bg);
            color: var(--text-main) !important;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            height: 120px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            justify-content: center;
            padding: 20px;
            text-align: left;
            transition: transform 0.1s;
            border-radius: 12px;
        }
        div[data-testid="column"] .stButton button:hover {
            transform: translateY(-2px);
            border-color: var(--primary);
            color: var(--primary) !important;
        }
        div[data-testid="column"] .stButton button p {
            font-family: 'Google Sans', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
        }

        /* Standard Buttons */
        .stButton button:not([style*="height: 120px"]) {
            background-color: var(--primary);
            color: white !important;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .stButton button:not([style*="height: 120px"]):hover {
            background-color: var(--primary-hover);
        }

        /* Inputs */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: var(--input-bg) !important;
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: none;
        }
        
        /* Containers */
        div[data-testid="stContainer"] {
            background-color: transparent;
            border-radius: 12px;
        }

        /* Login Card */
        .login-card {
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 450px;
            margin: 80px auto;
            border: 1px solid var(--border-color);
        }
        .login-title {
            color: var(--primary) !important;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA FETCHING & STATE MANAGEMENT ---
@st.cache_data(ttl=60)
def fetch_staff_data():
    try:
        response = requests.get(GOOGLE_SCRIPT_URL)
        if response.status_code == 200: return response.json()
        return []
    except: return []

def submit_data_to_google(payload):
    try:
        data_to_send = {
            "action": "save",
            "name": payload['name'],
            "email": payload.get('email', ''),
            "role": payload['role'],
            "cottage": payload['cottage'],
            "scores": {
                "primaryComm": payload['p_comm'],
                "secondaryComm": payload['s_comm'],
                "primaryMotiv": payload['p_mot'],
                "secondaryMotiv": payload['s_mot']
            }
        }
        response = requests.post(GOOGLE_SCRIPT_URL, json=data_to_send)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

if 'staff_df' not in st.session_state:
    raw_data = fetch_staff_data()
    df_raw = pd.DataFrame(raw_data)
    
    if not df_raw.empty:
        df_raw.columns = df_raw.columns.str.lower().str.strip() 
        if 'role' in df_raw.columns: df_raw['role'] = df_raw['role'].astype(str).str.strip()
        if 'cottage' in df_raw.columns: df_raw['cottage'] = df_raw['cottage'].astype(str).str.strip()
        if 'name' in df_raw.columns: df_raw['name'] = df_raw['name'].astype(str).str.strip()
    
    st.session_state.staff_df = df_raw

df_all = st.session_state.staff_df

# --- 5. SECURITY & LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user_role" not in st.session_state:
    st.session_state.current_user_role = None
if "current_user_cottage" not in st.session_state:
    st.session_state.current_user_cottage = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None

def check_password():
    MASTER_PW = st.secrets.get("ADMIN_PASSWORD", "admin2025")
    PS_PW = st.secrets.get("PS_PASSWORD", "ps2025")
    SS_PW = st.secrets.get("SS_PASSWORD", "ss2025")
    
    input_pw = st.session_state.password_input
    selected_user = st.session_state.user_select
    
    authorized = False
    
    if selected_user == "Administrator":
        if input_pw == MASTER_PW:
            authorized = True
            st.session_state.current_user_name = "Administrator"
            st.session_state.current_user_role = "Admin"
            st.session_state.current_user_cottage = "All"
        else:
            st.error("Incorrect Administrator Password.")
            return

    elif not df_all.empty:
        user_row = df_all[df_all['name'] == selected_user].iloc[0]
        role_raw = user_row.get('role', 'YDP')
        cottage_raw = user_row.get('cottage', 'All')
        
        if input_pw == MASTER_PW:
            authorized = True
        else:
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except:
                individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip():
                authorized = True
            elif not authorized:
                if "Program Supervisor" in role_raw or "Director" in role_raw or "Manager" in role_raw:
                    if input_pw == PS_PW: authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                elif "Shift Supervisor" in role_raw:
                    if input_pw == SS_PW: authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                else:
                    st.error("Access Restricted.")
                    return

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""
        <div class='login-card'>
            <div class='login-title'>Supervisor Access</div>
            <div style='color: #5f6368; margin-bottom: 20px;'>Select your name and enter your role's access code.</div>
    """, unsafe_allow_html=True)
    
    if not df_all.empty and 'name' in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Director"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Who are you?", user_names, key="user_select")
    else:
        st.selectbox("Who are you?", ["Administrator"], key="user_select")
        
    st.text_input("Access Code", type="password", key="password_input", on_change=check_password)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. DATA FILTERING ENGINE (RBAC) ---
def get_filtered_dataframe():
    user_role = str(st.session_state.current_user_role)
    user_cottage = str(st.session_state.current_user_cottage)
    current_user = str(st.session_state.current_user_name)
    
    current_df = st.session_state.staff_df

    if user_role == "Admin" or current_user == "Administrator" or "Director" in user_role or "Manager" in user_role:
        return current_df
    
    filtered_df = current_df.copy()
    
    if 'cottage' in current_df.columns and user_cottage != "All":
         filtered_df = filtered_df[filtered_df['cottage'] == user_cottage]
    
    if 'role' in current_df.columns:
        if "Program Supervisor" in user_role:
            pass
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
        elif "YDP" in user_role:
            filtered_df = filtered_df[filtered_df['name'] == current_user]

    return filtered_df

df = get_filtered_dataframe()

with st.sidebar:
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    st.divider()
    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# SUPERVISOR TOOL LOGIC STARTS HERE
# ==========================================

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# NOTE: Keeping your existing massive dictionaries (COMM_PROFILES, MOTIV_PROFILES, INTEGRATED_PROFILES, etc.)
# I am assuming they are populated as in your original script. 
# For brevity in this fix, I am ensuring the structure is correct around them.
# PASTE YOUR DICTIONARY DEFINITIONS HERE if running from scratch, 
# or ensure they are present in the script execution flow.

# --- MOCKING DATA FOR COMPLETENESS OF THIS FIX ---
# In your real app, keep your full dictionary definitions here.
if 'COMM_PROFILES' not in globals():
    # Use your original data here
    pass 

# ... [Insert your original COMM_PROFILES, MOTIV_PROFILES, INTEGRATED_PROFILES, TEAM_CULTURE_GUIDE, MISSING_VOICE_GUIDE, MOTIVATION_GAP_GUIDE, SUPERVISOR_CLASH_MATRIX, CAREER_PATHWAYS dictionaries here] ...
# For the sake of providing a working script, I will assume the previous context holds these. 
# If copying this script, ensure lines 330-1450 from your original code are inserted here.

# --- 5c. INTEGRATED PROFILES LOGIC ---
def generate_profile_content(comm, motiv):
    combo_key = f"{comm}-{motiv}"
    c_data = COMM_PROFILES.get(comm, {})
    m_data = MOTIV_PROFILES.get(motiv, {})
    i_data = INTEGRATED_PROFILES.get(combo_key, {})

    avoid_map = {
        "Director": ["Wasting time with small talk", "Vague answers", "Micromanaging"],
        "Encourager": ["Public criticism", "Ignoring feelings", "Transactional talk"],
        "Facilitator": ["Pushing for instant decisions", "Aggressive confrontation", "Dismissing group concerns"],
        "Tracker": ["Vague instructions", "Asking to break policy", "Chaos/Disorganization"]
    }

    return {
        "s1_b": c_data.get('bullets'),
        "s2_b": c_data.get('supervising_bullets'),
        "s3_b": m_data.get('bullets'),
        "s4_b": m_data.get('strategies_bullets'),
        "s5": f"**Profile:** {i_data.get('title')}\n\n{i_data.get('synergy')}",
        "s6": i_data.get('support', ''),
        "s7": i_data.get('thriving', ''),
        "s8": i_data.get('struggling', ''),
        "s9": "Professional Development Plan:",
        "s9_b": i_data.get('interventions', []),
        "s10_b": m_data.get('celebrate_bullets'),
        "coaching": i_data.get('questions', []),
        "advancement": i_data.get('advancement', ''),
        "cheat_do": c_data.get('supervising_bullets'),
        "cheat_avoid": avoid_map.get(comm, []),
        "cheat_fuel": m_data.get('strategies_bullets')
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def send_pdf_via_email(to_email, subject, body, pdf_bytes, filename="Guide.pdf"):
    try:
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        part = MIMEBase('application', "octet-stream")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email Error: {str(e)}"

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (26, 115, 232); green = (52, 168, 83); red = (234, 67, 53); black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20); pdf.set_text_color(*blue); pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12); pdf.set_text_color(*black); pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C'); pdf.ln(5)
    
    data = generate_profile_content(p_comm, p_mot)

    # Cheat Sheet
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Rapid Interaction Cheat Sheet", ln=True, fill=True, align='C')
    pdf.ln(2)

    def print_cheat_column(title, items, color_rgb):
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(*color_rgb)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        if items:
            for item in items:
                clean_item = item.replace("**", "")
                pdf.multi_cell(0, 5, clean_text(f"- {clean_item}"))
        pdf.ln(2)

    print_cheat_column("DO THIS (Communication):", data.get('cheat_do'), green)
    print_cheat_column("AVOID THIS (Triggers):", data.get('cheat_avoid'), red)
    print_cheat_column("FUEL (Motivation):", data.get('cheat_fuel'), blue)
    
    pdf.ln(5); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)

    def add_section(title, body, bullets=None):
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True); pdf.ln(2)
        pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
        
        if body:
            clean_body = body.replace("**", "").replace("* ", "- ")
            pdf.multi_cell(0, 5, clean_text(clean_body))
        
        if bullets:
            pdf.ln(1)
            for b in bullets:
                pdf.cell(5, 5, "-", 0, 0)
                clean_b = b.replace("**", "") 
                pdf.multi_cell(0, 5, clean_text(clean_b))
        pdf.ln(4)

    add_section(f"1. Communication Profile: {p_comm}", None, data['s1_b']) 
    add_section("2. Supervising Their Communication", None, data['s2_b'])
    add_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    add_section("4. Motivating This Staff Member", None, data['s4_b'])
    add_section("5. Integrated Leadership Profile", data['s5']) 
    add_section("6. How You Can Best Support Them", data['s6'])
    add_section("7. What They Look Like When Thriving", data['s7'])
    add_section("8. What They Look Like When Struggling", data['s8'])
    add_section("9. Individual Professional Development Plan (IPDP)", None, data['s9_b'])
    add_section("10. What You Should Celebrate", None, data['s10_b'])

    pdf.set_font("Arial", 'B', 12); pdf.set_text_color(*blue); pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "11. Coaching Questions", ln=True, fill=True); pdf.ln(2)
    pdf.set_font("Arial", '', 11); pdf.set_text_color(*black)
    if data['coaching']:
        for i, q in enumerate(data['coaching']):
            pdf.multi_cell(0, 5, clean_text(f"{i+1}. {q}"))
    pdf.ln(4)

    add_section("12. Helping Them Prepare for Advancement", data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)

    st.divider()
    st.markdown(f"### 📘 Supervisory Guide: {name}")
    st.caption(f"Role: {role} | Profile: {p_comm}/{s_comm} • {p_mot}/{s_mot}")

    # --- VISUALIZATION SECTION ---
    with st.container(border=True):
        st.subheader("📊 Profile At-A-Glance")
        vc1, vc2 = st.columns(2, gap="small")

        with vc1:
            comm_scores = {"Director": 2, "Encourager": 2, "Facilitator": 2, "Tracker": 2}
            if p_comm in comm_scores: comm_scores[p_comm] = 10
            if s_comm in comm_scores: comm_scores[s_comm] = 7

            radar_df = pd.DataFrame(dict(r=list(comm_scores.values()), theta=list(comm_scores.keys())))
            fig_comm = px.line_polar(radar_df, r='r', theta='theta', line_close=True, title="Communication Footprint", range_r=[0, 10])
            fig_comm.update_traces(fill='toself', line_color=BRAND_COLORS['blue'])
            fig_comm.update_layout(height=250, margin=dict(t=30, b=10, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_comm, use_container_width=True)

        with vc2:
            mot_scores = {"Achievement": 2, "Growth": 2, "Purpose": 2, "Connection": 2}
            if p_mot in mot_scores: mot_scores[p_mot] = 10
            if s_mot in mot_scores: mot_scores[s_mot] = 7

            sorted_mot = dict(sorted(mot_scores.items(), key=lambda item: item[1], reverse=True))
            mot_df = pd.DataFrame(dict(Driver=list(sorted_mot.keys()), Intensity=list(sorted_mot.values())))

            fig_mot = px.bar(mot_df, x="Intensity", y="Driver", orientation='h', title="Motivation Drivers", color="Intensity", color_continuous_scale=[BRAND_COLORS['gray'], BRAND_COLORS['blue']])
            fig_mot.update_layout(height=250, showlegend=False, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig_mot.update_xaxes(visible=False)
            st.plotly_chart(fig_mot, use_container_width=True)

    # --- CHEAT SHEET ---
    with st.expander("⚡ Rapid Interaction Cheat Sheet", expanded=True):
        cc1, cc2, cc3 = st.columns(3, gap="small")
        with cc1:
            st.markdown("##### ✅ Do This")
            if data['cheat_do']:
                for b in data['cheat_do']: st.success(b)
        with cc2:
            st.markdown("##### ⛔ Avoid This")
            if data['cheat_avoid']:
                for avoid in data['cheat_avoid']: st.error(avoid)
        with cc3:
            st.markdown("##### 🔋 Fuel")
            if data['cheat_fuel']:
                for b in data['cheat_fuel']: st.info(b)

    st.divider()

    def show_section(title, text, bullets=None):
        st.subheader(title)
        if text: st.write(text)
        if bullets:
            for b in bullets: st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)

    show_section(f"1. Communication Profile: {p_comm}", None, data['s1_b'])
    show_section("2. Supervising Their Communication", None, data['s2_b'])
    show_section(f"3. Motivation Profile: {p_mot}", None, data['s3_b'])
    show_section("4. Motivating This Staff Member", None, data['s4_b'])

    with st.container(border=True):
        st.subheader("5. Integrated Leadership Profile")
        st.caption("How their style and drive combine.")
        
        st.markdown("#### 🔗 The Synergy")
        st.info(str(data.get('s5', '')).strip() or "Integrated profile details available in full report.")
        
        show_section("6. How You Can Best Support Them", data['s6'])

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.subheader("7. Thriving")
        st.success(data['s7'])
    with c2:
        st.subheader("8. Struggling")
        st.error(data['s8'])

    st.markdown("<br>", unsafe_allow_html=True)
    show_section("9. Individual Professional Development Plan (IPDP)", None, data['s9_b'])
    show_section("10. What You Should Celebrate", None, data['s10_b'])
    
    st.subheader("11. Coaching Questions")
    for i, q in enumerate(data['coaching']):
        st.write(f"{i+1}. {q}")

    st.markdown("<br>", unsafe_allow_html=True)
    show_section("12. Helping Them Prepare for Advancement", data['advancement'])

def _integrated_balance_chart(comm_style: str, motiv_style: str):
    comm_map = {"Director": {"x": -8, "y": 8}, "Encourager": {"x": 7, "y": 7}, "Facilitator": {"x": 5, "y": -6}, "Tracker": {"x": -7, "y": -7}}
    mot_map = {"Achievement": {"x": -3, "y": 4}, "Growth": {"x": 2, "y": 7}, "Purpose": {"x": 5, "y": 3}, "Connection": {"x": 7, "y": -2}}
    c = comm_map.get(comm_style, {"x": 0, "y": 0}); m = mot_map.get(motiv_style, {"x": 0, "y": 0})
    task_people = (c["x"] + m["x"]) / 2; speed_process = (c["y"] + m["y"]) / 2
    df_bal = pd.DataFrame([{"Dimension": "Task  ←→  People", "Score": task_people}, {"Dimension": "Process  ←→  Speed", "Score": speed_process}])
    fig = px.bar(df_bal, x="Score", y="Dimension", orientation="h", range_x=[-10, 10], text="Score", title="Leadership Balance Snapshot")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.add_vline(x=0, line_width=2, line_color="gray")
    fig.update_layout(height=220, margin=dict(t=50, b=20, l=20, r=20), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False, zeroline=False)
    return fig

def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None; st.session_state.messages = []
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

# --- HERO SECTION ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Elmcrest Leadership Intelligence</div>
    <div class="hero-subtitle">
        Your command center for staff development. Select a tool below to begin.
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION BUTTONS ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4, gap="small")
with nav_col1:
    if st.button("📝 Supervisor's Guide\n\nCreate 12-point coaching manuals.", use_container_width=True): set_view("Supervisor's Guide")
with nav_col2:
    if st.button("🧬 Team DNA\n\nAnalyze unit culture & blindspots.", use_container_width=True): set_view("Team DNA")
with nav_col3:
    if st.button("⚖️ Conflict Mediator\n\nScripts for tough conversations.", use_container_width=True): set_view("Conflict Mediator")
with nav_col4:
    if st.button("🚀 Career Pathfinder\n\nPromotion readiness tests.", use_container_width=True): set_view("Career Pathfinder")
st.markdown("###")
if st.button("📈 Organization Pulse (See All Data)", use_container_width=True): set_view("Org Pulse")
st.divider()

# --- VIEW CONTROLLER ---

# 1. Supervisor's Guide
if st.session_state.current_view == "Supervisor's Guide":
    st.subheader("📝 Supervisor's Guide")
    sub1, sub2, sub3 = st.tabs(["Database", "Manual Generator", "📥 Input Offline Data"])
    
    with sub1:
        if not df.empty:
            filtered_staff_list = df.to_dict('records')
            options = {f"{s['name']} ({s['role']})": s for s in filtered_staff_list}
            staff_options_list = list(options.keys())
            
            current_selection = st.session_state.get("t1_staff_select")
            default_index = staff_options_list.index(current_selection) if current_selection in staff_options_list else None

            with st.container(border=True):
                sel = st.selectbox("Select Staff", staff_options_list, index=default_index, key="t1_staff_select", placeholder="Choose a staff member...")
                if sel:
                    d = options[sel]
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                    
                    if st.button("Generate Guide", type="primary", use_container_width=True):
                        st.session_state.generated_pdf = create_supervisor_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])
                        st.session_state.generated_filename = f"Guide_{d['name'].replace(' ', '_')}.pdf"
                        st.session_state.generated_name = d['name']
                        display_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])

            if "generated_pdf" in st.session_state and st.session_state.get("generated_name") == d['name']:
                st.divider()
                ac1, ac2 = st.columns([1, 2], gap="small")
                with ac1:
                    st.download_button(label="📥 Download PDF", data=st.session_state.generated_pdf, file_name=st.session_state.generated_filename, mime="application/pdf", use_container_width=True)
                with ac2:
                    with st.popover("📧 Email to Me", use_container_width=True):
                        email_input = st.text_input("Recipient Email", placeholder="name@elmcrest.org")
                        if st.button("Send Email"):
                            if email_input:
                                with st.spinner("Sending..."):
                                    success, msg = send_pdf_via_email(email_input, f"Supervisor Guide: {d['name']}", f"Attached is the Compass Guide for {d['name']}.", st.session_state.generated_pdf, st.session_state.generated_filename)
                                    if success: st.success(msg)
                                    else: st.error(msg)
                            else: st.warning("Enter email.")
            st.button("Reset", on_click=reset_t1)

    with sub2:
        with st.container(border=True):
            st.info("Use this tab to generate a PDF for someone who isn't in the database yet.")
            with st.form("manual"):
                c1,c2 = st.columns(2)
                mn = c1.text_input("Name"); mr = c2.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor"])
                mpc = c1.selectbox("Comm", COMM_TRAITS); mpm = c2.selectbox("Motiv", MOTIV_TRAITS)
                if st.form_submit_button("Generate PDF Only") and mn:
                    pdf_manual = create_supervisor_guide(mn, mr, mpc, None, mpm, None)
                    fname_manual = f"Guide_{mn.replace(' ', '_')}.pdf"
                    st.session_state.manual_pdf = pdf_manual
                    st.session_state.manual_fname = fname_manual
                    display_guide(mn, mr, mpc, None, mpm, None)

        if "manual_pdf" in st.session_state:
            st.download_button("📥 Download PDF", st.session_state.manual_pdf, st.session_state.manual_fname, "application/pdf", use_container_width=True)

    with sub3:
        with st.container(border=True):
            st.markdown("### 📥 Input Offline Results")
            with st.form("offline_input_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    off_name = st.text_input("Staff Name (Required)")
                    off_email = st.text_input("Email (Optional)")
                    off_role = st.selectbox("Role", ["YDP", "Shift Supervisor", "Program Supervisor", "Clinician", "TSS Staff", "Other"])
                    off_cottage = st.selectbox("Program/Cottage", ["Building 10", "Cottage 2", "Cottage 3", "Cottage 7", "Cottage 8", "Cottage 9", "Cottage 11", "Euclid", "Overnight", "Skeele Valley", "TSS Staff", "Other"])
                with col_b:
                    st.markdown("**Assessment Results**")
                    off_p_comm = st.selectbox("Primary Communication", COMM_TRAITS, key="off_pc")
                    off_s_comm = st.selectbox("Secondary Communication", COMM_TRAITS, key="off_sc")
                    off_p_mot = st.selectbox("Primary Motivation", MOTIV_TRAITS, key="off_pm")
                    off_s_mot = st.selectbox("Secondary Motivation", MOTIV_TRAITS, key="off_sm")
                
                if st.form_submit_button("💾 Save to Database", type="primary"):
                    if off_name:
                        with st.spinner("Saving..."):
                            payload = {"name": off_name, "email": off_email, "role": off_role, "cottage": off_cottage, "p_comm": off_p_comm, "s_comm": off_s_comm, "p_mot": off_p_mot, "s_mot": off_s_mot}
                            if submit_data_to_google(payload):
                                st.success(f"Saved {off_name}!")
                                new_row = payload.copy()
                                st.session_state.staff_df = pd.concat([st.session_state.staff_df, pd.DataFrame([new_row])], ignore_index=True)
                                time.sleep(1); st.rerun()
                            else: st.error("Failed to save.")
                    else: st.error("Name is required.")

# 2. TEAM DNA
elif st.session_state.current_view == "Team DNA":
    st.subheader("🧬 Team DNA")
    if not df.empty:
        with st.container(border=True):
            teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        
        if teams:
            tdf = df[df['name'].isin(teams)]
            def calculate_weighted_counts(dframe, p_col, s_col):
                p = dframe[p_col].value_counts() * 1.0; s = dframe[s_col].value_counts() * 0.5
                return p.add(s, fill_value=0).sort_values(ascending=False)

            c1, c2 = st.columns(2, gap="small")
            with c1:
                with st.container(border=True):
                    comm_counts = calculate_weighted_counts(tdf, 'p_comm', 's_comm')
                    fig = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, title="Communication Mix", color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']])
                    fig.update_layout(height=250, margin=dict(t=30, b=10, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                
                if not comm_counts.empty:
                    dom_style = comm_counts.idxmax()
                    ratio = comm_counts.max() / comm_counts.sum()
                    if ratio > 0.4:
                        guide = TEAM_CULTURE_GUIDE.get(dom_style, {})
                        with st.container(border=True):
                            st.warning(f"⚠️ **Dominant Culture:** {int(ratio*100)}% **{dom_style}**")
                            with st.expander(f"📖 Managing the {guide.get('title', dom_style)}", expanded=True):
                                st.markdown(f"**The Vibe:**\n{guide.get('impact_analysis')}")
                                st.markdown(guide.get('management_strategy'))
                                st.info(f"**🎉 Team Building:** {guide.get('team_building')}")
                    else:
                        with st.container(border=True):
                            st.info("**Balanced Culture:** No single style dominates.")

                p_present = set(tdf['p_comm'].unique()); s_present = set(tdf['s_comm'].unique())
                missing_styles = set(COMM_TRAITS) - p_present.union(s_present)
                if missing_styles:
                    with st.container(border=True):
                        st.error(f"🚫 **Missing Voices:** {', '.join(missing_styles)}")
                        cols = st.columns(len(missing_styles))
                        for idx, style in enumerate(missing_styles):
                            with cols[idx]:
                                data = MISSING_VOICE_GUIDE.get(style, {})
                                st.markdown(f"**Without a {style}:**")
                                st.write(data.get('risk'))
                                st.success(f"**Fix:** {data.get('fix')}")

            with c2:
                with st.container(border=True):
                    mot_counts = calculate_weighted_counts(tdf, 'p_mot', 's_mot')
                    fig = px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers", color_discrete_sequence=[BRAND_COLORS['blue']]*4)
                    fig.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                
                if not mot_counts.empty:
                    dom_mot = mot_counts.idxmax()
                    with st.container(border=True):
                        st.subheader(f"⚠️ Motivation Gap: {dom_mot} Driven")
                        mot_guide = MOTIVATION_GAP_GUIDE.get(dom_mot, {})
                        if mot_guide:
                            st.warning(mot_guide['warning'])
                            st.markdown(mot_guide['coaching'])
            
            st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    if not df.empty:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            p1 = c1.selectbox("Select Supervisor", df['name'].unique(), index=None, key="p1")
            p2 = c2.selectbox("Select Staff", df['name'].unique(), index=None, key="p2")
        
        if p1 and p2 and p1 != p2:
            d1 = df[df['name']==p1].iloc[0]; d2 = df[df['name']==p2].iloc[0]
            s1_p, s1_s = d1['p_comm'], d1['s_comm']; s2_p, s2_s = d2['p_comm'], d2['s_comm']
            st.divider()
            st.subheader(f"{s1_p} vs. {s2_p}")
            
            if s1_p in SUPERVISOR_CLASH_MATRIX and s2_p in SUPERVISOR_CLASH_MATRIX[s1_p]:
                clash_p = SUPERVISOR_CLASH_MATRIX[s1_p][s2_p]
                with st.container(border=True):
                    st.markdown(f"**Core Tension:** {clash_p['tension']}")
                    st.markdown(f"{clash_p['psychology']}")
                    st.markdown("**🚩 Watch For:**")
                    for w in clash_p['watch_fors']: st.markdown(f"- {w}")
                    st.divider()
                    c_a, c_b = st.columns(2, gap="small")
                    with c_a:
                        st.markdown("##### 🛠️ Protocol")
                        for i in clash_p['intervention_steps']: st.info(i)
                    with c_b:
                        st.markdown("##### 🗣️ Scripts")
                        script_tabs = st.tabs(list(clash_p['scripts'].keys()))
                        for i, (cat, text) in enumerate(clash_p['scripts'].items()):
                            with script_tabs[i]: st.success(f"\"{text}\"")
            else:
                st.info("No specific conflict protocol exists for this combination.")
            st.button("Reset", key="reset_t3", on_click=reset_t3)

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    if not df.empty:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            cand = c1.selectbox("Candidate", df['name'].unique(), index=None, key="career")
            role = c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager", "Director"], index=None, key="career_target")
        
        if cand and role:
            d = df[df['name']==cand].iloc[0]
            style = d['p_comm']
            path = CAREER_PATHWAYS.get(style, {}).get(role)
            if path:
                st.info(f"**Shift:** {path['shift']}")
                with st.container(border=True):
                    st.markdown(f"**Why it's hard:** {path['why']}")
                c_a, c_b = st.columns(2, gap="small")
                with c_a:
                    with st.container(border=True):
                        st.markdown("##### 🗣️ The Talk")
                        st.write(path['conversation'])
                        if 'supervisor_focus' in path: st.warning(f"**Watch:** {path['supervisor_focus']}")
                with c_b:
                    with st.container(border=True):
                        st.markdown("##### ✅ Assignment")
                        st.write(f"**Setup:** {path['assignment_setup']}")
                        st.write(f"**Task:** {path['assignment_task']}")
                        st.divider()
                        st.success(f"**Success:** {path['success_indicators']}")
                        st.error(f"**Red Flags:** {path['red_flags']}")
            st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    if not df.empty:
        total_staff = len(df)
        def calculate_weighted_pct(dframe, p_col, s_col):
            p = dframe[p_col].value_counts() * 1.0; s = dframe[s_col].value_counts() * 0.5
            total = p.add(s, fill_value=0)
            return (total / total.sum()) * 100

        comm_counts = calculate_weighted_pct(df, 'p_comm', 's_comm').sort_values(ascending=False)
        mot_counts = calculate_weighted_pct(df, 'p_mot', 's_mot').sort_values(ascending=False)
        
        with st.container(border=True):
            c1, c2, c3 = st.columns(3, gap="small")
            if not comm_counts.empty:
                dom_comm = comm_counts.idxmax()
                dom_mot = mot_counts.idxmax()
                c1.metric("Dominant Style", f"{dom_comm} ({int(comm_counts.max())}%)")
                c2.metric("Top Driver", f"{dom_mot} ({int(mot_counts.max())}%)") 
                c3.metric("Total Staff", total_staff)
        
        c_a, c_b = st.columns(2, gap="small")
        with c_a: 
            with st.container(border=True):
                st.markdown("##### 🗣️ Communication Mix")
                fig_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, color_discrete_sequence=[BRAND_COLORS['blue'], BRAND_COLORS['teal'], BRAND_COLORS['green'], BRAND_COLORS['gray']])
                fig_comm.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_comm, use_container_width=True)
        with c_b: 
            with st.container(border=True):
                st.markdown("##### 🔋 Motivation Drivers")
                fig_mot = px.bar(x=mot_counts.values, y=mot_counts.index, orientation='h', color_discrete_sequence=[BRAND_COLORS['blue']])
                fig_mot.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_mot, use_container_width=True)
    else: st.warning("No data available.")
