import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Elmcrest Supervisor Platform", page_icon="📊", layout="wide")

# --- 2. CONSTANTS ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- 3. CONTENT DICTIONARIES ---

# Defined at the top to prevent NameErrors
COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# --- SUPERVISOR CLASH MATRIX (Expanded) ---
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "tension": "The 'Bulldozer vs. Doormat' Dynamic. The Director pushes for results; the Encourager withdraws to protect themselves. The Director interprets withdrawal as incompetence; the Encourager interprets directness as hostility.",
            "root_cause": "Value Mismatch: The Director values **Utility** (is this useful?). The Encourager values **Affirmation** (am I valued?). When the Director skips the 'human' part to get to work, the Encourager feels dehumanized.",
            "watch_fors": [
                "The Encourager stops contributing in meetings (silent withdrawal).",
                "The Director starts interrupting or finishing the Encourager's sentences.",
                "The Encourager complains to peers that the Director is 'mean' or 'doesn't care'.",
                "The Director complains that the Encourager is 'too sensitive' or 'needy'."
            ],
            "intervention_steps": [
                "**Step 1: Pre-Frame.** Tell the Director that 'Efficiency without Empathy is Inefficiency.' If they break the relationship, the work stops.",
                "**Step 2: The Translate.** In the meeting, translate the Encourager's feelings into data. 'When they say they are stressed, they are telling you the team is about to break.'",
                "**Step 3: The Deal.** The Director agrees to listen for 5 minutes without solving. The Encourager agrees to move to action steps once heard."
            ],
            "scripts": {
                "To Director": "You are trying to fix the problem, but right now, the *relationship* is the problem. You cannot optimize a broken machine. Stop solving and start listening. Ask: 'How is this landing with you?' and wait.",
                "To Encourager": "The Director's brevity is not anger; it is urgency. They are stressed about the goal. You don't need to protect yourself from them; you need to tell them clearly: 'I can help you win, but I need you to lower your volume so I can think.'",
                "Joint": "We are speaking two different languages. [Director] is speaking 'Task'; [Encourager] is speaking 'Team'. Both are valid. [Director], please validate [Encourager]'s concern before we move to the next step."
            }
        },
        "Facilitator": {
            "tension": "The 'Gas vs. Brake' Dynamic. The Director wants to decide *now*. The Facilitator wants to ensure the process is fair and everyone is heard. The Director feels obstructed; the Facilitator feels steamrolled.",
            "root_cause": "Risk Perception: The Director fears **Stagnation** (doing nothing). The Facilitator fears **Error** (doing the wrong thing and upsetting the group).",
            "watch_fors": [
                "The Director issues a command via email to avoid a meeting.",
                "The Facilitator keeps saying 'We need to talk about this' but never decides.",
                "The Director visibly rolls eyes when the Facilitator asks for 'thoughts'.",
                "Decisions are made by the Director but passively resisted/ignored by the team."
            ],
            "intervention_steps": [
                "**Step 1: Define the Clock.** The Facilitator needs time; the Director needs a deadline. Negotiate it.",
                "**Step 2: Define the Veto.** Tell the Facilitator they have a 'Red Flag' right. If they see a major risk, they can stop the Director. Otherwise, the Director drives.",
                "**Step 3: The debrief.** After the action, review: 'Did we move too fast? Or did we wait too long?'"
            ],
            "scripts": {
                "To Director": "If you force this decision now, you get compliance, not buy-in. Compliance falls apart when you leave the room. Give them 24 hours to process, and you will get a better result.",
                "To Facilitator": "Silence looks like agreement to a Director. If you disagree, you must say 'Stop'. If you just say 'I'm not sure', they will keep moving. Be direct: 'We cannot do X because Y.'",
                "Joint": "We have a pace mismatch. [Director] wants to sprint; [Facilitator] wants to survey the route. We are going to set a timer. We will survey for 30 minutes, and then we will sprint. Agreed?"
            }
        },
        "Tracker": {
            "tension": "The 'Vision vs. Obstacle' Dynamic. The Director acts on gut/vision. The Tracker acts on data/policy. The Director sees the Tracker as the 'Department of No'. The Tracker sees the Director as a liability lawsuit waiting to happen.",
            "root_cause": "Authority Source: The Director trusts **Intuition**. The Tracker trusts **The Handbook**. They are fighting over what is 'True'.",
            "watch_fors": [
                "The Tracker quoting policy numbers in arguments.",
                "The Director saying 'Ask for forgiveness, not permission.'",
                "The Tracker hoarding information or access to prove a point.",
                "The Director bypassing the Tracker to get things done."
            ],
            "intervention_steps": [
                "**Step 1: Clarify Roles.** Director owns the 'What' (Destination). Tracker owns the 'How' (Safe Route).",
                "**Step 2: The 'Yes, If' Rule.** Coach the Tracker to never say 'No'. Instead say: 'Yes, we can do that, *if* we sign this waiver/change this budget.'",
                "**Step 3: Risk Acceptance.** The Director must explicitly state: 'I accept the risk of deviating from the standard here.'"
            ],
            "scripts": {
                "To Director": "They aren't trying to annoy you; they are trying to protect you. When you ignore their data, you tell them their job doesn't matter. Ask them: 'How do we do this legally?'",
                "To Tracker": "You are right about the rules, but you are losing the influence. Start with the solution. Say: 'I can get you to that goal, but we have to take this side road to stay compliant.'",
                "Joint": "We are on the same team. [Director] sets the destination. [Tracker] checks the brakes. [Director], you cannot drive the car if the brakes are cut. [Tracker], you cannot keep the car in the garage forever."
            }
        },
        "Director": {
            "tension": "The 'King vs. King' Dynamic. Two alphas. High conflict, high volume, low listening. Both think they are the smartest person in the room. It becomes about ego, not the work.",
            "root_cause": "Dominance: Both define safety as **Control**. When the other person takes control, they feel unsafe/disrespected.",
            "watch_fors": [
                "Interruptions and talking over each other.",
                "Public debates that feel like combat.",
                "Refusal to implement the other's idea.",
                "The team looking awkward while 'Mom and Dad fight'."
            ],
            "intervention_steps": [
                "**Step 1: Separate Lanes.** They cannot drive the same car. Give them distinct domains where they have total authority.",
                "**Step 2: The Truce.** Acknowledge the power struggle explicitly. 'You are both fighting for the wheel.'",
                "**Step 3: Disagree and Commit.** Once a decision is made by the final authority, the debate ends."
            ],
            "scripts": {
                "To Director A": "You are fighting to be right, not to be effective. Is this the hill you want to die on? Let them have this win so you can bank capital for the next one.",
                "To Director B": "You are reacting to their tone, not their idea. If you strip away the aggression, is their idea actually wrong?",
                "Joint": "We have two strong leaders here. We are wasting energy fighting each other. [Name], you own [Project A]. [Name], you own [Project B]. Stay out of each other's lanes."
            }
        }
    },
    "Encourager": {
        "Director": {
            "tension": "The 'Sensitivity Gap'. You (Encourager) feel personally attacked by their brevity. They (Director) feel annoyed by your 'fluff'. You over-explain to get validation; they tune out.",
            "root_cause": "Validation Style: You need **External** validation (words). They rely on **Internal** validation (results). You are starving for something they don't know how to cook.",
            "watch_fors": [
                "You apologizing before asking for something.",
                "You venting to peers about how 'mean' the Director is.",
                "The Director avoiding meetings with you because 'it takes too long'.",
                "You feeling exhausted/crying after supervision."
            ],
            "intervention_steps": [
                "**Step 1: The Headline.** Coach the Encourager to start with the conclusion, then the feelings. 'We need to fire Bob because he hurt the team.'",
                "**Step 2: The 'Why'.** Coach the Director to explain the *reason* for their speed, so the Encourager doesn't invent a story that they are angry.",
                "**Step 3: Scheduled Venting.** Give the Encourager 5 mins to process feelings, then hard pivot to tasks."
            ],
            "scripts": {
                "To Encourager": "I need you to translate your intuition into business risks. Don't say 'I feel bad about this.' Say 'If we do this, the team morale will drop and turnover will spike.' That is language the Director hears.",
                "To Director": "You are crushing them. You don't need to be their therapist, but you do need to be polite. 'Please' and 'Thank you' buy you speed. Use them.",
                "Joint": "We need to balance the 'What' and the 'Who'. [Director], you own the timeline. [Encourager], you own the communication plan to the staff. Make sure the message lands softly."
            }
        },
        "Facilitator": {
            "tension": "The 'Polite Stagnation'. You both value harmony. You want to help the specific person in front of you; they want to help the abstract 'Group'. You both hate being the bad guy, so bad behavior goes unchecked.",
            "root_cause": "Conflict Avoidance: You fear **Rejection**. They fear **Unfairness**. Neither fear motivates action; both motivate delay.",
            "watch_fors": [
                "Endless meetings where everyone agrees but nothing changes.",
                "Problems being 'managed' rather than 'solved'.",
                "Using passive language: 'It would be nice if...' instead of 'You must...'.",
                "Resentment building because no one is leading."
            ],
            "intervention_steps": [
                "**Step 1: Name the Fear.** 'We are scared to upset [Person], so we are hurting the program.'",
                "**Step 2: Assign the 'Bad Guy'.** Supervisor acts as the heavy: 'Blame me. Say I ordered it.'",
                "**Step 3: Script the Hard Conversation.** Don't let them ad-lib; write the script together."
            ],
            "scripts": {
                "To Encourager": "You are protecting [Person]'s feelings at the expense of the team's safety. That isn't kindness; it's enabling. We need to have the hard talk.",
                "To Facilitator": "We have heard enough perspectives. The data is in. The search for consensus is now just procrastination. Make the call.",
                "Joint": "We are being too nice. The team needs clarity, not just support. Who is going to deliver the news? Let's practice it right now."
            }
        },
        "Tracker": {
            "tension": "The 'Rigidity vs. Flow' Dynamic. You want to adapt to the moment; they want to follow the plan. You feel restricted; they feel chaotic.",
            "root_cause": "Safety Source: You find safety in **Connection**. They find safety in **Consistency**. Your exception to the rule threatens their safety.",
            "watch_fors": [
                "You making 'secret deals' with staff/youth to bypass rules.",
                "The Tracker policing you publicly.",
                "You feeling judged; them feeling undermined.",
                "Inconsistent application of consequences."
            ],
            "intervention_steps": [
                "**Step 1: The 'Why' of Rules.** Show the Encourager that rules protect the most vulnerable youth by creating predictability.",
                "**Step 2: The 'Why' of Exceptions.** Show the Tracker that rigid rules break rapport, which causes danger.",
                "**Step 3: The Hybrid.** 'We follow the rule (Tracker), but we deliver it with maximum empathy (Encourager).'"
            ],
            "scripts": {
                "To Encourager": "When you bend the rule, you don't just help that kid; you make the Tracker the 'bad guy' for the next shift. We have to be a united front.",
                "To Tracker": "You are right about the policy, but your delivery is cold. If they don't trust us, they won't follow the rule. Let the Encourager do the talking, but you check the plan."
            }
        },
        "Encourager": {
            "tension": "The 'Echo Chamber'. You validate each other perfectly. High warmth, low accountability. You risk becoming a clique that complains about 'Them' (Management) without solving anything.",
            "root_cause": "Emotional Contagion: You amplify each other's feelings. Stress becomes shared panic. Joy becomes a party. There is no grounding force.",
            "watch_fors": [
                "Supervision turning into a venting session.",
                "Lack of clear action items.",
                "Creating 'Us vs. Them' narratives about other departments.",
                "Ignoring metrics/data because 'we feel like we're doing good'."
            ],
            "intervention_steps": [
                "**Step 1: The 5-Minute Rule.** Only 5 minutes of venting allowed.",
                "**Step 2: The Pivot.** 'I hear that is hard. What is the first step to fixing it?'",
                "**Step 3: External Data.** Bring in a chart/checklist to force a reality check beyond feelings."
            ],
            "scripts": {
                "To Encourager A": "I love our connection. But we are spinning. Let's put our feelings in a box for 10 minutes and just solve the logistics.",
                "Joint": "We are great at supporting each other. Now we need to be great at challenging each other. Who is going to play 'Devil's Advocate' today?"
            }
        }
    },
    "Facilitator": {
        "Director": {
            "tension": "The 'Steamroll'. You are trying to gather input; they just bark orders. You feel disrespected and silenced. You worry they are running the program off a cliff.",
            "root_cause": "Decision Style: You process **Externally** (group talk). They process **Internally** (gut check). By the time you ask a question, they have already moved on.",
            "watch_fors": [
                "You staying silent in meetings then complaining later.",
                "The Director looking bored while you talk.",
                "You asking 'Does everyone agree?' and the Director saying 'Moving on.'",
                "The team looking confused about who is in charge."
            ],
            "intervention_steps": [
                "**Step 1: Interrupt.** You must learn to interrupt the Director. 'Hold on, I need to add a risk factor.'",
                "**Step 2: The Pre-Meeting.** Brief the Director beforehand. 'I am going to ask for feedback on X. Please don't answer first.'",
                "**Step 3: The Frame.** Frame your process as 'Risk Management' (which Directors value) not 'Inclusion' (which they might not)."
            ],
            "scripts": {
                "To Director": "You are moving too fast. If you want this to stick, you have to let me get the team on board. Give me 10 minutes to facilitate.",
                "To Facilitator": "You are giving away your power. When you ask 'What do you think?', the Director will always answer. Instead say: 'I want to hear from [Specific Person].'"
            }
        },
        "Tracker": {
            "tension": "The 'Details Loop'. You want to talk about the *concept*; they want to talk about the *form*. You get bogged down in formatting/logistics before you even agree on the idea.",
            "root_cause": "Scope: You are **Horizontal** (scanning everyone). They are **Vertical** (drilling down). You miss each other.",
            "watch_fors": [
                "Long email chains about minor details.",
                "Meetings running overtime.",
                "You feeling nitpicked; them feeling vague.",
                "Great ideas dying in the 'how-to' phase."
            ],
            "intervention_steps": [
                "**Step 1: Concept First.** 'We are not discussing the form yet. Do we agree on the goal?'",
                "**Step 2: Detail Second.** 'Now that we agree, Tracker, please build the checklist.'",
                "**Step 3: The Parking Lot.** Park detailed questions until the end of the meeting."
            ],
            "scripts": {
                "To Tracker": "We are at the 30,000-foot view right now. I need you to fly up here with me for 5 minutes. We will land and check the tires later.",
                "To Facilitator": "The Tracker isn't trying to kill your idea; they are trying to see how it works. Give them a specific task so they feel useful."
            }
        }
    },
    "Tracker": {
        "Director": {
            "tension": "The 'Micromanager' Label. You are just checking the work; they think you don't trust them. You see risk everywhere; they see opportunity.",
            "root_cause": "Trust: You trust **Verification**. They trust **Competence**. You verify by checking; they verify by doing.",
            "watch_fors": [
                "You sending emails with 'Corrections'.",
                "The Director avoiding you.",
                "You feeling anxious that 'it's all going to fall apart'.",
                "The Director withholding info so you don't 'slow them down'."
            ],
            "intervention_steps": [
                "**Step 1: Pick your Battles.** Differentiate between 'Safety Critical' (Intervene) and 'Preference' (Let it go).",
                "**Step 2: The Sandbox.** Give the Director a space where they can break things safely.",
                "**Step 3: Solution-First.** Don't say 'We can't.' Say 'We can, IF we do X.'"
            ],
            "scripts": {
                "To Director": "I am not trying to stop you. I am trying to make sure you don't get fired for a compliance error. Let me handle the paperwork so you can handle the people.",
                "To Tracker": "You are right, but you are annoying. Stop correcting their spelling and start correcting their liability risks. Focus on the big stuff."
            }
        }
    }
}
# Robustness for missing keys in Clash Matrix
for s in COMM_TRAITS:
    if s not in SUPERVISOR_CLASH_MATRIX: SUPERVISOR_CLASH_MATRIX[s] = {}
    for staff in COMM_TRAITS:
        if staff not in SUPERVISOR_CLASH_MATRIX[s]:
            SUPERVISOR_CLASH_MATRIX[s][staff] = {
                "tension": "General Style Difference.",
                "root_cause": "Different communication priorities.",
                "watch_fors": ["Misunderstanding intent", "Frustration in meetings"],
                "intervention_steps": ["Listen first", "Clarify goals"],
                "scripts": {"To Director": "Let's align on the goal.", "To Encourager": "Let's align on the goal.", "Joint": "Let's align."}
            }


