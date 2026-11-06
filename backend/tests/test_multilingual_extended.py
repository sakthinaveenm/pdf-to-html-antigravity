"""
Extended multilingual script tests and inline highlight boundary tests.
Covers Telugu, Malayalam, Bengali, Hindi, Arabic RTL, and cross-tag highlighting.
"""
import pytest
from backend.app.constants.languages import detect_script_from_text, get_direction_for_script
from backend.app.services.annotations.highlight_service import (
    annotation_service,
    utf16_offset_to_codepoint_offset,
    codepoint_offset_to_utf16_offset
)
from backend.app.schemas.highlight import HighlightCreate, HighlightUpdate, TextQuote, TextPosition
from backend.app.models.entities import Document
from backend.app.db.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    try:
        doc = Document(
            id="doc-multi-ext",
            title="Multilingual Test",
            filename="multi.pdf",
            sha256="fake-sha",
            storage_path="/tmp/doc"
        )
        db.add(doc)
        db.commit()
        yield db
    finally:
        db.close()

def test_script_detection_coverage():
    samples = {
        "tamil": "தமிழ்நாடு மற்றும் சென்னை",
        "devanagari": "नमस्ते भारत और दिल्ली",
        "telugu": "హైదరాబాదు మరియు తెలుగు భాష",
        "malayalam": "കേരളം ദൈവത്തിന്റെ സ്വന്തം നാട്",
        "kannada": "ಕರ್ನಾಟಕ ಮತ್ತು ಬೆಂಗಳೂರು",
        "bengali": "কলকাতা এবং বাংলা ভাষা",
        "arabic": "الجمهورية العربية المتحدة",
        "cjk": "自然语言处理与多语言文献数字化",
        "latin": "Artificial intelligence and computational linguistics"
    }

    for expected_script, text in samples.items():
        detected = detect_script_from_text(text)
        assert detected == expected_script, f"Failed for {expected_script}: got {detected}"

def test_script_direction_rtl_and_ltr():
    assert get_direction_for_script("arabic") == "rtl"
    assert get_direction_for_script("ara") == "rtl"
    assert get_direction_for_script("urd") == "rtl"
    assert get_direction_for_script("tamil") == "ltr"
    assert get_direction_for_script("devanagari") == "ltr"
    assert get_direction_for_script("latin") == "ltr"

def test_highlight_across_inline_formatting(memory_db):
    """
    Test highlighting across formatted spans:
    'This is <strong>very important</strong> text for analysis.'
    The quote spans across plain text into bold text.
    """
    exact_quote = "is very important text"
    create_req = HighlightCreate(
        blockIds=["blk-p1-s01"],
        quote=TextQuote(
            exact=exact_quote,
            prefix="This ",
            suffix=" for analysis."
        ),
        position=TextPosition(
            start=5,
            end=5 + len(exact_quote),
            unit="unicode-codepoint"
        ),
        color="#BAE6FD",
        note="Cross-span annotation"
    )

    created = annotation_service.create_highlight(memory_db, "doc-multi-ext", create_req, revision=1)
    assert created.id.startswith("hl-")
    assert created.exact_text == exact_quote

    # Update highlight color
    updated = annotation_service.update_highlight(memory_db, created.id, HighlightUpdate(color="#FED7AA"))
    assert updated.color == "#FED7AA"

    # Re-anchoring test when prefix changes
    updated_block_text = {
        "blk-p1-s01": "Notice: This is very important text for analysis and review."
    }
    annotation_service.reanchor_highlights_on_revision(memory_db, "doc-multi-ext", new_revision=2, block_texts=updated_block_text)

    all_hl = annotation_service.list_highlights(memory_db, "doc-multi-ext")
    assert len(all_hl) == 1
    assert all_hl[0].resolved is True
    # 'Notice: This ' = 13 characters -> 'is very important text' starts at index 13
    assert all_hl[0].position.start == 13

def test_legacy_indic_font_detection_and_decoding():
    from backend.app.services.ocr.legacy_indic_decoder import (
        is_legacy_indic_font,
        detect_legacy_indic_text,
        decode_chanakya_to_unicode
    )

    # 1. Font name detection
    assert is_legacy_indic_font("CODFBD+Walkman-Chanakya905Normal") is True
    assert is_legacy_indic_font("KrutiDev010") is True
    assert is_legacy_indic_font("DevLys010Bold") is True
    assert is_legacy_indic_font("Arial-BoldMT") is False

    # 2. Signature Mojibake detection
    sample_chanakya = "lk>snkjh ys[kkadu μ vk/kjHkwr vo/kj.kk,¡ vHkh rd vkius ,dy LokfeRo osQ foÙkh; fooj.kksa osQ ckjs esa lh[kk gSA"
    is_legacy, family = detect_legacy_indic_text(sample_chanakya)
    assert is_legacy is True
    assert family == "chanakya"

    # 3. Decoding precision for textbook Hindi terms
    decoded_title = decode_chanakya_to_unicode("lk>snkjh ys[kkadu")
    assert "साझेदारी" in decoded_title
    assert "लेखांकन" in decoded_title

    decoded_terms = decode_chanakya_to_unicode("vk/kjHkwr vo/kj.kk,¡")
    assert "आधारभूत" in decoded_terms or "आध्ारभूत" in decoded_terms


