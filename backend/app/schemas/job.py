"""
Pydantic schemas for Job creation, status polling, and batch queue management.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class JobCreateOptions(BaseModel):
    converter: str = "AUTO"             # AUTO, MARKER, DOCLING, NATIVE
    ocr_languages: str = "eng+tam+hin"  # Multi-language string
    force_ocr: bool = False
    max_pages: Optional[int] = None

class JobResponse(BaseModel):
    id: str
    documentId: str
    filename: str
    fileSize: int
    sha256: str
    status: str
    converter: str
    ocrLanguages: str
    forceOcr: bool
    progress: int
    currentStep: str
    errorMessage: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    completedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    total: int
    items: List[JobResponse]

class BatchUploadResponse(BaseModel):
    jobs: List[JobResponse]
