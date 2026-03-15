import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)   # pdf | docx | image
    document_type = Column(String(50), default="unknown")  # medical | legal | insurance | other
    original_text = Column(Text, nullable=True)
    simplified_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    highlights_json = Column(Text, nullable=True)    # stored as JSON string
    translated_text = Column(Text, nullable=True)
    target_language = Column(String(10), default="en")
    status = Column(String(20), default="processing")  # processing | done | error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def highlights(self) -> dict:
        if self.highlights_json:
            return json.loads(self.highlights_json)
        return {"important_terms": [], "risks_warnings": [], "key_clauses": []}

    @highlights.setter
    def highlights(self, value: dict):
        self.highlights_json = json.dumps(value)
