"""
Conversion Orchestrator.
Manages selection between Marker, Docling, and Native Hybrid converters,
handling capabilities, AUTO heuristics, and graceful fallbacks.
"""
import logging
from pathlib import Path
from typing import Optional, Dict

from backend.app.schemas.canonical import CanonicalDocument, DocumentWarning
from backend.app.services.converters.base import PDFConverter, ConversionOptions, ConverterCapabilities
from backend.app.services.converters.native_converter import NativeHybridConverter
from backend.app.services.converters.docling_converter import DoclingConverter
from backend.app.services.converters.marker_converter import MarkerConverter
from backend.app.services.pdf_inspector.inspector import PDFInspectionService, DocumentInspectionReport
from backend.app.constants.statuses import PageClassification

logger = logging.getLogger(__name__)

class ConversionOrchestrator:
    def __init__(self):
        self.native_converter = NativeHybridConverter()
        self.docling_converter = DoclingConverter()
        self.marker_converter = MarkerConverter()
        self.inspector = PDFInspectionService()

    def get_all_capabilities(self) -> Dict[str, ConverterCapabilities]:
        return {
            "NATIVE": self.native_converter.get_capabilities(),
            "DOCLING": self.docling_converter.get_capabilities(),
            "MARKER": self.marker_converter.get_capabilities(),
        }

    def convert(
        self,
        source_path: Path,
        options: ConversionOptions,
        preferred_engine: str = "AUTO"
    ) -> CanonicalDocument:
        inspection: DocumentInspectionReport = self.inspector.inspect(source_path)

        engine_to_use = preferred_engine.upper()
        if engine_to_use == "AUTO":
            # Auto heuristics:
            # If document is scanned or text encoding problem, Native Hybrid with Tesseract OCR is optimal
            if inspection.overall_classification in (PageClassification.SCANNED_IMAGE, PageClassification.TEXT_ENCODING_PROBLEM):
                engine_to_use = "NATIVE"
            else:
                # Digital text: Docling or Native
                if self.docling_converter.check_availability():
                    engine_to_use = "DOCLING"
                else:
                    engine_to_use = "NATIVE"

        logger.info(f"Converting {source_path.name} with engine: {engine_to_use}")

        # Execute with fallback chain
        if engine_to_use == "MARKER":
            try:
                return self.marker_converter.convert(source_path, options)
            except Exception as e:
                logger.warning(f"Marker conversion failed ({str(e)}), falling back to Docling")
                try:
                    res = self.docling_converter.convert(source_path, options)
                    res.warnings.append(DocumentWarning(code="CONVERTER_FALLBACK", message=f"Fell back from Marker to Docling: {str(e)}"))
                    return res
                except Exception as e2:
                    logger.warning(f"Docling fallback failed ({str(e2)}), falling back to Native")
                    res = self.native_converter.convert(source_path, options)
                    res.warnings.append(DocumentWarning(code="CONVERTER_FALLBACK", message=f"Fell back to Native: {str(e2)}"))
                    return res

        elif engine_to_use == "DOCLING":
            try:
                return self.docling_converter.convert(source_path, options)
            except Exception as e:
                logger.warning(f"Docling conversion failed ({str(e)}), falling back to Native")
                res = self.native_converter.convert(source_path, options)
                res.warnings.append(DocumentWarning(code="CONVERTER_FALLBACK", message=f"Fell back from Docling to Native: {str(e)}"))
                return res

        else:  # NATIVE
            return self.native_converter.convert(source_path, options)

conversion_orchestrator = ConversionOrchestrator()
