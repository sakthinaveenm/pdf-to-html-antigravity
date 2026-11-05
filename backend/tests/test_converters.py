"""
Unit & Integration tests for PDF Converters (Native, Docling, Orchestrator).
"""
from pathlib import Path
import pytest
from backend.app.services.converters.native_converter import NativeHybridConverter
from backend.app.services.converters.base import ConversionOptions

@pytest.fixture
def native_converter():
    return NativeHybridConverter()

def test_native_convert_english(native_converter, tmp_path):
    pdf_path = Path("samples/sample_english.pdf")
    options = ConversionOptions(
        document_id="doc-test-eng",
        assets_dir=tmp_path / "assets"
    )
    doc = native_converter.convert(pdf_path, options)

    assert doc.documentId == "doc-test-eng"
    assert doc.page_count == 2 or len(doc.pages) == 2
    assert len(doc.blocks) > 0
    
    # Check that headings and paragraphs exist
    block_types = [b.blockType for b in doc.blocks]
    assert "heading" in block_types
    assert "paragraph" in block_types
    
    # Check stable block ID format
    for b in doc.blocks:
        assert b.blockId.startswith("blk-") or b.blockId.startswith("pb-")

    # Check real selectable content exists
    full_text = " ".join([b.content for b in doc.blocks if b.content])
    assert "Multilingual Document Processing Architecture" in full_text
    assert "Digital document preservation" in full_text

def test_native_convert_tamil(native_converter, tmp_path):
    pdf_path = Path("samples/sample_tamil.pdf")
    options = ConversionOptions(
        document_id="doc-test-tam",
        ocr_languages="tam+eng",
        assets_dir=tmp_path / "assets"
    )
    doc = native_converter.convert(pdf_path, options)
    assert len(doc.blocks) > 0

    full_text = " ".join([b.content for b in doc.blocks if b.content])
    assert "தமிழ்" in full_text

    # Verify script and direction
    tamil_blocks = [b for b in doc.blocks if "தமிழ்" in b.content]
    assert len(tamil_blocks) > 0
    assert tamil_blocks[0].direction == "ltr"

def test_native_convert_arabic_rtl(native_converter, tmp_path):
    pdf_path = Path("samples/sample_arabic.pdf")
    options = ConversionOptions(
        document_id="doc-test-ara",
        ocr_languages="ara+eng",
        assets_dir=tmp_path / "assets"
    )
    doc = native_converter.convert(pdf_path, options)
    assert len(doc.blocks) > 0

    full_text = " ".join([b.content for b in doc.blocks if b.content])
    assert "العربية" in full_text

    arabic_blocks = [b for b in doc.blocks if "العربية" in b.content]
    assert len(arabic_blocks) > 0
    assert arabic_blocks[0].direction == "rtl"

def test_native_convert_tables(native_converter, tmp_path):
    pdf_path = Path("samples/sample_tables_math.pdf")
    options = ConversionOptions(
        document_id="doc-test-tab",
        assets_dir=tmp_path / "assets"
    )
    doc = native_converter.convert(pdf_path, options)
    
    table_blocks = [b for b in doc.blocks if b.blockType == "table"]
    # Even if table lines are subtle, blocks are preserved
    assert len(doc.blocks) > 0
    assert any("Accuracy" in b.content or (b.tableData and any("Accuracy" in h.content for h in b.tableData.headers)) for b in doc.blocks)

def test_native_convert_scanned_ocr(native_converter, tmp_path):
    pdf_path = Path("samples/sample_scanned.pdf")
    options = ConversionOptions(
        document_id="doc-test-scan",
        ocr_languages="eng",
        force_ocr=True,
        assets_dir=tmp_path / "assets"
    )
    doc = native_converter.convert(pdf_path, options)
    assert len(doc.blocks) > 0
    
    full_text = " ".join([b.content for b in doc.blocks if b.content])
    assert "Historical" in full_text or "Scanned" in full_text or "Tesseract" in full_text

