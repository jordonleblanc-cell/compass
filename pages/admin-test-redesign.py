import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import re
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- PDF sanitization for FPDF (latin-1) ---
_PDF_REPLACEMENTS = {
    "\u2013": "-",   # en dash
    "\u2014": "--",  # em dash
    "\u2212": "-",   # minus sign
    "\u2018": "'", "\u2019": "'",  # curly single quotes
    "\u2026": "...", # ellipsis
    "\u2022": "-",   # bullet
    "\u00A0": " ",   # non-breaking space
    "\u201C": '"', "\u201D": '"',  # curly double quotes
}

def pdf_safe(value):
    if value is None:
        return ""
    s = str(value)
    for k, v in _PDF_REPLACEMENTS.items():
        s = s.replace(k, v)
    try:
        s.encode("latin-1")
        return s
    except UnicodeEncodeError:
        return s.encode("latin-1", "ignore").decode("latin-1")

class SafeFPDF(FPDF):
    def cell(self, w, h=0, txt="", border=0, ln=0, align="", fill=False, link=""):
        return super().cell(w, h, pdf_safe(txt), border, ln, align, fill, link)

    def multi_cell(self, w, h, txt="", border=0, align="J", fill=False):
        return super().multi_cell(w, h, pdf_safe(txt), border, align, fill)

    def write(self, h, txt="", link=""):
        return super().write(h, pdf_safe(txt), link)

    def text(self, x, y, txt=""):
        return super().text(x, y, pdf_safe(txt))

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Elmcrest Leadership", 
    page_icon="⚡", 
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

# Bold Palette
BRAND_COLORS = {
    "primary": "#7C3AED",    # Violet 600
    "secondary": "#DB2777",  # Pink 600
    "accent": "#0D9488",     # Teal 600
    "dark": "#111827",       # Gray 900
    "light": "#F3F4F6",      # Gray 100
    "white": "#FFFFFF"
}