# (A) COMMUNICATION PROFILES (Detailed Structure for PDF & Screen)
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
            "bullets": ["Steamrolling quieter voices in meetings.", "Becoming visibly irritable or sarcastic with 'slow' processes.", "Making unilateral decisions without consulting stakeholders.", "Sacrificing long-term relationships for short-term compliance."]
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
            "bullets": ["Avoiding necessary hard conversations.", "Venting or gossiping as a way to manage stress.", "Disorganization or missed deadlines due to social distractions.", "Taking youth behaviors personally or becoming emotionally enmeshed."]
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

# (B) MOTIVATION PROFILES (Detailed Structure for PDF)
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

# --- CAREER PATHWAYS ---
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "why": "Directors act fast. They see a problem and fix it. As a Shift Sup, if they fix everything, their team learns nothing. They become the bottleneck.",
            "conversation": "You have high capacity and speed, which is a gift. To succeed as a Shift Supervisor, you have to resist the urge to 'rescue' the shift by doing everything yourself. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless safety dictates otherwise).",
            "assignment_task": "They must run the shift entirely through verbal direction and delegation to peers. They cannot touch paperwork or intervene in minor conflicts.",
            "success_indicators": "Did they let a staff member struggle through a task without jumping in? Did they give clear verbal instructions? Did they debrief afterwards?",
            "red_flags": "They ran out of the office to 'just do it quick'. They complain that their team is 'too slow'. They took over the radio.",
            "supervisor_focus": "Watch for 'Hero Mode'. If you see them jumping in to fix a crisis that their staff could handle, intervene. Pull them back and say, 'Let your team handle this. Coach them, don't save them.'"
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "why": "Program Sups need buy-in from people they don't supervise (School, Clinical). Directors tend to order people around, which alienates peers.",
            "conversation": "You are excellent at execution within your unit. However, program leadership requires getting buy-in from people you don't supervise (School, Clinical, other cottages). You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment_setup": "Identify a peer in another department (School/Clinical) they have friction with.",
            "assignment_task": "Task them with a cross-departmental project (e.g., improving school transitions). They must interview stakeholders and present a plan that incorporates *their* feedback.",
            "success_indicators": "The plan includes ideas that clearly didn't come from the Director. The peer reports feeling heard. The tone is collaborative.",
            "red_flags": "They present a plan that is 100% their own idea and complain that the other dept is 'difficult'. They try to use your authority to force the change.",
            "supervisor_focus": "Monitor their patience. If they complain about 'meetings' or 'politics', reframe it: 'That isn't politics; that is relationship building. That is the job now.'"
        },
        "Manager": {
            "shift": "From 'Tactical' to 'Strategic'.",
            "why": "Directors love fighting fires. Managers need to prevent fires. Directors often struggle to sit still long enough to plan.",
            "conversation": "You react beautifully to problems. The next level requires you to prevent them 6 months in advance. You need to shift from reliance on your force of will to reliance on sustainable systems.",
            "assignment_setup": "Assign a long-term strategic plan for a recurring seasonal issue (e.g., Summer Break Structure).",
            "assignment_task": "They must submit a plan with data projections, budget needs, and staffing models 3 months in advance.",
            "success_indicators": "The plan relies on systems, not just 'working harder'. They anticipate risks.",
            "red_flags": "They delay the planning until the last minute. The plan is just 'we will figure it out'.",
            "supervisor_focus": "Check their horizon. Are they talking about today's crisis or next month's risk? Push them to think longer term."
        }
    },
    "Encourager": {
        "Shift Supervisor": {
            "shift": "From 'Friend' to 'Guardian'.",
            "why": "Encouragers want to be liked. Shift Sups must be respected. If they can't hold a boundary, the shift becomes unsafe.",
            "conversation": "Your empathy is your superpower, but if you avoid hard conversations to keep the peace, you create an unsafe environment. The team needs you to be a 'Guardian' of the standard. Accountability is kindness.",
            "assignment_setup": "Identify a staff member who is consistently late or missing protocols.",
            "assignment_task": "Lead a policy reinforcement meeting with that staff member. You (Supervisor) observe but do not speak.",
            "success_indicators": "They state the expectation clearly without apologizing. They don't use 'The boss wants...' language.",
            "red_flags": "They apologize for the rule ('Sorry I have to tell you this...'). They make a joke to deflect the tension.",
            "supervisor_focus": "Watch for 'Apology Language'. If they give a directive and then apologize for it, correct them immediately. 'Do not apologize for leading.'"
        },
        "Program Supervisor": {
            "shift": "From 'Vibe' to 'Structure'.",
            "why": "Encouragers run on personality. Programs run on structure. They need to master the boring parts (budgets, audits) to protect the team.",
            "conversation": "You create an amazing climate. To lead a program, that climate must be backed by unshakeable structure. You need to master the unsexy parts of leadership so your team is protected.",
            "assignment_setup": "Assign ownership of a compliance audit or a complex schedule overhaul.",
            "assignment_task": "They must present the data and the rationale to the team, standing on the facts rather than just their relationship.",
            "success_indicators": "The audit is accurate. They can explain the 'why' without appealing to emotion.",
            "red_flags": "They ask a Tracker to do it for them. They procrastinate the paperwork to hang out with staff.",
            "supervisor_focus": "Inspect what you expect. Encouragers can be disorganized. Help them build a personal organization system so their administrative balls don't drop."
        },
        "Manager": {
            "shift": "From 'Caregiver' to 'Director'.",
            "why": "Managers deal with resource scarcity. Encouragers take 'No' personally and burn out trying to save everyone.",
            "conversation": "You naturally carry the emotions of your people. At the manager level, the weight is too heavy to carry alone. Your growth edge is caring deeply about the person without taking responsibility for their feelings.",
            "assignment_setup": "Have them manage a resource allocation conflict (e.g., denying a budget request or staffing request).",
            "assignment_task": "Deliver a 'No' to a request, explain the business reason, and withstand the disappointment of the staff member.",
            "success_indicators": "They hold the line. They don't promise to 'fix it later' just to stop the person from being sad.",
            "red_flags": "They cave to the request. They vent to the staff member about 'Upper Management' making them do it.",
            "supervisor_focus": "Watch for burnout. If they look exhausted, they are likely over-functioning emotionally. Ask: 'Who are you trying to save right now?'"
        }
    },
    "Facilitator": {
        "Shift Supervisor": {
            "shift": "From 'Peer' to 'Decider'.",
            "why": "Facilitators freeze when the team is split. Safety requires immediate direction without consensus.",
            "conversation": "You are gifted at ensuring everyone feels heard. As a Shift Sup, there will be moments where consensus is impossible and safety requires speed. You need to get comfortable making the '51% decision'—listening to input, but making the call even if 49% disagree.",
            "assignment_setup": "Put them in charge of a time-sensitive crisis drill or transition.",
            "assignment_task": "They must make immediate calls on staff positioning. Debrief afterwards: 'Where did you hesitate? How did it feel to give a direct command?' Affirm their authority.",
            "success_indicators": "They gave direct commands. They didn't ask 'What do you guys think?' during the crisis.",
            "red_flags": "They stood back and let a Director take over. They tried to have a meeting in the middle of a transition.",
            "supervisor_focus": "Push for speed. When they ask 'What do you think?', throw it back: 'You tell me. You're the leader.' Force them to exercise their judgment muscle."
        },
        "Program Supervisor": {
            "shift": "From 'Mediator' to 'Visionary'.",
            "why": "Facilitators lead from the middle. Program Sups must lead from the front and set the vision.",
            "conversation": "You act as a great buffer. But we need you to inject your own vision. Don't just wait to see what the group wants; tell us where you think the group needs to go.",
            "assignment_setup": "Ask them to propose a new initiative for the program culture.",
            "assignment_task": "Present it to the team as a direction, not a discussion topic. 'This is where we are going.'",
            "success_indicators": "They use declarative statements ('We will...'). They handle pushback without folding.",
            "red_flags": "They frame it as a question ('How would you guys feel about...?'). They retreat at the first sign of resistance.",
            "supervisor_focus": "Watch for 'The Buffer'. Are they just passing messages between staff and admin? Challenge them to take a stand on issues."
        },
        "Manager": {
            "shift": "From 'Process' to 'Outcome'.",
            "why": "Facilitators get bogged down in fairness and stall critical changes.",
            "conversation": "Fair process is vital, but sometimes it yields poor results. At this level, you must prioritize the outcome over the comfort of the process. You need to be willing to disrupt the harmony to achieve the mission.",
            "assignment_setup": "Task them with implementing a necessary but unpopular policy change.",
            "assignment_task": "Listen to complaints, validate feelings, but do NOT change the decision.",
            "success_indicators": "The policy gets implemented on time. They survive the team being unhappy with them.",
            "red_flags": "They delay implementation to 'get more feedback'. They water down the policy to make it nicer.",
            "supervisor_focus": "Monitor their tolerance for conflict. If they start delaying a necessary change to avoid upset, step in. 'The upset is inevitable; the delay is optional.'"
        }
    },
    "Tracker": {
        "Shift Supervisor": {
            "shift": "From 'Executor' to 'Overseer'.",
            "why": "Trackers don't trust others to do it right, so they micromanage. They burn out trying to do 5 jobs.",
            "conversation": "You are brilliant at the details. But you cannot track every detail personally. You have to let the team do the checklist, even if they do it differently than you would.",
            "assignment_setup": "The 'Hands-Off' Day. Assign them to supervise a complex task (intake/search).",
            "assignment_task": "Strictly prohibited from touching paperwork. Must guide a peer to do it verbally.",
            "success_indicators": "They kept their hands in their pockets. They gave clear corrections without taking over.",
            "red_flags": "They grabbed the pen. They sighed and said 'I'll just do it'.",
            "supervisor_focus": "Watch for micromanagement. If they are re-doing someone else's work, stop them. 'If it is 80% right, it is right enough. Move on.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "why": "Trackers want a rule for everything. Leadership involves judgment calls where no rule exists.",
            "conversation": "You excel when rules are clear. Leadership is full of gray areas. You need to develop your intuition to navigate dynamics that don't fit the spreadsheet.",
            "assignment_setup": "Handle a complex parent/youth complaint where standard rules don't apply.",
            "assignment_task": "Make a principle-based decision (fairness/safety) rather than a rule-based one.",
            "success_indicators": "They made a decision that wasn't in the handbook but made sense. They can explain the 'spirit' of the rule.",
            "red_flags": "They froze because 'there's no policy'. They applied a rule rigidly that made no sense in context.",
            "supervisor_focus": "Challenge their rigidity. If they say 'We can't do that, it's not the rule', ask 'What is the *intent* of the rule? Can we meet the intent a different way?'"
        },
        "Manager": {
            "shift": "From 'Compliance' to 'Culture'.",
            "why": "Trackers value efficiency over connection, risking a sterile, unhappy culture.",
            "conversation": "Culture eats strategy (and checklists) for breakfast. If you prioritize efficiency over connection, you will have a compliant but brittle organization. You need to invest as much energy in 'how people feel' as 'what people do'.",
            "assignment_setup": "Task them with a retention or morale initiative.",
            "assignment_task": "Spend one week focusing solely on staff development/relationships. Delegate metrics to a deputy.",
            "success_indicators": "They had non-work conversations. Staff report feeling seen.",
            "red_flags": "They turned the morale initiative into a checklist ('Did you have fun? Check yes').",
            "supervisor_focus": "Look for the 'Human Element'. In every supervision, ask them a question about people, not tasks. 'How is [Staff Name] doing really?'"
        }
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

# --- DISPLAY GUIDE ON SCREEN ---
def display_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])
    
    st.markdown(f"## 📑 Supervisory Guide: {name}")
    st.markdown(f"**Role:** {role} | **Profile:** {p_comm} × {p_mot}")
    st.divider()
    
    # 1
    st.subheader(f"1. Communication Profile: {p_comm}")
    st.write(c['s1_profile']['text'])
    for b in c['s1_profile']['bullets']: st.markdown(f"- {b}")
    
    # 2
    st.subheader("2. Supervising Their Communication")
    st.write(c['s2_supervising']['text'])
    for b in c['s2_supervising']['bullets']: st.markdown(f"- {b}")
    
    # 3
    st.subheader(f"3. Motivation Profile: {p_mot}")
    st.write(m['s3_profile']['text'])
    for b in m['s3_profile']['bullets']: st.markdown(f"- {b}")
    
    # 4
    st.subheader("4. Motivating This Staff Member")
    st.write(m['s4_motivating']['text'])
    for b in m['s4_motivating']['bullets']: st.markdown(f"- {b}")
    
    # 5 Integrated
    st.subheader("5. Integrated Leadership Profile")
    comm_key = c['s1_profile']['text'].split('.')[1]
    motiv_key = m['s3_profile']['text'].split('.')[2] if len(m['s3_profile']['text'].split('.')) > 2 else m['s3_profile']['text']
    integrated_text = (
        f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. "
        f"{comm_key} At the same time, {motiv_key} "
        f"This combination creates a unique leadership style: they will pursue their goal of {p_mot} using the tools of a {p_comm}. "
        "When these align, they are unstoppable. When they conflict, frustration mounts quickly."
    )
    st.write(integrated_text)
    
    # 6
    st.subheader("6. How You Can Best Support Them")
    st.write(m['s6_support']['text'])
    for b in m['s6_support']['bullets']: st.markdown(f"- {b}")
    
    # 7
    st.subheader("7. What They Look Like When Thriving")
    st.write(m['s7_thriving']['text'])
    for b in m['s7_thriving']['bullets']: st.markdown(f"- {b}")
    
    # 8
    st.subheader("8. What They Look Like When Struggling")
    st.write(c['s8_struggling']['text'])
    for b in c['s8_struggling']['bullets']: st.markdown(f"- {b}")
    
    # 9
    st.subheader("9. Supervisory Interventions")
    st.write("When this staff member is struggling, use these targeted interventions:")
    interventions = [
        f"Validate their Motivation ({p_mot}) before correcting behavior.",
        f"Address the Stress Response: Gently point out if they are becoming {c['s8_struggling']['bullets'][0].lower()}.",
        "Re-align Expectations: Ensure they know exactly what success looks like in this specific situation.",
        "Check for Burnout: Are they over-functioning in their style?"
    ]
    for i in interventions: st.markdown(f"- {i}")
    
    # 10
    st.subheader("10. What You Should Celebrate")
    st.write(m['s10_celebrate']['text'])
    for b in m['s10_celebrate']['bullets']: st.markdown(f"- {b}")
    
    # 11
    st.subheader("11. Coaching Questions")
    for q in c['s11_coaching']: st.markdown(f"- {q}")
    
    # 12
    st.subheader("12. Helping Them Prepare for Advancement")
    st.write(c['s12_advancement']['text'])
    for b in c['s12_advancement']['bullets']: st.markdown(f"- {b}")

