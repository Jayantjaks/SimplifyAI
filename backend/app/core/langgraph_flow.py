"""
LangGraph AI pipeline for document simplification.

Flow:
  classify → simplify → highlight → summarize ──┐
                                                 ├─ (hi) → translate → END
                                                 └─ (en)            → END
"""
import json
import re
from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from app.config import get_settings

settings = get_settings()
import sys
print(f"[FLOW-LOADED] langgraph_flow.py imported fresh, ai_provider={settings.ai_provider}", flush=True)
sys.stderr.write(f"[FLOW-LOADED-ERR] ai_provider={settings.ai_provider}\n")
sys.stderr.flush()


# ── LLM Factory ────────────────────────────────────────────────────────────

def _get_llm():
    """Return the configured LLM (Groq, Google Gemini, or OpenAI)."""
    import os
    s = get_settings()
    env_provider = os.environ.get("AI_PROVIDER", "(not in os.environ)")
    msg = f"[LLM] os={env_provider} | settings={s.ai_provider} | groq_key={s.groq_api_key[:6] if s.groq_api_key else 'empty'}"
    print(msg, flush=True)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

    if s.ai_provider == "groq":
        from langchain_groq import ChatGroq
        sys.stderr.write(f"[LLM] --> ChatGroq model={s.groq_model}\n")
        sys.stderr.flush()
        return ChatGroq(
            model=s.groq_model,
            api_key=s.groq_api_key,
            temperature=0.3,
        )

    if s.ai_provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=s.openai_model,
            api_key=s.openai_api_key,
            temperature=0.3,
        )

    if s.ai_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=s.gemini_model,
            google_api_key=s.google_api_key,
            temperature=0.3,
        )

    raise ValueError(
        f"Unknown ai_provider='{s.ai_provider}'. "
        f"Supported values: groq, openai, google"
    )


# ── State Definition ───────────────────────────────────────────────────────

class DocumentState(TypedDict):
    original_text: str
    document_type: str           # medical | legal | insurance | other
    simplified_text: str
    highlights: dict             # {important_terms, risks_warnings, key_clauses}
    summary: str
    target_language: str         # en | hi
    translated_text: Optional[str]
    error: Optional[str]


# ── Node Functions ─────────────────────────────────────────────────────────

def classify_node(state: DocumentState) -> DocumentState:
    """Identify whether the document is medical, legal, insurance, or other."""
    llm = _get_llm()
    prompt = f"""You are a document classifier.
Read the beginning of the document below and classify it into ONE of these categories:
  - medical
  - legal
  - insurance
  - other

Reply with ONLY the category word, nothing else.

Document (first 1000 chars):
{state["original_text"][:1000]}
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        doc_type = response.content.strip().lower()
        if doc_type not in {"medical", "legal", "insurance", "other"}:
            doc_type = "other"
        return {**state, "document_type": doc_type}
    except Exception as exc:
        return {**state, "document_type": "other", "error": str(exc)}


def simplify_node(state: DocumentState) -> DocumentState:
    """Rewrite the document in simple, plain English."""
    llm = _get_llm()
    doc_type = state.get("document_type", "other")

    type_context = {
        "medical": "a medical report or prescription",
        "legal": "a legal agreement or contract",
        "insurance": "an insurance policy or claim document",
        "other": "a complex document",
    }.get(doc_type, "a complex document")

    prompt = f"""You are a helpful assistant that simplifies complex documents.

The following is {type_context}. Rewrite it in simple, plain English so that
any ordinary person (with no medical or legal background) can understand it.

Rules:
- Use short sentences.
- Avoid jargon; if you must use a technical term, explain it in brackets.
- Preserve ALL important information – do not omit facts.
- Write in second person ("you") to make it personal and direct.

Document:
{state["original_text"]}

Simplified version:"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "simplified_text": response.content.strip()}
    except Exception as exc:
        return {**state, "simplified_text": "", "error": str(exc)}


