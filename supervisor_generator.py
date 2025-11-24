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

COMM_TRAITS = {
    "Director": {"focus": "Action & Speed", "blindspot": "Patience & Consensus", "needs": "Clarity & Autonomy"},
    "Encourager": {"focus": "Morale & Harmony", "blindspot": "Hard Truths & Conflict", "needs": "Validation & Connection"},
    "Facilitator": {"focus": "Fairness & Process", "blindspot": "Decisiveness & Speed", "needs": "Time & Perspective"},
    "Tracker": {"focus": "Details & Safety", "blindspot": "Flexibility & Big Picture", "needs": "Structure & Logic"}
}

# --- EXPANDED SUPERVISOR CLASH MATRIX ---
SUPERVISOR_CLASH_MATRIX = {
    "Director": {
        "Encourager": {
            "dynamic_text": "This is the classic 'Task vs. Relationship' friction. As a Director, you prioritize speed, clarity, and results. You likely view the Encourager's need for emotional processing as an obstacle to execution. Conversely, the Encourager views your directness as aggression. They feel unsafe when you skip the 'human element', causing them to withdraw or passively resist.",
            "dynamic_bullets": [
                "You push for 'What by When'; they want to know 'Who and How does it feel'.",
                "You interpret their silence as agreement; usually, it is fear or hurt.",
                "They interpret your brevity as anger."
            ],
            "self_check_text": "Am I optimizing for efficiency at the expense of effectiveness? If I 'win' this conversation by overpowering them with logic, I lose their loyalty. I need to realize that for an Encourager, feeling heard is a prerequisite for getting back to work.",
            "self_check_bullets": [
                "Did I start the meeting with a relational check-in, or did I dive straight into the error?",
                "Am I interrupting them to 'get to the point'?",
                "Is my tone conveying frustration before they even speak?"
            ],
            "script_text": "Bridge the gap between your need for speed and their need for safety.",
            "script_options": [
                "Opening: 'I know I can be intense when I’m focused on a goal. I want to pause and check in—how are you feeling about this project right now?'",
                "Validation: 'I value how much you care about the team. I don't want my directness to shut that down.'",
                "The Ask: 'I need your help to get us to the finish line. Can we agree on the plan, while you help me monitor the team's morale?'"
            ]
        },
        "Facilitator": {
            "dynamic_text": "The 'Gas vs. Brake' dynamic. You operate on 'Ready, Fire, Aim'. They operate on 'Ready, Aim, Aim...'. You feel slowed down and obstructed by their need for consensus. They feel steamrolled and reckless because you act without hearing every voice. You risk making fast decisions that fail because the team wasn't bought in.",
            "dynamic_bullets": [
                "You perceive their processing time as 'stalling'.",
                "They perceive your decisiveness as 'arrogance'.",
                "You interrupt to force a conclusion; they retreat into silence."
            ],
            "self_check_text": "Am I mistaking their 'processing time' for 'resistance'? If I force a decision before they are heard, I get compliance, not buy-in. I need to slow down to speed up.",
            "self_check_bullets": [
                "Did I give them the agenda in advance so they could prepare?",
                "Am I demanding an answer in the hallway instead of a scheduled meeting?",
                "Have I asked for their perspective, or just told them mine?"
            ],
            "script_text": "Acknowledge the pace difference and negotiate a deadline.",
            "script_options": [
                "Opening: 'I feel a lot of urgency to move this forward, but I know you need to ensure we aren't missing perspectives.'",
                "Validation: 'I respect your need to get this right. I don't want to be reckless.'",
                "The Ask: 'I can't wait forever, but I can wait 24 hours. What specific input do you need before we make the final call tomorrow?'"
            ]
        },
        "Tracker": {
            "dynamic_text": "The 'Vision vs. Obstacles' dynamic. You say 'Make it happen.' They say 'But Regulation 14.B says...'. You feel they are blocking you with red tape; they feel you are asking them to be negligent. You care about the destination; they care about the safe path.",
            "dynamic_bullets": [
                "You speak in broad strokes; they speak in footnotes.",
                "You get annoyed by 'details'; they get panicked by 'vague ideas'.",
                "They say 'No' to protect you; you hear 'No' as defiance."
            ],
            "self_check_text": "Am I dismissing their details because they are annoying, or because they are irrelevant? Usually, they are trying to keep me out of trouble. I need to stop fighting their data.",
            "self_check_bullets": [
                "Did I explain the 'Why' before demanding the 'What'?",
                "Am I asking them to violate a safety protocol just to save time?",
                "Did I roll my eyes when they brought up a policy?"
            ],
            "script_text": "Validate their expertise, then ask for a solution path.",
            "script_options": [
                "Opening: 'I appreciate you watching the compliance side of this. I know I miss those details sometimes.'",
                "Validation: 'I know this request pushes the envelope on our usual process.'",
                "The Ask: 'I feel frustrated when I hear 'No' without a 'How'. Instead of telling me why we can't do it, can you map out the safest path to get us to 'Yes'?'"
            ]
        },
        "Director": {
            "dynamic_text": "The 'Power Struggle'. Two alphas in a room. You both want to lead. The conversation quickly becomes a debate about who is right rather than what is best. You both interrupt, you both speak loudly, and neither listens. The risk is a permanent ego-clash.",
            "dynamic_bullets": [
                "Conversations feel like combat.",
                "You both fight for the last word.",
                "You micromanage them because they do it differently than you."
            ],
            "self_check_text": "Am I fighting to be 'The Boss' or to solve the problem? I need to give them a lane to lead. They don't need my protection; they need my trust.",
            "self_check_bullets": [
                "Am I arguing about the method (how) or the outcome (what)?",
                "Did I interrupt them more than once?",
                "Can I let them win this point?"
            ],
            "script_text": "Call a truce and divide the territory.",
            "script_options": [
                "Opening: 'We both have strong opinions and want to move fast. I think we are getting in each other's way.'",
                "Validation: 'I trust your ability to execute this.'",
                "The Ask: 'I'm going to define the 'What' (the Goal), and I'm going to trust you with the 'How'. I won't micromanage it. Go run with it.'"
            ]
        }
    },
    "Encourager": {
        "Director": {
            "dynamic_text": "The 'Soft vs. Hard' dynamic. They want the bottom line; you want the story. They interrupt you or check their phone while you talk, which hurts your feelings. You perceive them as 'mean' or 'uncaring'. You likely over-explain to try and get them to connect, which makes them tune out more.",
            "dynamic_bullets": [
                "You feel steamrolled by their speed.",
                "They seem annoyed by your relationship-building.",
                "You take their professional critiques personally."
            ],
            "self_check_text": "Am I taking their directness personally? Am I burying the headline? I need to speak their language (Results) to be heard. I cannot force them to be my therapist.",
            "self_check_bullets": [
                "Did I start with the main point, or a story?",
                "Am I reading malice into their brevity?",
                "Am I avoiding the hard truth because I want them to like me?"
            ],
            "script_text": "Speak their language (efficiency) to buy space for your language (humanity).",
            "script_options": [
                "Opening: 'I know you value efficiency, so I will give you the bottom line first.'",
                "Validation: 'I know we need to hit this target.'",
                "The Ask: 'To get there, I need you to soften your delivery with the team. If we push this hard, we will lose them, and that will hurt the result.'"
            ]
        },
        "Facilitator": {
            "dynamic_text": "The 'Nice-Off'. You want to protect the individual's feelings; they want to be fair to the group. You both avoid conflict, so decisions stall indefinitely. You spend meetings agreeing with each other but nothing changes because neither of you wants to be the 'bad guy' to the staff.",
            "dynamic_bullets": [
                "Meetings are pleasant but unproductive.",
                "Bad behavior persists because 'we don't want to upset them'.",
                "You defer to them; they defer to you."
            ],
            "self_check_text": "Am I prioritizing being liked over being effective? Are we circling the issue to avoid upsetting someone? I need to be the leader, not the friend.",
            "self_check_bullets": [
                "Have we talked about this issue 3 times without solving it?",
                "Am I waiting for them to do the hard part?",
                "Is my empathy actually enabling poor performance?"
            ],
            "script_text": "Name the dynamic and force a decision.",
            "script_options": [
                "Opening: 'I feel like we are both trying to be kind here, but the lack of a decision is actually hurting the team.'",
                "Validation: 'I love that we care about the staff.'",
                "The Ask: 'I'm going to make the call to move forward, even though it might be uncomfortable. I need you to back me up.'"
            ]
        },
        "Tracker": {
            "dynamic_text": "The 'Chaos vs. Order' dynamic. You bend rules to help people. They enforce rules to protect people. They think you are unsafe/chaotic; you think they are cold/robotic. You feel judged by their clipboard. They feel undermined by your exceptions.",
            "dynamic_bullets": [
                "You say 'It depends'; they say 'The rule is X'.",
                "You feel restricted by their process.",
                "They feel anxious about your spontaneity."
            ],
            "self_check_text": "Am I undermining their authority by being inconsistent? Structure is a form of care. If I change the rules based on my mood, I am not being kind, I am being confusing.",
            "self_check_bullets": [
                "Did I change a plan without telling them?",
                "Am I prioritizing a 'nice moment' over long-term consistency?",
                "Did I validate their concern for safety?"
            ],
            "script_text": "Validate the structure, then ask for flexibility.",
            "script_options": [
                "Opening: 'I know my flexibility stresses you out because you value consistency. I value it too.'",
                "Validation: 'Your attention to detail keeps us safe.'",
                "The Ask: 'Help me build a structure that still allows room for human judgment in this specific case, and I promise to stick to it.'"
            ]
        },
        "Encourager": {
            "dynamic_text": "The 'Therapy Session'. You connect deeply and support each other, but you may struggle to hold each other accountable. Meetings feel good—lots of venting and validation—but produce few action items. You risk creating a clique that feels 'us vs. them'.",
            "dynamic_bullets": [
                "You spend 80% of the meeting dealing with feelings.",
                "You avoid giving each other feedback.",
                "You enable each other's stress rather than solving it."
            ],
            "self_check_text": "Are we just venting? Venting feels good but changes nothing. I need to pivot this connection into action. We need to be professionals, not just friends.",
            "self_check_bullets": [
                "Did we create an action plan?",
                "Am I afraid to challenge them?",
                "Are we feeding each other's negativity?"
            ],
            "script_text": "Pivot from feelings to action.",
            "script_options": [
                "Opening: 'I love that we support each other. It helps me get through the day.'",
                "Validation: 'It is really hard right now.'",
                "The Ask: 'But to protect the program, I need to put my 'Boss Hat' on for a second. We have to fix [Issue], even if it feels hard.'"
            ]
        }
    },
    "Facilitator": {
        "Director": {
            "dynamic_text": "The 'Steamroll'. They demand a decision. You freeze because you haven't heard from everyone. They interpret your silence as agreement or incompetence. You feel unsafe speaking up because they are so forceful.",
            "dynamic_bullets": [
                "You retreat into silence when they push.",
                "They move forward assuming you agreed.",
                "You resent them for not listening."
            ],
            "self_check_text": "Am I hiding behind 'the team's opinion' to avoid taking a stand? I need to be decisive. Silence is consent. If I don't speak up, I can't complain later.",
            "self_check_bullets": [
                "Did I say 'I disagree' or did I just stay quiet?",
                "Am I waiting for permission to lead?",
                "Is my need for consensus an excuse for delay?"
            ],
            "script_text": "Assert your role as the risk-manager.",
            "script_options": [
                "Opening: 'I know you want an answer now. I am not stalling; I am risk-managing.'",
                "Validation: 'I agree we need to move.'",
                "The Ask: 'If we decide without [Person]'s input, the plan will fail. I will have the answer for you by [Time]. Can you wait until then?'"
            ]
        },
        "Encourager": {
            "dynamic_text": "The 'Fairness vs. Feelings' dynamic. You are looking at the system fairness; they are looking at the person's feelings. You might struggle to rein them in when they over-function for a client, creating inequity in the program.",
            "dynamic_bullets": [
                "They want an exception; you want a precedent.",
                "You feel they are playing favorites.",
                "They feel you are being too clinical."
            ],
            "self_check_text": "Am I being too clinical? I need to validate the heart behind their actions before correcting the process. They need to know I care about the person, not just the policy.",
            "self_check_bullets": [
                "Did I acknowledge their good intent?",
                "Am I focusing too much on 'being fair' and missing the crisis?",
                "Can I explain the 'why' of the rule?"
            ],
            "script_text": "Connect the specific exception to the general harm.",
            "script_options": [
                "Opening: 'I see how much you care about [Youth]. Your heart is in the right place.'",
                "Validation: 'I know you want to help.'",
                "The Ask: 'However, if we make a special exception for him, it creates unfairness for the other 10 kids. We need a solution that is fair to everyone.'"
            ]
        },
        "Tracker": {
            "dynamic_text": "The 'Analysis Paralysis' Loop. You want consensus; they want data. You both are risk-averse. You wait for everyone to agree; they wait for the perfect plan. The program stagnates because no one pulls the trigger.",
            "dynamic_bullets": [
                "Meetings end with 'let's look into it more'.",
                "Zero risk tolerance.",
                "Frustration from the team due to lack of direction."
            ],
            "self_check_text": "Am I waiting for perfect agreement? It doesn't exist. Leadership is making decisions with imperfect information. I need to declare a direction.",
            "self_check_bullets": [
                "Is this decision reversible? If yes, just make it.",
                "Am I afraid of being wrong?",
                "Do we really need more data?"
            ],
            "script_text": "Authorize the imperfect action.",
            "script_options": [
                "Opening: 'We have analyzed this enough. We are never going to be 100% sure.'",
                "Validation: 'I appreciate your caution.'",
                "The Ask: 'I am making the decision to go with Plan A. I need you to help me track the data to see if it works, and we can adjust later.'"
            ]
        },
        "Facilitator": {
            "dynamic_text": "The 'Committee'. Endless meetings. Great process, low output. You both listen, nod, and validate, but no one directs. The team feels heard but leaderless.",
            "dynamic_bullets": [
                "Conversations go in circles.",
                "Everyone feels good but nothing gets done.",
                "Conflict is buried under politeness."
            ],
            "self_check_text": "Who is driving the bus? If I don't set the destination, no one will. I need to stop facilitating and start directing.",
            "self_check_bullets": [
                "Did I state a clear decision at the end?",
                "Am I hoping they will decide so I don't have to?",
                "Is this meeting necessary?"
            ],
            "script_text": "Shift modes from Facilitator to Director.",
            "script_options": [
                "Opening: 'We are spinning. We have heard all the viewpoints.'",
                "Validation: 'I appreciate the dialogue.'",
                "The Ask: 'I'm going to step out of 'listening mode' and into 'directing mode'. Here is the plan we are going with.'"
            ]
        }
    },
    "Tracker": {
        "Director": {
            "dynamic_text": "The 'Micromanagement Trap'. You see their broad strokes as reckless. You ask 10 specific questions to ensure safety; they get annoyed and feel you don't trust them. You feel disrespected when they ignore your protocols.",
            "dynamic_bullets": [
                "You nag them about details; they avoid you.",
                "You feel anxious about their speed.",
                "They feel handcuffed by your questions."
            ],
            "self_check_text": "Am I trying to control them? I need to trust their intent and only block on true safety issues. Not every detail needs to be perfect; it just needs to be safe.",
            "self_check_bullets": [
                "Is this a 'Must Have' or a 'Nice to Have'?",
                "Am I asking questions to delay the action?",
                "Can I let them fail on a small thing?"
            ],
            "script_text": "Distinguish between blocking and helping.",
            "script_options": [
                "Opening: 'I'm not trying to slow you down; I'm trying to ensure this sticks.'",
                "Validation: 'I know you want to move fast.'",
                "The Ask: 'I don't need to control the whole project, but I do need veto power on these two specific safety compliance items. The rest is yours.'"
            ]
        },
        "Encourager": {
            "dynamic_text": "The 'Rules vs. Relationship' dynamic. You see their exceptions as chaos. They feel judged by your clipboard. You risk becoming the 'Principal' to their 'Cool Teacher'. They think you care more about the paperwork than the people.",
            "dynamic_bullets": [
                "You correct them publicly; they shut down.",
                "You quote policy; they quote feelings.",
                "Resentment builds over 'nitpicking'."
            ],
            "self_check_text": "Am I valuing the paperwork over the person? I need to explain the 'Why' (Safety) not just the 'What' (Rule). I need to connect before I correct.",
            "self_check_bullets": [
                "Did I say hello before I pointed out the error?",
                "Is this rule critical for safety?",
                "Am I being right or being effective?"
            ],
            "script_text": "Link the rule to the relationship.",
            "script_options": [
                "Opening: 'I know it feels rigid when I enforce that rule.'",
                "Validation: 'I know you are trying to connect with the youth.'",
                "The Ask: 'But when you bend the rule for that youth, it makes the shift unsafe for the rest of us because we don't know what to expect. I need you to follow the protocol to keep us safe.'"
            ]
        },
        "Facilitator": {
            "dynamic_text": "The 'Details vs. Concepts' dynamic. You want a checklist; they want a conversation. You get frustrated when meetings end without a clear 'To-Do' list. They feel you are rushing the relational process.",
            "dynamic_bullets": [
                "You check your watch while they talk.",
                "They feel you are transactional.",
                "You leave meetings confused about next steps."
            ],
            "self_check_text": "Am I being too rigid? Sometimes the 'deliverable' is just alignment, not a spreadsheet. I need to value the soft work they are doing.",
            "self_check_bullets": [
                "Did I listen or just wait to speak?",
                "Am I demanding clarity too soon?",
                "Can I tolerate some ambiguity?"
            ],
            "script_text": "Ask for the specific output.",
            "script_options": [
                "Opening: 'I appreciate the discussion and the perspective.'",
                "Validation: 'It is important we are all aligned.'",
                "The Ask: 'To help me execute this, can we spend the last 5 minutes defining exactly who is doing what by when?'"
            ]
        },
        "Tracker": {
            "dynamic_text": "The 'Audit'. You both love details. You might argue over *which* rule applies or the specific formatting of a document. You risk missing the forest for the trees, creating a perfect system that no one uses.",
            "dynamic_bullets": [
                "Arguments over semantics.",
                "Email wars with bullet points.",
                "Zero emotional connection."
            ],
            "self_check_text": "Are we rearranging deck chairs on the Titanic? We need to zoom out. The goal isn't a perfect spreadsheet; it's a functioning program.",
            "self_check_bullets": [
                "Does this detail actually matter?",
                "Are we ignoring the human element?",
                "When was the last time we talked about a person?"
            ],
            "script_text": "Zoom out to the goal.",
            "script_options": [
                "Opening: 'I think we are getting stuck in the weeds here.'",
                "Validation: 'I know we both want this to be accurate.'",
                "The Ask: 'Let's pause the detail work. What is the actual outcome we need for the client today? Let's solve for that first.'"
            ]
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
            "assignment_setup": "Assign them to lead a shift where they are physically restricted to the office or a central hub (unless safety dictates otherwise).",
            "assignment_task": "They must run the shift entirely through verbal direction and delegation to peers. They cannot touch paperwork or intervene in minor conflicts.",
            "success_indicators": "Did they let a staff member struggle through a task without jumping in? Did they give clear verbal instructions?",
            "red_flags": "They ran out of the office to 'just do it quick'. They complain that their team is 'too slow'.",
            "supervisor_focus": "Watch for 'Hero Mode'. If you see them jumping in to fix a crisis that their staff could handle, intervene. Pull them back and say, 'Let your team handle this. Coach them, don't save them.'"
        },
        "Program Supervisor": {
            "shift": "From 'Command' to 'Influence'.",
            "why": "Program Sups need buy-in from people they don't supervise (School, Clinical). Directors tend to order people around, which alienates peers.",
            "conversation": "You are excellent at execution within your unit. However, program leadership requires getting buy-in from people you don't supervise (School, Clinical, other cottages). You need to learn that 'slowing down' to build relationships is actually a strategic move that speeds up long-term results.",
            "assignment_setup": "Identify a peer in another department (School/Clinical) they have friction with.",
            "assignment_task": "Task them with a cross-departmental project (e.g., improving school transitions). They must interview stakeholders and present a plan that incorporates *their* feedback.",
            "success_indicators": "The plan includes ideas that clearly didn't come from the Director. The peer reports feeling heard.",
            "red_flags": "They present a plan that is 100% their own idea and complain that the other dept is 'difficult'.",
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
            "conversation": "You naturally carry the emotions of your people. At the manager level, the weight is too heavy to carry alone. Your growth edge is learning to set emotional boundaries—caring deeply about the person without taking responsibility for their feelings.",
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
            "conversation": "You are brilliant at the details. But you cannot track every detail personally at this level without burning out or micromanaging. Your growth is trusting your team. You have to let them do the checklist, even if they do it differently than you would.",
            "assignment_setup": "The 'Hands-Off' Day. Assign them to supervise a complex task (intake/search).",
            "assignment_task": "Strictly prohibited from touching paperwork. Must guide a peer to do it verbally.",
            "success_indicators": "They kept their hands in their pockets. They gave clear corrections without taking over.",
            "red_flags": "They grabbed the pen. They sighed and said 'I'll just do it'.",
            "supervisor_focus": "Watch for micromanagement. If they are re-doing someone else's work, stop them. 'If it is 80% right, it is right enough. Move on.'"
        },
        "Program Supervisor": {
            "shift": "From 'Black & White' to 'Gray'.",
            "why": "Trackers want a rule for everything. Leadership involves judgment calls where no rule exists.",
            "conversation": "You excel when the rules are clear. Program leadership is full of gray areas where the policy manual doesn't have an answer. You need to develop your intuition and judgment to navigate complex family or youth dynamics that don't fit the spreadsheet.",
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

# ... (The rest of the file: PDF Content, Helper Functions, and UI Logic remains the same) ...
# Note: I am omitting the repeated PDF/UI code here for brevity as it relies on the dictionaries above.
# The full file content would include lines 253-597 from the previous version unchanged.

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
    gray = (100, 100, 100)
    
    # HEADER
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(*blue)
    pdf.cell(0, 10, "Elmcrest Supervisory Guide", ln=True, align='C')
    
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(*black)
    pdf.cell(0, 8, clean_text(f"For: {name} ({role})"), ln=True, align='C')
    pdf.cell(0, 8, clean_text(f"Profile: {p_comm} x {p_mot}"), ln=True, align='C')
    pdf.ln(5)
    
    # Retrieve Data
    # (Note: Using the same dictionaries as before, ensuring robust fallbacks)
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

    # 1. Communication Profile
    add_heading(f"1. Communication Profile: {p_comm}")
    add_body(c_data['overview'])

    # 2. Supervising Their Communication
    add_heading("2. Supervising Their Communication")
    add_body(c_data['supervising'])

    # 3. Motivation Profile
    add_heading(f"3. Motivation Profile: {p_mot}")
    add_body(m_data['overview'])

    # 4. Motivating This Program Supervisor
    add_heading("4. Motivating This Staff Member")
    add_body(m_data['motivating'])

    # 5. Integrated Leadership Profile
    integrated_text = (
        f"This staff member leads with {p_comm} energy (focused on {c_data['overview'].split('leads with')[0] if 'leads with' in c_data['overview'] else 'their style'}) "
        f"and is fueled by a drive for {p_mot}. "
        f"They are at their best when they can communicate via {p_comm} channels to achieve {p_mot}-aligned outcomes."
    )
    add_heading("5. Integrated Leadership Profile")
    add_body(integrated_text)

    # 6. How You Can Best Support Them
    add_heading("6. How You Can Best Support Them")
    add_body(m_data['support'])

    # 7. What They Look Like When Thriving
    add_heading("7. What They Look Like When Thriving")
    add_bullets(m_data['thriving_bullets'])

    # 8. What They Look Like When Struggling
    add_heading("8. What They Look Like When Struggling")
    add_bullets(c_data['struggle_bullets'])

    # 9. Supervisory Interventions
    add_heading("9. Supervisory Interventions")
    intervention_text = (
        f"• Increase structure or flexibility depending on their {p_comm} style.\n"
        f"• Re-establish expectations or reclarify priorities to satisfy their {p_mot} drive.\n"
        f"• {m_data['intervention']}\n"
        f"• Provide emotional support without enabling overextension."
    )
    add_body(intervention_text)

    # 10. What You Should Celebrate
    add_heading("10. What You Should Celebrate")
    celebrate_intro = (
        f"• Their unique {p_comm} leadership strengths\n"
        f"• Their contributions to climate, safety, or structure\n"
        f"• {m_data['celebrate']}"
    )
    add_body(celebrate_intro)

    # 11. Coaching Questions
    add_heading("11. Coaching Questions")
    add_bullets(c_data['coaching'])

    # 12. Helping Them Prepare for Advancement
    add_heading("12. Helping Them Prepare for Advancement")
    add_body(c_data['advancement'])

    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP LOGIC ---

staff_list = fetch_staff_data()
df = pd.DataFrame(staff_list)

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
            def reset_t1(): st.session_state.t1_staff_select = None
            staff_options = {f"{s['name']} ({s['role']})": s for s in staff_list}
            selected_staff_name = st.selectbox(
                "Select Staff Member", options=list(staff_options.keys()), 
                index=None, key="t1_staff_select", placeholder="Choose a staff member..."
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
    st.write("Select yourself (Supervisor) and a staff member to resolve friction.")
    
    def reset_t3():
        st.session_state.p1 = None
        st.session_state.p2 = None

    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.selectbox("Select Yourself (Supervisor)", df['name'].unique(), index=None, key="p1", placeholder="Select first person...")
        with c2:
            p2_name = st.selectbox("Select Staff Member", df['name'].unique(), index=None, key="p2", placeholder="Select second person...")
            
        if p1_name and p2_name and p1_name != p2_name:
            p1 = df[df['name'] == p1_name].iloc[0]
            p2 = df[df['name'] == p2_name].iloc[0]
            
            # Here p1 is Supervisor, p2 is Staff
            sup_style = p1['p_comm']
            staff_style = p2['p_comm']
            
            st.divider()
            st.subheader(f"Dynamic: {sup_style} (You) vs. {staff_style} (Staff)")
            
            if sup_style == staff_style:
                st.warning("⚠️ **Same-Style Blindspot:** You both communicate the same way. This often means you amplify each other's weaknesses (e.g., two Directors moving too fast, or two Facilitators waiting too long).")
                st.info("💡 **Tip:** Consciously adopt the opposite style to create balance.")
            
            elif sup_style in SUPERVISOR_CLASH_MATRIX and staff_style in SUPERVISOR_CLASH_MATRIX[sup_style]:
                data = SUPERVISOR_CLASH_MATRIX[sup_style][staff_style]
                
                # Dynamic Section
                with st.expander("🔥 The Dynamic (Read First)", expanded=True):
                    st.markdown(f"**{data['dynamic_text']}**")
                    for b in data['dynamic_bullets']:
                        st.markdown(f"- {b}")

                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("#### 🛑 Self-Check")
                    st.write(data['self_check_text'])
                    for b in data['self_check_bullets']:
                        st.error(f"• {b}")
                with c_b:
                    st.markdown("#### 🗣️ The 1:1 Script")
                    st.write(data['script_text'])
                    for s in data['script_options']:
                        st.success(f"\"{s}\"")
            
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
                        st.warning(f"👀 **Supervisor Watch Item:**\n\n{path_data['supervisor_focus']}")
                        
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
    else:
        st.warning("No data available.")
