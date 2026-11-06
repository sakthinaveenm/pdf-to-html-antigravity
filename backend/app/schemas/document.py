"""
Pydantic schemas for Document metadata, revisions, and responses.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: str
    jobId: Optional[str] = None
    title: str
    filename: str
    sha256: str
    language: str
    pageCount: int
    currentRevision: int
    qualityStatus: str
    createdAt: datetime
    updatedAt: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int
    items: List[DocumentResponse]

class DocumentDeleteResponse(BaseModel):
    status: str
    documentId: str
    message: str

class DocumentRevisionCreate(BaseModel):
    html: str
    changeSummary: str = "Edited in HTML editor"

class DocumentRevisionResponse(BaseModel):
    id: str
    documentId: str
    revisionNumber: int
    changeSummary: str
    createdAt: datetime

class PageSnippetResponse(BaseModel):
    documentId: str
    pageNumber: int
    html: str
    plainText: str
    isCorrected: bool = False
    fontsDetected: List[str] = []
    detectedScript: Optional[str] = None
    wordCount: int = 0
    warnings: List[str] = []

class PageSnippetUpdateRequest(BaseModel):
    html: str
    changeSummary: Optional[str] = "Manual developer correction"


