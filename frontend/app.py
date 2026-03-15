"""
SimplifyAI – Streamlit Frontend

Run:
    streamlit run frontend/app.py
"""
import requests
import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="SimplifyAI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-title  { font-size: 2.4rem; font-weight: 700; color: #1E3A5F; }
    .sub-title   { font-size: 1.1rem; color: #555; margin-bottom: 1.5rem; }
    .doc-badge   { display: inline-block; padding: 2px 10px; border-radius: 12px;
                   font-size: 0.8rem; font-weight: 600; }
    .badge-medical    { background: #d4edda; color: #155724; }
    .badge-legal      { background: #cce5ff; color: #004085; }
    .badge-insurance  { background: #fff3cd; color: #856404; }
    .badge-other      { background: #e2e3e5; color: #383d41; }
    .risk-item   { background: #fff5f5; border-left: 4px solid #e74c3c;
                   padding: 6px 12px; border-radius: 4px; margin: 4px 0; }
    .term-item   { background: #f0f7ff; border-left: 4px solid #3498db;
                   padding: 6px 12px; border-radius: 4px; margin: 4px 0; }
    .clause-item { background: #f0fff4; border-left: 4px solid #2ecc71;
                   padding: 6px 12px; border-radius: 4px; margin: 4px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hospital.png", width=64)
    st.markdown("## SimplifyAI")
    st.markdown(
        "Upload any **medical** or **legal** document and get a plain-English explanation in seconds."
    )
    st.divider()

    page = st.radio(
        "Navigate",
        ["Simplify Document", "Document History"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Powered by LangChain + LangGraph + Google Gemini")


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


def badge(doc_type: str) -> str:
    return f'<span class="doc-badge badge-{doc_type}">{doc_type.upper()}</span>'


def render_highlights(highlights: dict):
    terms = highlights.get("important_terms", [])
    risks = highlights.get("risks_warnings", [])
    clauses = highlights.get("key_clauses", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Important Terms**")
        if terms:
            for t in terms:
                st.markdown(f'<div class="term-item">📌 {t}</div>', unsafe_allow_html=True)
        else:
            st.caption("None found")

    with col2:
        st.markdown("**Risks & Warnings**")
        if risks:
            for r in risks:
                st.markdown(f'<div class="risk-item">⚠️ {r}</div>', unsafe_allow_html=True)
        else:
            st.caption("No risks found")

    with col3:
        st.markdown("**Key Clauses / Actions**")
        if clauses:
            for c in clauses:
                st.markdown(f'<div class="clause-item">✅ {c}</div>', unsafe_allow_html=True)
        else:
            st.caption("None found")


def render_result(data: dict):
    st.success("Document processed successfully!")

    # Document type badge
    doc_type = data.get("document_type", "other")
    st.markdown(
        f"**Document Type:** {badge(doc_type)}",
        unsafe_allow_html=True,
    )
    st.divider()

    # Summary
    st.subheader("Quick Summary")
    summary = data.get("summary", "")
    if summary:
        st.markdown(summary)
    else:
        st.caption("No summary available.")

    # Highlights
    st.subheader("Key Highlights")
    render_highlights(data.get("highlights", {}))

    # Simplified text
    st.subheader("Simplified Explanation")
    simplified = data.get("simplified_text", "")
    if simplified:
        st.write(simplified)
    else:
        st.caption("No simplified text available.")

    # Hindi translation
    translated = data.get("translated_text")
    if translated:
        st.subheader("Hindi Translation (हिंदी अनुवाद)")
        st.write(translated)


# ── Page: Simplify Document ─────────────────────────────────────────────────

if page == "Simplify Document":
    st.markdown('<p class="main-title">🏥 SimplifyAI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">Upload a medical or legal document — get a simple explanation instantly.</p>',
        unsafe_allow_html=True,
    )

    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "tiff", "bmp"],
            help="Supported formats: PDF, DOCX, PNG, JPG, TIFF, BMP",
        )
        language = st.selectbox(
            "Output language",
            options=[("English", "en"), ("Hindi (हिंदी)", "hi")],
            format_func=lambda x: x[0],
        )
        submitted = st.form_submit_button("Simplify Document", type="primary", use_container_width=True)

    if submitted:
        if not uploaded_file:
            st.warning("Please upload a file first.")
        else:
            with st.spinner("Extracting text and running AI analysis... this may take 15-30 seconds."):
                try:
                    result = call_upload(
                        uploaded_file.getvalue(),
                        uploaded_file.name,
                        language[1],
                    )
                    render_result(result)
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend. Make sure the API server is running on port 8000.")
                except requests.exceptions.HTTPError as e:
                    detail = e.response.json().get("detail", str(e))
                    st.error(f"Error: {detail}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")


# ── Page: Document History ──────────────────────────────────────────────────

elif page == "Document History":
    st.markdown('<p class="main-title">📂 Document History</p>', unsafe_allow_html=True)
    st.caption("All previously processed documents.")

    try:
        docs = call_list()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend. Make sure the API server is running on port 8000.")
        docs = []
    except Exception as e:
        st.error(f"Error loading history: {e}")
        docs = []

    if not docs:
        st.info("No documents processed yet. Go to **Simplify Document** to get started.")
    else:
        for doc in docs:
            status_icon = "✅" if doc["status"] == "done" else ("❌" if doc["status"] == "error" else "⏳")
            with st.expander(
                f"{status_icon} {doc['filename']} — {doc['document_type'].upper()} — {doc['created_at'][:10]}"
            ):
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("View Details", key=f"view_{doc['id']}"):
                        st.session_state[f"detail_{doc['id']}"] = True
                    if st.button("Delete", key=f"del_{doc['id']}", type="secondary"):
                        call_delete(doc["id"])
                        st.rerun()

                if st.session_state.get(f"detail_{doc['id']}"):
                    with st.spinner("Loading..."):
                        try:
                            detail = call_get(doc["id"])
                            render_result(detail)
                        except Exception as e:
                            st.error(str(e))
