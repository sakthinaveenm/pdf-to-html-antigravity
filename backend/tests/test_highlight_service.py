"""
Unit & Integration tests for Annotation and Highlighting Service.
Tests Unicode codepoint vs UTF-16 conversions, quote/position anchoring,
persistence, and re-anchoring on revision changes.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.database import Base
from backend.app.models.entities import Document, Highlight
from backend.app.schemas.highlight import HighlightCreate, HighlightUpdate, TextQuote, TextPosition
from backend.app.services.annotations.highlight_service import (
    annotation_service,
    utf16_offset_to_codepoint_offset,
    codepoint_offset_to_utf16_offset
)

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    try:
        # Create a mock document
        doc = Document(
            id="doc-test-hl",
            title="Test Document",
            filename="test.pdf",
            sha256="test-sha",
            storage_path="/tmp/doc"
        )
        db.add(doc)
        db.commit()
        yield db
    finally:
        db.close()

def test_utf16_and_codepoint_conversions():
    # Regular ASCII
    text_ascii = "Hello world"
    assert utf16_offset_to_codepoint_offset(text_ascii, 5) == 5
    assert codepoint_offset_to_utf16_offset(text_ascii, 5) == 5

    # Indic Script (Tamil: தமிழ்)
    text_tamil = "தமிழ்"
    # Each Tamil character in BMP is 1 UTF-16 code unit
    assert utf16_offset_to_codepoint_offset(text_tamil, 3) == 3
    assert codepoint_offset_to_utf16_offset(text_tamil, 3) == 3

    # Supplementary Plane character (e.g. Emoji 🚀 = U+1F680, takes 2 UTF-16 code units)
    text_smp = "A🚀B"  # 'A' (1 unit), '🚀' (2 units), 'B' (1 unit) -> total 4 UTF-16 units, 3 codepoints
    assert utf16_offset_to_codepoint_offset(text_smp, 0) == 0  # before 'A'
    assert utf16_offset_to_codepoint_offset(text_smp, 1) == 1  # before '🚀'
    assert utf16_offset_to_codepoint_offset(text_smp, 3) == 2  # before 'B'
    assert utf16_offset_to_codepoint_offset(text_smp, 4) == 3  # after 'B'

    assert codepoint_offset_to_utf16_offset(text_smp, 0) == 0
    assert codepoint_offset_to_utf16_offset(text_smp, 1) == 1
    assert codepoint_offset_to_utf16_offset(text_smp, 2) == 3  # 1 + 2
    assert codepoint_offset_to_utf16_offset(text_smp, 3) == 4

def test_highlight_crud_and_anchoring(test_db):
    create_req = HighlightCreate(
        blockIds=["blk-001"],
        quote=TextQuote(
            exact="தமிழ் ஒரு அழகான மொழி",
            prefix="",
            suffix="."
        ),
        position=TextPosition(
            start=0,
            end=22,
            unit="unicode-codepoint"
        ),
        color="#FFEB3B",
        note="Note on Tamil language"
    )

    created = annotation_service.create_highlight(test_db, "doc-test-hl", create_req, revision=1)
    assert created.id.startswith("hl-")
    assert created.exact_text == "தமிழ் ஒரு அழகான மொழி"

    # List highlights
    all_hl = annotation_service.list_highlights(test_db, "doc-test-hl")
    assert len(all_hl) == 1
    assert all_hl[0].quote.exact == "தமிழ் ஒரு அழகான மொழி"
    assert all_hl[0].resolved is True

    # Update highlight
    updated = annotation_service.update_highlight(
        test_db,
        created.id,
        HighlightUpdate(color="#4CAF50", note="Updated note")
    )
    assert updated.color == "#4CAF50"
    assert updated.note == "Updated note"

    # Test re-anchoring when text shifts due to edits
    new_block_texts = {
        "blk-001": "வணக்கம்! தமிழ் ஒரு அழகான மொழி. இது மிகவும் தொன்மையானது."
    }
    annotation_service.reanchor_highlights_on_revision(test_db, "doc-test-hl", new_revision=2, block_texts=new_block_texts)

    all_hl_after = annotation_service.list_highlights(test_db, "doc-test-hl")
    assert all_hl_after[0].resolved is True
    assert all_hl_after[0].revision == 2
    # Offset should have shifted past 'வணக்கம்! ' (9 codepoints)
    assert all_hl_after[0].position.start == 9

    # Delete highlight
    deleted = annotation_service.delete_highlight(test_db, created.id)
    assert deleted is True
    assert len(annotation_service.list_highlights(test_db, "doc-test-hl")) == 0
