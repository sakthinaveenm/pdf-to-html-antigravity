"""
Unit and integration tests for universal multilingual capabilities:
ANY OCR language and ANY Document language.
"""
import pytest
from backend.app.constants.languages import (
    detect_script_from_text,
    get_direction_for_script,
    is_rtl,
    resolve_document_language,
    get_tesseract_langs_for_scripts,
    SCRIPT_TO_BCP47,
    SCRIPT_TO_TESSERACT
)
from backend.app.services.ocr.tesseract_service import ocr_service
from backend.app.services.html.generator import html_generation_service
from backend.app.schemas.canonical import (
    CanonicalDocument, DocumentBlock, BlockProvenance
)

def test_expanded_world_scripts_detection():
    """Verify script detection across major world writing systems."""
    test_cases = {
        "cyrillic": "Привет, мир! Это текст на русском языке.",
        "greek": "Γειά σου κόσμε! Αυτό είναι ένα ελληνικό κείμενο.",
        "hebrew": "שלום עולם! זהו טקסט בשפה העברית.",
        "thai": "สวัสดีชาวโลก! นี่คือข้อความภาษาไทย",
        "lao": "ສະບາຍດີຊາວໂລກ! ນີ້ແມ່ນຂໍ້ຄວາມພາສາລາວ",
        "tibetan": "བཀྲ་ཤིས་བདེ་ལེགས། འདི་ནི་བོད་ཡིག་གི་ཚིག་ཡིན།",
        "myanmar": "မင်္ဂလာပါကမ္ဘာလောက! ဤသည်မှာ မြန်မာစာသားဖြစ်သည်။",
        "georgian": "გამარჯობა მსოფლიო! ეს არის ქართული ტექსტი.",
        "armenian": "Բարև աշխարհ! Սա հայերեն տեքստ է։",
        "ethiopic": "ሰላም ዓለም! ይህ በአማርኛ የተጻፈ ጽሑፍ ነው።",
        "khmer": "សួស្តីពិភពលោក! នេះគឺជាអត្ថបទភាសាខ្មែរ។",
        "sinhala": "හෙලෝ ලෝකය! මෙය සිංහල භාෂාවෙන් ලියූ පෙළකි.",
        "odia": "ନମସ୍କାର ପୃଥିବୀ! ଏହା ଓଡ଼ିଆ ଭାଷାରେ ଲେଖାଯାଇଛି।",
        "devanagari": "नमस्ते दुनिया! यह हिंदी भाषा में एक पाठ है।",
        "tamil": "வணக்கம் உலகம்! இது தமிழ் மொழியில் ஒரு உரை.",
        "arabic": "مرحبا بالعالم! هذا نص باللغة العربية.",
        "cjk": "你好世界！这是中文简体文本。",
        "hiragana": "こんにちは世界！これは日本語のテキストです。",
        "hangul": "안녕하세요 세계! 이것은 한국어 텍스트입니다.",
        "latin": "Hello World! This is an English text."
    }

    for expected_script, text in test_cases.items():
        detected = detect_script_from_text(text)
        assert detected == expected_script, f"Failed for {expected_script}: detected '{detected}'"

def test_rtl_detection_all_languages_and_scripts():
    """Verify RTL detection for all Semitic and RTL scripts/languages."""
    # Language codes
    assert is_rtl("ar") is True
    assert is_rtl("ara") is True
    assert is_rtl("ar-SA") is True
    assert is_rtl("ar-EG") is True
    assert is_rtl("he") is True
    assert is_rtl("heb") is True
    assert is_rtl("he-IL") is True
    assert is_rtl("ur") is True
    assert is_rtl("urd") is True
    assert is_rtl("ur-PK") is True
    assert is_rtl("fa") is True
    assert is_rtl("fas") is True
    assert is_rtl("fa-IR") is True
    assert is_rtl("ps") is True
    assert is_rtl("pus") is True
    assert is_rtl("yi") is True
    assert is_rtl("yid") is True
    assert is_rtl("ug") is True
    assert is_rtl("syr") is True
    assert is_rtl("dv") is True

    # Script names
    assert is_rtl("arabic") is True
    assert is_rtl("hebrew") is True
    assert is_rtl("syriac") is True
    assert is_rtl("thaana") is True

    # Non-RTL
    assert is_rtl("en") is False
    assert is_rtl("ru") is False
    assert is_rtl("hi") is False
    assert is_rtl("ta") is False
    assert is_rtl("th") is False
    assert is_rtl("cyrillic") is False
    assert is_rtl("greek") is False
    assert is_rtl("devanagari") is False

