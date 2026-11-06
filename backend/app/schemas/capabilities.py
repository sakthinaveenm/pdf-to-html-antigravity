"""
Pydantic schemas for Document metadata, revisions, quality reports, and capabilities.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

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

class DocumentRevisionCreate(BaseModel):
    html: str
    changeSummary: str = "Edited in HTML editor"

class DocumentRevisionResponse(BaseModel):
    id: str
    documentId: str
    revisionNumber: int
    changeSummary: str
    createdAt: datetime

class QualityMetric(BaseModel):
    name: str
    score: float  # 0.0 to 1.0
    passed: bool
    details: str

class QualityReport(BaseModel):
    documentId: str
    overallStatus: str  # PASS, WARNING, REQUIRES_REVIEW, FAILED
    textSelectabilityScore: float
    unicodeIntegrityScore: float
    structuralScore: float
    metrics: List[QualityMetric]
    warnings: List[str]
    diagnostics: Dict[str, Any]

class ConverterInfo(BaseModel):
    name: str
    available: bool
    version: Optional[str] = None
    description: str

class SystemCapabilities(BaseModel):
    platform: str
    cpuCount: int
    totalRamGb: float
    gpuAvailable: bool
    gpuName: str
    gpuMemoryMb: int
    recommendedDevice: str
    defaultWorkers: int
    installedOcrLanguages: List[str]
    languageDetails: List[Dict[str, Any]] = Field(default_factory=list)
    converters: List[ConverterInfo]
    defaultConverter: str

