import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- Configuration ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- Constants ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

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

# --- RICH CONTENT DICTIONARIES ---

COMM_PROFILES = {
    "Director": {
        "s1_profile": {
            "text": "This staff member communicates primarily as a Director. They lead with clarity, structure, and urgency. In the complex environment of residential care, they act as a stabilizing force during chaos, naturally stepping up to fill leadership vacuums. They process information quickly and prefer to move to action immediately, often becoming impatient with long deliberations or ambiguous processes.",
            "bullets": ["Prioritizes efficiency and results over process.", "Speaks in headlines; brief and to the point.", "Comfortable making unpopular decisions if they believe it solves the problem.", "Views competence as the primary language of trust."]
        },
        "s2_supervising": {
            "text": "Supervising a Director requires a high-trust, low-friction approach. They respect leaders who are direct, competent, and concise. They will likely disengage if they feel micromanaged or if meetings feel like 'talking in circles' without resolution. Your goal is to be a remover of obstacles, allowing them to execute.",
            "bullets": ["Be concise: Lead with the bottom line, then fill in details.", "Grant autonomy: Define the 'what' clearly, but let them own the 'how'.", "Expect pushback: They often view debate as healthy problem-solving, not insubordination.", "Focus on outcomes: Measure their success by results, not just hours or methods."]
        },
        "s8_struggling": {
            "text": "Under stress, the Director's greatest strength (decisiveness) becomes their greatest liability (domination). When they feel a loss of control or perceive incompetence around them, they may double down on command-and-control tactics, alienating their team and reducing psychological safety.",
            "bullets": ["Steamrolling quieter voices in meetings.", " becoming visibly irritable or sarcastic with 'slow' processes.", "Making unilateral decisions without consulting stakeholders.", "Sacrificing long-term relationships for short-term compliance."]
        },
        "s11_coaching": [
            "What is the risk of moving this fast? Who might we be leaving behind?",
            "How can you frame this directive so the team feels supported rather than just commanded?",
            "I noticed you made that call quickly. Walk me through the alternatives you considered.",
            "Who haven't we heard from yet? What perspective might the quietest person in the room have?",
            "If you had to achieve this result without giving a single order, how would you do it?",
            "How is your current pace affecting the morale of your newest staff members?",
            "What is the difference between being 'right' and being 'effective' in this situation?",
            "How can you use your authority to empower someone else to lead this?",
            "You value competence. How are you teaching others to be competent rather than just fixing it for them?",
            "What emotional wake are you leaving behind you right now?"
        ],
        "s12_advancement": {
            "text": "For a Director to advance to senior leadership, they must shift from 'Command' to 'Influence'. They are likely already good at execution; their gap is political capital and consensus building. They need to learn that slowing down to bring people along is not a waste of time, but a strategic investment in sustainability.",
            "bullets": ["Assign cross-departmental projects where they have no direct authority and must use persuasion.", "Challenge them to mentor a 'Facilitator' type, forcing them to value a different style.", "Require them to present 3 options for a decision rather than just their favorite one.", "Focus development on 'soft skills': active listening, validation, and patience."]
        }
    },
    "Encourager": {
        "s1_profile": {
            "text": "This staff member communicates primarily as an Encourager. They act as the emotional glue of the team, leading with warmth, optimism, and high emotional intelligence. They are naturally attuned to the 'vibe' of the unit and will prioritize the well-being of staff and youth above almost everything else. They are persuasive, engaging, and often the person others go to for venting or support.",
            "bullets": ["Prioritizes relationships and harmony over efficiency.", "Highly empathetic; feels the emotions of the room.", "Communicates through stories and connection.", "Views emotional safety as the prerequisite for work."]
        },
        "s2_supervising": {
            "text": "Supervising an Encourager requires a relational investment. If you jump straight to business without checking in on them as a person, they may feel undervalued or commoditized. They need to know you care about them. Feedback must be delivered carefully, as they often struggle to separate professional critique from personal rejection.",
            "bullets": ["Connect first: Spend 5 minutes on rapport before tackling the agenda.", "Validate the invisible work: Acknowledge the emotional labor they do for the team.", "Frame feedback as 'growth': Show how changing a behavior helps them help others.", "Provide structure: They may need help organizing their ideas and time."]
        },
        "s8_struggling": {
            "text": "Under stress, the Encourager's desire for harmony can lead to conflict avoidance and a lack of accountability. They may struggle to hold boundaries with youth or staff because they don't want to be 'mean.' This can result in a chaotic environment where rules are applied inconsistently based on feelings.",
            "bullets": ["avoiding necessary hard conversations.", "Venting or gossiping as a way to manage stress.", "Disorganization or missed deadlines due to social distractions.", "Taking youth behaviors personally or becoming emotionally enmeshed."]
        },
        "s11_coaching": [
            "How can you deliver this hard truth while still remaining kind?",
            "Are we prioritizing popularity over effectiveness in this situation?",
            "What boundaries do you need to set right now to protect your own energy?",
            "If you avoid this conflict today, what is the cost to the team next week?",
            "How does holding this standard actually create safety for the youth?",
            "I know you want to help, but are you enabling them or empowering them?",
            "What is the data telling us, regardless of how we feel about it?",
            "How can you separate your personal worth from this professional outcome?",
            "You are carrying a lot of the team's emotions. Who is carrying yours?",
            "What is one thing you need to say 'No' to this week?"
        ],
        "s12_advancement": {
            "text": "For an Encourager to advance, they must master the 'Business' side of care. Their high EQ is a massive asset, but it must be backed by operational reliability. They need to learn that clarity and accountability are forms of kindness. Their growth lies in becoming a leader who is respected for their competence, not just liked for their personality.",
            "bullets": ["Assign responsibility for a compliance audit or budget management.", "Role-play disciplinary conversations until they can deliver them without apologizing.", "Challenge them to organize a project using a project management tool, not just conversation.", "Focus development on: Time management, objective decision-making, and professional boundaries."]
        }
    },
    "Facilitator": {
        "s1_profile": {
            "text": "This staff member communicates primarily as a Facilitator. They are the steady, calming presence in the room who seeks to ensure every voice is heard. They value fairness, process, and consensus. They rarely rush to judgment, preferring to gather all perspectives before deciding. They are excellent at de-escalating conflict and preventing rash decisions.",
            "bullets": ["Prioritizes fairness and inclusion over speed.", "Great listener; asks questions rather than giving orders.", "Dislikes conflict and sudden change.", "Views the 'process' as just as important as the 'result'."]
        },
        "s2_supervising": {
            "text": "Supervising a Facilitator requires patience. Do not pressure them for an immediate answer in the hallway; give them time to think and process. They often have brilliant insights into team dynamics but will not share them unless explicitly invited. You must create a safe space for them to voice dissenting opinions.",
            "bullets": ["Give advance notice: Send agendas early so they can prepare.", "Invite their voice: Ask 'What are you seeing that I am missing?'", "Validate fairness: Explain how your decisions consider the whole group.", "Push for closure: Gently help them land the plane when they are over-processing."]
        },
        "s8_struggling": {
            "text": "Under stress, the Facilitator can fall into 'Analysis Paralysis,' delaying critical decisions in a futile search for total consensus. They may become passive-aggressive or silent, holding tension internally rather than addressing it. They risk becoming a bottleneck because they are afraid of making a decision that might upset someone.",
            "bullets": ["Stalling projects to 'get more feedback'.", "Saying 'it's fine' when they clearly disagree.", "Letting poor performance slide to avoid rocking the boat.", "Being perceived by the team as indecisive or weak in a crisis."]
        },
        "s11_coaching": [
            "If you had to make a decision right now with only 80% of the info, what would it be?",
            "What is the cost to the team of waiting for total consensus?",
            "Where are you holding tension for the team that you need to release?",
            "Who specifically are you trying not to upset with this decision?",
            "How can you support the team's direction even if you don't fully agree?",
            "What is the 'least worst' option we have right now?",
            "You are listening to everyone else. What do *you* think?",
            "Is this a moment for collaboration or a moment for direction?",
            "How can we make this process fair without making it slow?",
            "What is the risk of doing nothing?"
        ],
        "s12_advancement": {
            "text": "For a Facilitator to advance, they must develop 'Executive Presence.' They need to learn to be decisive even when the room is split. Leadership often involves making 51/49 calls where half the people are unhappy. Their growth is shifting from a mediator (who stands in the middle) to a visionary (who stands in front).",
            "bullets": ["Assign them to lead a crisis response or a time-sensitive project.", "Challenge them to make a decision without calling a meeting first.", "Practice 'Disagree and Commit' strategies.", "Focus development on: Assertiveness, crisis command, and strategic vision."]
        }
    },
    "Tracker": {
        "s1_profile": {
            "text": "This staff member communicates primarily as a Tracker. They lead with data, details, and systems. They act as the guardian of quality and safety, noticing risks and gaps that others miss. They value logic, consistency, and accuracy. To them, the policy manual is not a suggestion; it is the roadmap to safety.",
            "bullets": ["Prioritizes accuracy and safety over speed.", "Detailed-oriented; loves checklists and plans.", "Skeptical of 'big ideas' without a plan.", "Views rules as the method to protect staff and youth."]
        },
        "s2_supervising": {
            "text": "Supervising a Tracker requires clarity and consistency. Ambiguity is their enemy. If you change direction frequently without explanation, they will lose trust in your leadership. Provide them with clear expectations, written instructions, and the 'why' behind decisions. They respond well to competence and reliability.",
            "bullets": ["Be specific: Avoid vague instructions like 'make it better'.", "Respect the system: Don't disrupt their workflow without cause.", "Show the logic: Explain the data or reasoning behind changes.", "Follow through: If you say you will do it, you must do it."]
        },
        "s8_struggling": {
            "text": "Under stress, the Tracker can become rigid, critical, and perfectionistic. They may get stuck in the weeds, nitpicking minor documentation errors while the house is on fire emotionally. They can come across as cold or uncaring to youth because they prioritize the rule over the relationship.",
            "bullets": ["Refusing to adapt to a crisis because 'it's not the procedure'.", "Correcting staff publicly on minor errors.", "Becoming cynical or blocking new initiatives.", "Overwhelming others with excessive details or emails."]
        },
        "s11_coaching": [
            "Does this specific detail change the safety outcome of the situation?",
            "How can we meet the standard here while keeping the relationship warm?",
            "What is the big picture goal, and are we sacrificing it for a minor procedural win?",
            "If we follow the rule perfectly but lose the kid's trust, did we succeed?",
            "What is the 'Good Enough' version of this task for right now?",
            "How can you delegate this task without hovering over them?",
            "I appreciate the data. What is the human story behind these numbers?",
            "Are you trying to be right, or are you trying to be helpful?",
            "How can we adapt the system to fit the current reality?",
            "What is the risk of being too rigid in this moment?"
        ],
        "s12_advancement": {
            "text": "For a Tracker to advance, they must shift from 'Compliance' to 'Strategy'. They need to learn to tolerate ambiguity and navigate the gray areas of leadership where no policy exists. They must learn to trust people, not just systems. Their growth involves delegating the details so they can focus on the horizon.",
            "bullets": ["Assign them a role that requires 'gray area' judgment calls (e.g., family negotiations).", "Challenge them to launch a project at 80% readiness ('Iterative design').", "Force them to delegate a complex task and only check the final result.", "Focus development on: Strategic thinking, adaptability, and people development."]
        }
    }
}

