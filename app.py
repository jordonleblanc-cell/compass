import streamlit as st
import random
import requests
import time
from fpdf import FPDF
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Elmcrest Compass", page_icon="🧭", layout="centered")

# --- 2. CSS STYLING (Modern Glassmorphism) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --primary: #015bad;
            --secondary: #51c3c5;
            --accent: #b9dca4;
            --bg-gradient-light: radial-gradient(circle at top left, #e0f2fe 0%, #ffffff 40%, #dcfce7 100%);
            --bg-gradient-dark: radial-gradient(circle at top left, #0f172a 0%, #1e293b 40%, #064e3b 100%);
            --text-main: #0f172a;
            --text-sub: #475569;
            --card-bg: rgba(255, 255, 255, 0.85);
            --card-border: rgba(255, 255, 255, 0.6);
            --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
            --input-bg: #f8fafc;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --text-main: #f1f5f9;
                --text-sub: #94a3b8;
                --card-bg: rgba(30, 41, 59, 0.85);
                --card-border: rgba(255, 255, 255, 0.1);
                --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.3);
                --input-bg: #0f172a;
            }
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        /* Main App Background */
        .stApp {
            background-image: var(--bg-gradient-light);
            background-attachment: fixed;
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-image: var(--bg-gradient-dark); }
        }

        /* Headers */
        h1, h2, h3 {
            color: var(--primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        p, label, li, .stMarkdown {
            color: var(--text-main) !important;
            line-height: 1.6;
        }

        /* Glassmorphism Container */
        .block-container {
            padding: 3rem 2rem;
            max-width: 800px;
            background-color: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            margin-top: 2rem;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            width: 100%;
            box-shadow: 0 4px 12px rgba(1, 91, 173, 0.2);
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(1, 91, 173, 0.3);
            opacity: 0.95;
        }

        /* Inputs */
        .stTextInput input, .stSelectbox [data-baseweb="select"] {
            background-color: var(--input-bg);
            border-radius: 12px;
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 0.5rem;
        }

        /* Centered Radio Buttons */
        .stRadio {
            background-color: transparent;
            padding: 10px 0 0 0; /* Reduced padding */
            display: flex;
            justify-content: center;
        }
        .stRadio [role="radiogroup"] {
            justify-content: space-between;
            width: 100%;
            max-width: 400px; /* Limit width for better alignment */
            margin: 0 auto;
        }
        div[role="radiogroup"] > label > div:first-of-type {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }
        
        /* Assessment Question Styling */
        .question-text {
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--text-main);
        }
        
        /* Labels for Scale */
        .scale-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-sub);
            max-width: 420px;
            margin: 0 auto;
            padding-top: 5px;
        }

        /* Custom Cards & Bars */
        .info-card {
            background-color: var(--input-bg);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--card-border);
        }
        .score-container {
            background-color: var(--input-bg);
            border-radius: 8px;
            height: 12px;
            width: 100%;
            margin-top: 5px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .score-fill {
            height: 100%;
            border-radius: 8px;
            background: linear-gradient(90deg, var(--secondary), var(--primary));
            transition: width 1s ease-in-out;
        }
        
        hr {
            margin: 2rem 0;
            border: 0;
            border-top: 1px solid var(--card-border);
            opacity: 0.5;
        }
        
        /* Alerts */
        .stAlert { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTS & DATA ---

ROLE_RELATIONSHIP_LABELS = {
    "Program Supervisor": {"directReportsLabel": "Shift Supervisors", "youthLabel": "youth on your units", "supervisorLabel": "Residential Programs Manager", "leadershipLabel": "agency leadership"},
    "Shift Supervisor": {"directReportsLabel": "YDPs", "youthLabel": "youth you support", "supervisorLabel": "Program Supervisor", "leadershipLabel": "agency leadership"},
    "YDP": {"directReportsLabel": "peers", "youthLabel": "youth in your care", "supervisorLabel": "Shift Supervisor", "leadershipLabel": "Program Supervisor"}
}

COMM_QUESTIONS = [
    {"id": "comm1", "text": "When a situation becomes chaotic, I naturally step in and start directing people toward a plan.", "style": "Director"},
    {"id": "comm2", "text": "I feel most effective when I can make quick decisions and move the team forward.", "style": "Director"},
    {"id": "comm3", "text": "In a crisis, I’d rather take charge and apologize later than wait too long for consensus.", "style": "Director"},
    {"id": "comm4", "text": "If expectations are unclear, I tend to define them myself and communicate them to others.", "style": "Director"},
    {"id": "comm5", "text": "I’m comfortable giving direct feedback, even when it may be hard for someone to hear.", "style": "Director"},
    {"id": "comm6", "text": "I pay close attention to the emotional tone of the team and lift people up when morale is low.", "style": "Encourager"},
    {"id": "comm7", "text": "I often use encouragement, humor, or positive energy to help staff get through hard shifts.", "style": "Encourager"},
    {"id": "comm8", "text": "I notice small wins and like to name them out loud so people know they’re seen.", "style": "Encourager"},
    {"id": "comm9", "text": "I tend to talk things through with people rather than just giving short instructions.", "style": "Encourager"},
    {"id": "comm10", "text": "I’m often the one coworkers come to when they need to vent or feel understood.", "style": "Encourager"},
    {"id": "comm11", "text": "I’m good at slowing conversations down so that different perspectives can be heard.", "style": "Facilitator"},
    {"id": "comm12", "text": "I try to stay calm and balanced when others are escalated or upset.", "style": "Facilitator"},
    {"id": "comm13", "text": "I often find myself summarizing what others are saying to move toward shared understanding.", "style": "Facilitator"},
    {"id": "comm14", "text": "I prefer to build agreement and buy-in rather than rely only on authority.", "style": "Facilitator"},
    {"id": "comm15", "text": "I pay attention to process (how we talk to each other) as much as the final decision.", "style": "Facilitator"},
    {"id": "comm16", "text": "I naturally notice details in documentation, routines, or schedules others overlook.", "style": "Tracker"},
    {"id": "comm17", "text": "I feel responsible for keeping procedures on track, even when others get distracted.", "style": "Tracker"},
    {"id": "comm18", "text": "I tend to ask clarifying questions when expectations or instructions feel vague.", "style": "Tracker"},
    {"id": "comm19", "text": "I’m more comfortable when I know exactly who is doing what and when it needs to be done.", "style": "Tracker"},
    {"id": "comm20", "text": "If something seems out of compliance, it really sticks with me until it’s addressed.", "style": "Tracker"},
]

MOTIVATION_QUESTIONS = [
    {"id": "mot1", "text": "I feel energized when I’m learning new skills or being stretched in healthy ways.", "style": "Growth"},
    {"id": "mot2", "text": "It’s important to me that I can look back and see I’m becoming more effective over time.", "style": "Growth"},
    {"id": "mot3", "text": "When I feel stuck in the same patterns with no development, my motivation drops.", "style": "Growth"},
    {"id": "mot4", "text": "I appreciate feedback that helps me improve, even if it’s uncomfortable in the moment.", "style": "Growth"},
    {"id": "mot5", "text": "Access to training, coaching, or new responsibilities matters a lot for my commitment.", "style": "Growth"},
    {"id": "mot6", "text": "I need to feel that what I’m doing connects to a bigger purpose for youth and families.", "style": "Purpose"},
    {"id": "mot7", "text": "I feel strongest when my work lines up with my values about dignity, justice, and safety.", "style": "Purpose"},
    {"id": "mot8", "text": "It’s hard for me to stay engaged when policies don’t make sense for the youth we serve.", "style": "Purpose"},
    {"id": "mot9", "text": "I’m often the one raising questions about whether a decision is really best for kids.", "style": "Purpose"},
    {"id": "mot10", "text": "I feel proudest when I can see real positive impact, not just tasks checked off.", "style": "Purpose"},
    {"id": "mot11", "text": "Having strong relationships with coworkers makes a big difference in my energy.", "style": "Connection"},
    {"id": "mot12", "text": "When the team feels disconnected, I feel it in my body and it’s harder to stay motivated.", "style": "Connection"},
    {"id": "mot13", "text": "I value feeling known and supported by my team and supervisor, not just evaluated.", "style": "Connection"},
    {"id": "mot14", "text": "I’m often thinking about the emotional climate of the unit and how people are relating.", "style": "Connection"},
    {"id": "mot15", "text": "I’m more likely to go above and beyond when I feel a sense of belonging.", "style": "Connection"},
    {"id": "mot16", "text": "I like having clear goals and being able to see, in concrete ways, when we’ve met them.", "style": "Achievement"},
    {"id": "mot17", "text": "I feel satisfied when I can see that my effort led to specific improvements.", "style": "Achievement"},
    {"id": "mot18", "text": "It’s frustrating when expectations keep shifting and I’m not sure what success looks like.", "style": "Achievement"},
    {"id": "mot19", "text": "I appreciate data, tracking tools, or simple dashboards that help show progress.", "style": "Achievement"},
    {"id": "mot20", "text": "I’m motivated by being trusted with projects where outcomes are clearly defined.", "style": "Achievement"},
]

COMM_PROFILES = {
    "Director": {"name": "Director Communicator", "tagline": "The Decisive Driver", "overview": "You move quickly toward action. In high-pressure moments, you step in and organize.", "conflictImpact": "May become blunt, controlling, or impatient under stress.", "traumaStrategy": "Your clear, firm presence feels regulating when paired with calm tone.", "roleTips": {"Program Supervisor": {"directReports": "Pause before final decisions. Ask: 'What are we not seeing?'", "youth": "Pair structure with choice. Offer two safe options.", "supervisor": "Frame strong ideas as joint problem-solving.", "leadership": "Name both opportunities and risks."}, "Shift Supervisor": {"directReports": "Emphasize you are directing the plan, not judging the person.", "youth": "Keep commands simple and tone steady.", "supervisor": "Be upfront about capacity.", "leadership": "Highlight what frontline staff are seeing."}, "YDP": {"directReports": "Ask 'Who can own what?' instead of assigning everything.", "youth": "Set clear limits and then stay present.", "supervisor": "Bring concise summaries of what's happening.", "leadership": "Speak plainly about what works and what doesn't."}}},
    "Encourager": {"name": "Encourager Communicator", "tagline": "The Relational Energizer", "overview": "You bring warmth, optimism, and emotional presence. You act as the emotional glue.", "conflictImpact": "May avoid hard truths or personalize feedback under stress.", "traumaStrategy": "Your ability to notice small wins helps youth feel seen.", "roleTips": {"Program Supervisor": {"directReports": "Balance encouragement with accountability.", "youth": "Validate feelings first, then move to expectations.", "supervisor": "Share the emotional climate of the cottage.", "leadership": "Highlight stories of human impact."}, "Shift Supervisor": {"directReports": "Be the safe person who also holds the line.", "youth": "Ask: 'What did you need that you didn't get?'", "supervisor": "Share where staff are struggling emotionally.", "leadership": "Name how culture influences motivation."}, "YDP": {"directReports": "Offer specific encouragement, not just general praise.", "youth": "Combine warmth with clear boundaries.", "supervisor": "Be honest when you are feeling overwhelmed.", "leadership": "Share stories of how relational care changes outcomes."}}},
    "Facilitator": {"name": "Facilitator Communicator", "tagline": "The Calm Bridge", "overview": "You listen deeply and seek fairness. You care about process as much as results.", "conflictImpact": "May delay decisions or absorb tension silently under stress.", "traumaStrategy": "Your steady presence helps de-escalate tense dynamics.", "roleTips": {"Program Supervisor": {"directReports": "Invite perspectives, then close with a clear decision.", "youth": "Reflect feelings back in simple language.", "supervisor": "Summarize themes you are hearing.", "leadership": "Translate frontline realities into proposals."}, "Shift Supervisor": {"directReports": "Create space for input, then name next steps.", "youth": "Use brief, validating statements.", "supervisor": "Share where you are holding tension.", "leadership": "Name how the team is functioning relationally."}, "YDP": {"directReports": "De-escalate by summarizing what each person is saying.", "youth": "Ask calm questions to open conversation.", "supervisor": "Share your read on the emotional climate.", "leadership": "Ask thoughtful questions to help planning."}}},
    "Tracker": {"name": "Tracker Communicator", "tagline": "The Structured Guardian", "overview": "You notice details, patterns, and risks. You protect the team through consistency.", "conflictImpact": "May become rigid, critical, or perfectionistic under stress.", "traumaStrategy": "Your consistency makes the environment predictable and safe.", "roleTips": {"Program Supervisor": {"directReports": "Share the 'why' behind procedures.", "youth": "Link routines to safety and trust.", "supervisor": "Bring prioritized lists of needs.", "leadership": "Translate compliance risks into practical steps."}, "Shift Supervisor": {"directReports": "Turn corrections into coaching.", "youth": "Present structure as something you do *with* them.", "supervisor": "Share where systems are breaking down.", "leadership": "Share examples of how tools reduce stress."}, "YDP": {"directReports": "Share reminders as partnership.", "youth": "Use predictable routines to lower anxiety.", "supervisor": "Bring specific examples, not general complaints.", "leadership": "Help design systems that work on the floor."}}}
}

MOTIVATION_PROFILES = {
    "Growth": {"name": "Growth Motivation", "tagline": "The Learner/Builder", "summary": "Energized by new skills and challenges. Stagnation is draining.", "boosters": ["Stretch assignments", "Coaching on skills", "New responsibilities"], "killers": ["Repetitive tasks", "Being ignored", "No development path"], "roleSupport": {"Program Supervisor": "Connect goals to career path.", "Shift Supervisor": "Practice new skills on shift.", "YDP": "Ask for realistic growth goals."}},
    "Purpose": {"name": "Purpose Motivation", "tagline": "The Mission Keeper", "summary": "Driven by meaning and values. Wants work to match beliefs.", "boosters": ["Connection to mission", "Ethical alignment", "Voice in decisions"], "killers": ["Bureaucracy", "Unjust policies", "Cynicism"], "roleSupport": {"Program Supervisor": "Collaborate on policy adjustments.", "Shift Supervisor": "Explain 'why' behind routines.", "YDP": "Name your values to your supervisor."}},
    "Connection": {"name": "Connection Motivation", "tagline": "The Community Builder", "summary": "Energized by relationships and team cohesion. Belonging is key.", "boosters": ["Team bonding", "Personal check-ins", "Shared wins"], "killers": ["Isolation", "Unresolved conflict", "Cold leadership"], "roleSupport": {"Program Supervisor": "Build peer support networks.", "Shift Supervisor": "Create shift rituals.", "YDP": "Flag isolation early."}},
    "Achievement": {"name": "Achievement Motivation", "tagline": "The Results Architect", "summary": "Cares about clear goals and concrete progress.", "boosters": ["Clear metrics", "Checklists", "Recognition of output"], "killers": ["Vague goals", "Moving goalposts", "Lack of recognition"], "roleSupport": {"Program Supervisor": "Co-design metrics.", "Shift Supervisor": "Set unit goals.", "YDP": "Define 'a good shift' concretely."}}
}

INTEGRATED_PROFILES = {
    "Director-Growth": {"title": "Director + Growth – The Driven Developer", "summary": "You lean into leadership and action, and you want to keep getting better at it.", "strengths": ["Decisive action", "Rapid learning", "Ambitious"], "watchouts": ["Impatience", "Burnout"]},
    "Director-Purpose": {"title": "Director + Purpose – The Ethical Guardian", "summary": "You make firm decisions through a values lens.", "strengths": ["Advocacy", "Clarity", "Integrity"], "watchouts": ["Rigidity", "Righteous anger"]},
    "Director-Connection": {"title": "Director + Connection – The Relational Driver", "summary": "You lead with energy and care about how the team is doing together.", "strengths": ["Mobilizing", "Protective", "Direct"], "watchouts": ["Overpowering", "Taking conflict personally"]},
    "Director-Achievement": {"title": "Director + Achievement – The Results Leader", "summary": "You want clear goals and you’re willing to lead the way to reach them.", "strengths": ["Execution", "Focus", "Speed"], "watchouts": ["Steamrolling", "Ignoring feelings"]},
    # (Add other combos if needed, fallback handles them dynamically)
}

# --- 4. FUNCTIONS ---

def normalize_role_key(role):
    if not role: return "YDP"
    r = role.lower()
    if "program" in r: return "Program Supervisor"
    if "shift" in r: return "Shift Supervisor"
    return "YDP"

def get_top_two(scores):
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    primary = sorted_scores[0][0] if len(sorted_scores) > 0 else None
    secondary = sorted_scores[1][0] if len(sorted_scores) > 1 else None
    return primary, secondary

def clean_text(text):
    if not text: return ""
    return text.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '-').replace('—', '-').encode('latin-1', 'replace').decode('latin-1')

def submit_to_google_sheets(data, action="save"):
    # Sends data to Google Scripts
    url = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"
    data["action"] = action
    try:
        requests.post(url, json=data)
        return True
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

def send_email_via_smtp(to_email, subject, body):
    try:
        sender_email = st.secrets["EMAIL_USER"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

def generate_text_report(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    lines = [f"ELMCREST COMPASS PROFILE FOR {user_info['name'].upper()}", "="*40, ""]
    
    # Comm
    lines.append(f"COMMUNICATION STYLE: {comm_prof['name']}")
    lines.append(f"Tagline: {comm_prof['tagline']}")
    lines.append(f"Overview: {comm_prof['overview']}")
    lines.append(f"Under Stress: {comm_prof['conflictImpact']}")
    lines.append("")
    lines.append("ROLE TIPS:")
    tips = comm_prof['roleTips'][role_key]
    lines.append(f"* With {role_labels['directReportsLabel']}: {tips['directReports']}")
    lines.append(f"* With {role_labels['youthLabel']}: {tips['youth']}")
    lines.append(f"* With {role_labels['supervisorLabel']}: {tips['supervisor']}")
    lines.append(f"* With {role_labels['leadershipLabel']}: {tips['leadership']}")
    lines.append("")
    
    # Motiv
    lines.append(f"MOTIVATION DRIVER: {mot_prof['name']}")
    lines.append(f"Tagline: {mot_prof['tagline']}")
    lines.append(f"Summary: {mot_prof['summary']}")
    lines.append("Boosters (Energizers):")
    for b in mot_prof['boosters']: lines.append(f"* {b}")
    lines.append("Drainers (De-energizers):")
    for k in mot_prof['killers']: lines.append(f"* {k}")
    lines.append(f"Support Needed: {mot_prof['roleSupport'][role_key]}")
    lines.append("")
    
    # Integrated
    if int_prof:
        lines.append(f"INTEGRATED PROFILE: {int_prof['title']}")
        lines.append(int_prof['summary'])
        lines.append("Strengths: " + ", ".join(int_prof['strengths']))
        lines.append("Watch-outs: " + ", ".join(int_prof['watchouts']))
        
    return "\n".join(lines)

def create_pdf(user_info, results, comm_prof, mot_prof, int_prof, role_key, role_labels):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (1, 91, 173)
    black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Compass Profile", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"Prepared for: {user_info['name']} | Role: {user_info['role']}"), ln=True, align='C')
    pdf.ln(5)
    
    # Comm
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, clean_text(f"Communication: {comm_prof['name']}"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*black)
    pdf.multi_cell(0, 6, clean_text(comm_prof['overview']))
    pdf.ln(3)
    
    # Role Tips
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "Role-Specific Tips:", ln=True, fill=True)
    tips = comm_prof['roleTips'][role_key]
    pdf.set_font("Arial", '', 11)
    pdf.ln(2)
    pdf.multi_cell(0, 6, clean_text(f"- Direct Reports: {tips['directReports']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Youth: {tips['youth']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Supervisor: {tips['supervisor']}"))
    pdf.multi_cell(0, 6, clean_text(f"- Leadership: {tips['leadership']}"))
    pdf.ln(5)

    # Motiv
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, clean_text(f"Motivation: {mot_prof['name']}"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(*black)
    pdf.multi_cell(0, 6, clean_text(mot_prof['summary']))
    pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Boosters (Energizers):", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    for b in mot_prof['boosters']: pdf.multi_cell(0, 6, clean_text(f"- {b}"))
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Drainers (De-energizers):", ln=True, fill=True)
    pdf.set_font("Arial", '', 11)
    for k in mot_prof['killers']: pdf.multi_cell(0, 6, clean_text(f"- {k}"))
    pdf.ln(5)
    
    # Integrated
    if int_prof:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(*blue)
        pdf.cell(0, 10, clean_text(f"Integrated: {int_prof['title']}"), ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(*black)
        pdf.multi_cell(0, 6, clean_text(int_prof['summary']))
        pdf.ln(2)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, "Strengths:", ln=True, fill=True)
        pdf.set_font("Arial", '', 11)
        for s in int_prof['strengths']: pdf.multi_cell(0, 6, clean_text(f"- {s}"))
    
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI HELPERS ---
def show_brand_header(subtitle):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.markdown("<div style='width:60px;height:60px;background:linear-gradient(135deg,#015bad,#51c3c5);border-radius:14px;color:white;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.4rem;box-shadow:0 4px 10px rgba(1,91,173,0.3);'>EC</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 60px;">
            <div style="color: #015bad; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.03em;">ELMCREST COMPASS</div>
            <div style="color: #64748b; font-size: 0.95rem; font-weight: 500;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def draw_score_bar(label, value, max_value=25):
    pct = (value / max_value) * 100
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.85rem; font-weight: 600; color: #475569;">
            <span>{label}</span>
            <span>{value}</span>
        </div>
        <div class="score-container">
            <div class="score-fill" style="width: {pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. APP LOGIC ---

if 'step' not in st.session_state:
    st.session_state.step = 'intro'
    comm_q, motiv_q = COMM_QUESTIONS.copy(), MOTIVATION_QUESTIONS.copy()
    random.shuffle(comm_q); random.shuffle(motiv_q)
    st.session_state.shuffled_comm = comm_q
    st.session_state.shuffled_motiv = motiv_q
    st.session_state.answers_comm = {}
    st.session_state.answers_motiv = {}
    st.session_state.user_info = {}

# --- INTRO ---
if st.session_state.step == 'intro':
    show_brand_header("Communication & Motivation Snapshot")
    st.markdown("#### 👋 Welcome")
    st.info("This assessment helps you understand your natural patterns at work. Your insights will shape a personalized profile built to support your growth.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("intro_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name", placeholder="e.g. Jane Doe")
        email = c2.text_input("Email Address", placeholder="e.g. jane@elmcrest.org")
        role = st.selectbox("Current Role", ["Program Supervisor", "Shift Supervisor", "YDP"], index=None, placeholder="Select your role...")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("Start Assessment →"):
            if not name or not email or not role: st.error("Please complete all fields.")
            else:
                st.session_state.user_info = {"name": name, "email": email, "role": role}
                st.session_state.step = 'comm'
                st.rerun()

# --- COMM ---
elif st.session_state.step == 'comm':
    show_brand_header("Part 1: Communication")
    st.progress(33)
    st.markdown("**Instructions:** Choose how strongly each statement fits you most days.")
    
    with st.form("comm_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_comm):
            # Card-like container for each question
            with st.container(border=True):
                st.markdown(f"<div class='question-text'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
                
                # Radio buttons
                answers[q['id']] = st.radio(
                    f"q_{i}", 
                    options=[1, 2, 3, 4, 5], 
                    horizontal=True, 
                    index=None, 
                    key=f"c_{q['id']}", 
                    label_visibility="collapsed"
                )
                
                # Scale labels inside the card
                st.markdown("""
                <div class="scale-labels">
                    <span>Strongly Disagree</span>
                    <span>Neutral</span>
                    <span>Strongly Agree</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation Logic
        if st.form_submit_button("Continue to Motivation →"):
            missed = [q['id'] for q in st.session_state.shuffled_comm if answers.get(q['id']) is None]
            if missed:
                st.error(f"Please answer all questions. You missed {len(missed)} questions.")
            else:
                st.session_state.answers_comm = answers
                st.session_state.step = 'motiv'
                st.rerun()

# --- MOTIV ---
elif st.session_state.step == 'motiv':
    show_brand_header("Part 2: Motivation")
    st.progress(66)
    st.markdown("**Instructions:** Focus on what keeps you engaged or drains you.")

    with st.form("motiv_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_motiv):
            # Card-like container for each question
            with st.container(border=True):
                st.markdown(f"<div class='question-text'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
                
                # Radio buttons
                answers[q['id']] = st.radio(
                    f"mq_{i}", 
                    options=[1, 2, 3, 4, 5], 
                    horizontal=True, 
                    index=None, 
                    key=f"m_{q['id']}", 
                    label_visibility="collapsed"
                )
                
                # Scale labels inside the card
                st.markdown("""
                <div class="scale-labels">
                    <span>Strongly Disagree</span>
                    <span>Neutral</span>
                    <span>Strongly Agree</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation Logic
        if st.form_submit_button("Complete & View Profile →"):
            missed = [q['id'] for q in st.session_state.shuffled_motiv if answers.get(q['id']) is None]
            if missed:
                st.error(f"Please answer all questions. You missed {len(missed)} questions.")
            else:
                st.session_state.answers_motiv = answers
                st.session_state.step = 'processing'
                st.rerun()

# --- PROCESSING ---
elif st.session_state.step == 'processing':
    c_scores = {k:0 for k in COMM_PROFILES}
    m_scores = {k:0 for k in MOTIVATION_PROFILES}
    for q in COMM_QUESTIONS: c_scores[q['style']] += st.session_state.answers_comm[q['id']]
    for q in MOTIVATION_QUESTIONS: m_scores[q['style']] += st.session_state.answers_motiv[q['id']]
    
    p_comm, s_comm = get_top_two(c_scores)
    p_mot, s_mot = get_top_two(m_scores)
    
    st.session_state.results = {
        "primaryComm": p_comm, "secondaryComm": s_comm,
        "primaryMotiv": p_mot, "secondaryMotiv": s_mot,
        "commScores": c_scores, "motivScores": m_scores
    }
    
    payload = {
        "name": st.session_state.user_info['name'],
        "email": st.session_state.user_info['email'],
        "role": st.session_state.user_info['role'],
        "scores": st.session_state.results
    }
    
    with st.spinner("Analyzing results..."):
        submit_to_google_sheets(payload, action="save")
        time.sleep(1.0)
    
    st.session_state.step = 'results'
    st.rerun()

# --- RESULTS ---
elif st.session_state.step == 'results':
    st.progress(100)
    res = st.session_state.results
    user = st.session_state.user_info
    role_key = normalize_role_key(user['role'])
    role_labels = ROLE_RELATIONSHIP_LABELS[role_key]
    
    show_brand_header(f"Profile for {user['name']}")
    
    comm_prof = COMM_PROFILES[res['primaryComm']]
    mot_prof = MOTIVATION_PROFILES[res['primaryMotiv']]
    int_key = f"{res['primaryComm']}-{res['primaryMotiv']}"
    int_prof = INTEGRATED_PROFILES.get(int_key)

    # --- ACTION BAR ---
    c1, c2 = st.columns(2)
    with c1:
        pdf_bytes = create_pdf(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="Elmcrest_Profile.pdf", mime="application/pdf")
    with c2:
        if st.button("📧 Email Me Full Report"):
            full_text = generate_text_report(user, res, comm_prof, mot_prof, int_prof, role_key, role_labels)
            with st.spinner("Sending..."):
                if send_email_via_smtp(user['email'], "Your Elmcrest Compass Profile", full_text):
                    st.success("Sent!")

    st.markdown("---")

    # --- COMM SECTION ---
    st.markdown(f"### 🗣️ {comm_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#015bad;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{comm_prof['tagline']}</div>
        <div style="line-height:1.6;">{comm_prof['overview']}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        with st.expander("Detailed Role Tips", expanded=True):
            tips = comm_prof['roleTips'][role_key]
            st.markdown(f"**With {role_labels['directReportsLabel']}:** {tips['directReports']}")
            st.markdown(f"**With Youth:** {tips['youth']}")
            st.markdown(f"**With Supervisor:** {tips['supervisor']}")
            st.markdown(f"**With Leadership:** {tips['leadership']}")
        st.warning(f"**Under Stress:** {comm_prof['conflictImpact']}")
        st.success(f"**Trauma Strategy:** {comm_prof['traumaStrategy']}")

    with col2:
        st.markdown("**Score Breakdown**")
        for style, score in res['commScores'].items():
            draw_score_bar(style, score)

    st.markdown("---")

    # --- MOTIV SECTION ---
    st.markdown(f"### 🔋 {mot_prof['name']}")
    st.markdown(f"""
    <div class="info-card">
        <div style="color:#015bad;font-weight:700;margin-bottom:5px;text-transform:uppercase;font-size:0.85rem;">{mot_prof['tagline']}</div>
        <div style="line-height:1.6;">{mot_prof['summary']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    c_a, c_b = st.columns(2)
    with c_a: 
        st.markdown("#### ✅ Boosters")
        for b in mot_prof['boosters']: st.write(f"• {b}")
    with c_b:
        st.markdown("#### 🔻 Drainers")
        for k in mot_prof['killers']: st.write(f"• {k}")
    
    st.info(f"**Support Needed:** {mot_prof['roleSupport'][role_key]}")

    # --- INTEGRATED SECTION ---
    if int_prof:
        st.markdown("---")
        st.markdown(f"### 🔗 Integrated: {int_prof['title']}")
        st.write(int_prof['summary'])
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("**Key Strengths**")
            for s in int_prof['strengths']: st.write(f"• {s}")
        with ic2:
            st.markdown("**Watch-outs**")
            for w in int_prof['watchouts']: st.write(f"• {w}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
