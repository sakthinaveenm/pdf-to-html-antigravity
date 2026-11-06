"""
Legacy Indic Font to Unicode Devanagari Decoder.
Handles non-Unicode 8-bit legacy DTP fonts historically used in Indian textbooks
(NCERT, state boards, PageMaker, InDesign):
- Walkman-Chanakya (Chanakya 905 Normal/Bold/Italic)
- Kruti Dev 010 / DevLys 010 / Shusha / 4C-Gandhi
"""
import re
from typing import Tuple, List

# Known legacy Indic font family patterns
LEGACY_INDIC_FONTS = (
    "chanakya", "walkman-chanakya", "walkmanchanakya",
    "kruti", "krutidev", "devlys", "shusha", "aps-dv",
    "shivaji", "bilingual", "preeti", "kantipur", "akruti",
    "shree-dev", "shreedev", "dv-", "richa", "varun", "suhas",
    "4c-", "chanakya905"
)

# Signature ASCII tokens that appear in KrutiDev / Chanakya text with high frequency
SIGNATURE_LEGACY_TOKENS = [
    "osq", "esa", "rfkk", "dks", "vksj", "vkius", "oqqn", "mís'",
    "ys[kkadu", "lk>snkjh", "ifjlfkfr;ksa", "gsa", "gsa", "gsaA", "gsa_",
    "rFkk", "dks", "vkSj", "vkius", "oqQN", "mís'", "ys[kkadu", "lk>snkjh",
    "ifjfLFkfr;ksa", "gSA", "gSaA", "vr%", "fy,", "vfèkd", "fn;k", "feydj"
]

def is_legacy_indic_font(font_name: str) -> bool:
    """Check if a font name belongs to a legacy non-Unicode Indic font family."""
    if not font_name:
        return False
    fn = font_name.lower()
    return any(lf in fn for lf in LEGACY_INDIC_FONTS)

def detect_legacy_indic_text(text: str) -> Tuple[bool, str]:
    """
    Analyzes text to detect if it is encoded in a legacy 8-bit Indic font
    (e.g., Chanakya or KrutiDev) rather than true Latin English.
    Returns (is_legacy, font_family_guess).
    """
    if not text or len(text.strip()) < 10:
        return False, ""

    sample = text[:2000]
    hits = sum(1 for token in SIGNATURE_LEGACY_TOKENS if token in sample)

    if hits >= 2:
        return True, "chanakya"
    return False, ""

# Chanakya multi-character mapping table (ordered by length descending)
CHANAKYA_MULTI_MAP = [
    ("mís';", "उद्देश्य"),
    ("mís'", "उद्देश्य"),
    ("oqQN", "कुछ"),
    ("osQ", "के"),
    ("sQ", "के"),
    ("losaQxs", "सकेंगे"),
    ("lsaQxs", "सकेंगे"),
    ("saQxs", "केंगे"),
    ("oQ", "क"),
    ("iQeZ", "फर्म"),
    ("iQ", "फ़"),
    ("izfØ;k", "प्रक्रिया"),
    ("izkjaHk", "प्रारंभ"),
    ("iz", "प्र"),
    ("Ø", "क्र"),
    ("xz", "ग्र"),
    ("nz", "द्र"),
    ("oz", "व्र"),
    ("Hkz", "भ्र"),
    ("lz", "स्र"),
    ("I;k", "ख्या"),
    ("i¼fr", "पद्धति"),
    ("lwphc¼", "सूचीबद्ध"),
    ("c¼", "बद्ध"),
    ("¼", "द्ध"),
    ("½", "द्य"),
    ("¿", "द्भ"),
    ("À", "द्म"),
    ("Á", "द्ब"),
    ("Â", "ह्य"),
    ("Ã", "ह्न"),
    ("Ä", "ह्ण"),
    ("Å", "ह्म"),
    ("Æ", "ह्ल"),
    ("Ç", "ह्व"),
    ("È", "ष्ट"),
    ("É", "ष्ठ"),
    ("Ê", "ङ्क"),
    ("Ë", "ङ्ग"),
    ("Ì", "ञ्च"),
    ("Í", "ज्ञ"),
    ("Î", "द्द"),
    ("Ï", "ट्ट"),
    ("Ð", "ट्ठ"),
    ("Ñ", "ड्ड"),
    ("Ò", "ड्ढ"),
    ("Ó", "क्त"),
    ("Ô", "क्त"),
    ("Õ", "रु"),
    ("Ö", "रू"),
    ("×", "त्र"),
    ("Ùk", "त्त"),
    ("Ù", "त्त"),
    ("Ú", "न्न"),
    ("Û", "ल्ल"),
    ("Ü", "श्व"),
    ("Ý", "फ्र"),
    ("Þ", "द्र"),
    ("ß", "प्र"),
    ("à", "श्र"),
    ("á", "ट्र"),
    ("â", "ड्र"),
    ("ã", "ढ्र"),
    ("ä", "छ्र"),
    ("èk", "ध"),
    ("é", "ण"),
    ("ê", "य"),
    ("ë", "स"),
    ("ì", "ह"),
    ("í", "द्"),
    ("î", "ध"),
    ("ï", "र"),
    ("ð", "ष"),
    ("ñ", "त्र"),
    ("ò", "ज्ञ"),
    ("ó", "श"),
    ("ô", "ष"),
    ("õ", "ह"),
    ("ö", "क्ष"),
    ("÷", "त्र"),
    ("ø", "ज्ञ"),
    ("ù", "श्र"),
    ("ú", "ं"),
    ("û", "ः"),
    ("ü", "ँ"),
    ("ý", "ऽ"),
    ("þ", "्"),
    ("ÿ", "़"),
    ("Hk", "भ"),
    ("Fk", "थ"),
    ("'k", "श"),
    ("[k", "ख"),
    ("?k", "घ"),
    (".k", "ण"),
    ("vkS", "औ"),
    ("vk", "आ"),
    ("vks", "ओ"),
    ("bZ", "ई"),
    ("mQ", "ऊ"),
    ("e`", "मृ"),
    ("d`", "कृ"),
    ("`", "ृ"),
    ("—", "—"),
    ("μ", "—"),
    ("¡", "ँ"),
    ("_", "।"),
    ("", "•"),
    ("\uf06c", "•"),
]

