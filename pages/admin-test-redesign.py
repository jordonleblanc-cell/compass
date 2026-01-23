import streamlit as st
import urllib.request
import json
import pandas as pd

# --- Configuration ---
DATA_URL = "https://script.google.com/macros/s/AKfycbymKxV156gkuGKI_eyKb483W4cGORMMcWqKsFcmgHAif51xQHyOCDO4KeXPJdK4gHpD/exec"

# --- Page Setup ---
st.set_page_config(
    page_title="Supervisor Profile Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data(ttl=60)  # Cache data for 60 seconds to prevent spamming the API
def fetch_data():
    try:
        req = urllib.request.Request(DATA_URL)
        req.add_header('User-Agent', 'Python-Streamlit-App')
        with urllib.request.urlopen(req) as response:
            data = response.read()
            return json.loads(data)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def extract_metrics(data):
    """Recursively find numeric values to display as metrics."""
    metrics = {}
    ignore_keys = ["id", "uid", "phone", "zip", "year", "zipcode"]
    
    for k, v in data.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if k.lower() not in ignore_keys:
                metrics[k] = v
        elif isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if isinstance(sub_v, (int, float)):
                        metrics[f"{k} {sub_k}"] = sub_v
    return metrics

def generate_interpretation(metrics):
    highs = []
    lows = []
    
    for k, v in metrics.items():
        # Normalization logic for interpretation
        score = v
        if v <= 1: score = v * 100
        
        if score > 80: highs.append(k)
        if score < 60: lows.append(k)
    
    return highs, lows

# --- Main App Logic ---

st.title("📊 Supervisor Performance Analytics")

if st.button("↻ Refresh Data"):
    st.cache_data.clear()
    st.rerun()

data = fetch_data()

if data:
    # 1. Header Profile
    col1, col2 = st.columns([3, 1])
    
    name = data.get("name") or data.get("Supervisor") or data.get("fullName") or "Unknown Supervisor"
    role = data.get("role") or data.get("Title") or data.get("position") or "Supervisor"
    dept = data.get("department") or data.get("Department") or "General Operations"
    
    with col1:
        st.header(name)
        st.subheader(f"{role} | {dept}")

    # 2. Interpretation Engine
    st.markdown("---")
    st.subheader("🤖 AI Interpretation")
    
    metrics = extract_metrics(data)
    highs, lows = generate_interpretation(metrics)
    
    if highs:
        st.success(f"**Strengths:** Performing exceptionally well in: {', '.join(highs)}.")
    if lows:
        st.warning(f"**Attention Needed:** Improvement plans recommended for: {', '.join(lows)}.")
    if not highs and not lows:
        st.info("Performance is steady. No extreme outliers detected.")

    # 3. Metrics Grid
    st.markdown("### Key Metrics")
    
    # Create dynamic columns for metrics
    m_keys = list(metrics.keys())
    
    # Chunk metrics into rows of 4
    for i in range(0, len(m_keys), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(m_keys):
                key = m_keys[i + j]
                val = metrics[key]
                
                # Format value nicely
                delta = None
                display_val = f"{val}"
                
                # Heuristic for percentages
                if isinstance(val, float) and val <= 1.0:
                    display_val = f"{val:.1%}"
                    if val > 0.8: delta = "High"
                elif val > 1000:
                    display_val = f"{val:,.0f}"
                
                with cols[j]:
                    st.metric(label=key.replace("_", " ").title(), value=display_val, delta=delta)

    # 4. Tables / Lists (Subordinates or Logs)
    st.markdown("---")
    list_key = None
    for k, v in data.items():
        if isinstance(v, list) and len(v) > 0:
            list_key = k
            break
            
    if list_key:
        st.subheader(f"📋 {list_key.title()}")
        # Convert list of dicts to DataFrame for nice display
        if isinstance(data[list_key][0], dict):
            df = pd.DataFrame(data[list_key])
            st.dataframe(df, use_container_width=True)
        else:
            st.write(data[list_key])

    # 5. Raw Data
    with st.expander("View Raw Database Output"):
        st.json(data)
        
else:
    st.warning("No data found or connection failed.")
