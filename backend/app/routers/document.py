"""
Document API routes.

POST /api/v1/upload          – upload a document and trigger AI processing
GET  /api/v1/documents       – list all processed documents
GET  /api/v1/documents/{id}  – get full details for one document
DELETE /api/v1/documents/{id} – delete a document record
"""
import json
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentListItem, DocumentResponse
from app.services.extraction import extract_text
from app.core.langgraph_flow import run_pipeline

router = APIRouter()
settings = get_settings()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp",
    "image/webp",
}


# ── Upload & Process ────────────────────────────────────────────────────────

@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document and simplify it with AI",
)
def upload_document(
    file: UploadFile = File(..., description="PDF, DOCX, or image file"),
    target_language: str = Form("en", description="Output language: 'en' or 'hi'"),
    db: Session = Depends(get_db),
):
    # ── Validate file size ────────────────────────────────────────────────
    file_bytes = file.file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is {settings.max_upload_size_mb} MB.",
        )

    # ── Validate language ─────────────────────────────────────────────────
    if target_language not in {"en", "hi"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_language must be 'en' (English) or 'hi' (Hindi).",
        )

    # ── Create DB record (status=processing) ─────────────────────────────
    doc = Document(
        filename=file.filename,
        file_type="unknown",
        target_language=target_language,
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # ── Extract text ──────────────────────────────────────────────────────
    try:
        original_text, file_type = extract_text(file_bytes, file.filename)
    except ValueError as exc:
        doc.status = "error"
        doc.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    doc.file_type = file_type
    doc.original_text = original_text
    db.commit()

    # ── Run AI pipeline ───────────────────────────────────────────────────
    try:
        result = run_pipeline(original_text, target_language=target_language)
    except Exception as exc:
        doc.status = "error"
        doc.error_message = f"AI pipeline error: {str(exc)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI processing failed: {str(exc)}",
        )

    # ── Persist results ───────────────────────────────────────────────────
    doc.document_type = result.get("document_type", "other")
    doc.simplified_text = result.get("simplified_text", "")
    doc.summary = result.get("summary", "")
    doc.highlights = result.get("highlights", {})
    doc.translated_text = result.get("translated_text")
    doc.status = "done"
    if result.get("error"):
        doc.error_message = result["error"]
    db.commit()
    db.refresh(doc)

    return _to_response(doc)


# ── List Documents ──────────────────────────────────────────────────────────

@router.get(
    "/documents",
    response_model=List[DocumentListItem],
    summary="List all processed documents",
)
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return docs


# ── Get Document ────────────────────────────────────────────────────────────

@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get full details for a single document",
)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id={document_id} not found.",
        )
    return _to_response(doc)


# ── Delete Document ─────────────────────────────────────────────────────────

@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document record",
)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id={document_id} not found.",
        )
    db.delete(doc)
    db.commit()


# ── Helper ──────────────────────────────────────────────────────────────────

def _to_response(doc: Document) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        document_type=doc.document_type,
        simplified_text=doc.simplified_text,
        summary=doc.summary,
        highlights=doc.highlights,
        translated_text=doc.translated_text,
        target_language=doc.target_language,
        status=doc.status,
        error_message=doc.error_message,
        created_at=doc.created_at,
    )
