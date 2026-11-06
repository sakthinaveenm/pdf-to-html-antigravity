"""
Multilingual language constants, universal script classifications, and Tesseract mappings.
Supports ANY document language and ANY OCR language across the entire Unicode space.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class LanguageInfo(BaseModel):
    code: str              # ISO 639-1 or 639-3 (e.g., 'ta', 'hi', 'ar', 'ru')
    bcp47: str             # BCP-47 tag (e.g., 'ta-IN', 'ar-SA', 'zh-CN', 'ru-RU')
    name: str              # English name
    native_name: str       # Native script name
    direction: str         # 'ltr' or 'rtl'
    tesseract_code: str    # Tesseract language pack code
    family: str            # 'indic', 'semitic', 'cjk', 'latin', 'cyrillic', 'hellenic', etc.
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
    "ru": LanguageInfo(code="ru", bcp47="ru-RU", name="Russian", native_name="Русский", direction="ltr", tesseract_code="rus", family="cyrillic"),
    "he": LanguageInfo(code="he", bcp47="he-IL", name="Hebrew", native_name="עברית", direction="rtl", tesseract_code="heb", family="semitic"),
    "th": LanguageInfo(code="th", bcp47="th-TH", name="Thai", native_name="ไทย", direction="ltr", tesseract_code="tha", family="tai-kadai"),
    "fa": LanguageInfo(code="fa", bcp47="fa-IR", name="Persian", native_name="فارسی", direction="rtl", tesseract_code="fas", family="iranian"),
    "vi": LanguageInfo(code="vi", bcp47="vi-VN", name="Vietnamese", native_name="Tiếng Việt", direction="ltr", tesseract_code="vie", family="austroasiatic"),
    "pt": LanguageInfo(code="pt", bcp47="pt-BR", name="Portuguese", native_name="Português", direction="ltr", tesseract_code="por", family="latin"),
    "it": LanguageInfo(code="it", bcp47="it-IT", name="Italian", native_name="Italiano", direction="ltr", tesseract_code="ita", family="latin"),
    "ne": LanguageInfo(code="ne", bcp47="ne-NP", name="Nepali", native_name="नेपाली", direction="ltr", tesseract_code="nep", family="indic", indic_script=True),
    "el": LanguageInfo(code="el", bcp47="el-GR", name="Greek", native_name="Ελληνικά", direction="ltr", tesseract_code="ell", family="hellenic"),
    "tr": LanguageInfo(code="tr", bcp47="tr-TR", name="Turkish", native_name="Türkçe", direction="ltr", tesseract_code="tur", family="turkic"),
}

RTL_LANGUAGES = {
    "ar", "ara", "ur", "urd", "he", "heb", "fa", "fas", "per",
    "ps", "pus", "yi", "yid", "ug", "uig", "sd", "snd", "dv", "div", "syr"
}

RTL_SCRIPTS = {
    "arabic", "arabic_ext", "arabic_supp", "hebrew", "syriac", "thaana"
}

UNICODE_RANGES = {
    # Indic Scripts
    "devanagari": (0x0900, 0x097F),
    "bengali": (0x0980, 0x09FF),
    "gurmukhi": (0x0A00, 0x0A7F),
    "gujarati": (0x0A80, 0x0AFF),
    "odia": (0x0B00, 0x0B7F),
    "tamil": (0x0B80, 0x0BFF),
    "telugu": (0x0C00, 0x0C7F),
    "kannada": (0x0C80, 0x0CFF),
    "malayalam": (0x0D00, 0x0D7F),
    "sinhala": (0x0D80, 0x0DFF),
    "tibetan": (0x0F00, 0x0FFF),

    # Semitic & RTL Scripts
    "arabic": (0x0600, 0x06FF),
    "arabic_ext": (0x0750, 0x077F),
    "arabic_supp": (0x08A0, 0x08FF),
    "syriac": (0x0700, 0x074F),
    "thaana": (0x0780, 0x07BF),
    "hebrew": (0x0590, 0x05FF),

    # Cyrillic & Hellenic
    "cyrillic": (0x0400, 0x052F),
    "greek": (0x0370, 0x03FF),
    "armenian": (0x0530, 0x058F),
    "georgian": (0x10A0, 0x10FF),

    # Southeast Asian
    "thai": (0x0E00, 0x0E7F),
    "lao": (0x0E80, 0x0EFF),
    "myanmar": (0x1000, 0x109F),
    "khmer": (0x1780, 0x17FF),

    # African
    "ethiopic": (0x1200, 0x137F),

    # East Asian (CJK)
    "hiragana": (0x3040, 0x309F),
    "katakana": (0x30A0, 0x30FF),
    "hangul": (0xAC00, 0xD7AF),
    "cjk": (0x4E00, 0x9FFF),
}

SCRIPT_TO_BCP47: Dict[str, str] = {
    "latin": "en",
    "devanagari": "hi",
    "bengali": "bn",
    "gurmukhi": "pa",
    "gujarati": "gu",
    "odia": "or",
    "tamil": "ta",
    "telugu": "te",
    "kannada": "kn",
    "malayalam": "ml",
    "sinhala": "si",
    "tibetan": "bo",
    "arabic": "ar",
    "arabic_ext": "ar",
    "arabic_supp": "ar",
    "syriac": "syr",
    "thaana": "dv",
    "hebrew": "he",
    "cyrillic": "ru",
    "greek": "el",
    "armenian": "hy",
    "georgian": "ka",
    "thai": "th",
    "lao": "lo",
    "myanmar": "my",
    "khmer": "km",
    "ethiopic": "am",
    "hiragana": "ja",
    "katakana": "ja",
    "hangul": "ko",
    "cjk": "zh",
}

SCRIPT_TO_TESSERACT: Dict[str, str] = {
    "latin": "eng",
    "devanagari": "hin",
    "bengali": "ben",
    "gurmukhi": "pan",
    "gujarati": "guj",
    "odia": "ori",
    "tamil": "tam",
    "telugu": "tel",
    "kannada": "kan",
    "malayalam": "mal",
    "sinhala": "sin",
    "tibetan": "bod",
    "arabic": "ara",
    "arabic_ext": "ara",
    "arabic_supp": "ara",
    "syriac": "syr",
    "thaana": "div",
    "hebrew": "heb",
    "cyrillic": "rus",
    "greek": "ell",
    "armenian": "hye",
    "georgian": "kat",
    "thai": "tha",
    "lao": "lao",
    "myanmar": "mya",
    "khmer": "khm",
    "ethiopic": "amh",
    "hiragana": "jpn",
    "katakana": "jpn",
    "hangul": "kor",
    "cjk": "chi_sim",
}

TESSERACT_LANG_NAMES: Dict[str, str] = {
    "afr": "Afrikaans",
    "amh": "Amharic (አማርኛ)",
    "ara": "Arabic (العربية)",
    "asm": "Assamese (অসমীয়া)",
    "aze": "Azerbaijani",
    "aze_cyrl": "Azerbaijani (Cyrillic)",
    "bel": "Belarusian (Беларуская)",
    "ben": "Bengali (বাংলা)",
    "bod": "Tibetan (བོད་ཡིག)",
    "bos": "Bosnian",
    "bre": "Breton",
    "bul": "Bulgarian (Български)",
    "cat": "Catalan",
    "ceb": "Cebuano",
    "ces": "Czech (Čeština)",
    "chi_sim": "Chinese - Simplified (简体中文)",
    "chi_sim_vert": "Chinese - Simplified Vertical",
    "chi_tra": "Chinese - Traditional (繁體中文)",
    "chi_tra_vert": "Chinese - Traditional Vertical",
    "chr": "Cherokee",
    "cos": "Corsican",
    "cym": "Welsh",
    "dan": "Danish (Dansk)",
    "deu": "German (Deutsch)",
    "div": "Divehi (ދިވެހި)",
    "dzo": "Dzongkha (རྫོང་ཁ)",
    "ell": "Greek (Ελληνικά)",
    "eng": "English",
    "enm": "English, Middle",
    "epo": "Esperanto",
    "equ": "Math / Equations",
    "est": "Estonian (Eesti)",
    "eus": "Basque (Euskara)",
    "fas": "Persian / Farsi (فارسی)",
    "fin": "Finnish (Suomi)",
    "fra": "French (Français)",
    "frk": "Frankish",
    "frm": "French, Middle",
    "gle": "Irish (Gaeilge)",
    "glg": "Galician (Galego)",
    "grc": "Greek, Ancient",
    "guj": "Gujarati (ગુજરાતી)",
    "hat": "Haitian Creole",
    "heb": "Hebrew (עברית)",
    "hin": "Hindi (हिन्दी)",
    "hrv": "Croatian (Hrvatski)",
    "hun": "Hungarian (Magyar)",
    "hye": "Armenian (Հայերեն)",
    "iku": "Inuktitut",
    "ind": "Indonesian (Bahasa Indonesia)",
    "isl": "Icelandic (Íslenska)",
    "ita": "Italian (Italiano)",
    "ita_old": "Italian - Old",
    "jav": "Javanese",
    "jpn": "Japanese (日本語)",
    "jpn_vert": "Japanese Vertical (日本語 縦書き)",
    "kan": "Kannada (ಕನ್ನಡ)",
    "kat": "Georgian (ქართული)",
    "kat_old": "Georgian - Old",
    "kaz": "Kazakh (Қазақ)",
    "khm": "Khmer (ភាសាខ្មែរ)",
    "kir": "Kyrgyz (Кыргызча)",
    "kor": "Korean (한국어)",
    "kor_vert": "Korean Vertical",
    "kur": "Kurdish (Kurdî)",
    "lao": "Lao (ພາສາລາວ)",
    "lat": "Latin",
    "lav": "Latvian (Latviešu)",
    "lit": "Lithuanian (Lietuvių)",
    "ltz": "Luxembourgish",
    "mal": "Malayalam (മലയാളം)",
    "mar": "Marathi (मराठी)",
    "mkd": "Macedonian (Македонски)",
    "mlt": "Maltese",
    "mon": "Mongolian (Монгол)",
    "mri": "Maori",
    "msa": "Malay (Bahasa Melayu)",
    "mya": "Burmese (မြန်မာ)",
    "nep": "Nepali (नेपाली)",
    "nld": "Dutch (Nederlands)",
    "nor": "Norwegian (Norsk)",
    "oci": "Occitan",
    "ori": "Odia (ଓଡ଼ିଆ)",
    "osd": "Orientation & Script Detection",
    "pan": "Punjabi (ਪੰਜਾਬੀ)",
    "pol": "Polish (Polski)",
    "por": "Portuguese (Português)",
    "pus": "Pashto (پښتو)",
    "que": "Quechua",
    "ron": "Romanian (Română)",
    "rus": "Russian (Русский)",
    "san": "Sanskrit (संस्कृतम्)",
    "sin": "Sinhala (සිංහල)",
    "slk": "Slovak (Slovenčina)",
    "slv": "Slovenian (Slovenščina)",
    "snd": "Sindhi (سنڌي)",
    "spa": "Spanish (Español)",
    "spa_old": "Spanish - Old",
    "sqi": "Albanian (Shqip)",
    "srp": "Serbian (Српски)",
    "srp_latn": "Serbian (Latin)",
    "sun": "Sundanese",
    "swa": "Swahili (Kiswahili)",
    "swe": "Swedish (Svenska)",
    "syr": "Syriac (ܣܘܪܝܝܐ)",
    "tam": "Tamil (தமிழ்)",
    "tat": "Tatar (Татар)",
    "tel": "Telugu (తెలుగు)",
    "tgk": "Tajik (Тоҷикӣ)",
    "tgl": "Tagalog / Filipino",
    "tha": "Thai (ไทย)",
    "tir": "Tigrinya (ትግርኛ)",
    "ton": "Tongan",
    "tur": "Turkish (Türkçe)",
    "uig": "Uyghur (ئۇيغۇرچە)",
    "ukr": "Ukrainian (Українська)",
    "urd": "Urdu (اردو)",
    "uzb": "Uzbek (Oʻzbek)",
    "uzb_cyrl": "Uzbek (Cyrillic)",
    "vie": "Vietnamese (Tiếng Việt)",
    "yid": "Yiddish (ייִדיש)",
    "yor": "Yoruba (Èdè Yorùbá)",
}

def detect_script_from_text(text: str) -> str:
    """Detect dominant non-Latin script from Unicode character codepoints."""
    if not text:
        return "latin"
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

def is_rtl(lang_or_script: str) -> bool:
    """Check if a language code or script name is written Right-to-Left."""
    if not lang_or_script:
        return False
    lower = lang_or_script.strip().lower()
    # Normalize language tags like 'ar-SA', 'fa-IR', 'ur-PK'
    base_lang = lower.split("-")[0].split("_")[0]
    return (
        lower in RTL_LANGUAGES
        or base_lang in RTL_LANGUAGES
        or lower in RTL_SCRIPTS
    )

def get_direction_for_script(script_or_lang: str) -> str:
    """Return text direction 'rtl' or 'ltr'."""
    return "rtl" if is_rtl(script_or_lang) else "ltr"

def resolve_document_language(user_lang: Optional[str], detected_script: Optional[str]) -> str:
    """
    Resolve the canonical document language:
    - If user explicitly requested a document language (e.g. 'ru', 'fr', 'zh-TW', 'hi'), use it.
    - If user specified 'AUTO' or None, map the detected script to standard BCP-47 / ISO tag.
    - Gracefully defaults to 'en'.
    """
    if user_lang and user_lang.strip().upper() not in ("", "AUTO", "NONE"):
        return user_lang.strip()
    
    if detected_script and detected_script in SCRIPT_TO_BCP47:
        return SCRIPT_TO_BCP47[detected_script]
    
    return "en"

def get_tesseract_langs_for_scripts(scripts: List[str]) -> str:
    """Combine tesseract codes for detected scripts, always including 'eng'."""
    codes = {"eng"}
    for s in scripts:
        s_lower = s.lower()
        if s_lower in SCRIPT_TO_TESSERACT:
            codes.add(SCRIPT_TO_TESSERACT[s_lower])
        elif s_lower in TESSERACT_LANG_NAMES:
            codes.add(s_lower)
    return "+".join(sorted(codes))
