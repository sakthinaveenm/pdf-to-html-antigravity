"""
Abstract base class and schemas for PDF Converters.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.canonical import CanonicalDocument

class ConversionOptions(BaseModel):
    document_id: str
    ocr_languages: str = "eng"
    document_language: Optional[str] = "AUTO"
    force_ocr: bool = False
    max_pages: Optional[int] = None
    assets_dir: Path
    device: str = "cpu"

class ConverterCapabilities(BaseModel):
    engine_name: str
    is_available: bool
    version: Optional[str] = None
    supports_ocr: bool = False
    supports_tables: bool = True
    supports_equations: bool = True
    supports_gpu: bool = False
    notes: str = ""

class PDFConverter(ABC):
    @abstractmethod
    def convert(self, source_path: Path, options: ConversionOptions) -> CanonicalDocument:
        """Convert a PDF file to the Canonical Document Model AST."""
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if the converter engine and required models/dependencies are present."""
        pass

    @abstractmethod
    def get_capabilities(self) -> ConverterCapabilities:
        """Return engine capabilities and hardware compatibility."""
        pass