# --- PDF Generator ---
def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    blue = (1, 91, 173)
    black = (0, 0, 0)
    
    # HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
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
        f"Validate their Motivation ({p_mot}) before correcting behavior.",
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

staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

# RESET FUNCTIONS (Defined at module level for safety)
def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

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
                    # Generate PDF Logic
                    pdf_bytes = create_supervisor_guide(
                        data['name'], data['role'], 
                        data['p_comm'], data['s_comm'], 
                        data['p_mot'], data['s_mot']
                    )
                    st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf", mime="application/pdf")
                    
                    # DISPLAY ON SCREEN
                    st.divider()
                    display_guide(data['name'], data['role'], data['p_comm'], data['s_comm'], data['p_mot'], data['s_mot'])

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
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")
                
                # DISPLAY ON SCREEN
                st.divider()
                display_guide(m_name, m_role, m_p_comm, "None", m_p_mot, "None")

# --- TAB 2: TEAM DNA ---
with tab2:
    st.markdown("### 🧬 Team Dynamics Mapper")
    if not df.empty:
        team_selection = st.multiselect("Build your Team", df['name'].tolist(), key="t2_team_select")
        
        if team_selection:
            team_df = df[df['name'].isin(team_selection)]
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Communication Mix")
                comm_counts = team_df['p_comm'].value_counts()
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4), use_container_width=True)
            with c2:
                st.subheader("Motivation Drivers")
                mot_counts = team_df['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values), use_container_width=True)
            
            st.markdown("---")
            st.button("Clear Team Selection", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1", placeholder="Select first person...")
        with c2:
            p2_name = st.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2", placeholder="Select second person...")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            sup_style, staff_style = p1['p_comm'], p2['p_comm']
            
            st.divider()
            st.subheader(f"Dynamic: {sup_style} (You) vs. {staff_style} (Staff)")
            
            if sup_style == staff_style:
                st.warning("⚠️ **Same-Style Blindspot:** You both communicate the same way.")
            elif sup_style in SUPERVISOR_CLASH_MATRIX and staff_style in SUPERVISOR_CLASH_MATRIX[sup_style]:
                data = SUPERVISOR_CLASH_MATRIX[sup_style][staff_style]
                
                with st.expander("🔥 The Dynamic (Read First)", expanded=True):
                    st.write(data['tension'])
                    st.markdown("**✅ Pre-Meeting Mindset:**")
                    for item in data['prep']: st.markdown(f"- {item}")
                    st.markdown("**📋 Step-by-Step Protocol:**")
                    for item in data['protocol']: st.markdown(f"- {item}")
                
                st.divider()
                st.markdown("#### 🗣️ 1:1 Script Options")
                st.info(f"**To You:** {data['scripts'].get('To Director') or data['scripts'].get('To Encourager') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}")
                st.warning(f"**To Them:** {data['scripts'].get('To Encourager') or data['scripts'].get('To Director') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}")
                st.success(f"**Joint:** {data['scripts']['Joint']}")
            
            st.markdown("---")
            st.button("Reset Conflict Tool", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    
    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select candidate...")
        with col_b:
            target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select target role...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            
            st.divider()
            st.markdown(f"**Candidate:** {cand['name']} ({style})")
            st.markdown(f"**Target:** {target_role}")
            
            path_data = CAREER_PATHWAYS.get(style, {}).get(target_role)
            
            if path_data:
                st.info(f"💡 **The Core Shift:** {path_data['shift']}")
                st.markdown(f"**Why it's hard for a {style}:** {path_data['why']}")
                
                st.divider()
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                    if 'supervisor_focus' in path_data:
                        st.warning(f"👀 **Supervisor Focus:**\n\n{path_data['supervisor_focus']}")
                with c2:
                    st.markdown("#### ✅ The Developmental Assignment")
                    with st.container(border=True):
                        st.write(f"**Setup:** {path_data['assignment_setup']}")
                        st.write(f"**The Task:** {path_data['assignment_task']}")
                        st.divider()
                        st.success(f"**🏆 Success looks like:** {path_data['success_indicators']}")
                        st.error(f"**🚩 Red flag:** {path_data['red_flags']}")
            else:
                st.write("Standard advancement path.")
            
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
            st.info("Tip: If 'Shift Supervisors' are mostly 'Encouragers' but 'Program Supervisors' are mostly 'Directors', expect friction during hand-offs.")
    else:
        st.warning("No data available.")