MOTIVATION_PROFILES = {
    "Growth": {
        "s3_profile": {
            "text": "Their primary motivator is Growth. This staff member is energized by the potential for development, learning, and mastery. They view their role not just as a job, but as a stepping stone in their professional journey. They are bored by repetition and engaged by difficulty.",
            "bullets": ["Seeks feedback and constructive criticism.", "Bored by status quo; loves 'pilots' and new initiatives.", "Values mentorship and training opportunities."]
        },
        "s4_motivating": {
            "text": "To motivate them, you must feed their curiosity. Frame tasks as 'challenges' or 'learning opportunities.' Give them problems to solve, not just lists to execute. If they feel they are stagnating, they will check out.",
            "bullets": ["Assign 'stretch' projects that require new skills.", "Ask 'What are you learning right now?' in supervision.", "Connect their daily grunt work to their long-term career goals."]
        },
        "s6_support": {
            "text": "Support them by being a sponsor. Advocate for them to attend trainings or shadow other departments. Ensure they have a clear developmental pathway. If you can't offer a promotion yet, offer a new responsibility that builds their resume.",
            "bullets": ["Sponsor them for external certifications.", "Delegate tasks that 'level them up'.", "Be transparent about the skills they need for the next level."]
        },
        "s7_thriving": {
            "text": "When thriving, they are the innovators of the team.",
            "bullets": ["Proactive questions about the 'why' and 'how'.", "Volunteering for difficult tasks.", "Mentoring peers on new skills.", "High energy during change initiatives."]
        },
        "s10_celebrate": {
            "text": "Celebrate their adaptability and skill acquisition. Do not just praise the result; praise the growth it took to get there.",
            "bullets": ["'I saw how you learned that new system—great work.'", "'You've really grown in your de-escalation skills.'", "Publicly acknowledging their professional development."]
        }
    },
    "Purpose": {
        "s3_profile": {
            "text": "Their primary motivator is Purpose. This staff member is driven by meaning, alignment, and values. They need to know that their work matters and makes a tangible difference in the lives of youth. They will endure difficult conditions if they believe the cause is just.",
            "bullets": ["Deeply committed to the mission and the youth.", "Sensitive to perceived injustice or lack of care.", "Values 'The Why' above 'The What'."]
        },
        "s4_motivating": {
            "text": "To motivate them, connect every directive back to the mission. Don't just say 'Fill out the log'; say 'This log helps us advocate for the youth in court.' Be transparent about the ethical reasoning behind decisions.",
            "bullets": ["Start meetings with a 'mission moment' or success story.", "Invite their input on decisions that impact client care.", "Explain the 'why' behind unpopular policies."]
        },
        "s6_support": {
            "text": "Support them by validating their passion. When they raise concerns, listen seriously—they are often the conscience of the team. Help them navigate the bureaucracy without losing their heart. Protect them from cynicism.",
            "bullets": ["Create space for them to voice ethical concerns.", "Remind them of the long-term impact they are having.", "Shield them from unnecessary 'corporate' noise."]
        },
        "s7_thriving": {
            "text": "When thriving, they are the passionate advocates of the program.",
            "bullets": ["Going the extra mile for a youth.", "High integrity and ethical standards.", "Inspiring peers with their dedication.", "Resilient in the face of client trauma."]
        },
        "s10_celebrate": {
            "text": "Celebrate their impact. Use specific stories of how they changed a life. Public praise should focus on their character and dedication.",
            "bullets": ["'That youth trusts you because you showed up.'", "'Thank you for keeping us focused on what matters.'", "Sharing a specific success story involving a youth."]
        }
    },
    "Connection": {
        "s3_profile": {
            "text": "Their primary motivator is Connection. This staff member is energized by relationships, belonging, and team cohesion. They work for the 'who', not just the 'what'. If the team feels like a family, they will work tirelessly. If they feel isolated, they will wither.",
            "bullets": ["Values harmony, collaboration, and inclusion.", "Highly sensitive to team conflict or cliques.", "Energized by group work and shared success."]
        },
        "s4_motivating": {
            "text": "To motivate them, prioritize the team dynamic. Use 'We' language. Creating opportunities for them to collaborate with others rather than working solo. Recognize the team's success, not just individuals.",
            "bullets": ["Facilitate team lunches or bonding moments.", "Assign them to work in pairs or groups.", "Check in on them personally before talking business."]
        },
        "s6_support": {
            "text": "Support them by ensuring they are not isolated. Be a warm, accessible presence. If there is conflict on the team, intervene quickly, as it drains them faster than anyone else.",
            "bullets": ["Be available for quick check-ins.", "Repair relational ruptures immediately.", "Ensure they feel 'part of the inner circle'."]
        },
        "s7_thriving": {
            "text": "When thriving, they are the morale boosters of the unit.",
            "bullets": ["Collaborative and supportive of peers.", "Creating a warm, welcoming atmosphere.", "High morale and laughter.", "Strong rapport with difficult staff and youth."]
        },
        "s10_celebrate": {
            "text": "Celebrate their contribution to the culture. Acknowledge how they support others.",
            "bullets": ["'You really held the team together today.'", "'Thanks for checking in on [New Staff Member].'", "Publicly appreciating their positivity."]
        }
    },
    "Achievement": {
        "s3_profile": {
            "text": "Their primary motivator is Achievement. This staff member loves progress, clarity, and winning. They want to know the score. They feel satisfied when they can check items off a list and see concrete evidence of their hard work.",
            "bullets": ["Goal-oriented and competitive (with self or others).", "Loves data, metrics, and completed checklists.", "Frustrated by ambiguity or moving goalposts."]
        },
        "s4_motivating": {
            "text": "To motivate them, set clear, measurable goals. Define exactly what 'success' looks like. Give them autonomy to figure out the path, but be rigid about the deadline and the standard. Use visual trackers.",
            "bullets": ["Use checklists or dashboards to show progress.", "Set daily or weekly 'wins'.", "Give them autonomy to crush the goal their way."]
        },
        "s6_support": {
            "text": "Support them by removing blockers. They hate inefficiency. Protect their time from useless meetings. Give them the resources they need to execute. Be decisive.",
            "bullets": ["Clarify expectations in writing.", "Eliminate red tape where possible.", "Provide the right tools/resources immediately."]
        },
        "s7_thriving": {
            "text": "When thriving, they are the engines of productivity.",
            "bullets": ["High volume of high-quality work.", "Meeting deadlines consistently.", "Organized and efficient.", "Driving projects to completion."]
        },
        "s10_celebrate": {
            "text": "Celebrate the win. Acknowledge the output and the reliability.",
            "bullets": ["'You said you'd do it, and you did it.'", "'Great job hitting that deadline.'", " recognizing their reliability and high standards."]
        }
    }
}

