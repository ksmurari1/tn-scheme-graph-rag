from __future__ import annotations

import streamlit as st

from src.scheme_graph.config import settings
from src.scheme_graph.graph_retriever import SchemeGraphService
from src.scheme_graph.visualization import graph_html
from src.scheme_graph.llm_service import answer_question
from src.scheme_graph.guardrails import check_question


st.set_page_config(
    page_title="SmartAgri AI | Tamil Nadu Scheme Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep theme styling in .streamlit/config.toml; this CSS handles layout and cards.
st.markdown(
    """
    <style>
    :root {
      --navy: #123A70;
      --blue: #2478D4;
      --sky: #EAF5FF;
      --line: #D7E8F8;
      --ink: #17324D;
      --muted: #526B84;
    }

    /* Main application */
    .stApp {
      background: linear-gradient(180deg, #F7FBFF 0%, #FFFFFF 48%, #F5FAFF 100%);
      color: var(--ink);
      font-family: Arial, sans-serif;
    }

    .block-container {
      padding-top: 1.15rem;
      padding-bottom: 2.2rem;
      max-width: 1600px;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #EAF5FF 0%, #F7FBFF 100%);
      border-right: 1px solid var(--line);
      font-family: Arial, sans-serif;
    }

    /* Sidebar: force readable black text */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
      color: #000000 !important;
      font-family: Arial, sans-serif !important;
      font-size: 15px !important;
      opacity: 1 !important;
    }

    /* Sidebar headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
      color: #000000 !important;
      font-family: Arial, sans-serif !important;
      font-weight: 700 !important;
    }

    /* Sidebar radio buttons */
    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label p {
      color: #000000 !important;
      font-size: 15px !important;
    }

    /* Sidebar select boxes */
    [data-testid="stSidebar"] [data-baseweb="select"] * {
      color: #000000 !important;
      font-family: Arial, sans-serif !important;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
      background: #175FA9 !important;
      color: #FFFFFF !important;
      border-color: #175FA9 !important;
    }

    .stButton > button {
      border-radius: 11px;
      font-weight: 700;
      font-family: Arial, sans-serif;
    }

    /* Hero banner */
    .hero {
      padding: 1.45rem 1.6rem;
      border-radius: 22px;
      color: white;
      background: linear-gradient(115deg, #123A70 0%, #2478D4 58%, #68B9F5 100%);
      box-shadow: 0 12px 34px rgba(25,91,160,.16);
      margin-bottom: 1.1rem;
    }

    .hero h1 {
      margin: 0;
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -.03em;
      color: white;
    }

    .hero p {
      margin: .4rem 0 0 0;
      color: #F0F8FF;
      font-size: 1rem;
    }

    .eyebrow {
      text-transform: uppercase;
      letter-spacing: .13em;
      font-size: .72rem;
      font-weight: 800;
      color: #D9EEFF;
    }

    /* Content panels and scheme cards */
    .panel,
    .scheme-card {
      background: #FFFFFF;
      border: 1px solid #D7E8F8;
      border-radius: 16px;
      padding: 1rem 1.1rem;
      box-shadow: 0 4px 18px rgba(28,92,150,.045);
      margin-bottom: .75rem;
    }

    .scheme-title {
      color: #123A70;
      font-weight: 750;
      font-size: 1.05rem;
      margin-bottom: .45rem;
    }

    .chip {
      display: inline-block;
      padding: .22rem .58rem;
      margin: .12rem .22rem .3rem 0;
      border-radius: 999px;
      font-size: .78rem;
      font-weight: 700;
      border: 1px solid transparent;
    }

    .chip-blue {
      color: #164E8A;
      background: #EAF4FF;
      border-color: #C9E2FA;
    }

    .chip-green {
      color: #17633A;
      background: #E9F8EF;
      border-color: #BDE7CA;
    }

    .chip-amber {
      color: #7A4B00;
      background: #FFF4D6;
      border-color: #F0D38B;
    }

    .chip-grey {
      color: #4B5563;
      background: #F0F2F5;
      border-color: #D8DDE5;
    }

    .muted {
      color: #405A74;
      font-size: .9rem;
    }

    /* Main page headings */
    h1, h2, h3 {
      color: #123A70;
      letter-spacing: -.02em;
    }

    h2 {
      font-size: 1.65rem;
    }

    h3 {
      font-size: 1.3rem;
    }

    /* Chat messages */
    div[data-testid="stChatMessage"] {
      border: 1px solid #DCEAF7;
      border-radius: 14px;
      padding: .75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _safe_text(value: object, fallback: str = "Not available in retrieved record") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _render_scheme_cards(evidence: list[dict], language: str) -> None:
    if not evidence:
        st.info("No matching scheme records were retrieved. Try a crop, scheme name, or department.")
        return

    st.markdown("#### Retrieved scheme records")
    st.caption(
        "These cards come directly from Neo4j retrieval. The AI explanation is shown separately."
        if language == "English"
        else "இந்த அட்டைகள் Neo4j-இல் இருந்து பெறப்பட்ட பதிவுகளை காட்டுகின்றன. AI விளக்கம் தனியாக காட்டப்படும்."
    )

    for item in evidence:
        name = _safe_text(item.get("matched"), "Unnamed scheme")
        active = str(item.get("active") or "").strip().lower()
        status_html = (
            '<span class="chip chip-green">Source flag: active</span>'
            if active == "yes"
            else '<span class="chip chip-amber">Marked inactive in source data</span>'
            if active == "no"
            else '<span class="chip chip-grey">Status not specified</span>'
        )
        year = _safe_text(item.get("year"), "Year not specified")
        department = _safe_text(item.get("department"), "Department not specified")
        score = item.get("score")

        with st.container(border=True):
            st.markdown(f'<div class="scheme-title">{name}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="chip chip-blue">{department}</span>'
                f'<span class="chip chip-blue">{year}</span>{status_html}',
                unsafe_allow_html=True,
            )
            if score is not None:
                st.caption(f"Retrieval ranking score: {score} (not a confidence percentage)")
            with st.expander("Why this record matched / View retrieved evidence"):
                st.text(_safe_text(item.get("evidence")))
            source_url = item.get("source_url") or item.get("url")
            if source_url:
                st.markdown(f"[Official scheme data source]({source_url})")
            else:
                st.caption("No source URL was recorded for this scheme.")


def _render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    st.markdown("**Official source data**")
    for source in sources:
        title = _safe_text(source.get("title"), "Official scheme record")
        metadata = " · ".join(
            str(v) for v in [source.get("department"), source.get("year")] if v
        )
        url = source.get("url")
        if url:
            st.markdown(f"- **{title}**" + (f" — {metadata}" if metadata else "") + f" · [Open source data]({url})")
        else:
            st.markdown(f"- **{title}**" + (f" — {metadata}" if metadata else ""))


with st.sidebar:
    st.markdown("## 🌱 SmartAgri AI")
    st.caption("Tamil Nadu Scheme Intelligence")
    st.divider()
    language = st.selectbox("Response language", ["English", "Tamil"], index=0)
    view = st.radio(
        "Workspace",
        ["Scheme Explorer", "Ask SmartAgri AI", "Source & system status"],
    )
    st.divider()
    st.markdown("**Knowledge source**")
    st.caption("Official Tamil Nadu agriculture scheme data")
    st.caption("Historical records may be inactive. Verify current availability with the relevant department.")
    st.divider()
    st.caption("Evidence-led scheme discovery")

st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">Tamil Nadu • Public scheme discovery</div>
      <h1>SmartAgri AI</h1>
      <p>Explore government schemes through connected knowledge — with source-aware answers in {language}.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

neo4j_configured = bool(
    settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password
)
openai_configured = bool(settings.openai_api_key)

if not neo4j_configured:
    st.warning("Neo4j is not configured. Check NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD in your local .env.")
if not openai_configured:
    st.info("OPENAI_API_KEY is not configured. Graph inspection can work, but AI answers require the key.")

service = SchemeGraphService()

if view == "Source & system status":
    st.subheader("System readiness")
    c1, c2, c3 = st.columns(3)
    c1.metric("Neo4j settings", "Configured" if neo4j_configured else "Missing")
    c2.metric("OpenAI key", "Configured" if openai_configured else "Missing")
    c3.metric("Configured source URLs", len(settings.source_urls))
    st.markdown("### Current data snapshot")
    try:
        overview = service.get_overview()
        a, b, c = st.columns(3)
        a.metric("Departments", overview.get("departments", 0))
        b.metric("Schemes", overview.get("schemes", 0))
        c.metric("Relationships", overview.get("relationships", 0))
    except Exception as exc:
        st.warning(f"Could not read graph statistics: {exc}")
    st.markdown("### Data ingestion")
    st.write("Inspect source redirects and links before ingesting new content.")
    st.code("python scripts\\inspect_source.py\npython scripts\\ingest_schemes.py")
    st.markdown("### Safety")
    st.write("Retrieval uses read-only graph queries. Eligibility, benefits and current availability must be verified against official evidence.")

elif view == "Scheme Explorer":
    st.subheader("Explore the knowledge graph")
    st.caption("Browse connected departments and scheme records from Neo4j.")
    left, right = st.columns([1.5, 1])
    with left:
        if st.button("Load graph overview", type="primary", use_container_width=True):
            try:
                st.session_state["overview"] = service.get_overview()
                st.success("Graph overview loaded.")
            except Exception as exc:
                st.error(f"Could not connect to Neo4j: {exc}")

    overview = st.session_state.get("overview")
    if overview:
        a, b, c = st.columns(3)
        a.metric("Departments", overview.get("departments", 0))
        b.metric("Schemes", overview.get("schemes", 0))
        c.metric("Relationships", overview.get("relationships", 0))
        st.markdown("### Connected scheme map")
        graph_limit = st.slider("Maximum relationships to display", min_value=20, max_value=123, value=100, step=10)
        try:
            elements = service.get_graph(limit=graph_limit)
            if elements.get("nodes"):
                st.components.v1.html(
                    graph_html(elements["nodes"], elements["edges"]),
                    height=650,
                    scrolling=False,
                )
            else:
                st.info("The graph is empty.")
        except Exception as exc:
            st.error(f"Graph visualization could not be loaded: {exc}")
    else:
        st.markdown(
            """
            <div class="panel">
              <h3>From source data to connected knowledge</h3>
              <p>Each scheme is connected to its department. Scheme descriptions, eligibility and required documents are shown when present in the retrieved record.</p>
              <p class="muted">Select <b>Load graph overview</b> to inspect the current Neo4j graph.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel">
              <h3>Graph design principles</h3>
              <ul>
                <li>Visible source provenance</li>
                <li>Relationship-first exploration</li>
                <li>Evidence-led answers</li>
                <li>Read-only graph retrieval</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Quick Cypher")
        st.code("MATCH (n) RETURN labels(n), count(*) AS total", language="cypher")

elif view == "Ask SmartAgri AI":
    st.subheader("Ask about government schemes")
    st.caption("Retrieved scheme records are shown separately from the AI explanation.")

    suggestions = [
        "Which schemes mention cotton, and what documents do they require?",
        "Which schemes mention paddy?",
        "What eligibility information is available for cotton farmers?",
    ]
    if language == "Tamil":
        suggestions = [
            "பருத்தி தொடர்பான திட்டங்கள் மற்றும் தேவையான ஆவணங்கள் என்ன?",
            "நெல் தொடர்பான திட்டங்கள் உள்ளனவா?",
            "பருத்தி விவசாயிகளுக்கான தகுதி விவரங்கள் என்ன?",
        ]

    st.markdown("**Try a suggested question**")
    suggestion_cols = st.columns(len(suggestions))
    for idx, suggestion in enumerate(suggestions):
        if suggestion_cols[idx].button(
            suggestion,
            key=f"suggest_{language}_{idx}",
            use_container_width=True,
        ):
            st.session_state["pending_prompt"] = suggestion
            st.rerun()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for idx, msg in enumerate(st.session_state.chat_history):
        avatar = "👩‍🌾" if msg["role"] == "user" else "🌱"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("evidence"):
                with st.expander("Why this answer? — Retrieved scheme records"):
                    _render_scheme_cards(msg["evidence"], msg.get("language", "English"))

                graph_key = msg.get("graph_state_key") or f"query_graph_{idx}"
                if st.button(
                    "Show graph for this question",
                    key=f"show_query_graph_{idx}",
                    use_container_width=True,
                ):
                    try:
                        st.session_state[graph_key] = service.get_query_graph(
                            msg["evidence"], msg.get("question", "")
                        )
                    except Exception as exc:
                        st.error(f"Could not build query graph: {exc}")

                graph_data = st.session_state.get(graph_key)
                if graph_data and graph_data.get("nodes"):
                    st.markdown("#### Graph for this question")
                    st.caption(
                        "Solid arrows show stored Department → Scheme relationships. "
                        "Dashed query links show which schemes were retrieved for this question."
                    )
                    st.components.v1.html(
                        graph_html(graph_data["nodes"], graph_data["edges"]),
                        height=480,
                        scrolling=False,
                    )

            _render_sources(msg.get("sources", []))
            if msg["role"] == "assistant" and msg.get("feedback_key"):
                feedback_value = st.session_state.get(msg["feedback_key"])
                if feedback_value is None:
                    try:
                        st.feedback("thumbs", key=msg["feedback_key"])
                    except Exception:
                        st.caption("Feedback controls require a recent Streamlit version.")

    prompt = st.chat_input(
        "Ask about schemes, eligibility, benefits or documents…"
        if language == "English"
        else "திட்டங்கள், தகுதி அல்லது ஆவணங்கள் பற்றி கேளுங்கள்…"
    )
    if not prompt:
        prompt = st.session_state.pop("pending_prompt", None)

    if prompt:
        with st.chat_message("user", avatar="👩‍🌾"):
            st.markdown(prompt)

        allowed, reason = check_question(prompt)
        reply = ""
        evidence = []
        sources = []

        if not allowed:
            reply = reason
        else:
            try:
                with st.status("Working through your question…", expanded=True) as status:
                    st.write("1. Safety check completed.")
                    st.write("2. Searching the Neo4j scheme graph…")
                    evidence = service.retrieve(prompt, limit=8)
                    st.write(f"3. Retrieved {len(evidence)} scheme record(s).")
                    st.write("4. Preparing an evidence-grounded answer…")
                    reply, sources = answer_question(prompt, evidence, language=language)
                    status.update(label="Answer ready", state="complete", expanded=False)
            except Exception as exc:
                reply = "I couldn't complete the graph-backed answer. Check Neo4j/OpenAI configuration and try again."
                st.error(f"Technical detail: {exc}")

        # Predict the assistant message index before storing it, so the graph
        # button keeps the same key after Streamlit reruns.
        assistant_idx = len(st.session_state.chat_history) + 1
        graph_state_key = f"query_graph_{assistant_idx}"
        feedback_key = f"feedback_{len(st.session_state.chat_history)}"

        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
        })
        assistant_message = {
            "role": "assistant",
            "content": reply,
            "question": prompt,
            "sources": sources,
            "evidence": evidence,
            "language": language,
            "feedback_key": feedback_key,
            "graph_state_key": graph_state_key,
        }
        st.session_state.chat_history.append(assistant_message)

        with st.chat_message("assistant", avatar="🌱"):
            st.markdown(reply)
            if evidence:
                with st.expander("Why this answer? — Retrieved scheme records", expanded=True):
                    _render_scheme_cards(evidence, language)

                if st.button(
                    "Show graph for this question",
                    key=f"show_query_graph_{assistant_idx}",
                    use_container_width=True,
                ):
                    try:
                        st.session_state[graph_state_key] = service.get_query_graph(
                            evidence, prompt
                        )
                    except Exception as exc:
                        st.error(f"Could not build query graph: {exc}")

                graph_data = st.session_state.get(graph_state_key)
                if graph_data and graph_data.get("nodes"):
                    st.markdown("#### Graph for this question")
                    st.caption(
                        "Solid arrows show stored Department → Scheme relationships. "
                        "Dashed query links show which schemes were retrieved for this question."
                    )
                    st.components.v1.html(
                        graph_html(graph_data["nodes"], graph_data["edges"]),
                        height=480,
                        scrolling=False,
                    )
            _render_sources(sources)

            try:
                st.feedback("thumbs", key=feedback_key)
            except Exception:
                st.caption("Upgrade Streamlit to enable answer feedback.")
