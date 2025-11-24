import streamlit as st
import random
import requests
import time

# --- Configuration & Styling ---
st.set_page_config(page_title="Elmcrest Compass", page_icon="🧭", layout="centered")

# Custom CSS with Polished UI & Automatic Dark/Light Mode
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* CSS Variables for Theming */
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
        }

        /* Main App Background */
        .stApp {
            background-image: var(--bg-gradient-light);
            background-attachment: fixed;
        }
        @media (prefers-color-scheme: dark) {
            .stApp { background-image: var(--bg-gradient-dark); }
        }

        /* Typography */
        h1, h2, h3 {
            color: var(--primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        p, label, li, .stMarkdown {
            color: var(--text-main) !important;
            line-height: 1.6;
        }
        .small-text {
            color: var(--text-sub) !important;
            font-size: 0.85rem;
        }

        /* Card / Block Container */
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

        /* Buttons - Modern Gradient */
        .stButton button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(1, 91, 173, 0.2);
            width: 100%;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(1, 91, 173, 0.3);
            opacity: 0.95;
        }
        .stButton button:active {
            transform: translateY(0);
        }

        /* Inputs & Selects */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: var(--input-bg) !important;
            color: var(--text-main) !important;
            border-radius: 12px;
            border: 1px solid var(--card-border) !important;
            padding: 0.5rem 1rem;
        }

        /* Radio Buttons - Clean up spacing */
        .stRadio {
            background-color: transparent;
            padding: 10px 0;
        }
        
        /* Custom Score Bar Styling */
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

        /* Info Cards in Results */
        .info-card {
            background-color: var(--input-bg);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid var(--card-border);
        }
        
        /* Divider */
        hr {
            margin: 2rem 0;
            border: 0;
            border-top: 1px solid var(--card-border);
            opacity: 0.5;
        }

        /* Radio selection color */
        div[role="radiogroup"] > label > div:first-of-type {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Constants & Data ---

ROLE_RELATIONSHIP_LABELS = {
    "Program Supervisor": {
        "directReportsLabel": "Shift Supervisors",
        "youthLabel": "youth on your units",
        "supervisorLabel": "Residential Programs Manager",
        "leadershipLabel": "agency leadership and cross-program partners",
    },
    "Shift Supervisor": {
        "directReportsLabel": "Youth Development Professionals (YDPs)",
        "youthLabel": "youth you support each shift",
        "supervisorLabel": "Program Supervisor",
        "leadershipLabel": "Residential Programs Manager and agency leadership",
    },
    "YDP": {
        "directReportsLabel": "peers you work alongside",
        "youthLabel": "youth in your care",
        "supervisorLabel": "Shift Supervisor",
        "leadershipLabel": "Program Supervisor and agency leaders",
    },
}

COMMUNICATION_QUESTIONS = [
    {"id": "comm1", "text": "When a situation becomes chaotic on the unit, I naturally step in and start directing people toward a plan.", "style": "Director"},
    {"id": "comm2", "text": "I feel most effective when I can make quick decisions and move the team forward, even if not everyone agrees yet.", "style": "Director"},
    {"id": "comm3", "text": "In a crisis, I’d rather take charge and apologize later than wait too long for consensus.", "style": "Director"},
    {"id": "comm4", "text": "If expectations are unclear, I tend to define them myself and communicate them to others.", "style": "Director"},
    {"id": "comm5", "text": "I’m comfortable giving direct feedback, even when I know it may be hard for someone to hear.", "style": "Director"},
    {"id": "comm6", "text": "I pay close attention to the emotional tone of the team and try to lift people up when morale is low.", "style": "Encourager"},
    {"id": "comm7", "text": "I often use encouragement, humor, or positive energy to help youth and staff get through hard shifts.", "style": "Encourager"},
    {"id": "comm8", "text": "I notice small wins and like to name them out loud so people know they’re seen.", "style": "Encourager"},
    {"id": "comm9", "text": "I tend to talk things through with people rather than just giving short instructions.", "style": "Encourager"},
    {"id": "comm10", "text": "I’m often the one coworkers come to when they need to vent or feel understood.", "style": "Encourager"},
    {"id": "comm11", "text": "I’m good at slowing conversations down so that different perspectives can be heard before we decide.", "style": "Facilitator"},
    {"id": "comm12", "text": "I try to stay calm and balanced when others are escalated or upset.", "style": "Facilitator"},
    {"id": "comm13", "text": "I often find myself summarizing what others are saying so the team can move toward shared understanding.", "style": "Facilitator"},
    {"id": "comm14", "text": "I prefer to build agreement and buy-in rather than rely only on authority or position.", "style": "Facilitator"},
    {"id": "comm15", "text": "I pay attention to process (how we talk to each other) as much as the final decision.", "style": "Facilitator"},
    {"id": "comm16", "text": "I naturally notice details in documentation, routines, or schedules that other people may overlook.", "style": "Tracker"},
    {"id": "comm17", "text": "I feel responsible for keeping procedures and routines on track, even when others get distracted.", "style": "Tracker"},
    {"id": "comm18", "text": "I tend to ask clarifying questions when expectations or instructions feel vague.", "style": "Tracker"},
    {"id": "comm19", "text": "I’m more comfortable when I know exactly who is doing what and when it needs to be done.", "style": "Tracker"},
    {"id": "comm20", "text": "If something seems out of compliance or off-routine, it really sticks with me until it’s addressed.", "style": "Tracker"},
]

MOTIVATION_QUESTIONS = [
    {"id": "mot1", "text": "I feel energized when I’m learning new skills or being stretched in healthy ways.", "style": "Growth"},
    {"id": "mot2", "text": "It’s important to me that I can look back and see I’m becoming more effective in my work over time.", "style": "Growth"},
    {"id": "mot3", "text": "When I feel stuck in the same patterns with no development, my motivation drops.", "style": "Growth"},
    {"id": "mot4", "text": "I appreciate feedback that helps me improve, even if it’s uncomfortable in the moment.", "style": "Growth"},
    {"id": "mot5", "text": "Access to training, coaching, or new responsibilities matters a lot for my long-term commitment.", "style": "Growth"},
    {"id": "mot6", "text": "I need to feel that what I’m doing connects to a bigger purpose, especially for youth and families.", "style": "Purpose"},
    {"id": "mot7", "text": "I feel strongest when my work lines up with my values about dignity, justice, and safety.", "style": "Purpose"},
    {"id": "mot8", "text": "It’s hard for me to stay engaged when policies or practices don’t make sense for the youth we serve.", "style": "Purpose"},
    {"id": "mot9", "text": "I’m often the one raising questions about whether a decision is really best for kids or staff.", "style": "Purpose"},
    {"id": "mot10", "text": "I feel proudest of my work when I can see real positive impact, not just tasks checked off.", "style": "Purpose"},
    {"id": "mot11", "text": "Having strong relationships with coworkers makes a big difference in how much energy I bring to work.", "style": "Connection"},
    {"id": "mot12", "text": "When the team feels disconnected, I feel it in my body and it’s harder to stay motivated.", "style": "Connection"},
    {"id": "mot13", "text": "I value feeling known and supported by my team and supervisor, not just evaluated.", "style": "Connection"},
    {"id": "mot14", "text": "I’m often thinking about the emotional climate of the unit and how people are relating to each other.", "style": "Connection"},
    {"id": "mot15", "text": "I’m more likely to go above and beyond when I feel a sense of belonging with my team.", "style": "Connection"},
    {"id": "mot16", "text": "I like having clear goals and being able to see, in concrete ways, when we’ve met them.", "style": "Achievement"},
    {"id": "mot17", "text": "I feel satisfied when I can see that my effort led to specific improvements for the unit or youth.", "style": "Achievement"},
    {"id": "mot18", "text": "It’s frustrating when expectations keep shifting and I’m not sure what success looks like.", "style": "Achievement"},
    {"id": "mot19", "text": "I appreciate data, tracking tools, or simple dashboards that help show progress.", "style": "Achievement"},
    {"id": "mot20", "text": "I’m motivated by being trusted with projects where outcomes are clearly defined.", "style": "Achievement"},
]

COMM_PROFILES = {
    "Director": {
        "name": "Director Communicator",
        "tagline": "The Decisive Driver",
        "overview": "You move quickly toward action. In high-pressure moments, you’re often the one who steps in, organizes people, and pushes the team toward a clear decision. Your directness can bring structure and safety when things feel chaotic.",
        "conflictImpact": "Under stress, you may become more blunt, controlling, or impatient. Others may feel talked over or rushed, even when your goal is safety. When you slow your pace just enough to check in, your leadership becomes easier for people to trust and follow.",
        "traumaStrategy": "Your clear, firm presence can feel regulating for youth and staff when paired with calm tone and predictable follow-through. Short, concrete statements such as “Here’s the plan for the next 10 minutes…” help everyone re-orient after a tough moment.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "With Shift Supervisors, pause before final decisions and ask: “What are we not seeing from the floor?” This invites real input instead of just compliance.",
                "youth": "With youth, pair structure with choice. Offer two safe options instead of only one directive, so they keep some sense of control.",
                "supervisor": "With your Residential Programs Manager, frame your strong ideas as joint problem-solving: “Here’s what I’d recommend, and here’s where I’d love your perspective.”",
                "leadership": "With agency leadership, name both opportunities and risks: “We can move quickly on this, and here’s what support we’d need to keep staff and youth safe.”",
            },
            "Shift Supervisor": {
                "directReports": "With YDPs, emphasize that you’re directing the plan, not judging the person. Ask for quick input before locking in decisions when safety allows.",
                "youth": "In crisis with youth, keep commands simple and tone steady. Circle back later for repair and explanation when everyone is regulated.",
                "supervisor": "With your Program Supervisor, be upfront about capacity: “We can implement this, but here’s the trade-off on this shift.”",
                "leadership": "With leadership, highlight what frontline staff are seeing so decisions are grounded in reality, not just policy.",
            },
            "YDP": {
                "directReports": "With peers, use your leadership to organize tasks, not to override. Ask, “Who can own what?” instead of assigning everything yourself.",
                "youth": "With youth, set clear limits and then stay present. “I’m not going to let you hurt yourself or anyone else. Here’s how I can help right now.”",
                "supervisor": "With your Shift Supervisor, bring concise summaries of what’s happening and at least one proposed solution.",
                "leadership": "When in spaces with higher-level leaders, speak plainly about what’s working and what’s not, while staying curious rather than confrontational.",
            },
        },
    },
    "Encourager": {
        "name": "Encourager Communicator",
        "tagline": "The Relational Energizer",
        "overview": "You bring warmth, optimism, and emotional presence. You notice when people need encouragement and often become the person youth and coworkers seek out when they’re struggling.",
        "conflictImpact": "Under stress, you may talk more, avoid hard truths, or personalize feedback. You might try to smooth things over quickly to keep relationships intact, even when deeper repair is needed.",
        "traumaStrategy": "Your ability to notice and name small wins is powerful for youth with trauma histories. Combine empathy with clear, consistent boundaries so that care doesn’t slide into inconsistency.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "With Shift Supervisors, balance encouragement with accountability: “I believe in you, and this part still needs to happen consistently.”",
                "youth": "With youth, validate feelings first (“That was a really hard moment”) and then gently move into expectations.",
                "supervisor": "With your Residential Programs Manager, share both the emotional climate and the operational realities so they see the full picture.",
                "leadership": "With agency leadership, highlight stories that show the human impact of decisions, not just the numbers.",
            },
            "Shift Supervisor": {
                "directReports": "With YDPs, be the safe person who also holds the line. Appreciate effort and still be clear about non-negotiables.",
                "youth": "Use your connection to help youth feel seen. After escalations, ask: “What did you need that you didn’t get in that moment?”",
                "supervisor": "With your Program Supervisor, share where staff are struggling emotionally and what would help sustain them.",
                "leadership": "Name how culture, recognition, and communication from leadership influence day-to-day motivation on the unit.",
            },
            "YDP": {
                "directReports": "With peers, offer encouragement that is specific (“I saw how patient you were then”), not just general praise.",
                "youth": "With youth, your warmth is a resource. Combine it with clear statements about safety and boundaries.",
                "supervisor": "With your Shift Supervisor, be honest about when you’re feeling overwhelmed so they can support you early, not when you’re burnt out.",
                "leadership": "When you have the chance, share short, concrete stories that show how relational care changes outcomes for youth.",
            },
        },
    },
    "Facilitator": {
        "name": "Facilitator Communicator",
        "tagline": "The Calm Bridge",
        "overview": "You listen deeply, notice different perspectives, and help people stay at the table when things are tense. You care about process and fairness, not just the final decision.",
        "conflictImpact": "Under stress, you may delay decisions or quietly absorb tension to keep the peace. You might say “it’s fine” when it isn’t, which can leave issues unresolved.",
        "traumaStrategy": "Your steady presence and ability to slow things down are powerful in a trauma-heavy environment. Naming what you see (“There’s a lot of tension in the room right now…”) can help others regulate and refocus.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "With Shift Supervisors, invite their perspectives and then close with a clear decision: “I hear you both. Here’s the plan we’re going to try.”",
                "youth": "With youth, reflect their feelings back in simple language before problem-solving. This often lowers intensity.",
                "supervisor": "With your Residential Programs Manager, summarize themes you’re hearing from different units, not just isolated incidents.",
                "leadership": "With agency leadership, translate frontline realities into patterns and proposals: “Here’s what I’m seeing across programs and one option we could pilot.”",
            },
            "Shift Supervisor": {
                "directReports": "With YDPs, create space for input and then name next steps so people aren’t left in limbo.",
                "youth": "In conflict with youth, your calm tone is a resource. Use brief, validating statements and short choices to avoid overload.",
                "supervisor": "With your Program Supervisor, be honest about where you’re holding tension silently so they can support you in addressing it.",
                "leadership": "Name how your team is functioning relationally, not just whether tasks are complete.",
            },
            "YDP": {
                "directReports": "With peers, you can de-escalate team dynamics by summarizing what each person is trying to say and finding shared ground.",
                "youth": "With youth, your calm questions (“What happened from your perspective?”) can open up conversations others can’t reach.",
                "supervisor": "With your Shift Supervisor, bring them your read on the unit’s emotional climate, not just incidents.",
                "leadership": "When you’re in mixed-level meetings, your thoughtful questions can help the group arrive at more workable plans.",
            },
        },
    },
    "Tracker": {
        "name": "Tracker Communicator",
        "tagline": "The Structured Guardian",
        "overview": "You notice patterns, details, and gaps in systems. You help keep routines, documentation, and safety steps on track, which protects youth and staff from unnecessary risk.",
        "conflictImpact": "Under stress, you may become more rigid or critical. You might focus so strongly on rules that others experience you as inflexible or harsh, even when your concern is safety.",
        "traumaStrategy": "Your consistency and attention to detail make the environment more predictable—something youth with trauma histories often need. When paired with warm tone and choice, your structure becomes a powerful form of care.",
        "roleTips": {
            "Program Supervisor": {
                "directReports": "With Shift Supervisors, share the “why” behind procedures and invite their ideas about how to make compliance more realistic.",
                "youth": "With youth, avoid leading with “because that’s the rule.” Instead, link routines to safety and trust: “We do it this way so everyone knows what to expect.”",
                "supervisor": "With your Residential Programs Manager, bring prioritized lists: what must be fixed now, what can wait, and what’s just a concern to watch.",
                "leadership": "With agency leadership, translate compliance risks into practical steps the organization can take to support staff more effectively.",
            },
            "Shift Supervisor": {
                "directReports": "With YDPs, turn corrections into coaching: “Here’s what the policy says, and here’s how I can help you make it manageable.”",
                "youth": "With youth, present structure as something you’re doing with them, not to them. Use visuals, routines, and simple language.",
                "supervisor": "With your Program Supervisor, share where systems are breaking down and what support would help.",
                "leadership": "When asked, share concrete examples of how better tools or clearer procedures would reduce errors and stress.",
            },
            "YDP": {
                "directReports": "With peers, share reminders in a way that sounds like partnership: “Can I help you remember this step?”",
                "youth": "With youth, predictable routines (same order, same words) can help them feel safer, especially during transitions.",
                "supervisor": "With your Shift Supervisor, bring specific examples instead of general complaints. Offer at least one possible solution.",
                "leadership": "If you’re ever invited into bigger conversations, your eye for detail can help teams design systems that actually work on the floor.",
            },
        },
    },
}