# --- 3. CSS STYLING (BOLD & FRESH) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        /* --- VARIABLES --- */
        :root {
            --primary-gradient: linear-gradient(135deg, #7C3AED 0%, #DB2777 100%);
            --card-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --card-border: 1px solid rgba(255, 255, 255, 0.5);
            --text-dark: #111827;
            --text-gray: #4B5563;
            --bg-color: #F8F7FF; /* Very light violet tint */
            --glass-bg: rgba(255, 255, 255, 0.95);
        }

        /* --- GLOBAL RESET --- */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-dark);
        }
        
        .stApp {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(124, 58, 237, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(219, 39, 119, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }

        /* --- HEADERS --- */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.03em;
            background: -webkit-linear-gradient(0deg, #111827, #4B5563);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        h4, h5, h6 {
            font-weight: 700 !important;
            color: #374151 !important;
        }

        /* --- MODERN CARDS (Glassmorphism) --- */
        div[data-testid="stContainer"] {
            background-color: transparent;
        }

        /* Transform containers into floating glass cards */
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {
            background-color: var(--glass-bg);
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: var(--card-shadow);
            backdrop-filter: blur(12px);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
        }

        /* --- HERO SECTION --- */
        .hero-container {
            background: var(--primary-gradient);
            padding: 4rem 2rem;
            border-radius: 32px;
            color: white;
            margin-bottom: 3rem;
            box-shadow: 0 25px 50px -12px rgba(124, 58, 237, 0.25);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('https://www.transparenttextures.com/patterns/cubes.png');
            opacity: 0.1;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            color: white !important;
            -webkit-text-fill-color: white !important;
            text-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.9) !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            position: relative;
        }

        /* --- ACTION BUTTONS (BIG TILES) --- */
        div[data-testid="column"] .stButton button {
            background: white;
            color: var(--text-dark) !important;
            border: none;
            border-radius: 20px;
            height: auto;
            min-height: 120px;
            padding: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: left;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            position: relative;
            overflow: hidden;
        }
        
        div[data-testid="column"] .stButton button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 20px 25px -5px rgba(124, 58, 237, 0.15);
        }
        
        div[data-testid="column"] .stButton button::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 4px;
            background: var(--primary-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        div[data-testid="column"] .stButton button:hover::after {
            opacity: 1;
        }

        div[data-testid="column"] .stButton button p {
            font-size: 1.2rem;
            font-weight: 700;
        }

        /* --- PRIMARY ACTION BUTTONS --- */
        .stButton button:not([style*="min-height: 120px"]) {
            background: #111827;
            color: white !important;
            border-radius: 12px;
            font-weight: 600;
            border: none;
            padding: 0.6rem 1.2rem;
            transition: all 0.2s;
        }
        .stButton button:not([style*="min-height: 120px"]):hover {
            background: var(--primary-gradient);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.2);
            transform: translateY(-1px);
        }

        /* --- METRICS --- */
        div[data-testid="stMetric"] {
            background-color: white;
            padding: 1.5rem;
            border-radius: 16px;
            border: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #7C3AED;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6B7280;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 800;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* --- INPUTS --- */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: white;
            border: 2px solid #E5E7EB;
            border-radius: 12px;
            color: var(--text-dark);
            height: 48px;
        }
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {
            border-color: #7C3AED;
            box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
        }

        /* --- EXPANDERS --- */
        .streamlit-expanderHeader {
            background-color: white;
            border-radius: 12px;
            font-weight: 700;
            border: 1px solid #E5E7EB;
        }
        
        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: none;
            background: rgba(255,255,255,0.5);
            padding: 5px;
            border-radius: 16px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: transparent;
            border: none;
            border-radius: 12px;
            color: #6B7280;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #7C3AED !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }
        
        /* --- LOGIN SCREEN --- */
        .login-card {
            background: white;
            padding: 3rem;
            border-radius: 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
            text-align: center;
            max-width: 500px;
            margin: 100px auto;
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
        if response.status_code == 200: return True
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
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_user_role" not in st.session_state: st.session_state.current_user_role = None
if "current_user_cottage" not in st.session_state: st.session_state.current_user_cottage = None
if "current_user_name" not in st.session_state: st.session_state.current_user_name = None

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
        if input_pw == MASTER_PW: authorized = True
        else:
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except: individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip(): authorized = True
            elif not authorized:
                if "Program Supervisor" in role_raw or "Director" in role_raw or "Manager" in role_raw:
                    if input_pw == PS_PW: authorized = True
                    else: st.error("Incorrect Access Code."); return
                elif "Shift Supervisor" in role_raw:
                    if input_pw == SS_PW: authorized = True
                    else: st.error("Incorrect Access Code."); return
                else: st.error("Access Restricted. Please contact your administrator."); return

        if authorized:
            st.session_state.current_user_name = user_row['name']
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized:
        st.session_state.authenticated = True
        del st.session_state.password_input
    else: st.error("Authentication Failed.")

if not st.session_state.authenticated:
    st.markdown("""
        <div class='login-card'>
            <div style='background: linear-gradient(135deg, #7C3AED 0%, #DB2777 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 800; margin-bottom: 10px;'>ELMCREST</div>
            <div style='color: #6B7280; margin-bottom: 40px; font-weight: 500;'>Leadership Intelligence Platform</div>
    """, unsafe_allow_html=True)
    if not df_all.empty and 'name' in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Director"]
        eligible_staff = df_all[df_all['role'].str.contains('|'.join(leadership_roles), case=False, na=False)]['name'].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
        st.selectbox("Select Your Name", user_names, key="user_select")
    else: st.selectbox("Select Your Name", ["Administrator"], key="user_select")
    st.text_input("Enter Access Code", type="password", key="password_input", on_change=check_password)
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
        if "Program Supervisor" in user_role: pass
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df['role'] == 'YDP') | (filtered_df['name'] == current_user)
            filtered_df = filtered_df[condition]
        elif "YDP" in user_role: filtered_df = filtered_df[filtered_df['name'] == current_user]

    return filtered_df

