import streamlit as st
import time
from src.graph import run_research_pipeline

# ---------- Page config ----------
st.set_page_config(
    page_title="Agentic Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    /* Global */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #161b22 100%);
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* Hero */
    .hero {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff 0%, #a371f7 50%, #f778ba 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .hero p {
        font-size: 1.1rem;
        color: #8b949e;
        max-width: 700px;
        margin: 0 auto;
    }

    /* Agent cards */
    .agent-row {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .agent-card {
        flex: 1;
        min-width: 140px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .agent-card.active {
        border-color: #58a6ff;
        box-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        background: #1c2128;
    }
    .agent-card.done {
        border-color: #3fb950;
        background: #12261b;
    }
    .agent-card .icon { font-size: 1.5rem; }
    .agent-card .name {
        font-size: 0.85rem;
        font-weight: 600;
        color: #c9d1d9;
        margin-top: 6px;
    }
    .agent-card .status {
        font-size: 0.7rem;
        color: #8b949e;
        margin-top: 3px;
    }

    /* Report container */
    .report-container {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid #30363d;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #58a6ff 0%, #a371f7 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #161b22;
        border-radius: 8px;
        padding: 8px 16px;
        border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background: #1f6feb !important;
        border-color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "state" not in st.session_state:
    st.session_state.state = None
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "topic" not in st.session_state:
    st.session_state.topic = ""

# ---------- Hero ----------
st.markdown("""
<div class="hero">
    <h1>🔬 Agentic Research Assistant</h1>
    <p>Four specialized AI agents collaborate to research any topic and generate a cited, structured report — autonomously.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🔬 About")
    st.markdown(
        "Agentic Research Assistant turns any topic into a fully cited, "
        "structured research report — in minutes, not hours."
    )

    st.divider()

    st.markdown("### ✨ What You Get")
    st.markdown("""
    - 📄 A structured report with executive summary
    - 🔗 Real sources, properly cited
    - 🎯 Focused sub-questions explored
    - 📥 One-click download as Markdown
    """)

    st.divider()

    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific — *"AI in radiology diagnostics"* works better than *"AI"*
    - Add a year or region for sharper results
    - Ask a question format for exploratory topics
    """)

    st.divider()

    st.caption("Powered by multi-agent AI · v1.0")

# ---------- Agent status row ----------
agents = [
    ("🧠", "Planner"),
    ("🔍", "Researcher"),
    ("📊", "Analyst"),
    ("✍️", "Writer"),
]

def render_agents(current_stage):
    cards = '<div class="agent-row">'
    for i, (icon, name) in enumerate(agents, 1):
        cls = "agent-card"
        status = "Idle"
        if current_stage >= 5:
            cls += " done"; status = "Complete"
        elif current_stage == i:
            cls += " active"; status = "Running..."
        elif current_stage > i:
            cls += " done"; status = "Complete"
        cards += f'<div class="{cls}"><div class="icon">{icon}</div><div class="name">{name}</div><div class="status">{status}</div></div>'
    cards += '</div>'
    st.markdown(cards, unsafe_allow_html=True)

agent_slot = st.empty()
with agent_slot.container():
    render_agents(st.session_state.stage)

# ---------- Input ----------
col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g., The impact of AI on healthcare diagnostics",
        label_visibility="collapsed"
    )
with col2:
    start = st.button("🚀 Start Research", use_container_width=True, type="primary")

# ---------- Run ----------
if start and topic:
    st.session_state.topic = topic
    st.session_state.stage = 1
    with agent_slot.container():
        render_agents(1)

    progress = st.progress(0, text="Initializing agents...")
    status = st.empty()

    def update_progress(msg):
        if "Planner" in msg:
            st.session_state.stage = 1
        elif "Researcher" in msg:
            st.session_state.stage = 2
        elif "Analyst" in msg:
            st.session_state.stage = 3
        elif "Writer" in msg:
            st.session_state.stage = 4
        with agent_slot.container():
            render_agents(st.session_state.stage)

        pct = {1: 15, 2: 45, 3: 70, 4: 90}.get(st.session_state.stage, 0)
        progress.progress(pct, text=msg)
        status.info(msg)

    state = run_research_pipeline(topic, progress_callback=update_progress)

    st.session_state.state = state
    st.session_state.stage = 5
    progress.progress(100, text="✅ Research complete")
    with agent_slot.container():
        render_agents(5)
    status.success(f"Report generated for: **{topic}**")

# ---------- Results ----------
if st.session_state.state:
    state = st.session_state.state
    topic = st.session_state.topic

    st.markdown("---")

    # Metrics row
    m1, m2, m3 = st.columns(3)
    m1.metric("Sub-questions", len(state.sub_questions))
    m2.metric("Sources analyzed", sum(len(f.results) for f in state.findings))
    m3.metric("Errors", len(state.errors))

    # Tabs (Methodology removed)
        # Tabs
    tab1, tab2 = st.tabs(["📄 Report", "🔍 Research Scope"])

    with tab1:
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(state.final_report)
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button(
            "📥 Download Report (Markdown)",
            data=state.final_report,
            file_name=f"research_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown"
        )

    with tab2:
        st.caption("These are the sub-questions the Planner agent explored to build your report:")
        for i, sq in enumerate(state.sub_questions, 1):
            with st.expander(f"**{i}. {sq.question}**", expanded=False):
                st.caption(f"**Why this matters:** {sq.rationale}")