MOTIVATION_PROFILES = {
    "Growth": {
        "name": "Growth Motivation",
        "tagline": "The Learner/Builder",
        "summary": "You’re energized when you can see yourself developing. Stretch assignments, feedback, and new skills matter to you. Stagnation is draining.",
        "boosters": ["Clear opportunities to learn new skills tied to real work on the unit.", "Supportive coaching that notices progress, not just mistakes.", "Chances to step into new responsibilities with backup from your supervisor."],
        "killers": ["Feeling stuck in the same patterns with no development.", "Being asked to do more without any investment in your growth.", "Learning that feels disconnected from youth or Elmcrest’s mission."],
        "roleSupport": {
            "Program Supervisor": "Name learning goals with each Shift Supervisor and connect them to youth outcomes and career paths at Elmcrest.",
            "Shift Supervisor": "Check in with YDPs about what they want to get better at and look for chances on shift to practice together.",
            "YDP": "Ask for small, realistic growth goals (one skill at a time) and let your supervisor know when you’re ready for more.",
        },
    },
    "Purpose": {
        "name": "Purpose Motivation",
        "tagline": "The Mission Keeper",
        "summary": "You’re driven by meaning and alignment. You want your daily work to match your values about safety, dignity, and justice for youth and staff.",
        "boosters": ["Clear connections between decisions and what’s best for youth and families.", "Spaces where it’s safe to raise ethical concerns without being dismissed.", "Chances to help shape practices to make them more trauma-informed and equitable."],
        "killers": ["Feeling that the system is asking you to act against your values.", "Policies that don’t make sense for the youth you serve.", "Being told “that’s just how it is” when you raise real concerns."],
        "roleSupport": {
            "Program Supervisor": "Share where policies feel misaligned with the mission and collaborate with your manager on realistic adjustments.",
            "Shift Supervisor": "Help YDPs understand how unit routines protect dignity and safety, not just compliance.",
            "YDP": "Name your values to your supervisor so they know what matters most to you in hard calls.",
        },
    },
    "Connection": {
        "name": "Connection Motivation",
        "tagline": "The Community Builder",
        "summary": "You’re most energized when relationships are strong and the team feels like a real community. Belonging fuels your resilience.",
        "boosters": ["Regular relational check-ins, not just task updates.", "Moments where team effort and mutual support are noticed and appreciated.", "Stable assignments that allow trust to build over time."],
        "killers": ["Persistent conflict or tension that never gets addressed.", "Isolation, working long stretches without feeling part of a team.", "Only hearing from others when something is wrong."],
        "roleSupport": {
            "Program Supervisor": "Intentionally build connection among Shift Supervisors through huddles, shared problem-solving, and peer support.",
            "Shift Supervisor": "Create small rituals on shift (check-ins, appreciations) that help YDPs feel less alone in hard work.",
            "YDP": "Let your supervisor know when you’re feeling isolated so they can help you reconnect with the team.",
        },
    },
    "Achievement": {
        "name": "Achievement Motivation",
        "tagline": "The Results Architect",
        "summary": "You care about clear goals and concrete progress. You want to know what success looks like and see evidence that you’re getting there.",
        "boosters": ["Specific, realistic goals tied to youth outcomes or team functioning.", "Simple ways to track progress (checklists, brief run-downs, quick metrics).", "Recognition that names concrete contributions, not just general praise."],
        "killers": ["Constantly shifting expectations with no clear targets.", "Doing a lot of work that never gets acknowledged.", "Only hearing about what went wrong, never what improved."],
        "roleSupport": {
            "Program Supervisor": "Co-design a small set of meaningful metrics with your manager (e.g., transitions, incident trends) and review them in supervision.",
            "Shift Supervisor": "Set unit-level goals with YDPs (e.g., smoother transitions, consistent routines) and celebrate progress together.",
            "YDP": "Ask your supervisor to help you define what “a good shift” looks like in concrete terms, then check in about it regularly.",
        },
    },
}