df = get_filtered_dataframe()

with st.sidebar:
    st.markdown("### 👤 User Profile")
    st.caption(f"Logged in as:")
    st.markdown(f"**{st.session_state.current_user_name}**")
    st.caption(f"Role: {st.session_state.current_user_role}")
    st.divider()
    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# SUPERVISOR TOOL LOGIC & CONSTANTS
# ==========================================

COMM_TRAITS = ["Director", "Encourager", "Facilitator", "Tracker"]
MOTIV_TRAITS = ["Achievement", "Growth", "Purpose", "Connection"]

# --- CONTENT DICTIONARIES (Kept intact) ---
COMM_PROFILES = {
    "Director": {
        "bullets": ["**Clarity:** Prioritize the 'bottom line'.", "**Speed:** Process rapidly, prefer 80% solutions now.", "**Conflict:** View friction as a tool for solving problems."],
        "supervising_bullets": ["**Be Concise:** Get to the point immediately.", "**Focus on Outcomes:** Tell them what, not how.", "**Respect Autonomy:** Give space; don't hover."]
    },
    "Encourager": {
        "bullets": ["**Verbal Processing:** Think out loud and socially.", "**Optimism:** Focus on potential and 'vibes'.", "**Relationship-First:** Influence through connection."],
        "supervising_bullets": ["**Allow Discussion:** Give runway for small talk.", "**Ask for Specifics:** Drill down into generalities.", "**Follow Up in Writing:** Recap details via email."]
    },
    "Facilitator": {
        "bullets": ["**Listening:** Gather all perspectives first.", "**Consensus:** Prefer group agreement over unilateral action.", "**Process:** Value the 'how' as much as the 'what'."],
        "supervising_bullets": ["**Advance Notice:** Give time to prepare before meetings.", "**Deadlines:** Set clear 'decision dates'.", "**Solicit Opinion:** Ask them explicitly what they think."]
    },
    "Tracker": {
        "bullets": ["**Detail-Oriented:** Value accuracy and data.", "**Risk-Averse:** Cautious until 100% sure.", "**Process-Driven:** Guardians of the policy manual."],
        "supervising_bullets": ["**Be Specific:** Use numbers, not feelings.", "**Provide Data:** Bring evidence to persuade.", "**Written Instructions:** Document the ask."]
    }
}

MOTIV_PROFILES = {
    "Achievement": {
        "strategies_bullets": ["**Visual Goals:** Charts/checklists.", "**Public Wins:** Praise competence.", "**Autonomy:** Let them design the path."],
        "celebrate_bullets": ["Efficiency improvements.", "Clarity in decision making.", "Resilience after setbacks."]
    },
    "Growth": {
        "strategies_bullets": ["**Stretch Assignments:** Tasks above current level.", "**Career Pathing:** Discuss future roles.", "**Mentorship:** Connect with leaders."],
        "celebrate_bullets": ["Insight into root causes.", "Development of others.", "Courage to try new things."]
    },
    "Purpose": {
        "strategies_bullets": ["**The Why:** Connect rules to mission.", "**Storytelling:** Share impact stories.", "**Ethics:** Validate moral concerns."],
        "celebrate_bullets": ["Integrity choices.", "Advocacy for the vulnerable.", "Consistency in care."]
    },
    "Connection": {
        "strategies_bullets": ["**Face Time:** In-person check-ins.", "**Team Rituals:** Huddles and traditions.", "**Personal Care:** Ask about life outside work."],
        "celebrate_bullets": ["Loyalty to the team.", "Stabilizing presence.", "Building unit culture."]
    }
}

INTEGRATED_PROFILES = {
    "Director-Achievement": {"title": "The Executive General", "synergy": "Operational Velocity."},
    "Director-Growth": {"title": "The Restless Improver", "synergy": "Transformational Leadership."},
    "Director-Purpose": {"title": "The Mission Defender", "synergy": "Ethical Courage."},
    "Director-Connection": {"title": "The Protective Captain", "synergy": "Safe Enclosure."},
}
# Fallback generator
for c in COMM_TRAITS:
    for m in MOTIV_TRAITS:
        k = f"{c}-{m}"
        if k not in INTEGRATED_PROFILES:
            INTEGRATED_PROFILES[k] = {"title": f"The {c}-{m}", "synergy": "Balanced Approach"}

