"""
Tests for Page-by-Page Book Conversion, Editor-Ready HTML Snippets,
Formatting Preservation, and Page-Level API Endpoints.
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.canonical import (
    CanonicalDocument, DocumentBlock, BlockProvenance, PageMetadata, BlockStyle, TableData, TableRow, TableCell
)
from backend.app.services.html.generator import html_generation_service
from backend.app.config.settings import settings

client = TestClient(app)

@pytest.fixture
def sample_multilingual_book_ast():
    blocks = [
        # Page 1: Tamil Science Textbook Heading + Paragraph
        DocumentBlock(
            blockId="blk-p1-s001-a1",
            blockType="heading",
            sourcePage=1,
            language="tamil",
            direction="ltr",
            content="அறிவியல் பாடம் 1: தாவரங்களின் வாழ்க்கை",
            readingOrder=1,
            provenance=BlockProvenance(engine="native", page=1),
            level=1,
            style=BlockStyle(
                fontFamily="'Noto Sans Tamil', 'Latha', sans-serif",
                fontSize=26.0,
                fontWeight="bold",
                color="#1e3a8a",
                textAlign="center",
                lineHeight=1.3,
                marginTop="1em",
                marginBottom="0.5em"
            )
        ),
        DocumentBlock(
            blockId="blk-p1-s002-b2",
            blockType="paragraph",
            sourcePage=1,
            language="tamil",
            direction="ltr",
            content="தாவரங்கள் ஒளிச்சேர்க்கை (Photosynthesis) மூலம் தங்கள் உணவைத் தயாரிக்கின்றன.",
            readingOrder=2,
            provenance=BlockProvenance(engine="native", page=1),
            style=BlockStyle(
                fontFamily="'Noto Sans Tamil', 'Latha', sans-serif",
                fontSize=16.0,
                fontWeight="normal",
                color="#111827",
                textAlign="justify",
                lineHeight=1.65,
                marginTop="0.5em",
                marginBottom="0.75em"
            )
        ),
        # Page 1: Structured Table
        DocumentBlock(
            blockId="blk-p1-s003-c3",
            blockType="table",
            sourcePage=1,
            readingOrder=3,
            provenance=BlockProvenance(engine="native", page=1),
            tableData=TableData(
                headers=[
                    TableCell(content="தாவர பாகம்", is_header=True),
                    TableCell(content="பணி (Function)", is_header=True)
                ],
                rows=[
                    TableRow(cells=[
                        TableCell(content="வேர் (Root)", is_header=False),
                        TableCell(content="நீரை உறிஞ்சுதல்", is_header=False)
                    ]),
                    TableRow(cells=[
                        TableCell(content="இலை (Leaf)", is_header=False),
                        TableCell(content="ஒளிச்சேர்க்கை", is_header=False)
                    ])
                ]
            )
        ),
        # Page 2: Arabic RTL Content + Equation
        DocumentBlock(
            blockId="blk-p2-s001-d4",
            blockType="heading",
            sourcePage=2,
            language="arabic",
            direction="rtl",
            content="الفصل الثاني: المعادلات الكيميائية",
            readingOrder=1,
            provenance=BlockProvenance(engine="native", page=2),
            level=2,
            style=BlockStyle(
                fontFamily="'Noto Sans Arabic', 'Geeza Pro', sans-serif",
                fontSize=22.0,
                fontWeight="bold",
                color="#047857",
                textAlign="right",
                lineHeight=1.4
            )
        ),
        DocumentBlock(
            blockId="blk-p2-s002-e5",
            blockType="equation",
            sourcePage=2,
            language="latin",
            direction="ltr",
            content="6CO2 + 6H2O -> C6H12O6 + 6O2",
            readingOrder=2,
            provenance=BlockProvenance(engine="native", page=2),
            mathFormula="6CO_2 + 6H_2O \\rightarrow C_6H_{12}O_6 + 6O_2"
        )
    ]

    pages = [
        PageMetadata(
            pageNumber=1,
            width=595.0,
            height=842.0,
            classification="DIGITAL_TEXT",
            detectedScript="tamil",
            fontsDetected=["TamilSangamMN", "Arial"],
            wordCount=25
        ),
        PageMetadata(
            pageNumber=2,
            width=595.0,
            height=842.0,
            classification="DIGITAL_TEXT",
            detectedScript="arabic",
            fontsDetected=["GeezaPro", "TimesNewRoman"],
            wordCount=15
        )
    ]

    return CanonicalDocument(
        documentId="doc-book-test-101",
        sourceFileName="Tamil_Science_Book.pdf",
        sourceChecksum="a" * 64,
        title="Tamil Science Book Grade 8",
        language="ta",
        revision=1,
        pages=pages,
        blocks=blocks
    )

def test_editor_ready_page_snippet_format(sample_multilingual_book_ast):
    """Verify that page snippet is an HTML fragment with inline CSS and no html/head/body."""
    snippet_p1 = html_generation_service.generate_page_snippet(sample_multilingual_book_ast, page_num=1)
    
    # Must NOT contain html/head/body wrappers
    assert "<!DOCTYPE html>" not in snippet_p1
    assert "<html>" not in snippet_p1
    assert "<head>" not in snippet_p1
    assert "<body>" not in snippet_p1

    # Must contain section for page 1
    assert '<section data-page="1"' in snippet_p1
    assert 'class="ue-page"' in snippet_p1

    # Must contain inline styles preserving formatting
    assert 'style="' in snippet_p1
    assert "Noto Sans Tamil" in snippet_p1
    assert "font-size: 26.0px" in snippet_p1 or "font-size: 26px" in snippet_p1
    assert "color: #1e3a8a" in snippet_p1
    assert "text-align: center" in snippet_p1
    assert "text-align: justify" in snippet_p1

    # Must preserve exact Tamil Unicode characters
    assert "அறிவியல் பாடம் 1: தாவரங்களின் வாழ்க்கை" in snippet_p1
    assert "தாவரங்கள் ஒளிச்சேர்க்கை (Photosynthesis)" in snippet_p1

    # Must include table with borders and cell formatting
    assert "<table" in snippet_p1
    assert "border-collapse: collapse" in snippet_p1
    assert "தாவர பாகம்" in snippet_p1
    assert "வேர் (Root)" in snippet_p1

def test_page_snippet_arabic_rtl_and_equation(sample_multilingual_book_ast):
    """Verify that page 2 preserves Arabic RTL direction and math equations."""
    snippet_p2 = html_generation_service.generate_page_snippet(sample_multilingual_book_ast, page_num=2)

    assert '<section data-page="2"' in snippet_p2
    assert "الفصل الثاني: المعادلات الكيميائية" in snippet_p2
    assert 'dir="rtl"' in snippet_p2
    assert "text-align: right" in snippet_p2
    assert "Noto Sans Arabic" in snippet_p2
    assert "math-equation" in snippet_p2

def test_generate_page_standalone(sample_multilingual_book_ast):
    """Verify standalone HTML document generation for a single page."""
    standalone = html_generation_service.generate_page_standalone(sample_multilingual_book_ast, page_num=1)

    assert "<!DOCTYPE html>" in standalone
    assert "<html" in standalone
    assert "<head>" in standalone
    assert "<style>" in standalone
    assert "<body>" in standalone
    assert '<section data-page="1"' in standalone
    assert "அறிவியல் பாடம் 1" in standalone

def test_generate_all_pages_bundle(tmp_path, sample_multilingual_book_ast):
    """Verify writing pages/0001/paste.html and standalone.html to disk."""
    doc_dir = tmp_path / "doc-book-test-101"
    doc_dir.mkdir(parents=True, exist_ok=True)

    html_generation_service.generate_all_pages_bundle(sample_multilingual_book_ast, doc_dir)

    page1_dir = doc_dir / "pages" / "0001"
    page2_dir = doc_dir / "pages" / "0002"

    assert page1_dir.exists()
    assert (page1_dir / "paste.html").exists()
    assert (page1_dir / "standalone.html").exists()
    assert (page1_dir / "metadata.json").exists()

    assert page2_dir.exists()
    assert (page2_dir / "paste.html").exists()

    p1_content = (page1_dir / "paste.html").read_text(encoding="utf-8")
    assert "அறிவியல் பாடம் 1" in p1_content
    assert "font-size:" in p1_content

def test_page_api_endpoints(sample_multilingual_book_ast):
    """Test REST API endpoints for page-by-page snippet retrieval, correction, and reset."""
    doc_id = sample_multilingual_book_ast.documentId
    doc_dir = settings.DOCUMENTS_DIR / doc_id
    if doc_dir.exists():
        import shutil
        shutil.rmtree(doc_dir)
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # Save document.json AST and generate pages
    (doc_dir / "document.json").write_text(sample_multilingual_book_ast.model_dump_json(indent=2), encoding="utf-8")
    html_generation_service.generate_all_pages_bundle(sample_multilingual_book_ast, doc_dir)

    # Register document in database if not present
    from backend.app.db.database import SessionLocal
    from backend.app.models.entities import Document
    db = SessionLocal()
    try:
        existing = db.query(Document).filter(Document.id == doc_id).first()
        if not existing:
            doc_rec = Document(
                id=doc_id,
                title=sample_multilingual_book_ast.title,
                filename="Tamil_Science_Book.pdf",
                sha256="b" * 64,
                language="ta",
                page_count=2,
                current_revision=1,
                quality_status="PASS",
                storage_path=str(doc_dir)
            )
            db.add(doc_rec)
            db.commit()
    finally:
        db.close()

    # 1. GET page 1 snippet
    res = client.get(f"/api/v1/documents/{doc_id}/pages/1/snippet")
    assert res.status_code == 200
    data = res.json()
    assert data["pageNumber"] == 1
    assert "அறிவியல் பாடம் 1" in data["html"]
    assert data["isCorrected"] is False
    assert len(data["plainText"]) > 0

    # 2. GET page 1 standalone HTML preview
    res_standalone = client.get(f"/api/v1/documents/{doc_id}/pages/1/standalone")
    assert res_standalone.status_code == 200
    assert "<!DOCTYPE html>" in res_standalone.text

    # 3. PUT manual developer correction on page 1
    corrected_html = '<section data-page="1" class="ue-page"><h1 style="color: red;">Corrected Tamil Heading</h1></section>'
    res_update = client.put(
        f"/api/v1/documents/{doc_id}/pages/1/snippet",
        json={"html": corrected_html, "changeSummary": "Fixed heading color"}
    )
    assert res_update.status_code == 200
    up_data = res_update.json()
    assert up_data["isCorrected"] is True
    assert "Corrected Tamil Heading" in up_data["html"]

    # Verify backup exists
    assert (doc_dir / "pages" / "0001" / "paste.original.html").exists()

    # 4. POST reset page 1 back to converter version
    res_reset = client.post(f"/api/v1/documents/{doc_id}/pages/1/reset")
    assert res_reset.status_code == 200
    reset_data = res_reset.json()
    assert reset_data["isCorrected"] is False
    assert "அறிவியல் பாடம் 1" in reset_data["html"]