INTEGRATED_PROFILES = {
    "Director-Growth": {"title": "Director + Growth – The Driven Developer", "summary": "You lean into leadership and action, and you want to keep getting better at it. You’re often the one pushing for both clear direction and higher skill.", "strengths": ["Stepping up quickly when there’s a gap in leadership.", "Driving improvement efforts and being willing to try new approaches.", "Using feedback as fuel when it’s offered constructively."], "watchouts": ["Moving so fast that others don’t feel heard or ready to change.", "Turning frustration inward as harsh self-criticism when things go wrong."]},
    "Director-Purpose": {"title": "Director + Purpose – The Ethical Guardian", "summary": "You make firm decisions through a values lens. You care not just that things get done, but that they’re done in a way that feels right for youth and staff.", "strengths": ["Advocating when you believe something is unsafe or unfair.", "Holding strong boundaries that protect dignity and safety.", "Staying steady in crises because you know what you stand for."], "watchouts": ["Feeling intense frustration when systems don’t match your values.", "Coming across as inflexible or critical when you’re protecting what matters most."]},
    "Director-Connection": {"title": "Director + Connection – The Relational Driver", "summary": "You lead with energy and care about how the team is doing together. You want people to feel both guided and included.", "strengths": ["Bringing people together quickly around a plan.", "Using your influence to support relational repair on the team.", "Being both directive and emotionally present in hard moments."], "watchouts": ["Accidentally shutting down dissent because your enthusiasm is so strong.", "Carrying the emotional load for everyone and burning out quietly."]},
    "Director-Achievement": {"title": "Director + Achievement – The Results Leader", "summary": "You want clear goals and you’re willing to lead the way to reach them. You often think in terms of outcomes and progress for the unit.", "strengths": ["Turning big goals into concrete plans and timelines.", "Owning responsibility for follow-through and results.", "Helping others see what success can look like in practical terms."], "watchouts": ["Focusing so much on outcomes that people feel like numbers.", "Getting discouraged when external factors block your progress."]},
    "Encourager-Growth": {"title": "Encourager + Growth – The Supportive Builder", "summary": "You grow through relationships. You want to keep improving while helping others feel seen and supported along the way.", "strengths": ["Coaching others through change with encouragement and empathy.", "Turning feedback into relational learning rather than shame.", "Helping youth and staff notice their own growth over time."], "watchouts": ["Avoiding necessary conflict because you don’t want anyone to feel hurt.", "Overextending yourself emotionally in the name of helping."]},
    "Encourager-Purpose": {"title": "Encourager + Purpose – The Heart-Centered Advocate", "summary": "You care deeply about people and the mission. You want the way we treat youth and staff to reflect what we say we believe.", "strengths": ["Naming when something doesn’t feel right emotionally or ethically.", "Creating spaces where people feel safe enough to be honest.", "Connecting the “why” behind policies to human impact."], "watchouts": ["Taking misalignment personally and feeling hopeless or cynical.", "Feeling responsible for everyone’s emotions on the unit."]},
    "Encourager-Connection": {"title": "Encourager + Connection – The Community Energizer", "summary": "You thrive when the team feels like a real community. You are often a key source of warmth and hope when things are hard.", "strengths": ["Building bridges between staff who might otherwise drift apart.", "Helping youth feel emotionally safe enough to try again after setbacks.", "Keeping morale from collapsing during tough stretches."], "watchouts": ["Using positivity to cover pain that actually needs to be named.", "Feeling deeply discouraged when team conflict goes unresolved."]},
    "Encourager-Achievement": {"title": "Encourager + Achievement – The Celebrating Achiever", "summary": "You’re motivated by progress and love to celebrate it with others. Shared wins matter more to you than solo credit.", "strengths": ["Recognizing and naming concrete improvements others might miss.", "Motivating the team through positive reinforcement and visible progress.", "Aligning emotional support with clear goals."], "watchouts": ["Feeling like you’ve failed when outcomes don’t match your effort.", "Struggling when success is harder to see or takes longer to emerge."]},
    "Facilitator-Growth": {"title": "Facilitator + Growth – The Reflective Improver", "summary": "You grow by paying attention to patterns in people and processes. You’re curious about what could work better for everyone.", "strengths": ["Spotting small process changes that reduce stress and conflict.", "Supporting others to learn from incidents without shame.", "Holding space for reflection after hard moments."], "watchouts": ["Over-processing to the point that decisions or changes stall.", "Taking on quiet responsibility for fixing everything yourself."]},
    "Facilitator-Purpose": {"title": "Facilitator + Purpose – The Values-Centered Bridge", "summary": "You want conversations and decisions to reflect the mission. You tend to look for ways to align people around what matters most.", "strengths": ["Helping people with different perspectives find shared ground.", "Naming values (safety, dignity, fairness) in concrete ways.", "Translating between frontline realities and system expectations."], "watchouts": ["Carrying the emotional and ethical weight of the team by yourself.", "Staying neutral so long that your own values never get voiced."]},
    "Facilitator-Connection": {"title": "Facilitator + Connection – The Relational Stabilizer", "summary": "You care how people are relating and want the team to function as a healthy system, not just a group of individuals.", "strengths": ["Calming tense conversations and helping people hear each other.", "Keeping youth, staff, and supervisors connected in realistic ways.", "Quietly preventing conflicts from becoming ruptures."], "watchouts": ["Avoiding direct conversations when something truly needs to change.", "Feeling responsible for peace even when systems are the real issue."]},
    "Facilitator-Achievement": {"title": "Facilitator + Achievement – The Process Architect", "summary": "You’re interested in how to reach goals in a way that feels fair and sustainable. You think in terms of both outcomes and process.", "strengths": ["Designing routines that help the team succeed without burning out.", "Helping others understand the “why” behind expectations.", "Balancing the need for results with respect for people’s limits."], "watchouts": ["Over-complicating processes in an effort to make them perfect.", "Feeling stuck when you can see the goal but lack authority to change systems."]},
    "Tracker-Growth": {"title": "Tracker + Growth – The Systems Builder", "summary": "You’re interested in getting better at building and maintaining systems that work. You notice where the structure supports growth and where it blocks it.", "strengths": ["Improving documentation and routines over time instead of just maintaining them.", "Helping others learn the steps that keep youth and staff safer.", "Turning feedback about errors into better systems, not just blame."], "watchouts": ["Being too hard on yourself when mistakes happen under pressure.", "Pushing for improvement faster than others are ready to move."]},
    "Tracker-Purpose": {"title": "Tracker + Purpose – The Mission-Aligned Organizer", "summary": "You link structure to values. For you, routines and documentation aren’t just tasks—they’re part of protecting what matters most.", "strengths": ["Connecting policies and procedures to safety and dignity for youth.", "Raising concerns when systems drift away from mission.", "Holding high standards because you know who is impacted when we cut corners."], "watchouts": ["Feeling morally distressed when others don’t share your sense of responsibility.", "Coming across as overly rigid when you’re actually trying to protect people."]},
    "Tracker-Connection": {"title": "Tracker + Connection – The Relational Organizer", "summary": "You want systems that support relationships, not replace them. You pay attention to both structure and how people feel inside it.", "strengths": ["Designing or protecting routines that make the environment more predictable and relational.", "Noticing when relational strain shows up in documentation or tasks being missed.", "Bringing calm, organized energy when others feel scattered."], "watchouts": ["Feeling alone in caring about both structure and relationships.", "Becoming critical when others don’t follow through on agreed routines."]},
    "Tracker-Achievement": {"title": "Tracker + Achievement – The Precision Builder", "summary": "You want systems to work and you want to see evidence that they’re working. You’re motivated by clear expectations and reliable follow-through.", "strengths": ["Keeping important details from falling through the cracks.", "Turning big goals into repeatable steps and checklists.", "Catching early warning signs when things begin to slip."], "watchouts": ["Becoming perfectionistic about details that don’t actually change outcomes.", "Feeling personally responsible when system-level issues impact results."]},
}

