import json
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

DATA_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- Lightweight interpretation dictionaries (edit to match your internal language) ---
COMM_DESC = {
    "Director": {
        "summary": "Direct, decisive, action-oriented.",
        "best_with": [
            "Lead with the point first (what you need, by when).",
            "Offer options, then recommend one.",
            "Keep meetings focused; clarify ownership."
        ],
        "watch_for": ["Can sound blunt under stress.", "May move faster than others are ready for."]
    },
    "Tracker": {
        "summary": "Detail-oriented, process-driven, consistent.",
        "best_with": [
            "Provide steps, expectations, and definitions of “done.”",
            "Use checklists and timelines.",
            "Confirm constraints (policy, compliance, safety)."
        ],
        "watch_for": ["May get stuck in details when urgency is high.", "Can feel frustrated by ambiguity."]
    },
    "Encourager": {
        "summary": "Relational, supportive, morale-building.",
        "best_with": [
            "Start with people impact and appreciation.",
            "Invite input and collaboration.",
            "Address conflict gently but clearly."
        ],
        "watch_for": ["May avoid hard conversations too long.", "Can feel drained by constant negativity."]
    },
    "Facilitator": {
        "summary": "Collaborative, consensus-seeking, thoughtful.",
        "best_with": [
            "Bring them in early to shape plans.",
            "Ask for perspectives and tradeoffs.",
            "Summarize decisions and next steps to avoid drift."
        ],
        "watch_for": ["Can slow decisions if alignment isn’t clear.", "May over-consult when time is tight."]
    },
}

MOT_DESC = {
    "Connection": {
        "summary": "Motivated by belonging, relationships, and being part of a team.",
        "fuel": ["Team cohesion", "1:1 check-ins", "Shared wins", "Feeling seen and supported"],
        "deplete": ["Isolation", "Cold/transactional leadership", "Unresolved interpersonal conflict"]
    },
    "Achievement": {
        "summary": "Motivated by goals, progress, and measurable results.",
        "fuel": ["Clear targets", "Dashboards/metrics", "Fast feedback loops", "Recognition for wins"],
        "deplete": ["Vague priorities", "No closure", "Repeated fire drills without progress"]
    },
    "Purpose": {
        "summary": "Motivated by meaning, mission, and impact.",
        "fuel": ["Connecting tasks to resident outcomes", "Values clarity", "Story-based impact sharing"],
        "deplete": ["Busywork", "Misalignment with mission", "Feeling like quality doesn’t matter"]
    },
    "Growth": {
        "summary": "Motivated by learning, mastery, and development.",
        "fuel": ["Coaching", "New challenges", "Training", "Constructive feedback"],
        "deplete": ["Stagnation", "No pathway to improve", "Only being used for output"]
    },
}

def burnout_label(value: float | None) -> str:
    if value is None:
        return "Not provided"
    if value <= 1.5:
        return "Low"
    if value <= 3.0:
        return "Moderate"
    if value <= 4.0:
        return "High"
    return "Very High"

def burnout_guidance(value: float | None) -> list[str]:
    if value is None:
        return ["Consider adding a burnout rating (1–5) for better insights."]
    if value <= 1.5:
        return ["Keep routines that are working.", "Protect time for recovery to prevent creep."]
    if value <= 3.0:
        return ["Add 1–2 boundary protections this week.", "Clarify top priorities; reduce ‘maybe’ tasks."]
    if value <= 4.0:
        return ["Reduce load or redistribute where possible.", "Increase support (coverage, coaching, check-ins)."]
    return [
        "Treat as urgent: reduce load immediately if possible.",
        "Escalate support needs and coverage plans.",
        "Prioritize rest, safety, and sustainability."
    ]

@st.cache_data(ttl=60)
def fetch_data(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)

    # Normalize columns that might vary
    for col in ["cottage", "burnout"]:
        if col in df.columns:
            df[col] = df[col].replace("", pd.NA)

    # Parse timestamps
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    # Burnout numeric
    if "burnout" in df.columns:
        df["burnout_num"] = pd.to_numeric(df["burnout"], errors="coerce")

    # Clean cottage to string for display but keep a sortable helper
    if "cottage" in df.columns:
        df["cottage_str"] = df["cottage"].astype(str)
    else:
        df["cottage_str"] = "Unknown"

    return df

def latest_profile_per_email(df: pd.DataFrame) -> pd.DataFrame:
    if "email" not in df.columns:
        return df.copy()
    # keep latest timestamp row per email
    d = df.copy()
    if "timestamp" in d.columns:
        d = d.sort_values("timestamp")
    return d.groupby("email", as_index=False).tail(1).reset_index(drop=True)