def test_resolve_document_language():
    """Verify document language resolution with explicit codes, AUTO, and fallbacks."""
    # Explicit user choice always takes precedence
    assert resolve_document_language("ru", "devanagari") == "ru"
    assert resolve_document_language("sr-Latn-RS", "cyrillic") == "sr-Latn-RS"
    assert resolve_document_language("fr-CA", "latin") == "fr-CA"
    assert resolve_document_language("de-CH", "latin") == "de-CH"
    assert resolve_document_language("he", "hebrew") == "he"
    assert resolve_document_language("th", "thai") == "th"

    # AUTO resolves based on detected script
    assert resolve_document_language("AUTO", "cyrillic") == "ru"
    assert resolve_document_language("AUTO", "greek") == "el"
    assert resolve_document_language("AUTO", "hebrew") == "he"
    assert resolve_document_language("AUTO", "thai") == "th"
    assert resolve_document_language("AUTO", "devanagari") == "hi"
    assert resolve_document_language("AUTO", "tamil") == "ta"
    assert resolve_document_language("AUTO", "arabic") == "ar"
    assert resolve_document_language("AUTO", "cjk") == "zh"
    assert resolve_document_language("AUTO", "hangul") == "ko"
    assert resolve_document_language("AUTO", "hiragana") == "ja"

    # Fallback when none provided
    assert resolve_document_language(None, None) == "en"
    assert resolve_document_language("", None) == "en"

def test_tesseract_languages_validation_permissive():
    """Verify validate_languages accepts any installed language pack and handles AUTO."""
    # Multiple installed languages
    valid, missing = ocr_service.validate_languages("eng+rus+fra")
    assert "eng" in valid
    assert "rus" in valid
    assert "fra" in valid

    # Auto mode with detected script
    valid_auto, _ = ocr_service.validate_languages("AUTO", detected_scripts=["cyrillic"])
    assert "rus" in valid_auto

    valid_auto_hebrew, _ = ocr_service.validate_languages("AUTO", detected_scripts=["hebrew"])
    assert "heb" in valid_auto_hebrew

    valid_auto_thai, _ = ocr_service.validate_languages("AUTO", detected_scripts=["thai"])
    assert "tha" in valid_auto_thai

    # Graceful handling of non-existent language
    valid_fallback, missing = ocr_service.validate_languages("xyz_nonexistent_pack")
    assert "xyz_nonexistent_pack" in missing
    assert "eng" in valid_fallback  # Safe fallback

def test_semantic_html_generation_arbitrary_language_and_rtl():
    """Verify HTML generator outputs correct lang and dir attributes for arbitrary languages."""
    # 1. Hebrew RTL document
    hebrew_doc = CanonicalDocument(
        documentId="doc-heb-test",
        sourceFileName="hebrew.pdf",
        sourceChecksum="dummy-sha",
        title="Hebrew Test",
        language="he",
        blocks=[
            DocumentBlock(
                blockId="blk-h1",
                blockType="heading",
                sourcePage=1,
                language="he",
                direction="rtl",
                content="שלום עולם",
                readingOrder=1,
                provenance=BlockProvenance(engine="native", page=1),
                level=1
            ),
            DocumentBlock(
                blockId="blk-p1",
                blockType="paragraph",
                sourcePage=1,
                language="he",
                direction="rtl",
                content="זהו משפט בעברית",
                readingOrder=2,
                provenance=BlockProvenance(engine="native", page=1)
            )
        ]
    )

    hebrew_html = html_generation_service.generate_html(hebrew_doc, standalone=True)
    assert '<html lang="he" dir="rtl">' in hebrew_html
    assert '<article class="canonical-document" lang="he" dir="rtl"' in hebrew_html
    assert 'dir="rtl"' in hebrew_html
    assert 'שלום עולם' in hebrew_html

    # 2. Russian Cyrillic LTR document
    russian_doc = CanonicalDocument(
        documentId="doc-rus-test",
        sourceFileName="russian.pdf",
        sourceChecksum="dummy-sha",
        title="Russian Test",
        language="ru",
        blocks=[
            DocumentBlock(
                blockId="blk-r1",
                blockType="paragraph",
                sourcePage=1,
                language="ru",
                direction="ltr",
                content="Привет, мир!",
                readingOrder=1,
                provenance=BlockProvenance(engine="native", page=1)
            )
        ]
    )

    russian_html = html_generation_service.generate_html(russian_doc, standalone=True)
    assert '<html lang="ru" dir="ltr">' in russian_html
    assert '<article class="canonical-document" lang="ru" dir="ltr"' in russian_html
    assert 'Привет, мир!' in russian_html

    # 3. Custom BCP-47 tag (e.g. Serbian Latin 'sr-Latn')
    custom_doc = CanonicalDocument(
        documentId="doc-custom-test",
        sourceFileName="custom.pdf",
        sourceChecksum="dummy-sha",
        title="Custom Lang Test",
        language="sr-Latn",
        blocks=[
            DocumentBlock(
                blockId="blk-c1",
                blockType="paragraph",
                sourcePage=1,
                language="sr-Latn",
                direction="ltr",
                content="Ovo je tekst na srpskom jeziku.",
                readingOrder=1,
                provenance=BlockProvenance(engine="native", page=1)
            )
        ]
    )

    custom_html = html_generation_service.generate_html(custom_doc, standalone=True)
    assert '<html lang="sr-Latn" dir="ltr">' in custom_html
    assert '<article class="canonical-document" lang="sr-Latn" dir="ltr"' in custom_html