# --- Helper Functions ---

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

def submit_to_google_sheets(data):
    url = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return True
        else:
            st.warning(f"Data saved, but server returned status: {response.status_code}")
            return True
    except Exception as e:
        st.error(f"Error submitting to Google Sheets: {e}")
        return False

# --- Logic & State Management ---

if 'step' not in st.session_state:
    st.session_state.step = 'intro'
    comm_q = COMMUNICATION_QUESTIONS.copy()
    motiv_q = MOTIVATION_QUESTIONS.copy()
    random.shuffle(comm_q)
    random.shuffle(motiv_q)
    st.session_state.shuffled_comm = comm_q
    st.session_state.shuffled_motiv = motiv_q
    st.session_state.answers_comm = {}
    st.session_state.answers_motiv = {}
    st.session_state.user_info = {}

# --- Helper Views ---

def show_brand_header(subtitle):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.markdown("""
        <div style="
            width: 55px; height: 55px; 
            background: linear-gradient(135deg, #015bad, #51c3c5); 
            border-radius: 12px; 
            color: white; 
            display: flex; align-items: center; justify-content: center; 
            font-weight: 800; font-size: 1.2rem;
            box-shadow: 0 4px 12px rgba(1, 91, 173, 0.25);">
            EC
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; justify-content: center; height: 55px;">
            <div style="color: #015bad; font-weight: 800; font-size: 1.5rem; line-height: 1.2;">ELMCREST COMPASS</div>
            <div style="color: #64748b; font-size: 0.95rem; font-weight: 500;">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

def draw_score_bar(label, value, max_value=25):
    """Draws a custom HTML progress bar for scores"""
    percentage = (value / max_value) * 100
    st.markdown(f"""
    <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.9rem; font-weight: 600;">
            <span>{label}</span>
            <span>{value}</span>
        </div>
        <div class="score-container">
            <div class="score-fill" style="width: {percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Main App ---

if st.session_state.step == 'intro':
    show_brand_header("Communication & Motivation Snapshot")
    
    st.markdown("### Welcome to your Compass")
    st.info("This assessment helps you understand your natural communication and motivation patterns at work. Your insights will shape a personalized profile built to support your growth.")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("intro_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
        with col2:
            email = st.text_input("Email Address", placeholder="e.g. jane@elmcrest.org")
            
        role = st.selectbox("Current Role", ["Program Supervisor", "Shift Supervisor", "YDP"], help="Tailors results to your specific leadership level.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Start Assessment →")
        if submitted:
            if not name or not email:
                st.error("Please complete your name and email.")
            else:
                st.session_state.user_info = {"name": name, "email": email, "role": role}
                st.session_state.step = 'comm'
                st.rerun()

elif st.session_state.step == 'comm':
    show_brand_header("Part 1: Communication")
    st.progress(33)
    st.markdown("**Instructions:** Choose how strongly each statement fits you most days at Elmcrest.")
    
    with st.form("comm_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_comm):
            st.markdown(f"<div style='margin-top: 20px; font-weight: 500;'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
            val = st.radio(
                f"q_{i}", 
                options=[1, 2, 3, 4, 5], 
                horizontal=True, 
                key=f"c_{q['id']}",
                label_visibility="collapsed"
            )
            st.markdown("""
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-sub); margin-top:-5px; padding-bottom:10px; border-bottom:1px dashed var(--card-border);">
                <span>Strongly Disagree</span><span>Strongly Agree</span>
            </div>
            """, unsafe_allow_html=True)
            answers[q['id']] = val
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Continue to Motivation →")
        if submitted:
            st.session_state.answers_comm = answers
            st.session_state.step = 'motiv'
            st.rerun()

elif st.session_state.step == 'motiv':
    show_brand_header("Part 2: Motivation")
    st.progress(66)
    st.markdown("**Instructions:** Focus on what keeps you engaged or drains you in the work.")

    with st.form("motiv_form"):
        answers = {}
        for i, q in enumerate(st.session_state.shuffled_motiv):
            st.markdown(f"<div style='margin-top: 20px; font-weight: 500;'>{i+1}. {q['text']}</div>", unsafe_allow_html=True)
            val = st.radio(
                f"q_m_{i}", 
                options=[1, 2, 3, 4, 5], 
                horizontal=True, 
                key=f"m_{q['id']}",
                label_visibility="collapsed"
            )
            st.markdown("""
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-sub); margin-top:-5px; padding-bottom:10px; border-bottom:1px dashed var(--card-border);">
                <span>Strongly Disagree</span><span>Strongly Agree</span>
            </div>
            """, unsafe_allow_html=True)
            answers[q['id']] = val
            
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Complete & View Profile →")
        if submitted:
            st.session_state.answers_motiv = answers
            st.session_state.step = 'processing'
            st.rerun()

elif st.session_state.step == 'processing':
    # Calculate Scores
    comm_scores = {k: 0 for k in COMM_PROFILES.keys()}
    for q in COMMUNICATION_QUESTIONS:
        val = st.session_state.answers_comm.get(q['id'], 3)
        comm_scores[q['style']] += val

    motiv_scores = {k: 0 for k in MOTIVATION_PROFILES.keys()}
    for q in MOTIVATION_QUESTIONS:
        val = st.session_state.answers_motiv.get(q['id'], 3)
        motiv_scores[q['style']] += val
    
    p_comm, s_comm = get_top_two(comm_scores)
    p_motiv, s_motiv = get_top_two(motiv_scores)
    
    # Store results
    st.session_state.results = {
        "primaryComm": p_comm,
        "secondaryComm": s_comm,
        "primaryMotiv": p_motiv,
        "secondaryMotiv": s_motiv,
        "commScores": comm_scores,
        "motivScores": motiv_scores
    }
    
    # Payload
    payload = {
        "name": st.session_state.user_info['name'],
        "email": st.session_state.user_info['email'],
        "role": st.session_state.user_info['role'],
        "scores": {
            "communication": comm_scores,
            "motivation": motiv_scores,
            "primaryComm": p_comm,
            "secondaryComm": s_comm,
            "primaryMotiv": p_motiv,
            "secondaryMotiv": s_motiv,
        }
    }
    
    with st.spinner("Analyzing results..."):
        submit_to_google_sheets(payload)
        time.sleep(1.5) # Slight artificial delay for UX smoothness
    
    st.session_state.step = 'results'
    st.rerun()

elif st.session_state.step == 'results':
    st.progress(100)
    res = st.session_state.results
    role = st.session_state.user_info['role']
    role_key = normalize_role_key(role)
    role_labels = ROLE_RELATIONSHIP_LABELS[role_key]
    
    show_brand_header(f"Profile for {st.session_state.user_info['name']}")
    
    st.success("Analysis Complete! Your results have been saved to the Elmcrest database.")

    # --- Comm Section ---
    comm_prof = COMM_PROFILES[res['primaryComm']]
    
    st.markdown(f"## 🗣️ Communication Style")
    
    with st.container():
        st.markdown(f"""
        <div class="info-card">
            <h2 style="margin-top:0;">{comm_prof['name']}</h2>
            <div style="color: #015bad; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; font-size: 0.9rem;">{comm_prof['tagline']}</div>
            <p>{comm_prof['overview']}</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        with st.expander("Detailed Role Tips", expanded=True):
            tips = comm_prof['roleTips'][role_key]
            st.markdown(f"**With {role_labels['directReportsLabel']}:**\n{tips['directReports']}")
            st.markdown(f"**With youth:**\n{tips['youth']}")
            st.markdown(f"**With your Supervisor:**\n{tips['supervisor']}")
            st.markdown(f"**With Leadership:**\n{tips['leadership']}")
            
        st.markdown(f"**⚠️ Under Stress:** {comm_prof['conflictImpact']}")
        st.markdown(f"**🛡️ Trauma Strategy:** {comm_prof['traumaStrategy']}")

    with col2:
        st.markdown("### Score Breakdown")
        for style, score in res['commScores'].items():
            draw_score_bar(style, score)

    st.markdown("---")

    # --- Motivation Section ---
    mot_prof = MOTIVATION_PROFILES[res['primaryMotiv']]
    
    st.markdown(f"## 🔋 Motivation Driver")
    
    with st.container():
        st.markdown(f"""
        <div class="info-card">
            <h2 style="margin-top:0;">{mot_prof['name']}</h2>
            <div style="color: #015bad; font-weight: 600; margin-bottom: 10px; text-transform: uppercase; font-size: 0.9rem;">{mot_prof['tagline']}</div>
            <p>{mot_prof['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### ✅ Boosters")
        for b in mot_prof['boosters']:
            st.markdown(f"- {b}")
    with c2:
        st.markdown("### 🔻 Drainers")
        for k in mot_prof['killers']:
            st.markdown(f"- {k}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(f"**Support needed:** {mot_prof['roleSupport'][role_key]}")

    st.markdown("---")

    # --- Integrated Section ---
    int_key = f"{res['primaryComm']}-{res['primaryMotiv']}"
    if int_key in INTEGRATED_PROFILES:
        int_prof = INTEGRATED_PROFILES[int_key]
        st.markdown(f"## 🔗 Integrated Profile: {int_prof['title']}")
        st.write(int_prof['summary'])
        
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("#### Key Strengths")
            for s in int_prof['strengths']:
                st.markdown(f"✅ {s}")
        with ic2:
            st.markdown("#### Watch-outs")
            for w in int_prof['watchouts']:
                st.markdown(f"⚠️ {w}")

    st.markdown("---")
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
