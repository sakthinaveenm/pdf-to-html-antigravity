"""
Unit & Integration tests for PDFInspectionService.
"""
from pathlib import Path
import pytest
from backend.app.services.pdf_inspector.inspector import PDFInspectionService
from backend.app.constants.statuses import PageClassification

@pytest.fixture
def inspector():
    return PDFInspectionService()

def test_inspect_english_pdf(inspector):
    pdf_path = Path("samples/sample_english.pdf")
    report = inspector.inspect(pdf_path)
    assert report.is_valid_pdf is True
    assert report.page_count == 2
    assert report.encrypted is False
    assert report.overall_classification in (PageClassification.DIGITAL_TEXT, PageClassification.MIXED_CONTENT)
    assert len(report.pages) == 2
    assert report.pages[0].text_char_count > 50

def test_inspect_tamil_pdf(inspector):
    pdf_path = Path("samples/sample_tamil.pdf")
    report = inspector.inspect(pdf_path)
    assert report.is_valid_pdf is True
    assert report.page_count == 1
    assert "tam" in report.recommended_ocr_languages or "tamil" in [p.detected_script for p in report.pages]

def test_inspect_scanned_pdf(inspector):
    pdf_path = Path("samples/sample_scanned.pdf")
    report = inspector.inspect(pdf_path)
    assert report.is_valid_pdf is True
    assert report.page_count == 1
    assert report.pages[0].classification == PageClassification.SCANNED_IMAGE
    assert report.overall_classification == PageClassification.SCANNED_IMAGE

def test_inspect_nonexistent_pdf(inspector):
    pdf_path = Path("samples/nonexistent_file.pdf")
    report = inspector.inspect(pdf_path)
    assert report.is_valid_pdf is False
    assert len(report.warnings) > 0
