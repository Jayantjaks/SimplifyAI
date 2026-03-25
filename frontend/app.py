"""
SimplifyAI – Streamlit Frontend

Run:
    streamlit run frontend/app.py
"""
import requests
import streamlit as st
import time

# ── Config ─────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="SimplifyAI — Document Simplifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ─────────────────────────────────────── */
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* ── Hero ────────────────────────────────────────── */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
}
.hero-icon {
    font-size: 4rem;
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}
.hero-sub {
    font-size: 1.15rem;
    color: #a0aec0;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Glass cards ────────────────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: transform 0.3s, box-shadow 0.3s;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
}

/* ── Section headers ────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}
.section-icon {
    font-size: 1.6rem;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
}

/* ── Badges ─────────────────────────────────────── */
.doc-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.badge-medical {
    background: linear-gradient(135deg, #43e97b, #38f9d7);
    color: #064e3b;
}
.badge-legal {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
}
.badge-insurance {
    background: linear-gradient(135deg, #f6d365, #fda085);
    color: #7c2d12;
}
.badge-other {
    background: linear-gradient(135deg, #a8edea, #fed6e3);
    color: #374151;
}

/* ── Highlight cards ────────────────────────────── */
.highlight-card {
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    transition: transform 0.2s;
}
.highlight-card:hover { transform: scale(1.01); }

.term-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
    border-left: 4px solid #818cf8;
}
.risk-card {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
    border-left: 4px solid #f87171;
}
.clause-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
    border-left: 4px solid #34d399;
}
.highlight-text {
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.5;
    margin: 0;
}

/* ── Stats row ──────────────────────────────────── */
.stat-box {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* ── Upload area ────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.03);
    border: 2px dashed rgba(102, 126, 234, 0.4);
    border-radius: 16px;
    padding: 1rem;
    transition: border-color 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(102, 126, 234, 0.8);
}

/* ── Buttons ────────────────────────────────────── */
.stButton > button[kind="primary"],
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5) !important;
}

/* ── Sidebar ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #e2e8f0;
}
[data-testid="stSidebar"] .stMarkdown p, 
[data-testid="stSidebar"] .stMarkdown li {
    color: #a0aec0;
}

/* ── History cards ──────────────────────────────── */
.history-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s;
}
.history-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(102, 126, 234, 0.3);
}
.history-name {
    color: #e2e8f0;
    font-weight: 600;
    font-size: 1rem;
}
.history-meta {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: 4px;
}

/* ── Summary box ────────────────────────────────── */
.summary-box {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    color: #e2e8f0;
    line-height: 1.8;
}

/* ── Simplified text ────────────────────────────── */
.simplified-box {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.8rem;
    color: #cbd5e1;
    line-height: 1.9;
    font-size: 0.95rem;
}

/* ── Translation box ────────────────────────────── */
.translation-box {
    background: linear-gradient(135deg, rgba(249, 115, 22, 0.1), rgba(234, 179, 8, 0.1));
    border: 1px solid rgba(249, 115, 22, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    color: #e2e8f0;
    line-height: 1.9;
}

/* ── Progress animation ─────────────────────────── */
.processing-text {
    color: #a0aec0;
    font-size: 1rem;
    text-align: center;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* ── Empty state ────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 3rem;
    color: #64748b;
}
.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}
.empty-state-text {
    font-size: 1.1rem;
    color: #94a3b8;
}

/* ── Misc ───────────────────────────────────────── */
.stDivider { border-color: rgba(255,255,255,0.06) !important; }
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">🧠</div>
        <h2 style="margin:0; background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 1.6rem;">SimplifyAI</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">
            AI Document Simplifier
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate",
        ["🔬 Simplify Document", "📂 Document History"],
        label_visibility="collapsed",
    )

    st.divider()

    # ── Features list ──
    st.markdown("""
    <div style="padding: 0.5rem;">
        <p style="color:#94a3b8; font-size:0.78rem; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.8rem;">Features</p>
        <div style="color:#cbd5e1; font-size:0.88rem; line-height:2.2;">
            📄 PDF, DOCX & Image support<br>
            🏷️ Auto document classification<br>
            ✍️ Plain English rewriting<br>
            ⚡ Key terms & risk extraction<br>
            📝 Bullet-point summaries<br>
            🌐 Hindi translation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem;">
        <p style="color:#475569; font-size:0.72rem;">
            Powered by LangChain + LangGraph + Groq AI
        </p>
    </div>
    """, unsafe_allow_html=True)


