"""
Unit & Integration tests for HTML Generation and Normalization Services.
"""
import pytest
from backend.app.schemas.canonical import CanonicalDocument, DocumentBlock, BlockProvenance
from backend.app.services.html.generator import html_generation_service
from backend.app.services.html.normalizer import html_normalization_service

@pytest.fixture
def sample_canonical_doc():
    blocks = [
        DocumentBlock(
            blockId="blk-p1-s001-a1b2",
            blockType="heading",
            sourcePage=1,
            language="ta",
            direction="ltr",
            content="தமிழ் இலக்கியம்",
            readingOrder=1,
            provenance=BlockProvenance(engine="native", page=1),
            level=1
        ),
        DocumentBlock(
            blockId="blk-p1-s002-c3d4",
            blockType="paragraph",
            sourcePage=1,
            language="ta",
            direction="ltr",
            content="தமிழ் ஒரு அழகான மொழி.",
            readingOrder=2,
            provenance=BlockProvenance(engine="native", page=1)
        ),
        DocumentBlock(
            blockId="blk-p1-s003-e5f6",
            blockType="paragraph",
            sourcePage=1,
            language="ar",
            direction="rtl",
            content="العربية لغة جميلة.",
            readingOrder=3,
            provenance=BlockProvenance(engine="native", page=1)
        )
    ]
    return CanonicalDocument(
        documentId="doc-test-101",
        sourceFileName="test.pdf",
        sourceChecksum="dummy-hash",
        title="Multilingual Test",
        language="ta",
        revision=1,
        pages=[],
        blocks=blocks,
        assets={},
        metadata={}
    )

def test_generate_semantic_html(sample_canonical_doc):
    html_output = html_generation_service.generate_html(sample_canonical_doc, standalone=True)

    assert "<!DOCTYPE html>" in html_output
    assert '<article class="canonical-document"' in html_output
    assert '<section data-page="1">' in html_output
    assert '<h1 id="blk-p1-s001-a1b2" data-block-id="blk-p1-s001-a1b2"' in html_output
    assert "தமிழ் இலக்கியம்" in html_output
    assert '<p id="blk-p1-s002-c3d4" data-block-id="blk-p1-s002-c3d4"' in html_output
    assert 'dir="rtl"' in html_output
    assert "العربية لغة جميلة." in html_output
    assert "Responsive Offline Reader Stylesheet" in html_output

def test_html_normalization_and_sanitization():
    unsafe_html = """
    <article data-document-id="doc-1">
      <section data-page="1">
        <h1 data-block-id="blk-1">Safe Title</h1>
        <script>alert('xss');</script>
        <p data-block-id="blk-2" onclick="steal()">Click me <img src="x" onerror="alert(1)" /></p>
        <a href="javascript:alert('pwned')">Evil link</a>
        <a href="https://example.com">Good link</a>
      </section>
    </article>
    """
    clean_html = html_normalization_service.normalize(unsafe_html, document_id="doc-1")

    assert "<script>" not in clean_html
    assert "alert('xss')" not in clean_html
    assert "onclick" not in clean_html
    assert "onerror" not in clean_html
    assert "javascript:" not in clean_html
    assert "Safe Title" in clean_html
    assert "https://example.com" in clean_html
    assert 'data-block-id="blk-1"' in clean_html

def test_unicode_combining_characters_preservation():
    # Tamil character with vowel sign: கி (க + ி), தமிழ்
    indic_text = '<p data-block-id="blk-tam">தமிழ் ஒரு தொன்மையான செம்மொழி.</p>'
    normalized = html_normalization_service.normalize(indic_text)
    assert "தமிழ் ஒரு தொன்மையான செம்மொழி." in normalized