def render_style_block(title: str, key: str, desc_map: dict):
    st.subheader(title)
    if not key or key not in desc_map:
        st.info("No data available.")
        return
    info = desc_map[key]
    st.markdown(f"**{key}** — {info['summary']}")
    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Works best when you:**")
        for item in info.get("best_with", info.get("fuel", [])):
            st.write(f"- {item}")
    with cols[1]:
        st.markdown("**Watch-outs:**")
        for item in info.get("watch_for", info.get("deplete", [])):
            st.write(f"- {item}")

# -------------------- UI --------------------
st.set_page_config(page_title="Supervisor Profile Dashboard", layout="wide")
st.title("Supervisor Profile Dashboard")

with st.sidebar:
    st.header("Data")
    if st.button("Refresh now"):
        st.cache_data.clear()

    st.caption("Source: Google Apps Script JSON endpoint")
    st.code(DATA_URL, language="text")

df_raw = fetch_data(DATA_URL)

if df_raw.empty:
    st.error("No data returned from the endpoint.")
    st.stop()

df = latest_profile_per_email(df_raw)

# Make a stable selector label
df["selector_label"] = df.apply(
    lambda r: f"{r.get('name','Unknown')}  •  {r.get('email','(no email)')}", axis=1
)

# Sidebar selection
with st.sidebar:
    st.header("Select supervisor")
    # Optional: filter by role first
    roles = sorted([r for r in df["role"].dropna().unique().tolist()]) if "role" in df.columns else []
    role_filter = st.multiselect("Role filter (optional)", roles, default=[])
    dff = df.copy()
    if role_filter:
        dff = dff[dff["role"].isin(role_filter)]

    # Fallback if filter eliminates all
    if dff.empty:
        st.warning("No records match that role filter. Showing all.")
        dff = df.copy()

    selected_label = st.selectbox("Profile", dff["selector_label"].tolist(), index=0)
    selected = dff[dff["selector_label"] == selected_label].iloc[0].to_dict()

# Layout
left, right = st.columns([1, 1])

with left:
    st.subheader("Supervisor snapshot")
    c1, c2, c3 = st.columns(3)
    c1.metric("Name", selected.get("name", "—"))
    c2.metric("Role", selected.get("role", "—"))
    c3.metric("Cottage", str(selected.get("cottage", selected.get("cottage_str", "—"))))

    burnout_val = selected.get("burnout_num", None)
    st.markdown("### Burnout")
    st.markdown(f"**Rating:** {'' if burnout_val is None else burnout_val}  \n**Level:** {burnout_label(burnout_val)}")
    for tip in burnout_guidance(burnout_val):
        st.write(f"- {tip}")

    # Timestamp
    ts = selected.get("timestamp", None)
    if pd.notna(ts):
        local = ts.tz_convert("America/New_York")
        st.caption(f"Last updated: {local.strftime('%Y-%m-%d %I:%M %p %Z')}")

with right:
    st.subheader("Profile interpretation")
    render_style_block("Primary communication style", selected.get("p_comm", ""), COMM_DESC)
    render_style_block("Secondary communication style", selected.get("s_comm", ""), COMM_DESC)
    render_style_block("Primary motivator", selected.get("p_mot", ""), MOT_DESC)
    render_style_block("Secondary motivator", selected.get("s_mot", ""), MOT_DESC)

st.divider()

# Team views
st.header("Team / cohort view")

colA, colB, colC = st.columns(3)
with colA:
    same_cottage = st.checkbox("Show same cottage", value=True)
with colB:
    same_role = st.checkbox("Show same role", value=False)
with colC:
    include_history = st.checkbox("Include historical submissions (all rows)", value=False)

base = df_raw if include_history else df

team = base.copy()
if same_cottage and "cottage" in base.columns:
    team = team[team["cottage"].astype(str) == str(selected.get("cottage"))]
if same_role and "role" in base.columns:
    team = team[team["role"] == selected.get("role")]

# Clean display columns
display_cols = [c for c in ["timestamp","name","email","role","cottage","p_comm","s_comm","p_mot","s_mot","burnout"] if c in team.columns]
team_disp = team[display_cols].copy()

# Sort latest first if timestamp exists
if "timestamp" in team_disp.columns:
    team_disp = team_disp.sort_values("timestamp", ascending=False)

st.dataframe(team_disp, use_container_width=True)

# Simple cohort summaries
st.subheader("Quick summaries")
sum_cols = st.columns(3)

with sum_cols[0]:
    if "p_comm" in team.columns:
        st.markdown("**Primary comm styles**")
        st.write(team["p_comm"].value_counts(dropna=True))

with sum_cols[1]:
    if "p_mot" in team.columns:
        st.markdown("**Primary motivators**")
        st.write(team["p_mot"].value_counts(dropna=True))

with sum_cols[2]:
    if "burnout_num" in team.columns:
        st.markdown("**Burnout (avg)**")
        avg = team["burnout_num"].dropna().mean()
        st.write("—" if pd.isna(avg) else round(float(avg), 2))

st.caption("Tip: Edit the COMM_DESC and MOT_DESC dictionaries to match your organization’s language and coaching guidance.")
