"""
Pydantic schemas for the persistent text selection and highlighting system.
Supports Text Quote Anchoring (W3C Web Annotation Data Model)
and Text Position Anchoring (Unicode codepoint units).
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class TextQuote(BaseModel):
    exact: str
    prefix: str = ""
    suffix: str = ""

class TextPosition(BaseModel):
    start: int
    end: int
    unit: str = "unicode-codepoint"  # 'unicode-codepoint' vs 'utf16-codeunit'

class HighlightCreate(BaseModel):
    blockIds: List[str]
    quote: TextQuote
    position: TextPosition
    color: str = "#FFEB3B"
    note: Optional[str] = None

class HighlightUpdate(BaseModel):
    color: Optional[str] = None
    note: Optional[str] = None
    resolved: Optional[bool] = None

class HighlightResponse(BaseModel):
    id: str
    documentId: str
    revision: int
    blockIds: List[str]
    quote: TextQuote
    position: TextPosition
    color: str
    note: Optional[str] = None
    resolved: bool = True
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

