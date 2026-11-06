"""
SQLAlchemy models for Jobs, Documents, Revisions, and Highlights.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    sha256 = Column(String(64), nullable=False, index=True)
    
    status = Column(String(32), nullable=False, default="QUEUED", index=True)
    converter = Column(String(32), nullable=False, default="AUTO")
    ocr_languages = Column(String(512), nullable=False, default="eng")
    document_language = Column(String(64), nullable=True, default="AUTO")
    force_ocr = Column(Boolean, nullable=False, default=False)
    
    progress = Column(Integer, nullable=False, default=0)
    current_step = Column(String(128), nullable=False, default="Queued")
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), nullable=True, index=True)
    title = Column(String(512), nullable=False, default="Untitled Document")
    filename = Column(String(255), nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    language = Column(String(64), nullable=False, default="en")
    page_count = Column(Integer, nullable=False, default=1)
    current_revision = Column(Integer, nullable=False, default=1)
    quality_status = Column(String(32), nullable=False, default="PASS")
    
    storage_path = Column(String(512), nullable=False)
    metadata_json = Column(Text, nullable=True)
    inspection_json = Column(Text, nullable=True)
    quality_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="document", cascade="all, delete-orphan")

class DocumentRevision(Base):
    __tablename__ = "document_revisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    html_content = Column(Text, nullable=False)
    ast_json = Column(Text, nullable=True)
    change_summary = Column(String(255), nullable=False, default="Updated document content")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    document = relationship("Document", back_populates="revisions")

class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    revision = Column(Integer, nullable=False, default=1)
    block_ids = Column(Text, nullable=False)  # JSON serialized list of block IDs
    
    # Text Quote Anchoring
    exact_text = Column(Text, nullable=False)
    prefix = Column(Text, nullable=False, default="")
    suffix = Column(Text, nullable=False, default="")
    
    # Text Position Anchoring (Unicode code points)
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    offset_unit = Column(String(32), nullable=False, default="unicode-codepoint")
    
    color = Column(String(32), nullable=False, default="#FFEB3B")
    note = Column(Text, nullable=True)
    resolved = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    document = relationship("Document", back_populates="highlights")

