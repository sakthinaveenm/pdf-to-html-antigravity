"""
Multilingual language constants, script classifications, and Tesseract mappings.
Target languages:
English, Tamil, Hindi, Telugu, Malayalam, Kannada, Bengali, Marathi,
Gujarati, Punjabi, Sanskrit, Arabic, Urdu, Chinese (Simp/Trad), Japanese,
Korean, French, German, Spanish.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class LanguageInfo(BaseModel):
    code: str              # ISO 639-1 or 639-3 (e.g., 'ta', 'hi', 'ar')
    bcp47: str             # BCP-47 tag (e.g., 'ta-IN', 'ar-SA', 'zh-CN')
    name: str              # English name
    native_name: str       # Native script name
    direction: str         # 'ltr' or 'rtl'
    tesseract_code: str    # Tesseract language pack code
    family: str            # 'indic', 'semitic', 'cjk', 'latin'
    indic_script: bool = False

TARGET_LANGUAGES: Dict[str, LanguageInfo] = {
    "en": LanguageInfo(code="en", bcp47="en-US", name="English", native_name="English", direction="ltr", tesseract_code="eng", family="latin"),
    "ta": LanguageInfo(code="ta", bcp47="ta-IN", name="Tamil", native_name="தமிழ்", direction="ltr", tesseract_code="tam", family="indic", indic_script=True),
    "hi": LanguageInfo(code="hi", bcp47="hi-IN", name="Hindi", native_name="हिन्दी", direction="ltr", tesseract_code="hin", family="indic", indic_script=True),
    "te": LanguageInfo(code="te", bcp47="te-IN", name="Telugu", native_name="తెలుగు", direction="ltr", tesseract_code="tel", family="indic", indic_script=True),
    "ml": LanguageInfo(code="ml", bcp47="ml-IN", name="Malayalam", native_name="മലയാളം", direction="ltr", tesseract_code="mal", family="indic", indic_script=True),
    "kn": LanguageInfo(code="kn", bcp47="kn-IN", name="Kannada", native_name="ಕನ್ನಡ", direction="ltr", tesseract_code="kan", family="indic", indic_script=True),
    "bn": LanguageInfo(code="bn", bcp47="bn-BD", name="Bengali", native_name="বাংলা", direction="ltr", tesseract_code="ben", family="indic", indic_script=True),
    "mr": LanguageInfo(code="mr", bcp47="mr-IN", name="Marathi", native_name="मराठी", direction="ltr", tesseract_code="mar", family="indic", indic_script=True),
    "gu": LanguageInfo(code="gu", bcp47="gu-IN", name="Gujarati", native_name="ગુજરાતી", direction="ltr", tesseract_code="guj", family="indic", indic_script=True),
    "pa": LanguageInfo(code="pa", bcp47="pa-IN", name="Punjabi", native_name="ਪੰਜਾਬੀ", direction="ltr", tesseract_code="pan", family="indic", indic_script=True),
    "sa": LanguageInfo(code="sa", bcp47="sa-IN", name="Sanskrit", native_name="संस्कृतम्", direction="ltr", tesseract_code="san", family="indic", indic_script=True),
    "ar": LanguageInfo(code="ar", bcp47="ar-SA", name="Arabic", native_name="العربية", direction="rtl", tesseract_code="ara", family="semitic"),
    "ur": LanguageInfo(code="ur", bcp47="ur-PK", name="Urdu", native_name="اردو", direction="rtl", tesseract_code="urd", family="semitic"),
    "zh": LanguageInfo(code="zh", bcp47="zh-CN", name="Chinese (Simplified)", native_name="简体中文", direction="ltr", tesseract_code="chi_sim", family="cjk"),
    "ja": LanguageInfo(code="ja", bcp47="ja-JP", name="Japanese", native_name="日本語", direction="ltr", tesseract_code="jpn", family="cjk"),
    "ko": LanguageInfo(code="ko", bcp47="ko-KR", name="Korean", native_name="한국어", direction="ltr", tesseract_code="kor", family="cjk"),
    "fr": LanguageInfo(code="fr", bcp47="fr-FR", name="French", native_name="Français", direction="ltr", tesseract_code="fra", family="latin"),
    "de": LanguageInfo(code="de", bcp47="de-DE", name="German", native_name="Deutsch", direction="ltr", tesseract_code="deu", family="latin"),
    "es": LanguageInfo(code="es", bcp47="es-ES", name="Spanish", native_name="Español", direction="ltr", tesseract_code="spa", family="latin"),
}

RTL_LANGUAGES = {"ar", "ur", "he", "fa", "ara", "urd", "heb", "fas"}

UNICODE_RANGES = {
    "tamil": (0x0B80, 0x0BFF),
    "devanagari": (0x0900, 0x097F),
    "telugu": (0x0C00, 0x0C7F),
    "malayalam": (0x0D00, 0x0D7F),
    "kannada": (0x0C80, 0x0CFF),
    "bengali": (0x0980, 0x09FF),
    "gujarati": (0x0A80, 0x0AFF),
    "gurmukhi": (0x0A00, 0x0A7F),
    "arabic": (0x0600, 0x06FF),
    "cjk": (0x4E00, 0x9FFF),
    "hiragana": (0x3040, 0x309F),
    "katakana": (0x30A0, 0x30FF),
    "hangul": (0xAC00, 0xD7AF),
}

def detect_script_from_text(text: str) -> Optional[str]:
    """Detect dominant non-Latin script from Unicode character codepoints."""
    counts: Dict[str, int] = {}
    for ch in text:
        cp = ord(ch)
        for script, (start, end) in UNICODE_RANGES.items():
            if start <= cp <= end:
                counts[script] = counts.get(script, 0) + 1
                break
    if not counts:
        return "latin"
    return max(counts.items(), key=lambda x: x[1])[0]

def get_direction_for_script(script_or_lang: str) -> str:
    """Return text direction 'rtl' or 'ltr'."""
    lower = script_or_lang.lower()
    if lower in RTL_LANGUAGES or lower == "arabic":
        return "rtl"
    return "ltr"

def get_tesseract_langs_for_scripts(scripts: List[str]) -> str:
    """Combine tesseract codes for detected scripts, always including 'eng'."""
    mapping = {
        "tamil": "tam",
        "devanagari": "hin",
        "telugu": "tel",
        "malayalam": "mal",
        "kannada": "kan",
        "bengali": "ben",
        "gujarati": "guj",
        "gurmukhi": "pan",
        "arabic": "ara",
        "cjk": "chi_sim",
        "hiragana": "jpn",
        "katakana": "jpn",
        "hangul": "kor",
    }
    codes = {"eng"}
    for s in scripts:
        if s in mapping:
            codes.add(mapping[s])
    return "+".join(sorted(codes))
