import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import re
from pathlib import Path
import importlib.util

# =========================
# DYNAMIC IMPORT: admin-test-alt.py
# =========================
def load_core_module():
    """
    Loads your existing app code (admin-test-alt.py) as a module named `core`,
    even though the filename contains a hyphen.
    """
    repo_root = Path(__file__).resolve().parents[1]  # pages/ -> repo root
    candidate_paths = [
        repo_root / "admin-test-alt.py",
        repo_root / admin_test_alt.py",
    ]

    core_path = None
    for p in candidate_paths:
        if p.exists():
            core_path = p
            break

    if core_path is None:
        st.error(
            "Could not find your existing file in the repo root.\n\n"
            f"Tried:\n- {candidate_paths[0]}\n- {candidate_paths[1]}"
        )
        st.stop()

    spec = importlib.util.spec_from_file_location("core", str(core_path))
    if spec is None or spec.loader is None:
        st.error(f"Failed to create import spec for {core_path}")
        st.stop()

    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    return core, core_path


core, core_path = load_core_module()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Elmcrest Supervisor Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# MODERN CSS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    :root{
        --primary:#1a73e8;
        --primary2:#1557b0;
        --bg:#f7f8fb;
        --card:#ffffff;
        --text:#202124;
        --muted:#5f6368;
        --border:#e6e7eb;
        --shadow: 0 2px 10px rgba(0,0,0,0.06);
        --shadow2: 0 12px 30px rgba(0,0,0,0.08);
        --radius: 18px;
    }

    .stApp { background: var(--bg); }

    h1,h2,h3,h4,h5{
        font-family: "Google Sans", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        color: var(--text);
        letter-spacing: -0.2px;
    }

    p, li, div, span, label {
        font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        color: var(--text);
    }

    [data-testid="stSidebarNav"] {display: none;}

    .hero {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary2) 100%);
        border-radius: var(--radius);
        padding: 26px 26px 20px 26px;
        box-shadow: 0 10px 30px rgba(26,115,232,0.25);
        color: #fff;
        margin-bottom: 18px;
    }

    .hero-title{
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        color: #fff;
    }
    .hero-sub{
        margin-top: 6px;
        font-size: 0.98rem;
        color: rgba(255,255,255,0.92);
        max-width: 900px;
        line-height: 1.45;
    }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 18px;
        box-shadow: var(--shadow);
    }

    .pill {
        display: inline-block;
        padding: 6px 10px;
        background: #f0f4ff;
        border: 1px solid #dfe7ff;
        color: #20408f;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .action-grid button {
        height: 112px !important;
        border-radius: 18px !important;
        border: 1px solid var(--border) !important;
        background: #fff !important;
        text-align: left !important;
        padding: 16px 16px !important;
        box-shadow: var(--shadow) !important;
        transition: 0.15s ease-in-out;
    }
    .action-grid button:hover{
        transform: translateY(-2px);
        border-color: var(--primary) !important;
        box-shadow: var(--shadow2) !important;
        color: var(--primary) !important;
    }

    [data-testid="stExpander"] {
        border-radius: 14px;
        border: 1px solid var(--border);
        overflow: hidden;
        background: #fff;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# DATA NORMALIZATION (fixes your KeyError safely)
# =========================
def normalize_staff_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Expand nested `scores` if present
    if "scores" in df.columns:
        def to_dict(v):
            if isinstance(v, dict):
                return v
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return {}
            return {}

        scores_df = pd.json_normalize(df["scores"].apply(to_dict))
        scores_df.columns = scores_df.columns.astype(str).str.strip().str.lower()
        df = df.drop(columns=["scores"]).reset_index(drop=True)
        df = pd.concat([df, scores_df.reset_index(drop=True)], axis=1)

    # Alias mapping (covers common variants)
    aliases = {
        "primarycomm": ["primarycomm", "primary_comm", "p_comm", "primarycommstyle", "primarycommunication"],
        "secondarycomm": ["secondarycomm", "secondary_comm", "s_comm", "secondarycommstyle", "secondarycommunication"],
        "primarymotiv": ["primarymotiv", "primary_motiv", "p_mot", "primarymotivation"],
        "secondarymotiv": ["secondarymotiv", "secondary_motiv", "s_mot", "secondarymotivation"],
    }

    for canonical, options in aliases.items():
        for opt in options:
            if opt in df.columns:
                df[canonical] = df[opt]
                break

    for c in ["name", "role", "cottage", "email"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    return df


def safe_mean(df: pd.DataFrame, cols: list[str]):
    cols = [c for c in cols if c in df.columns]
    if df is None or df.empty or not cols:
        return None
    vals = df[cols].apply(pd.to_numeric, errors="coerce")
    m = vals.stack().mean()
    return None if pd.isna(m) else float(m)


@st.cache_data(ttl=60)
def fetch_staff_df() -> pd.DataFrame:
    raw = core.fetch_staff_data()  # from your existing file
    df_raw = pd.DataFrame(raw)
    return normalize_staff_df(df_raw)


# =========================
# AUTH STATE (same shape as your original)
# =========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user_role" not in st.session_state:
    st.session_state.current_user_role = None
if "current_user_cottage" not in st.session_state:
    st.session_state.current_user_cottage = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None

df_all = fetch_staff_df()
st.session_state.staff_df = df_all


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
        try:
            user_row = df_all[df_all["name"] == selected_user].iloc[0]
        except Exception:
            st.error("User not found.")
            return

        role_raw = str(user_row.get("role", "YDP"))
        cottage_raw = str(user_row.get("cottage", "All"))

        if input_pw == MASTER_PW:
            authorized = True
        else:
            # Individual pw by last name key
            try:
                last_name = selected_user.strip().split()[-1]
                individual_pw = st.secrets.get(f"{last_name}_password")
            except Exception:
                individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip():
                authorized = True
            else:
                if ("Program Supervisor" in role_raw) or ("Director" in role_raw) or ("Manager" in role_raw):
                    if input_pw == PS_PW:
                        authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                elif "Shift Supervisor" in role_raw:
                    if input_pw == SS_PW:
                        authorized = True
                    else:
                        st.error("Incorrect Access Code.")
                        return
                else:
                    st.error("Access Restricted. Please contact your administrator.")
                    return

        if authorized:
            st.session_state.current_user_name = user_row["name"]
            st.session_state.current_user_role = role_raw
            st.session_state.current_user_cottage = cottage_raw

    if authorized:
        st.session_state.authenticated = True
        if "password_input" in st.session_state:
            del st.session_state.password_input
    else:
        st.error("Authentication Failed.")


def get_filtered_dataframe():
    user_role = str(st.session_state.current_user_role or "")
    user_cottage = str(st.session_state.current_user_cottage or "All")
    current_user = str(st.session_state.current_user_name or "")
    current_df = st.session_state.staff_df

    if current_df is None or current_df.empty:
        return pd.DataFrame()

    if (user_role == "Admin") or (current_user == "Administrator") or ("Director" in user_role) or ("Manager" in user_role):
        return current_df

    filtered = current_df.copy()

    if "cottage" in filtered.columns and user_cottage != "All":
        filtered = filtered[filtered["cottage"] == user_cottage]

    if "role" in filtered.columns:
        if "Program Supervisor" in user_role:
            pass
        elif "Shift Supervisor" in user_role:
            filtered = filtered[(filtered["role"] == "YDP") | (filtered["name"] == current_user)]
        elif "YDP" in user_role:
            filtered = filtered[filtered["name"] == current_user]

    return filtered


# =========================
# LOGIN SCREEN
# =========================
if not st.session_state.authenticated:
    st.markdown(f"""
    <div class="card" style="max-width:520px; margin: 70px auto;">
      <h2 style="margin-top:0;">Supervisor Access</h2>
      <p style="color: var(--muted); margin-bottom: 6px;">
        Loaded core file: <b>{core_path.name}</b>
      </p>
      <p style="color: var(--muted); margin-bottom: 16px;">
        Select your name and enter your access code to manage your team.
      </p>
    </div>
    """, unsafe_allow_html=True)

    if not df_all.empty and "name" in df_all.columns and "role" in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Director"]
        eligible_staff = df_all[df_all["role"].str.contains("|".join(leadership_roles), case=False, na=False)]["name"].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
    else:
        user_names = ["Administrator"]

    colA, colB, colC = st.columns([1, 6, 1])
    with colB:
        st.selectbox("Who are you?", user_names, key="user_select")
        st.text_input("Access Code", type="password", key="password_input", on_change=check_password)

    st.stop()


# =========================
# SIDEBAR + NAV
# =========================
with st.sidebar:
    st.markdown("### Session")
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    st.caption(f"Cottage: **{st.session_state.current_user_cottage}**")
    st.divider()

    view = st.radio("Navigate", ["Dashboard", "Team Profiles", "Insights", "Coaching", "Reports"], index=0)

    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()


df = get_filtered_dataframe()

# =========================
# PROFILE HELPERS (reuse your full dictionaries)
# =========================
def render_bullets(title: str, bullets: list[str]):
    if bullets:
        st.markdown(f"**{title}**")
        for b in bullets:
            st.markdown(f"- {b}")

def comm_profile(trait: str):
    return core.COMM_PROFILES.get(trait, {}) if hasattr(core, "COMM_PROFILES") else {}

def motiv_profile(trait: str):
    return core.MOTIV_PROFILES.get(trait, {}) if hasattr(core, "MOTIV_PROFILES") else {}

def integrated_profile(key: str):
    return core.INTEGRATED_PROFILES.get(key, {}) if hasattr(core, "INTEGRATED_PROFILES") else {}


# =========================
# DASHBOARD
# =========================
if view == "Dashboard":
    avg_comm = safe_mean(df, ["primarycomm", "secondarycomm"])
    avg_motiv = safe_mean(df, ["primarymotiv", "secondarymotiv"])
    cottage_count = df["cottage"].nunique() if ("cottage" in df.columns and not df.empty) else 0

    st.markdown("""
    <div class="hero">
        <div class="hero-title">Supervisor Dashboard</div>
        <div class="hero-sub">
            Review your team’s assessment patterns, pull coaching guidance, and generate reports—fast.
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Staff in Scope", 0 if df.empty else len(df))
    with m2:
        st.metric("Avg Comm Score", "–" if avg_comm is None else round(avg_comm, 1))
    with m3:
        st.metric("Avg Motivation Score", "–" if avg_motiv is None else round(avg_motiv, 1))
    with m4:
        st.metric("Cottages in Scope", cottage_count)

    st.divider()
    st.markdown("### In your scope (preview)")
    preview_cols = [c for c in ["name", "role", "cottage", "primarycomm", "primarymotiv"] if c in df.columns]
    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        st.dataframe(df[preview_cols].head(15), use_container_width=True)


# =========================
# TEAM PROFILES
# =========================
elif view == "Team Profiles":
    st.markdown("## Team Profiles")

    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        f1, f2, f3 = st.columns([2, 2, 3])
        with f1:
            cottage_filter = st.selectbox(
                "Filter by cottage",
                ["All"] + sorted(df["cottage"].dropna().unique().tolist()) if "cottage" in df.columns else ["All"],
            )
        with f2:
            role_filter = st.selectbox(
                "Filter by role",
                ["All"] + sorted(df["role"].dropna().unique().tolist()) if "role" in df.columns else ["All"],
            )
        with f3:
            q = st.text_input("Search by name", placeholder="Type a staff name…")

        filtered = df.copy()
        if cottage_filter != "All" and "cottage" in filtered.columns:
            filtered = filtered[filtered["cottage"] == cottage_filter]
        if role_filter != "All" and "role" in filtered.columns:
            filtered = filtered[filtered["role"] == role_filter]
        if q.strip() and "name" in filtered.columns:
            filtered = filtered[filtered["name"].str.contains(re.escape(q.strip()), case=False, na=False)]

        st.caption(f"Showing **{len(filtered)}** staff record(s).")

        for _, row in filtered.iterrows():
            name = row.get("name", "Staff")
            role = row.get("role", "")
            cottage = row.get("cottage", "")
            p_comm = row.get("primarycomm", None)
            s_comm = row.get("secondarycomm", None)
            p_mot = row.get("primarymotiv", None)
            s_mot = row.get("secondarymotiv", None)

            st.markdown('<div class="card">', unsafe_allow_html=True)

            left, right = st.columns([3, 2])
            with left:
                st.markdown(f"### {name}")
                st.caption(f"Role: **{role}**  |  Cottage: **{cottage}**")

                if p_comm:
                    st.markdown(f'<span class="pill">Comm: {p_comm}</span>', unsafe_allow_html=True)
                if s_comm:
                    st.markdown(f'<span class="pill">Comm #2: {s_comm}</span>', unsafe_allow_html=True)
                if p_mot:
                    st.markdown(f'<span class="pill">Motivation: {p_mot}</span>', unsafe_allow_html=True)
                if s_mot:
                    st.markdown(f'<span class="pill">Motivation #2: {s_mot}</span>', unsafe_allow_html=True)

            with right:
                integrated_key = f"{p_comm}-{p_mot}" if (p_comm and p_mot) else None
                ip = integrated_profile(integrated_key) if integrated_key else {}
                if ip:
                    st.markdown("**Integrated Profile**")
                    st.write(ip.get("title", integrated_key))
                    st.caption(ip.get("synergy", ""))

            tabs = st.tabs(["Coaching (fast)", "Deep guidance", "Questions"])
            with tabs[0]:
                if p_comm:
                    cp = comm_profile(str(p_comm))
                    sb = cp.get("supervising_bullets", [])
                    if sb:
                        st.markdown("**Best supervisor moves**")
                        for b in sb[:3]:
                            st.markdown(f"- {b}")
                if p_mot:
                    mp = motiv_profile(str(p_mot))
                    sb = mp.get("strategies_bullets", [])
                    if sb:
                        st.markdown("**Motivation strategies**")
                        for b in sb[:3]:
                            st.markdown(f"- {b}")

            with tabs[1]:
                if p_comm:
                    cp = comm_profile(str(p_comm))
                    render_bullets("How they tend to communicate", cp.get("bullets", []))
                    render_bullets("How to supervise", cp.get("supervising_bullets", []))
                if p_mot:
                    mp = motiv_profile(str(p_mot))
                    render_bullets("What drives them", mp.get("bullets", []))
                    render_bullets("Strategies that work", mp.get("strategies_bullets", []))
                    render_bullets("How to celebrate them", mp.get("celebrate_bullets", []))
                    deep = mp.get("celebrate_deep_dive", "")
                    if deep:
                        st.markdown(deep)

                if integrated_key and ip:
                    st.divider()
                    st.markdown(f"### {ip.get('title', integrated_key)}")
                    st.write(ip.get("synergy", ""))
                    with st.expander("Support notes"):
                        st.markdown(ip.get("support", ""))
                    with st.expander("Thriving patterns"):
                        st.markdown(ip.get("thriving", ""))
                    with st.expander("Struggling patterns"):
                        st.markdown(ip.get("struggling", ""))
                    with st.expander("Interventions"):
                        for item in ip.get("interventions", []):
                            st.markdown(f"- {item}")
                    with st.expander("Advancement coaching"):
                        st.markdown(ip.get("advancement", ""))

            with tabs[2]:
                if integrated_key and ip:
                    qs = ip.get("questions", [])
                    if qs:
                        st.markdown("**Useful supervision questions**")
                        for qx in qs:
                            st.markdown(f"- {qx}")
                else:
                    st.caption("Integrated questions appear when both a primary comm + primary motiv are available.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")


# =========================
# INSIGHTS
# =========================
elif view == "Insights":
    st.markdown("## Team Insights")
    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        c1, c2 = st.columns(2)
        if "primarycomm" in df.columns:
            with c1:
                fig = px.histogram(df, x="primarycomm", title="Primary Communication Styles")
                st.plotly_chart(fig, use_container_width=True)
        if "primarymotiv" in df.columns:
            with c2:
                fig2 = px.histogram(df, x="primarymotiv", title="Primary Motivations")
                st.plotly_chart(fig2, use_container_width=True)


# =========================
# COACHING PLAYBOOK
# =========================
elif view == "Coaching":
    st.markdown("## Coaching Playbook")
    st.markdown("Use this when you want the framework without opening staff cards.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Communication styles")
        comm_trait = st.selectbox("Choose a communication trait", sorted(list(core.COMM_PROFILES.keys())))
        cp = comm_profile(comm_trait)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        render_bullets("Core patterns", cp.get("bullets", []))
        with st.expander("Supervising guidance"):
            render_bullets("How to supervise", cp.get("supervising_bullets", []))
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### Motivation drivers")
        motiv_trait = st.selectbox("Choose a motivation trait", sorted(list(core.MOTIV_PROFILES.keys())))
        mp = motiv_profile(motiv_trait)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        render_bullets("Core patterns", mp.get("bullets", []))
        with st.expander("Strategies"):
            render_bullets("Strategies that work", mp.get("strategies_bullets", []))
        with st.expander("Celebration language"):
            render_bullets("Celebrate", mp.get("celebrate_bullets", []))
            deep = mp.get("celebrate_deep_dive", "")
            if deep:
                st.markdown(deep)
        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# REPORTS (hooks)
# =========================
elif view == "Reports":
    st.markdown("## Reports & Exports")
    st.caption("Hooks are ready so you can wire your existing PDF/email logic without changing your data model.")

    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        names = df["name"].dropna().unique().tolist() if "name" in df.columns else []
        chosen = st.selectbox("Choose staff member", names)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("📄 Generate Coaching PDF"):
                st.info("Hook: call your existing PDF generator here (from core).")
        with c2:
            if st.button("✉️ Email Coaching Snapshot"):
                st.info("Hook: call your existing email sender here (from core).")
        with c3:
            if st.button("📊 Export CSV (filtered scope)"):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", data=csv, file_name="staff_scope_export.csv", mime="text/csv")