# --- PDF Generator ---
def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (1, 91, 173)
    black = (0, 0, 0)
    
    # Header
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(8)
    
    # Fetch Data
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

    def add_section(title, content_dict, is_bullets_only=False):
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(*blue)
        pdf.set_fill_color(240, 245, 250)
        pdf.cell(0, 8, title, ln=True, fill=True)
        pdf.ln(3)
        
        pdf.set_text_color(*black)
        pdf.set_font("Arial", '', 11)
        
        if not is_bullets_only and 'text' in content_dict:
            pdf.multi_cell(0, 5, clean_text(content_dict['text']))
            pdf.ln(3)
            
        if 'bullets' in content_dict:
            for b in content_dict['bullets']:
                pdf.set_font("Arial", 'B', 14) # Bullet symbol
                pdf.cell(5, 5, chr(149), 0, 0)
                pdf.set_font("Arial", '', 11)
                pdf.multi_cell(0, 5, clean_text(b))
        pdf.ln(5)

    # 1. Communication Profile
    add_section(f"1. Communication Profile: {p_comm}", c['s1_profile'])

    # 2. Supervising Their Communication
    add_section("2. Supervising Their Communication", c['s2_supervising'])

    # 3. Motivation Profile
    add_section(f"3. Motivation Profile: {p_mot}", m['s3_profile'])

    # 4. Motivating This Staff Member
    add_section("4. Motivating This Staff Member", m['s4_motivating'])

    # 5. Integrated Leadership Profile
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "5. Integrated Leadership Profile", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(*black)
    pdf.set_font("Arial", '', 11)
    
    # Dynamic Synthesis
    comm_key = c['s1_profile']['text'].split('.')[1] # Grab the descriptor sentence
    motiv_key = m['s3_profile']['text'].split('.')[2] # Grab the descriptor sentence
    integrated_text = (
        f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. "
        f"{comm_key} At the same time, {motiv_key} "
        f"This combination creates a unique leadership style: they will pursue their goal of {p_mot} using the tools of a {p_comm}. "
        "When these align, they are unstoppable. When they conflict (e.g., a Director who wants 'Growth' but is stuck in repetitive tasks), frustration mounts quickly."
    )
    pdf.multi_cell(0, 5, clean_text(integrated_text))
    pdf.ln(5)

    # 6. How You Can Best Support Them
    add_section("6. How You Can Best Support Them", m['s6_support'])

    # 7. What They Look Like When Thriving
    add_section("7. What They Look Like When Thriving", m['s7_thriving'])

    # 8. What They Look Like When Struggling
    add_section("8. What They Look Like When Struggling", c['s8_struggling'])

    # 9. Supervisory Interventions
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "9. Supervisory Interventions", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(*black)
    pdf.set_font("Arial", '', 11)
    
    intervention_intro = "When this staff member is struggling, use these targeted interventions:"
    pdf.multi_cell(0, 5, intervention_intro)
    pdf.ln(2)
    
    interventions = [
        f"Validate their Motivation: Acknowledge their need for {p_mot} before correcting behavior.",
        f"Address the Stress Response: Gently point out if they are becoming {c['s8_struggling']['bullets'][0]}.",
        "Re-align Expectations: Ensure they know exactly what success looks like in this specific situation.",
        "Check for Burnout: Are they over-functioning in their style (e.g., too much talking, too much controlling)?"
    ]
    for i in interventions:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(5, 5, chr(149), 0, 0)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, clean_text(i))
    pdf.ln(5)

    # 10. What You Should Celebrate
    add_section("10. What You Should Celebrate", m['s10_celebrate'])

    # 11. Coaching Questions
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*blue)
    pdf.set_fill_color(240, 245, 250)
    pdf.cell(0, 8, "11. Coaching Questions", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_text_color(*black)
    pdf.set_font("Arial", '', 11)
    for q in c['s11_coaching']:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(5, 5, chr(149), 0, 0)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 5, clean_text(q))
    pdf.ln(5)

    # 12. Helping Them Prepare for Advancement
    add_section("12. Helping Them Prepare for Advancement", c['s12_advancement'])

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
            
    subtab1, subtab2 = st.tabs(["📚 From Database", "✏️ Manual Entry"])
    
    with subtab1:
        if not df.empty:
            def reset_t1():
                st.session_state.t1_staff_select = None

            staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            selected_staff_name = st.selectbox(
                "Select Staff Member", 
                options=list(staff_options.keys()), 
                index=None, 
                key="t1_staff_select",
                placeholder="Choose a staff member..."
            )
            
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
                
                st.markdown("---")
                st.button("Reset Selection", key="reset_t1_db", on_click=reset_t1)
        else:
            st.info("Database is empty or loading...")

    with subtab2:
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
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    st.write("Select multiple staff members to analyze the culture of a specific unit or team.")
    
    def reset_t2():
        st.session_state.t2_team_select = []

    if not df.empty:
        team_selection = st.multiselect("Build your Team", df['name'].tolist(), key="t2_team_select")
        
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Communication Mix")
                comm_counts = team_df['p_comm'].value_counts()
                fig_team_comm = px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4)
                st.plotly_chart(fig_team_comm, use_container_width=True)
                
                if not comm_counts.empty:
                    dominant_style = comm_counts.idxmax()
                    dom_pct = comm_counts.max() / len(team_df)
                    if dom_pct > 0.5:
                        st.warning(f"⚠️ **Echo Chamber Risk:** {int(dom_pct*100)}% of this team are **{dominant_style}s**.")
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                fig_team_mot = px.bar(x=mot_counts.index, y=mot_counts.values)
                st.plotly_chart(fig_team_mot, use_container_width=True)
            
            st.markdown("---")
            st.button("Clear Team Selection", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    st.write("Select two staff members who are struggling to collaborate.")
    
    def reset_t3():
        st.session_state.p1 = None
        st.session_state.p2 = None

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Staff Member A", df['name'].unique(), index=None, key="p1", placeholder="Select first person...")
        with c2:
            p2_name = st.selectbox("Staff Member B", df['name'].unique(), index=None, key="p2", placeholder="Select second person...")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            
            style1 = p1['p_comm']
            style2 = p2['p_comm']
            
            st.divider()
            st.subheader(f"The Clash: {style1} vs. {style2}")
            st.markdown("_(Conflict Matrix scripts would populate here as in previous versions)_")
            
            st.markdown("---")
            st.button("Reset Conflict Tool", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    st.write("Analyze readiness for promotion.")
    
    def reset_t4():
        st.session_state.career = None
        st.session_state.career_target = None

    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select candidate...")
        with col_b:
            target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select target role...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']}")
            st.write("_(Career path logic would populate here)_")
            
            st.markdown("---")
            st.button("Reset Career Path", key="reset_btn_t4", on_click=reset_t4)

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Communication Styles")
            fig_org_comm = px.pie(df, names='p_comm', color='p_comm', color_discrete_map={'Director':'#015bad', 'Encourager':'#b9dca4', 'Facilitator':'#51c3c5', 'Tracker':'#64748b'})
            st.plotly_chart(fig_org_comm, use_container_width=True)
        with c2:
            st.subheader("Motivation Drivers")
            fig_org_mot = px.bar(df, x='p_mot', color='p_mot')
            st.plotly_chart(fig_org_mot, use_container_width=True)
        
        st.divider()
        if 'role' in df.columns:
            role_breakdown = pd.crosstab(df['role'], df['p_comm'])
            st.dataframe(role_breakdown.style.background_gradient(cmap="Blues"), use_container_width=True)
    else:
        st.warning("No data available.")