# ── Helper functions ────────────────────────────────────────────────────────

def call_upload(file_bytes: bytes, filename: str, language: str) -> dict:
    resp = requests.post(
        f"{API_BASE}/upload",
        files={"file": (filename, file_bytes)},
        data={"target_language": language},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def call_list() -> list:
    resp = requests.get(f"{API_BASE}/documents", timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_get(doc_id: int) -> dict:
    resp = requests.get(f"{API_BASE}/documents/{doc_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def call_delete(doc_id: int):
    requests.delete(f"{API_BASE}/documents/{doc_id}", timeout=10)


def badge_html(doc_type: str) -> str:
    return f'<span class="doc-badge badge-{doc_type}">{doc_type.upper()}</span>'


def render_highlights(highlights: dict):
    terms = highlights.get("important_terms", [])
    risks = highlights.get("risks_warnings", [])
    clauses = highlights.get("key_clauses", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📌</span>
            <h3 class="section-title" style="font-size:1.1rem;">Important Terms</h3>
        </div>
        """, unsafe_allow_html=True)
        if terms:
            for t in terms:
                st.markdown(f'<div class="highlight-card term-card"><p class="highlight-text">{t}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b; font-size:0.9rem;">None found</p>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">⚠️</span>
            <h3 class="section-title" style="font-size:1.1rem;">Risks & Warnings</h3>
        </div>
        """, unsafe_allow_html=True)
        if risks:
            for r in risks:
                st.markdown(f'<div class="highlight-card risk-card"><p class="highlight-text">{r}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b; font-size:0.9rem;">No risks found</p>', unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">✅</span>
            <h3 class="section-title" style="font-size:1.1rem;">Key Clauses</h3>
        </div>
        """, unsafe_allow_html=True)
        if clauses:
            for c in clauses:
                st.markdown(f'<div class="highlight-card clause-card"><p class="highlight-text">{c}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#64748b; font-size:0.9rem;">None found</p>', unsafe_allow_html=True)


def render_result(data: dict):
    # ── Success banner ──
    doc_type = data.get("document_type", "other")
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:1.5rem;">
        <div style="font-size:2.5rem; margin-bottom:0.5rem;">✨</div>
        <h3 style="color:#e2e8f0; margin:0 0 0.5rem;">Document Processed Successfully</h3>
        <p style="color:#94a3b8; margin-bottom:1rem;">Your document has been analyzed and simplified</p>
        {badge_html(doc_type)}
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──
    highlights = data.get("highlights", {})
    terms_count = len(highlights.get("important_terms", []))
    risks_count = len(highlights.get("risks_warnings", []))
    clauses_count = len(highlights.get("key_clauses", []))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{doc_type[0].upper()}</div>
            <div class="stat-label">Doc Type</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{terms_count}</div>
            <div class="stat-label">Key Terms</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{risks_count}</div>
            <div class="stat-label">Risks Found</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{clauses_count}</div>
            <div class="stat-label">Key Clauses</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Summary ──
    summary = data.get("summary", "")
    if summary:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">📋</span>
            <h3 class="section-title">Quick Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Highlights ──
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🔍</span>
        <h3 class="section-title">Key Highlights</h3>
    </div>
    """, unsafe_allow_html=True)
    render_highlights(highlights)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Simplified text ──
    simplified = data.get("simplified_text", "")
    if simplified:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">✍️</span>
            <h3 class="section-title">Simplified Explanation</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="simplified-box">{simplified}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Hindi translation ──
    translated = data.get("translated_text")
    if translated:
        st.markdown("""
        <div class="section-header">
            <span class="section-icon">🌐</span>
            <h3 class="section-title">Hindi Translation (हिंदी अनुवाद)</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="translation-box">{translated}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# ── Page: Simplify Document ────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════

if page == "🔬 Simplify Document":
    # Hero
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">🧠</div>
        <h1 class="hero-title">SimplifyAI</h1>
        <p class="hero-sub">
            Upload any complex medical, legal, or insurance document
            and get a clear, plain-English explanation in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Upload card ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📤</span>
        <h3 class="section-title">Upload Your Document</h3>
    </div>
    """, unsafe_allow_html=True)

    col_upload, col_settings = st.columns([2, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "tiff", "bmp"],
            help="Supported: PDF, DOCX, PNG, JPG, TIFF, BMP (max 10 MB)",
            label_visibility="collapsed",
        )
        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:0.5rem;
                        background:rgba(102,126,234,0.1); border-radius:10px; margin-top:0.5rem;">
                <span style="font-size:1.5rem;">📎</span>
                <div>
                    <div style="color:#e2e8f0; font-weight:600;">{uploaded_file.name}</div>
                    <div style="color:#64748b; font-size:0.82rem;">{file_size:.2f} MB</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_settings:
        st.markdown('<p style="color:#94a3b8; font-size:0.82rem; margin-bottom:0.5rem;">OUTPUT LANGUAGE</p>', unsafe_allow_html=True)
        language = st.selectbox(
            "Language",
            options=[("🇬🇧  English", "en"), ("🇮🇳  Hindi (हिंदी)", "hi")],
            format_func=lambda x: x[0],
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.button("🚀  Simplify Document", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Process ──
    if submitted:
        if not uploaded_file:
            st.warning("⚠️ Please upload a file first.")
        else:
            progress_placeholder = st.empty()
            result_placeholder = st.container()

            with progress_placeholder.container():
                st.markdown("""
                <div class="glass-card" style="text-align:center; padding:3rem;">
                    <div style="font-size:3rem; margin-bottom:1rem;" class="hero-icon">⚙️</div>
                    <h3 style="color:#e2e8f0;">Processing Your Document</h3>
                    <p class="processing-text">Extracting text and running AI analysis...</p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                steps = ["Extracting text...", "Classifying document...", "Simplifying...", "Extracting highlights...", "Generating summary..."]
                if language[1] == "hi":
                    steps.append("Translating to Hindi...")

                try:
                    # Animate progress while the API call runs
                    for i, step_text in enumerate(steps[:-1]):
                        progress_bar.progress((i + 1) * (80 // len(steps)), text=step_text)
                        time.sleep(0.3)

                    result = call_upload(
                        uploaded_file.getvalue(),
                        uploaded_file.name,
                        language[1],
                    )
                    progress_bar.progress(100, text="Done!")
                    time.sleep(0.3)

                    progress_placeholder.empty()

                    with result_placeholder:
                        render_result(result)

                except requests.exceptions.ConnectionError:
                    progress_placeholder.empty()
                    st.error("🔌 Cannot connect to the backend. Make sure the API server is running on port 8000.")
                except requests.exceptions.HTTPError as e:
                    progress_placeholder.empty()
                    detail = e.response.json().get("detail", str(e))
                    st.error(f"❌ Error: {detail}")
                except Exception as e:
                    progress_placeholder.empty()
                    st.error(f"❌ Unexpected error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ── Page: Document History ─────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📂 Document History":
    st.markdown("""
    <div class="hero-container" style="padding:1.5rem 1rem;">
        <h1 class="hero-title" style="font-size:2.2rem;">Document History</h1>
        <p class="hero-sub" style="font-size:1rem;">All previously processed documents</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        docs = call_list()
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to the backend. Make sure the API server is running on port 8000.")
        docs = []
    except Exception as e:
        st.error(f"Error loading history: {e}")
        docs = []

    if not docs:
        st.markdown("""
        <div class="glass-card empty-state">
            <div class="empty-state-icon">📭</div>
            <p class="empty-state-text">No documents processed yet.<br>
            Go to <strong>Simplify Document</strong> to get started!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Stats bar ──
        total = len(docs)
        done = sum(1 for d in docs if d["status"] == "done")
        errors = sum(1 for d in docs if d["status"] == "error")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Total Documents</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number" style="background:linear-gradient(135deg,#43e97b,#38f9d7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{done}</div>
                <div class="stat-label">Completed</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number" style="background:linear-gradient(135deg,#f87171,#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{errors}</div>
                <div class="stat-label">Errors</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for doc in docs:
            status_icon = "✅" if doc["status"] == "done" else ("❌" if doc["status"] == "error" else "⏳")
            doc_type = doc.get("document_type", "other")
            date_str = doc["created_at"][:10] if doc.get("created_at") else ""

            with st.expander(f"{status_icon}  {doc['filename']}  |  {badge_html(doc_type)}  |  {date_str}", expanded=False):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col2:
                    if st.button("🔍 View", key=f"view_{doc['id']}", use_container_width=True):
                        st.session_state[f"detail_{doc['id']}"] = True
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{doc['id']}", use_container_width=True):
                        call_delete(doc["id"])
                        st.rerun()

                if st.session_state.get(f"detail_{doc['id']}"):
                    with st.spinner("Loading document details..."):
                        try:
                            detail = call_get(doc["id"])
                            render_result(detail)
                        except Exception as e:
                            st.error(str(e))
