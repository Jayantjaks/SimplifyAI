from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    target_language: str = "en"


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    document_type: str
    simplified_text: Optional[str] = None
    summary: Optional[str] = None
    highlights: dict = {}
    translated_text: Optional[str] = None
    target_language: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: int
    filename: str
    document_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessRequest(BaseModel):
    target_language: str = "en"   # en | hi