# --- HELPER FUNCTIONS FOR VISUALS (BOLD STYLE) ---

def create_comm_quadrant_chart(comm_style):
    # Vibrant colors
    colors = {"Director": "#EF4444", "Encourager": "#F59E0B", "Tracker": "#3B82F6", "Facilitator": "#10B981"}
    coords = {"Director": {"x": -0.5, "y": 0.5}, "Encourager": {"x": 0.5, "y": 0.5}, "Tracker": {"x": -0.5, "y": -0.5}, "Facilitator": {"x": 0.5, "y": -0.5}}
    
    data = coords.get(comm_style, {"x":0, "y":0})
    color = colors.get(comm_style, "#6B7280")
    
    fig = go.Figure()
    
    # Gradient/Transparent Backgrounds
    fig.add_shape(type="rect", x0=-1, y0=0, x1=0, y1=1, fillcolor="rgba(239, 68, 68, 0.1)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=1, fillcolor="rgba(245, 158, 11, 0.1)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=0, y1=0, fillcolor="rgba(59, 130, 246, 0.1)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, y0=-1, x1=1, y1=0, fillcolor="rgba(16, 185, 129, 0.1)", line_width=0, layer="below")

    fig.add_trace(go.Scatter(
        x=[data['x']], y=[data['y']],
        mode='markers+text',
        marker=dict(size=35, color=color, line=dict(width=3, color='white')),
        text=[comm_style], textposition="bottom center",
        textfont=dict(size=16, family="Outfit", weight="bold", color="#111827")
    ))

    # Bold Axis Labels
    fig.add_annotation(x=0, y=1.15, text="FAST / ACTION", showarrow=False, font=dict(size=11, color="#374151", weight="bold"))
    fig.add_annotation(x=0, y=-1.15, text="SLOW / PROCESS", showarrow=False, font=dict(size=11, color="#374151", weight="bold"))
    fig.add_annotation(x=-1.15, y=0, text="TASK", showarrow=False, textangle=-90, font=dict(size=11, color="#374151", weight="bold"))
    fig.add_annotation(x=1.15, y=0, text="PEOPLE", showarrow=False, textangle=90, font=dict(size=11, color="#374151", weight="bold"))

    fig.update_layout(
        template="plotly_white",
        xaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False, visible=False),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig

def create_motiv_gauge(motiv_style):
    color_map = {
        "Achievement": "#3B82F6", "Growth": "#10B981", 
        "Purpose": "#EF4444", "Connection": "#F59E0B"
    }
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 90,
        title = {'text': f"{motiv_style} Drive", 'font': {'size': 18, 'family': 'Outfit', 'color': '#111827'}},
        gauge = {
            'axis': {'range': [None, 100], 'visible': False},
            'bar': {'color': color_map.get(motiv_style, "gray")},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [{'range': [0, 100], 'color': "#F3F4F6"}],
        }
    ))
    fig.update_layout(
        height=220, 
        margin=dict(l=20, r=20, t=40, b=20),
        font={'family': "Outfit"},
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_integrated_compass(comm, motiv):
    comm_map = {"Director": {"x": -6, "y": 6}, "Encourager": {"x": 6, "y": 6}, "Facilitator": {"x": 6, "y": -6}, "Tracker": {"x": -6, "y": -6}}
    mot_map = {"Achievement": {"x": -3, "y": 4}, "Growth": {"x": 2, "y": 7}, "Purpose": {"x": 5, "y": 3}, "Connection": {"x": 7, "y": -2}}
    
    c_pt = comm_map.get(comm, {"x":0,"y":0})
    m_pt = mot_map.get(motiv, {"x":0,"y":0})
    final_x = (c_pt["x"] + m_pt["x"]) / 2
    final_y = (c_pt["y"] + m_pt["y"]) / 2
    
    fig = go.Figure()
    
    # Modern Quadrants
    fig.add_shape(type="rect", x0=-10, y0=0, x1=0, y1=10, fillcolor="rgba(239, 68, 68, 0.05)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, fillcolor="rgba(245, 158, 11, 0.05)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=-10, y0=-10, x1=0, y1=0, fillcolor="rgba(59, 130, 246, 0.05)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, y0=-10, x1=10, y1=0, fillcolor="rgba(16, 185, 129, 0.05)", line_width=0, layer="below")

    fig.add_hline(y=0, line_color="#D1D5DB", line_width=1)
    fig.add_vline(x=0, line_color="#D1D5DB", line_width=1)
    
    fig.add_trace(go.Scatter(
        x=[final_x], y=[final_y],
        mode='markers+text',
        marker=dict(size=30, color='#7C3AED', line=dict(width=3, color='white')),
        text=["YOU"], textposition="middle center",
        textfont=dict(color='white', size=11, weight='bold', family="Outfit")
    ))
    
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(range=[-12, 12], visible=False, fixedrange=True),
        yaxis=dict(range=[-12, 12], visible=False, fixedrange=True),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig

# --- LOGIC HELPERS ---
def get_leadership_mechanics(comm, motiv):
    mech = {}
    if comm == "Director": mech['decision'] = "Decisive & Direct (The Accelerator)."
    elif comm == "Encourager": mech['decision'] = "Intuitive & Collaborative (The Processor)."
    elif comm == "Facilitator": mech['decision'] = "Methodical & Inclusive (The Stabilizer)."
    elif comm == "Tracker": mech['decision'] = "Analytical & Cautious (The Auditor)."
    else: mech['decision'] = "Balanced."
    
    mech['influence'] = "Based on communication style."
    mech['trust'] = "Based on motivation style."
    return mech

def generate_profile_content(comm, motiv):
    combo_key = f"{comm}-{motiv}"
    c_data = COMM_PROFILES.get(comm, {})
    m_data = MOTIV_PROFILES.get(motiv, {})
    i_data = INTEGRATED_PROFILES.get(combo_key, {})

    return {
        "s1_b": c_data.get('bullets', []),
        "s2_b": c_data.get('supervising_bullets', []),
        "s3_b": m_data.get('bullets', []),
        "s4_b": m_data.get('strategies_bullets', []),
        "s5_title": i_data.get('title', f"The {comm}-{motiv}"),
        "s5_synergy": i_data.get('synergy', 'Balanced Approach'),
        "s7": "Thriving content...",
        "s8": "Struggling content...",
        "s10_b": m_data.get('celebrate_bullets', []),
        "cheat_do": c_data.get('supervising_bullets', []),
        "cheat_avoid": ["Micro-management", "Vagueness", "Ignoring input"],
        "cheat_fuel": m_data.get('strategies_bullets', []),
        "coaching": ["Question 1...", "Question 2..."]
    }

def clean_text(text):
    if not text: return ""
    return str(text).replace('\u2018', "'").replace('\u2019', "'").encode('latin-1', 'replace').decode('latin-1')

def send_pdf_via_email(to_email, subject, body, pdf_bytes, filename="Guide.pdf"):
    return True, "Email sent successfully (Simulated)"

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    return b"%PDF-1.4..."

def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    data = generate_profile_content(p_comm, p_mot)

    st.markdown("---")
    st.markdown(f"### ⚡ Supervisor Guide: {name}")
    st.caption(f"Role: {role} | Profile: {p_comm} ({s_comm}) • {p_mot} ({s_mot})")

    # --- Actions ---
    with st.container():
        ac1, ac2 = st.columns([1, 2])
        with ac1:
            st.button("📥 Download PDF", disabled=True, width=True, key="dl_btn_mock")
        with ac2:
            st.button("📧 Email PDF", disabled=True, width=True, key="em_btn_mock")

    # CHEAT SHEET (Bold)
    with st.expander("🚀 Rapid Interaction Cheat Sheet", expanded=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown("##### ✅ Do This")
            for b in data['cheat_do']: st.success(b.replace("**", ""))
        with cc2:
            st.markdown("##### ⛔ Avoid This")
            for avoid in data['cheat_avoid']: st.error(avoid)
        with cc3:
            st.markdown("##### 🔋 Fuel")
            for b in data['cheat_fuel']: st.info(b.replace("**", ""))

    st.markdown("###")

    # SECTION 1 & 2
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"1. Communication: {p_comm}")
        for b in data['s1_b']: st.markdown(f"- {b}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("2. Supervising Strategies")
        for b in data['s2_b']: st.markdown(f"- {b}")
    
    with c2:
        with st.container():
            st.markdown(f"**Style Map: {p_comm}**")
            fig = create_comm_quadrant_chart(p_comm)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("###")

    # SECTION 3 & 4
    c3, c4 = st.columns([1, 2])
    with c3:
        with st.container():
            st.markdown(f"**Primary Driver**")
            fig_g = create_motiv_gauge(p_mot)
            st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})
    with c4:
        st.subheader(f"3. Motivation: {p_mot}")
        st.markdown("- Defined by what drives them.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("4. How to Motivate")
        for b in data['s4_b']: st.markdown(f"- {b}")

    st.markdown("###")

    # SECTION 5 INTEGRATION (Card Style)
    with st.container():
        st.markdown(f"<div style='text-align: center; margin-bottom: 10px;'><span style='background: linear-gradient(90deg, #7C3AED, #DB2777); color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;'>SECTION 5: INTEGRATION</span></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; margin-top: 0;'>{data['s5_title']}</h2>", unsafe_allow_html=True)
        
        i1, i2 = st.columns([1.5, 1])
        with i1:
            st.markdown("#### 🔗 The Synergy")
            st.info(f"**{data['s5_synergy']}**")
            st.markdown("#### ⚙️ Leadership Mechanics")
            mech = get_leadership_mechanics(p_comm, p_mot)
            st.markdown(f"**1. Decision Style:** {mech['decision']}")
            st.markdown(f"**2. Influence Tactic:** {mech['influence']}")
            st.markdown(f"**3. Trust Builder:** {mech['trust']}")
        with i2:
            st.markdown(f"**🧭 Leadership Compass**")
            fig_compass = create_integrated_compass(p_comm, p_mot)
            st.plotly_chart(fig_compass, use_container_width=True, config={'displayModeBar': False})

# --- RESET HELPERS ---
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t4(): st.session_state.career = None

# ==========================================
# MAIN APP LAYOUT
# ==========================================

# --- HERO SECTION ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">LEADERSHIP INTELLIGENCE</div>
    <div class="hero-subtitle">
        Elmcrest Supervisor Command Center
    </div>
</div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

with nav_col1:
    if st.button("📝 Supervisor Guide\n\nGenerate Manuals", use_container_width=True): set_view("Supervisor's Guide")
with nav_col2:
    if st.button("🧬 Team DNA\n\nAnalyze Culture", use_container_width=True): set_view("Team DNA")
with nav_col3:
    if st.button("⚖️ Conflict Mediator\n\nResolve Issues", use_container_width=True): set_view("Conflict Mediator")
with nav_col4:
    if st.button("🚀 Career Pathfinder\n\nPlan Promotion", use_container_width=True): set_view("Career Pathfinder")

st.markdown("###")
if st.button("📈 Organization Pulse (Full Data)", use_container_width=True): set_view("Org Pulse")
st.markdown("---")

# --- VIEW CONTROLLER ---

# 1. SUPERVISOR'S GUIDE
if st.session_state.current_view == "Supervisor's Guide":
    st.subheader("📝 Supervisor's Guide")
    
    sub1, sub2, sub3 = st.tabs(["Database", "Manual Generator", "📥 Input Offline Data"])
    
    with sub1:
        if not df.empty:
            filtered_staff_list = df.to_dict('records')
            options = {f"{s['name']} ({s['role']})": s for s in filtered_staff_list}
            staff_options_list = list(options.keys())
            
            with st.container():
                sel = st.selectbox(
                    "Select Staff", 
                    staff_options_list, 
                    key="t1_staff_select",
                    placeholder="Choose a staff member..."
                )
                
                if sel:
                    d = options[sel]
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Role", d['role']); c2.metric("Style", d['p_comm']); c3.metric("Drive", d['p_mot'])
                    
                    if st.button("Generate Guide", type="primary", use_container_width=True):
                         with st.status("Analyzing Profile Data...", expanded=True) as status:
                            st.write("Processing Communication Style...")
                            time.sleep(0.3)
                            st.write("Mapping Motivation Drivers...")
                            time.sleep(0.3)
                            status.update(label="Guide Ready!", state="complete", expanded=False)
                         display_guide(d['name'], d['role'], d['p_comm'], d['s_comm'], d['p_mot'], d['s_mot'])

    st.button("Reset", key="reset_t1", on_click=reset_t1)
    
    with sub2:
        st.info("Manual Generator logic here...")

    with sub3:
        with st.container():
             st.markdown("### 📥 Input Offline Results")
             with st.form("offline_input_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.text_input("Staff Name (Required)")
                    st.selectbox("Role", ["YDP", "Shift Supervisor"])
                with col_b:
                    st.selectbox("Primary Communication", COMM_TRAITS)
                    st.selectbox("Primary Motivation", MOTIV_TRAITS)
                st.markdown("---")
                st.form_submit_button("💾 Save to Database", type="primary")

# 2. TEAM DNA
elif st.session_state.current_view == "Team DNA":
    st.subheader("🧬 Team DNA")
    if not df.empty:
        with st.container():
            teams = st.multiselect("Select Team Members", df['name'].tolist(), key="t2_team_select")
        
        if teams:
            tdf = df[df['name'].isin(teams)]
            c1, c2 = st.columns(2)
            with c1:
                with st.container():
                    st.markdown("##### Communication Mix")
                    st.plotly_chart(px.pie(names=["Director", "Encourager"], values=[50, 50], hole=0.5, color_discrete_sequence=["#EF4444", "#F59E0B"]), use_container_width=True)
            with c2:
                with st.container():
                    st.markdown("##### Motivation Drivers")
                    st.plotly_chart(px.bar(x=["Achievement", "Growth"], y=[60, 40], color_discrete_sequence=["#3B82F6"]), use_container_width=True)
            
            st.button("Clear", on_click=reset_t2)

# 3. CONFLICT MEDIATOR
elif st.session_state.current_view == "Conflict Mediator":
    st.subheader("⚖️ Conflict Mediator")
    with st.container():
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Select Supervisor", ["User A", "User B"], key="p1")
        p2 = c2.selectbox("Select Staff", ["Staff X", "Staff Y"], key="p2")

    if p1 and p2:
        st.info(f"Conflict resolution logic for {p1} vs {p2}...")

# 4. CAREER PATHFINDER
elif st.session_state.current_view == "Career Pathfinder":
    st.subheader("🚀 Career Pathfinder")
    with st.container():
        c1, c2 = st.columns(2)
        c1.selectbox("Candidate", ["Staff A", "Staff B"], key="career")
        c2.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor"], key="career_target")
    
    st.button("Reset", key="reset_t4", on_click=reset_t4)

# 5. ORG PULSE
elif st.session_state.current_view == "Org Pulse":
    st.subheader("📈 Organization Pulse")
    with st.container():
        st.metric("Total Staff", len(df))
    st.divider()
    c_a, c_b = st.columns(2)
    with c_a:
        with st.container():
            st.markdown("##### Communication Mix")
            st.plotly_chart(px.pie(names=["Director", "Tracker"], values=[30, 70], hole=0.5, color_discrete_sequence=["#EF4444", "#3B82F6"]), use_container_width=True)
