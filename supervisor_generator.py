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

# --- CAREER PATHWAYS (Expanded) ---
CAREER_PATHWAYS = {
    "Director": {
        "Shift Supervisor": {
            "shift": "From 'Doing' to 'Enabling'.",
            "why": "Directors act fast. They see a problem and fix it. As a Shift Sup, if they fix everything, their team learns nothing. They become the bottleneck.",
            "conversation": "You have high capacity and speed, which is a gift. To succeed as a Shift Supervisor, you have to resist the urge to 'rescue' the shift by doing everything yourself. Your success is no longer defined by how many tasks *you* complete, but by how confident your team feels completing theirs.",
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless absolute safety dictates otherwise).",
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

# --- PDF Content Dictionaries (Full Text) ---
COMM_PROFILES = {
    "Director": {
        "overview": "This staff member communicates primarily as a Director, meaning they lead with clarity, structure, and urgency.",
        "supervising": "Be direct, concise, and outcome-focused. They respect leaders who get to the point. Define the 'what' clearly, but give autonomy on the 'how'.",
        "struggle_bullets": ["Decreased patience", "Over-assertiveness", "Fatigue/Irritability", "Rigid enforcement"],
        "coaching": ["What are the risks of moving this fast?", "Who haven't we heard from yet?", "How can you frame this so the team feels supported?", "What is the difference between being 'right' and being 'effective'?", "If you had to achieve this result without giving a single order, how would you do it?"],
        "advancement": "Challenge them to lead through influence rather than authority. Help them practice patience."
    },
    "Encourager": {
        "overview": "This staff member communicates primarily as an Encourager, leading with warmth, optimism, and emotional intelligence.",
        "supervising": "Connect relationally before diving into tasks. Validate their emotional labor. Frame criticism around professional growth.",
        "struggle_bullets": ["Avoidance of conflict", "Disorganization", "Prioritizing being liked", "Emotional exhaustion"],
        "coaching": ["How can you deliver this hard news while remaining kind?", "Are we prioritizing popularity over effectiveness?", "What boundaries do you need to set?", "If you avoid this conflict today, what is the cost to the team next week?", "How does holding this standard actually create safety for the youth?"],
        "advancement": "Help them master the operational side. Challenge them to see clarity and accountability as kindness."
    },
    "Facilitator": {
        "overview": "This staff member communicates primarily as a Facilitator, leading by listening, gathering perspectives, and seeking fairness.",
        "supervising": "Give them time to process. Ask for observations explicitly. Validate fairness but push for decisions.",
        "struggle_bullets": ["Analysis paralysis", "Passive-aggressiveness", "Saying 'it's fine' when it isn't", "Getting stuck in the middle"],
        "coaching": ["If you had to decide right now, what would you do?", "What is the cost of waiting?", "Where are you holding tension?", "Who specifically are you trying not to upset with this decision?", "How can you support the team's direction even if you don't fully agree?"],
        "advancement": "Encourage them to be more vocal and decisive. Help them be assertive without being aggressive."
    },
    "Tracker": {
        "overview": "This staff member communicates primarily as a Tracker, leading with details, data, and systems.",
        "supervising": "Provide clear expectations. Respecting their systems builds trust. Explain the 'why' behind changes.",
        "struggle_bullets": ["Rigidity/Perfectionism", "Getting stuck in weeds", "Coming across as cold", "Prioritizing policy over people"],
        "coaching": ["Does this detail change the outcome?", "How can we meet the standard while keeping the relationship warm?", "What is the big picture goal?", "If we follow the rule perfectly but lose the kid's trust, did we succeed?", "What is the 'Good Enough' version of this task?"],
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
        "celebrate": "Celebrate moments where their work directly impacted a youth's life."
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
        if response.status_code == 200: return response.json()
        return []
    except Exception: return []

def create_supervisor_guide(name, role, p_comm, s_comm, p_mot, s_mot):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    blue = (1, 91, 173); black = (0, 0, 0)
    
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
    c = COMM_PROFILES.get(p_comm, COMM_PROFILES["Director"])
    m = MOTIVATION_PROFILES.get(p_mot, MOTIVATION_PROFILES["Achievement"])

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
    add_body(c['s1_profile']['text'])
    add_bullets(c['s1_profile']['bullets'])

    add_heading("2. Supervising Their Communication")
    add_body(c['s2_supervising']['text'])
    add_bullets(c['s2_supervising']['bullets'])

    add_heading(f"3. Motivation Profile: {p_mot}")
    add_body(m['s3_profile']['text'])
    add_bullets(m['s3_profile']['bullets'])

    add_heading("4. Motivating This Staff Member")
    add_body(m['s4_motivating']['text'])
    add_bullets(m['s4_motivating']['bullets'])

    integrated_text = (
        f"This staff member operates at the intersection of {p_comm} energy and {p_mot} drive. "
        f"They lead with {p_comm} traits (prioritizing {COMM_TRAITS.get(p_comm, {}).get('focus', 'their style')}) "
        f"while seeking {p_mot} outcomes (valuing {MOTIVATION_PROFILES.get(p_mot, {}).get('s3_profile', {}).get('bullets', ['result'])[0]}). "
        "When these align, they are unstoppable. When they conflict, frustration mounts quickly."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    add_heading("6. How You Can Best Support Them")
    add_body(m['s6_support']['text'])
    add_bullets(m['s6_support']['bullets'])

    add_heading("7. What They Look Like When Thriving")
    add_body(m['s7_thriving']['text'])
    add_bullets(m['s7_thriving']['bullets'])

    add_heading("8. What They Look Like When Struggling")
    add_body(c['s8_struggling']['text'])
    add_bullets(c['s8_struggling']['bullets'])

    add_heading("9. Supervisory Interventions")
    add_bullets([
        f"Validate their Motivation ({p_mot}) before correcting behavior.",
        f"Address the Stress Response: Gently point out if they are becoming {c['s8_struggling']['bullets'][0].lower()}.",
        "Re-align Expectations: Ensure they know exactly what success looks like in this specific situation.",
        "Check for Burnout: Are they over-functioning in their style?"
    ])

    add_heading("10. What You Should Celebrate")
    add_body(m['s10_celebrate']['text'])
    add_bullets(m['s10_celebrate']['bullets'])

    add_heading("11. Coaching Questions")
    add_bullets(c['s11_coaching'])

    add_heading("12. Helping Them Prepare for Advancement")
    add_body(c['s12_advancement']['text'])
    add_bullets(c['s12_advancement']['bullets'])

    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP LOGIC ---

staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

def reset_t1(): st.session_state.t1_staff_select = None
def reset_t2(): st.session_state.t2_team_select = []
def reset_t3(): st.session_state.p1 = None; st.session_state.p2 = None
def reset_t4(): st.session_state.career = None; st.session_state.career_target = None

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Guide Generator", "🧬 Team DNA", "⚖️ Conflict Mediator", "🚀 Career Pathfinder", "📈 Org Pulse"])

# --- TAB 1: GUIDE GENERATOR ---
with tab1:
    st.markdown("### Generate Individual Supervisory Guides")
    c_a, c_b = st.columns([3, 1])
    with c_b: 
        if st.button("🔄 Refresh Database"): st.cache_data.clear(); st.rerun()
    
    subtab1, subtab2 = st.tabs(["📚 From Database", "✏️ Manual Entry"])
    
    with subtab1:
        if not df.empty:
            staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            selected_staff_name = st.selectbox("Select Staff Member", options=list(staff_options.keys()), index=None, key="t1_staff_select", placeholder="Choose a staff member...")
            if selected_staff_name:
                data = staff_options[selected_staff_name]
                col1, col2, col3 = st.columns(3)
                col1.metric("Role", data['role'])
                col2.metric("Communication", data['p_comm'])
                col3.metric("Motivation", data['p_mot'])
                if st.button("Generate Guide for " + data['name'], type="primary"):
                    pdf_bytes = create_supervisor_guide(
                        data['name'], data['role'], data['p_comm'], data['s_comm'], data['p_mot'], data['s_mot']
                    )
                    st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{data['name'].replace(' ', '_')}.pdf", mime="application/pdf")
                st.markdown("---")
                st.button("Reset Selection", key="reset_t1_db", on_click=reset_t1)
        else: st.info("Database empty.")

    with subtab2:
        with st.form("manual_form"):
            c1, c2 = st.columns(2)
            with c1:
                m_name = st.text_input("Staff Name")
                m_role = st.selectbox("Role", ["Program Supervisor", "Shift Supervisor", "YDP"])
            with c2:
                m_p_comm = st.selectbox("Primary Communication", ["Director", "Encourager", "Facilitator", "Tracker"])
                m_p_mot = st.selectbox("Primary Motivation", ["Growth", "Purpose", "Connection", "Achievement"])
            if st.form_submit_button("Generate Guide") and m_name:
                pdf_bytes = create_supervisor_guide(m_name, m_role, m_p_comm, "None", m_p_mot, "None")
                st.download_button(label="Download PDF Guide", data=pdf_bytes, file_name=f"Supervisor_Guide_{m_name.replace(' ', '_')}.pdf", mime="application/pdf")

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
                comm_counts = team_df['p_comm'].value_counts()
                st.plotly_chart(px.pie(names=comm_counts.index, values=comm_counts.values, hole=0.4, title="Communication Mix"), use_container_width=True)
            with c2:
                mot_counts = team_df['p_mot'].value_counts()
                st.plotly_chart(px.bar(x=mot_counts.index, y=mot_counts.values, title="Motivation Drivers"), use_container_width=True)
            st.markdown("---")
            st.button("Clear Team", key="reset_btn_t2", on_click=reset_t2)

# --- TAB 3: CONFLICT MEDIATOR ---
with tab3:
    st.markdown("### ⚖️ Conflict Resolution Script")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: p1_name = st.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1", placeholder="Select...")
        with c2: p2_name = st.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2", placeholder="Select...")
        
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            sup_style, staff_style = p1['p_comm'], p2['p_comm']
            st.divider()
            st.subheader(f"Dynamic: {sup_style} (You) vs. {staff_style} (Staff)")
            
            if sup_style == staff_style:
                st.warning("Same-Style Conflict: You amplify each other's weaknesses.")
            elif sup_style in SUPERVISOR_CLASH_MATRIX and staff_style in SUPERVISOR_CLASH_MATRIX[sup_style]:
                data = SUPERVISOR_CLASH_MATRIX[sup_style][staff_style]
                
                with st.expander("🔥 The Tension & Root Cause (Read First)", expanded=True):
                    st.markdown(f"**{data['tension']}**")
                    st.markdown(f"**Root Cause:** {data['root_cause']}")
                    st.markdown("**👀 Watch For:**")
                    for w in data['watch_fors']: st.markdown(f"- {w}")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🛠️ Intervention Plan")
                    for s in data['intervention_steps']: st.markdown(s)
                with c_b:
                    st.markdown("#### 🗣️ Script Library")
                    st.info(f"**To You:** {data['scripts'].get('To Director') or data['scripts'].get('To Encourager') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}") # Dynamic fallback
                    st.warning(f"**To Them:** {data['scripts'].get('To Encourager') or data['scripts'].get('To Director') or data['scripts'].get('To Facilitator') or data['scripts'].get('To Tracker')}")
                    st.success(f"**Joint:** {data['scripts']['Joint']}")

            st.markdown("---")
            st.button("Reset", key="reset_btn_t3", on_click=reset_t3)

# --- TAB 4: CAREER PATHFINDER ---
with tab4:
    st.markdown("### 🚀 Career Gap Analysis")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: candidate_name = st.selectbox("Select Candidate", df['name'].unique(), index=None, key="career", placeholder="Select candidate...")
        with c2: target_role = st.selectbox("Target Role", ["Shift Supervisor", "Program Supervisor", "Manager"], index=None, key="career_target", placeholder="Select target role...")
        
        if candidate_name and target_role:
            cand = df[df['name'] == candidate_name].iloc[0]
            style = cand['p_comm']
            path_data = CAREER_PATHWAYS.get(style, {}).get(target_role)
            
            if path_data:
                st.info(f"💡 **The Shift:** {path_data['shift']}")
                st.markdown(f"**The Why:** {path_data['why']}")
                st.divider()
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🗣️ The Coaching Conversation")
                    st.write(path_data['conversation'])
                    st.warning(f"**👀 Watch For:** {path_data.get('supervisor_focus')}")
                with c_b:
                    st.markdown("#### ✅ The 'Litmus Test' Assignment")
                    with st.container(border=True):
                        st.markdown(f"**Setup:** {path_data['assignment_setup']}")
                        st.markdown(f"**Task:** {path_data['assignment_task']}")
                        st.divider()
                        st.success(f"**🏆 Success:** {path_data['success_indicators']}")
                        st.error(f"**🚩 Red Flag:** {path_data['red_flags']}")
            st.markdown("---")
            st.button("Reset", key="reset_btn_t4", on_click=reset_t4)

# --- TAB 5: ORG PULSE ---
with tab5:
    st.markdown("### 📈 Organization Pulse")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.pie(df, names='p_comm', title="Communication Styles"), use_container_width=True)
        with c2: st.plotly_chart(px.bar(df, x='p_mot', title="Motivation Drivers"), use_container_width=True)
        if 'role' in df.columns:
            st.dataframe(pd.crosstab(df['role'], df['p_comm']).style.background_gradient(cmap="Blues"), use_container_width=True)
    else: st.warning("No data available.")