def highlight_node(state: DocumentState) -> DocumentState:
    """Extract important terms, risks/warnings, and key clauses as structured data."""
    llm = _get_llm()
    prompt = f"""Analyze the document below and extract three categories of information.
Return ONLY valid JSON (no markdown, no backticks) in exactly this structure:

{{
  "important_terms": ["term1", "term2"],
  "risks_warnings": ["risk or warning sentence 1", "risk or warning sentence 2"],
  "key_clauses": ["key clause or action item 1", "key clause or action item 2"]
}}

Guidelines:
- important_terms: Medical/legal/insurance terms that the user must know (max 10).
- risks_warnings: Any risk, side effect, penalty, or warning mentioned (max 10).
- key_clauses: Important actions, deadlines, conditions, or obligations (max 10).

Document:
{state["simplified_text"] or state["original_text"]}
"""
    default_highlights = {
        "important_terms": [],
        "risks_warnings": [],
        "key_clauses": [],
    }
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        # Strip accidental markdown code fences
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        highlights = json.loads(raw)
        # Ensure all keys exist
        for key in default_highlights:
            highlights.setdefault(key, [])
        return {**state, "highlights": highlights}
    except Exception as exc:
        return {**state, "highlights": default_highlights, "error": str(exc)}


def summarize_node(state: DocumentState) -> DocumentState:
    """Generate a concise bullet-point summary."""
    llm = _get_llm()
    prompt = f"""Create a clear, concise bullet-point summary of this document.

Rules:
- Use 5 to 8 bullet points maximum.
- Each bullet point should be one short sentence.
- Start each bullet with "• ".
- Focus on the most important facts, actions, or conclusions.

Document:
{state["simplified_text"] or state["original_text"]}

Summary:"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "summary": response.content.strip()}
    except Exception as exc:
        return {**state, "summary": "", "error": str(exc)}


def translate_node(state: DocumentState) -> DocumentState:
    """Translate the simplified text to Hindi."""
    llm = _get_llm()
    text_to_translate = state.get("simplified_text") or state.get("original_text", "")
    prompt = f"""Translate the following English text to Hindi.
Keep the meaning accurate and use simple, everyday Hindi (not overly formal).

Text:
{text_to_translate}

Hindi translation:"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "translated_text": response.content.strip()}
    except Exception as exc:
        return {**state, "translated_text": None, "error": str(exc)}


# ── Routing ────────────────────────────────────────────────────────────────

def _route_after_summarize(state: DocumentState) -> str:
    """After summarizing, translate to Hindi if requested."""
    if state.get("target_language") == "hi":
        return "translate"
    return END


# ── Build Graph ────────────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    graph = StateGraph(DocumentState)

    graph.add_node("classify", classify_node)
    graph.add_node("simplify", simplify_node)
    graph.add_node("highlight", highlight_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("translate", translate_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "simplify")
    graph.add_edge("simplify", "highlight")
    graph.add_edge("highlight", "summarize")
    graph.add_conditional_edges(
        "summarize",
        _route_after_summarize,
        {"translate": "translate", END: END},
    )
    graph.add_edge("translate", END)

    return graph.compile()


# Compiled pipeline – import and call .invoke(state) directly
pipeline = build_pipeline()


def run_pipeline(original_text: str, target_language: str = "en") -> DocumentState:
    """
    Run the full document processing pipeline.

    Args:
        original_text:   Raw extracted text from the document.
        target_language: Output language – 'en' (default) or 'hi' (Hindi).

    Returns:
        Final DocumentState dict with all processed fields.
    """
    initial_state: DocumentState = {
        "original_text": original_text,
        "document_type": "other",
        "simplified_text": "",
        "highlights": {},
        "summary": "",
        "target_language": target_language,
        "translated_text": None,
        "error": None,
    }
    return pipeline.invoke(initial_state)
