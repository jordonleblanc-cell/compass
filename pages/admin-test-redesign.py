import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import re
import time

# =========================
# IMPORT YOUR EXISTING APP CORE
# =========================
# This keeps ALL your original data structures and information intact:
# - COMM_PROFILES / MOTIV_PROFILES / INTEGRATED_PROFILES
# - PDF safe utilities (SafeFPDF, pdf_safe)
# - Email utilities (if you have them)
# - RBAC + login logic (we re-use the same approach)
#
# Make sure your old file is renamed to: admin_test_alt.py
try:
    import admin_test_alt as core
except Exception as e:
    st.error(
        "Could not import your existing module (admin_test_alt.py). "
        "Make sure you renamed your original file correctly.\n\n"
        f"Import error: {e}"
    )
    st.stop()


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
# THEME / CSS (Modern, calmer UI)
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

    /* Hide Streamlit default sidebar nav (you already do this in your core CSS) */
    [data-testid="stSidebarNav"] {display: none;}

    .hero {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary2) 100%);
        border-radius: var(--radius);
        padding: 26px 26px 20px 26px;
        box-shadow: 0 10px 30px rgba(26,115,232,0.25);
        color: #fff;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
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

    .card-tight { padding: 14px; }

    .muted { color: var(--muted); }

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

    /* Make expanders feel like modern drawers */
    [data-testid="stExpander"] {
        border-radius: 14px;
        border: 1px solid var(--border);
        overflow: hidden;
        background: #fff;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# DATA NORMALIZATION (fixes your KeyError)
# =========================
def _normalize_staff_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Expand nested `scores` if present (dicts)
    if "scores" in df.columns:
        def to_dict(v):
            if isinstance(v, dict):
                return v
            # sometimes stored as JSON string
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

    # Canonical aliases (supports your current payload naming differences)
    aliases = {
        "primarycomm": ["primarycomm", "primary_comm", "p_comm", "primarycommstyle", "primarycommunication", "primarycomm"],
        "secondarycomm": ["secondarycomm", "secondary_comm", "s_comm", "secondarycommstyle", "secondarycommunication", "secondarycomm"],
        "primarymotiv": ["primarymotiv", "primary_motiv", "p_mot", "primarymotivation", "primarymotiv"],
        "secondarymotiv": ["secondarymotiv", "secondary_motiv", "s_mot", "secondarymotivation", "secondarymotiv"],
    }

    for canonical, options in aliases.items():
        for opt in options:
            opt = opt.lower()
            if opt in df.columns:
                df[canonical] = df[opt]
                break

    # Clean common text columns
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


# =========================
# RE-USE YOUR EXISTING DATA FETCH
# =========================
# Your core file already has:
# - GOOGLE_SCRIPT_URL
# - fetch_staff_data()
# We’ll use that, then normalize.
@st.cache_data(ttl=60)
def fetch_staff_df():
    raw = core.fetch_staff_data()  # returns list[dict] in your current app
    df_raw = pd.DataFrame(raw)
    return _normalize_staff_df(df_raw)


# =========================
# AUTH / RBAC: REUSE YOUR CURRENT APPROACH
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

# We reuse your check_password logic by calling the function from core if it exists.
# If you want to keep EXACTLY the same login, we can invoke core.check_password,
# but it is tied to your original session keys.
#
# Easiest: copy your login screen behavior with minimal edits and then reuse RBAC filter.
def _check_password_redesign():
    MASTER_PW = st.secrets.get("ADMIN_PASSWORD", "admin2025")
    PS_PW = st.secrets.get("PS_PASSWORD", "ps2025")
    SS_PW = st.secrets.get("SS_PASSWORD", "ss2025")

    input_pw = st.session_state.password_input
    selected_user = st.session_state.user_select
    authorized = False

    # Administrator
    if selected_user == "Administrator":
        if input_pw == MASTER_PW:
            authorized = True
            st.session_state.current_user_name = "Administrator"
            st.session_state.current_user_role = "Admin"
            st.session_state.current_user_cottage = "All"
        else:
            st.error("Incorrect Administrator Password.")
            return

    # Staff leader
    if not df_all.empty and selected_user != "Administrator":
        try:
            user_row = df_all[df_all["name"] == selected_user].iloc[0]
        except Exception:
            st.error("User not found. Please contact administrator.")
            return

        role_raw = str(user_row.get("role", "YDP")).strip()
        cottage_raw = str(user_row.get("cottage", "All")).strip()

        # Master override
        if input_pw == MASTER_PW:
            authorized = True
        else:
            # Try individual password in secrets based on last name (your existing pattern)
            try:
                last_name = selected_user.strip().split()[-1]
                secret_key = f"{last_name}_password"
                individual_pw = st.secrets.get(secret_key)
            except Exception:
                individual_pw = None

            if individual_pw and str(input_pw).strip() == str(individual_pw).strip():
                authorized = True
            else:
                # Role-based codes
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
    """RBAC filter matching your original behavior."""
    user_role = str(st.session_state.current_user_role or "")
    user_cottage = str(st.session_state.current_user_cottage or "All")
    current_user = str(st.session_state.current_user_name or "")
    current_df = st.session_state.staff_df

    if current_df is None or current_df.empty:
        return pd.DataFrame()

    # Admin/Director/Manager sees all
    if (user_role == "Admin") or (current_user == "Administrator") or ("Director" in user_role) or ("Manager" in user_role):
        return current_df

    filtered_df = current_df.copy()

    # Cottage limitation
    if "cottage" in filtered_df.columns and user_cottage != "All":
        filtered_df = filtered_df[filtered_df["cottage"] == user_cottage]

    # Role limitation
    if "role" in filtered_df.columns:
        if "Program Supervisor" in user_role:
            pass
        elif "Shift Supervisor" in user_role:
            condition = (filtered_df["role"] == "YDP") | (filtered_df["name"] == current_user)
            filtered_df = filtered_df[condition]
        elif "YDP" in user_role:
            filtered_df = filtered_df[filtered_df["name"] == current_user]

    return filtered_df


# =========================
# LOGIN SCREEN (Modern)
# =========================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="card" style="max-width:520px; margin: 70px auto; padding: 26px;">
      <h2 style="margin-top:0;">Supervisor Access</h2>
      <p class="muted" style="margin-bottom: 16px;">
        Select your name and enter your access code to manage your team.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Build eligible list (same as original intent)
    if not df_all.empty and "name" in df_all.columns and "role" in df_all.columns:
        leadership_roles = ["Program Supervisor", "Shift Supervisor", "Manager", "Director"]
        eligible_staff = df_all[df_all["role"].str.contains("|".join(leadership_roles), case=False, na=False)]["name"].unique().tolist()
        user_names = ["Administrator"] + sorted(eligible_staff)
    else:
        user_names = ["Administrator"]

    # Form inside same card
    colA, colB, colC = st.columns([1, 6, 1])
    with colB:
        st.selectbox("Who are you?", user_names, key="user_select")
        st.text_input("Access Code", type="password", key="password_input", on_change=_check_password_redesign)

    st.stop()


# =========================
# SIDEBAR SESSION
# =========================
with st.sidebar:
    st.markdown("### Session")
    st.caption(f"Logged in as: **{st.session_state.current_user_name}**")
    st.caption(f"Role: **{st.session_state.current_user_role}**")
    st.caption(f"Cottage: **{st.session_state.current_user_cottage}**")
    st.divider()

    view = st.radio(
        "Navigate",
        ["Dashboard", "Team Profiles", "Insights", "Coaching", "Reports"],
        index=0
    )

    if st.button("Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()


# =========================
# DATA FOR THIS USER
# =========================
df = get_filtered_dataframe()


# =========================
# HELPERS: profile rendering (reuses your full dictionaries unchanged)
# =========================
def render_bullets(title: str, bullets: list[str]):
    if not bullets:
        return
    st.markdown(f"**{title}**")
    for b in bullets:
        st.markdown(f"- {b}")


def get_comm_profile(trait: str):
    return core.COMM_PROFILES.get(trait, {}) if hasattr(core, "COMM_PROFILES") else {}


def get_motiv_profile(trait: str):
    return core.MOTIV_PROFILES.get(trait, {}) if hasattr(core, "MOTIV_PROFILES") else {}


def get_integrated_profile(key: str):
    return core.INTEGRATED_PROFILES.get(key, {}) if hasattr(core, "INTEGRATED_PROFILES") else {}


# =========================
# DASHBOARD VIEW
# =========================
if view == "Dashboard":
    avg_comm = safe_mean(df, ["primarycomm", "secondarycomm"])
    avg_motiv = safe_mean(df, ["primarymotiv", "secondarymotiv"])
    cottage_count = df["cottage"].nunique() if ("cottage" in df.columns and not df.empty) else 0

    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Supervisor Dashboard</div>
        <div class="hero-sub">
            Use this console to review your team’s assessment patterns, pull coaching guidance,
            and generate reports—without digging through long pages.
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

    st.markdown("### Quick actions")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown('<div class="action-grid">', unsafe_allow_html=True)
        if st.button("🧠 Review Team Profiles\n\nOpen staff cards & coaching drawers"):
            st.session_state._nav = "Team Profiles"
        st.markdown('</div>', unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="action-grid">', unsafe_allow_html=True)
        if st.button("📊 View Trends\n\nCommunication & motivation distributions"):
            st.session_state._nav = "Insights"
        st.markdown('</div>', unsafe_allow_html=True)
    with a3:
        st.markdown('<div class="action-grid">', unsafe_allow_html=True)
        if st.button("🎯 Coaching Playbook\n\nTrait guidance and scripts"):
            st.session_state._nav = "Coaching"
        st.markdown('</div>', unsafe_allow_html=True)
    with a4:
        st.markdown('<div class="action-grid">', unsafe_allow_html=True)
        if st.button("📄 Reports\n\nPDF + email-ready outputs"):
            st.session_state._nav = "Reports"
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # A small “What’s in your scope” preview table
    st.markdown("### In your scope (preview)")
    preview_cols = [c for c in ["name", "role", "cottage", "primarycomm", "primarymotiv"] if c in df.columns]
    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        st.dataframe(df[preview_cols].head(15), use_container_width=True)


# =========================
# TEAM PROFILES VIEW (Card-based + progressive disclosure)
# =========================
elif view == "Team Profiles":
    st.markdown("## Team Profiles")

    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        # Filters
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

        # Cards
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
                # Integrated profile key if both exist
                integrated_key = None
                if p_comm and p_mot:
                    integrated_key = f"{p_comm}-{p_mot}"
                ip = get_integrated_profile(integrated_key) if integrated_key else {}

                if ip:
                    st.markdown("**Integrated Profile**")
                    st.write(ip.get("title", integrated_key))
                    st.caption(ip.get("synergy", ""))

            # Progressive disclosure drawers
            tabs = st.tabs(["Coaching (fast)", "Deep guidance", "Questions"])
            with tabs[0]:
                # Quick: show 2-3 highest value items
                if p_comm:
                    cp = get_comm_profile(str(p_comm))
                    sb = cp.get("supervising_bullets", []) if isinstance(cp, dict) else []
                    if sb:
                        st.markdown("**Best supervisor moves**")
                        for b in sb[:3]:
                            st.markdown(f"- {b}")
                if p_mot:
                    mp = get_motiv_profile(str(p_mot))
                    sb = mp.get("strategies_bullets", []) if isinstance(mp, dict) else []
                    if sb:
                        st.markdown("**Motivation strategies**")
                        for b in sb[:3]:
                            st.markdown(f"- {b}")

            with tabs[1]:
                if p_comm:
                    cp = get_comm_profile(str(p_comm))
                    render_bullets("How they tend to communicate", cp.get("bullets", []))
                    render_bullets("How to supervise", cp.get("supervising_bullets", []))
                if p_mot:
                    mp = get_motiv_profile(str(p_mot))
                    render_bullets("What drives them", mp.get("bullets", []))
                    render_bullets("Strategies that work", mp.get("strategies_bullets", []))
                    render_bullets("How to celebrate them", mp.get("celebrate_bullets", []))
                    deep = mp.get("celebrate_deep_dive", "")
                    if deep:
                        st.markdown(deep)

                if integrated_key:
                    ip = get_integrated_profile(integrated_key)
                    if ip:
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
                if integrated_key:
                    ip = get_integrated_profile(integrated_key)
                    qs = ip.get("questions", []) if isinstance(ip, dict) else []
                    if qs:
                        st.markdown("**Useful supervision questions**")
                        for qx in qs:
                            st.markdown(f"- {qx}")
                else:
                    st.caption("Integrated questions appear when both a primary comm + primary motiv are available.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")  # spacing


# =========================
# INSIGHTS VIEW (Charts)
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

        st.divider()

        # Optional breakdown by cottage
        if "cottage" in df.columns and "primarycomm" in df.columns:
            st.markdown("### By cottage (communication)")
            fig3 = px.histogram(df, x="primarycomm", color="cottage", barmode="group")
            st.plotly_chart(fig3, use_container_width=True)


# =========================
# COACHING VIEW (Playbook)
# =========================
elif view == "Coaching":
    st.markdown("## Coaching Playbook")

    st.markdown("Use this section when you want the *framework* without digging into staff cards.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Communication styles")
        comm_trait = st.selectbox(
            "Choose a communication trait",
            sorted(list(core.COMM_PROFILES.keys())) if hasattr(core, "COMM_PROFILES") else [],
        )
        if comm_trait:
            cp = get_comm_profile(comm_trait)
            st.markdown('<div class="card card-tight">', unsafe_allow_html=True)
            render_bullets("Core patterns", cp.get("bullets", []))
            with st.expander("Supervising guidance"):
                render_bullets("How to supervise", cp.get("supervising_bullets", []))
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("### Motivation drivers")
        motiv_trait = st.selectbox(
            "Choose a motivation trait",
            sorted(list(core.MOTIV_PROFILES.keys())) if hasattr(core, "MOTIV_PROFILES") else [],
        )
        if motiv_trait:
            mp = get_motiv_profile(motiv_trait)
            st.markdown('<div class="card card-tight">', unsafe_allow_html=True)
            render_bullets("Core patterns", mp.get("bullets", []))
            with st.expander("Strategies"):
                render_bullets("Strategies that work", mp.get("strategies_bullets", []))
            with st.expander("Celebration language"):
                render_bullets("Celebrate", mp.get("celebrate_bullets", []))
                deep = mp.get("celebrate_deep_dive", "")
                if deep:
                    st.markdown(deep)
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("### Integrated profiles")
    st.caption("Pick a combo to view the integrated coaching framework.")
    left, right = st.columns(2)
    with left:
        comm_pick = st.selectbox("Communication", sorted(list(core.COMM_PROFILES.keys())))
    with right:
        motiv_pick = st.selectbox("Motivation", sorted(list(core.MOTIV_PROFILES.keys())))

    key = f"{comm_pick}-{motiv_pick}"
    ip = get_integrated_profile(key)
    if not ip:
        st.warning(f"No integrated profile found for {key}.")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {ip.get('title', key)}")
        st.write(ip.get("synergy", ""))

        with st.expander("Support"):
            st.markdown(ip.get("support", ""))
        with st.expander("Thriving"):
            st.markdown(ip.get("thriving", ""))
        with st.expander("Struggling"):
            st.markdown(ip.get("struggling", ""))
        with st.expander("Interventions"):
            for item in ip.get("interventions", []):
                st.markdown(f"- {item}")
        with st.expander("Questions"):
            for qx in ip.get("questions", []):
                st.markdown(f"- {qx}")
        with st.expander("Advancement"):
            st.markdown(ip.get("advancement", ""))

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# REPORTS VIEW (Hooks that keep your existing PDF/email tooling)
# =========================
elif view == "Reports":
    st.markdown("## Reports & Exports")
    st.caption("This is wired as hooks so you can re-use your existing PDF/email code unchanged.")

    if df.empty:
        st.info("No staff records found for your access scope.")
    else:
        st.markdown("### Generate outputs")

        staff_names = df["name"].dropna().unique().tolist() if "name" in df.columns else []
        chosen = st.selectbox("Choose staff member", staff_names)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Generate Coaching PDF"):
                st.info("Hook: call your existing PDF generator here.")
                # Example: core.generate_pdf_for_staff(chosen)  # if you have it

        with col2:
            if st.button("✉️ Email Coaching Snapshot"):
                st.info("Hook: call your existing email sender here.")
                # Example: core.email_snapshot(chosen)

        with col3:
            if st.button("📊 Export CSV (filtered scope)"):
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", data=csv, file_name="staff_scope_export.csv", mime="text/csv")


# =========================
# QUICK ACTION NAV (from dashboard buttons)
# =========================
if "_nav" in st.session_state:
    target = st.session_state._nav
    del st.session_state._nav

    # mimic sidebar selection by rerun + setting a state
    st.session_state._force_view = target
    st.rerun()

if "_force_view" in st.session_state:
    # If user jumped here, try to align sidebar
    # (Streamlit radio doesn't accept external set cleanly; this keeps logic simple.)
    del st.session_state._force_view