CHANAKYA_CHAR_MAP = {
    'a': 'ं', 'b': 'इ', 'c': 'ब', 'd': 'क', 'e': 'म',
    'g': 'ग', 'h': 'ी', 'i': 'प', 'j': 'र', 'k': 'ा',
    'l': 'स', 'm': 'उ', 'n': 'द', 'o': 'व', 'p': 'च',
    'q': 'ु', 'r': 'त', 's': 'े', 't': 'ज', 'u': 'न',
    'v': 'अ', 'w': 'ू', 'x': 'ग', 'y': 'ल', 'z': '्र',
    'A': '।', 'B': 'ठ', 'C': 'ब्', 'D': 'क्', 'E': 'ढ',
    'F': 'थ्', 'G': 'घ', 'H': 'भ्', 'I': 'क्ष', 'J': 'ज्ञ',
    'K': 'ज्ञ', 'L': 'स्', 'M': 'ङ', 'N': 'छ', 'O': 'व्',
    'P': 'च्', 'Q': 'फ़', 'R': 'त्', 'S': 'े', 'T': 'त्',
    'U': 'न्', 'V': 'ट', 'W': 'ठ', 'X': 'ग्', 'Y': 'ड',
    'Z': 'र्',
    '[': 'ख्', ']': '्', '{': 'दृ', '}': 'द्ध',
    ';': 'य', ':': 'ः', '/': 'ध्', ',': 'ए',
    '>': 'झ', '<': 'ष्', '"': 'ष्', "'": 'श्',
    '&': 'र्',
}

def decode_chanakya_to_unicode(text: str) -> str:
    """
    Decodes text from Walkman-Chanakya font encoding to standard Unicode Devanagari.
    """
    if not text:
        return ""

    s = text

    # Step 1: Multi-char ligatures and punctuation
    for src, dst in CHANAKYA_MULTI_MAP:
        s = s.replace(src, dst)

    # Step 2: Chhoti 'i' (f) pre-base matra reordering
    def _reorder_i(match):
        chars = match.group(1)
        mapped = "".join(CHANAKYA_CHAR_MAP.get(c, c) for c in chars)
        return mapped + "ि"

    s = re.sub(r'f([A-Za-z\[\]\<\>\/\,\.\;\'\"\{\}\—\-\+]+)', _reorder_i, s)

    # Step 3: Reph (Z) post-base reordering
    def _reorder_reph(match):
        chars = match.group(1)
        mapped = "".join(CHANAKYA_CHAR_MAP.get(ch, ch) for ch in chars)
        return "र्" + mapped

    s = re.sub(r'([A-Za-z\[\]\<\>\/\,\.\;\'\"\{\}]+)Z', _reorder_reph, s)

    # Step 4: Map remaining single characters
    chars_out = []
    for ch in s:
        chars_out.append(CHANAKYA_CHAR_MAP.get(ch, ch))
    out = "".join(chars_out)

    # Step 5: Post-processing phonetic vowel and matra ligatures
    post_fixes = [
        ("अा", "आ"),
        ("एे", "ऐ"),
        ("उू", "ऊ"),
        ("ओा", "आ"),
        ("गाे", "गो"),
        ("गाें", "गों"),
        ("लाे", "लो"),
        ("काे", "को"),
        ("ताे", "तो"),
        ("जाे", "जो"),
        ("साे", "सो"),
        ("पाे", "पो"),
        ("बाे", "बो"),
        ("भाे", "भो"),
        ("माे", "मो"),
        ("दाे", "दो"),
        ("राे", "रो"),
        ("हाे", "हो"),
        ("नाे", "नो"),
        ("याे", "यो"),
        ("वाे", "वो"),
        ("षाे", "षो"),
        ("शाे", "शो"),
        ("चाे", "चो"),
        ("गे।", "है।"),
        ("गें।", "हैं।"),
        ("गे", "है"),
        ("गें", "हैं"),
        ("ृत", "अत"),
        ("ृप", "अप"),
        ("ृभ", "अभ"),
        ("ृध", "अध"),
        ("ृस", "अस"),
        ("ृन", "अन"),
        ("ृल", "अल"),
        ("ृक", "अक"),
        ("ृम", "अम"),
        ("ृव", "अव"),
    ]
    for src, dst in post_fixes:
        out = out.replace(src, dst)

    return out

