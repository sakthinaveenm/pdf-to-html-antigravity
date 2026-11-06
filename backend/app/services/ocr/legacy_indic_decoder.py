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

# Fonts known to be pure Latin English (to protect from accidental transliteration)
STANDARD_LATIN_FONTS = (
    "bookman", "arial", "times", "timesnewroman", "minion",
    "minionpro", "helvetica", "courier", "georgia", "verdana",
    "calibri", "tahoma", "garamond", "cambria", "palatino",
    "rupeeforadian"
)

# Signature ASCII tokens that appear in KrutiDev / Chanakya text with high frequency
SIGNATURE_LEGACY_TOKENS = [
    "osq", "esa", "rfkk", "dks", "vksj", "vkius", "oqqn", "mís'",
    "ys[kkadu", "lk>snkjh", "ifjlfkfr;ksa", "gsa", "gsa", "gsaA", "gsa_",
    "rFkk", "dks", "vkSj", "vkius", "oqQN", "mís'", "ys[kkadu", "lk>snkjh",
    "ifjfLFkfr;ksa", "gSA", "gSaA", "vr%", "fy,", "vfèkd", "fn;k", "feydj",
    "ikB~;iqLrd", "vkeq[k", "laLdj.k", "iqueqZæ.k", "fo\"k;&lwph", "vè;k;",
    "osQ", "oQh", "oQ", "d{kk"
]

def is_legacy_indic_font(font_name: str) -> bool:
    """Check if a font name belongs to a legacy non-Unicode Indic font family."""
    if not font_name:
        return False
    fn = font_name.lower()
    return any(lf in fn for lf in LEGACY_INDIC_FONTS)

def is_latin_font(font_name: str) -> bool:
    """Check if font is a known standard Latin/English font."""
    if not font_name:
        return False
    fn = font_name.lower()
    return any(lf in fn for lf in STANDARD_LATIN_FONTS)

def detect_legacy_indic_text(text: str) -> Tuple[bool, str]:
    """
    Analyzes text to detect if it is encoded in a legacy 8-bit Indic font
    (e.g., Chanakya or KrutiDev) rather than true Latin English.
    Returns (is_legacy, font_family_guess).
    """
    if not text or len(text.strip()) < 4:
        return False, ""

    sample = text[:2000]
    hits = sum(1 for token in SIGNATURE_LEGACY_TOKENS if token in sample)

    if hits >= 2:
        return True, "chanakya"
    return False, ""

# Chanakya multi-character compounds and phrases (ordered by length descending)
CHANAKYA_MULTI_MAP = [
    ("izksI+ksQlj", "प्रोफ़ेसर"),
    ("izksi+sQlj", "प्रोफ़ेसर"),
    ("izksi+sQ", "प्रोफ़े"),
    ("mís';", "उद्देश्य"),
    ("mís'", "उद्देश्य"),
    ("vki+Q", "ऑफ़"),
    ("baLVhV~;wV", "इंस्टीट्यूट"),
    ("ikB~;iqLrdksa", "पाठ्यपुस्तकों"),
    ("ikB~;iqLrd", "पाठ्यपुस्तक"),
    ("ikB~;iqLrosaQ", "पाठ्यपुस्तकें"),
    ("ikB~;p;kZ", "पाठ्यचर्या"),
    ("ikB~;Øe", "पाठ्यक्रम"),
    ("ikB~; lkexzh", "पाठ्य सामग्री"),
    ("ikB~;", "पाठ्य"),
    ("ys[kk'kkL=k", "लेखाशास्त्र"),
    ("ys[kk'kkL=", "लेखाशास्त्र"),
    ("ys[kkadu", "लेखांकन"),
    ("lk>snkjh", "साझेदारी"),
    ("lk>snkjksa", "साझेदारों"),
    ("lk>snkj", "साझेदार"),
    ("voèkkj.kk,¡", "अवधारणाएँ"),
    ("vo/kj.kk,¡", "अवधारणाएँ"),
    ("vkèkkjHkwr", "आधारभूत"),
    ("vk/kjHkwr", "आधारभूत"),
    ("vkèkkfjr", "आधारित"),
    ("fo\"k;&lwph", "विषय-सूची"),
    ("fo\"k;", "विषय"),
    ("lfefr", "समिति"),
    ("vkeq[k", "आमुख"),
    ("iqul±;kstu", "पुनर्संयोजन"),
    ("iquxZBu%", "पुनर्गठन : "),
    ("iquxZBu", "पुनर्गठन"),
    ("iqujh{k.k", "पुनरीक्षण"),
    ("iqueqZæ.k", "पुनर्मुद्रण"),
    ("la'kksf/r", "संशोधित"),
    ("la'kksfèkr", "संशोधित"),
    ("laLdj.k", "संस्करण"),
    ("izFke", "प्रथम"),
    ("vizSy", "अप्रैल"),
    ("pS=k", "चैत्र"),
    ("dkfrZd", "कार्तिक"),
    ("vxzgk;.k", "अग्रहायण"),
    ("ifj\"kn~", "परिषद्"),
    ("ifj\"kn", "परिषद्"),
    ("'kSf{kd", "शैक्षिक"),
    ("vuqla/ku", "अनुसंधान"),
    ("izf'k{k.k", "प्रशिक्षण"),
    ("jk\"Vªh;", "राष्ट्रीय"),
    ("jk\"Vªh", "राष्ट्रीय"),
    ("jk\"Vª", "राष्ट्र"),
    ("fl¼kar", "सिद्धांत"),
    ("fojklr", "विरासत"),
    ("foijhr", "विपरीत"),
    ("izHkkoo'k", "प्रभाववश"),
    ("O;oLFkk", "व्यवस्था"),
    ("cqfu;knh", "बुनियादी"),
    ("Ldwyh", "स्कूली"),
    ("Ldwy", "स्कूल"),
    ("cPpksa", "बच्चों"),
    ("dksfoM&19", "कोविड-19"),
    ("egkekjh", "महामारी"),
    ("fo|kfFkZ;ksa", "विद्यार्थियों"),
    ("jpukRed", "रचनात्मक"),
    ("vuqHkokRed", "अनुभवात्मक"),
    ("i`\"BHkwfe", "पृष्ठभूमि"),
    ("lsokfuo`Ùk", "सेवानिवृत्त"),
    ("fuxjkuh", "निगरानी"),
    ("ekWfuVfjax", "मॉनिटरिंग"),
    ("desVh", "कमेटी"),
    ("dydÙkk", "कलकत्ता"),
    ("fo'ofo|ky;", "विश्वविद्यालय"),
    ("dksydkrk", "कोलकाता"),
    ("lykgdkj", "सलाहकार"),
    ("funs'kd", "निदेशक"),
    ("fnYyh", "दिल्ली"),
    ("u;h fnYyh", "नयी दिल्ली"),
    ("egkjktk vxzlsu", "महाराजा अग्रसेन"),
    ("esustesaV", "मैनेजमेंट"),
    ("eSustesaV", "मैनेजमेंट"),
    ("LVMht+", "स्टडीज़"),
    ("ifjlaifÙk;ksa", "परिसंपत्तियों"),
    ("nkf;Roksa", "दायित्वों"),
    ("iqueZwY;kadu", "पुनर्मूल्यांकन"),
    ("lafpr", "संचित"),
    ("ykHkksa", "लाभों"),
    ("gkfu;ksa", "हानियों"),
    ("lek;kstu", "समायोजन"),
    ("iw¡th", "पूँजी"),
    ("e`R;q", "मृत्यु"),
    ("fo?kVu", "विघटन"),
    ("fuiVkjk", "निपटारा"),
    ("O;ogkj", "व्यवहार"),
    ("vuqj{k.k", "अनुरक्षण"),
    ("foHkktu", "विभाजन"),
    ("xkjaVh", "गारंटी"),
    ("iwoZ", "पूर्व"),
    ("izos'k", "प्रवेश"),
    ("vuqikr", "अनुपात"),
    ("R;kx", "त्याग"),
    ("vfHkykHk", "अभिलाभ"),
    ("[;kfr", "ख्याति"),
    ("fof'k\"V", "विशिष्ट"),
    ("igyw", "पहलू"),
    ("igy", "पहलू"),
    ("d{kk", "कक्षा"),
    ("oQh", "की"),
    ("osQ", "के"),
    ("sQ", "के"),
    ("oQ", "क"),
    ("iQeZ", "फर्म"),
    ("iQ", "फ़"),
    ("iQhV", "फ़ीट"),
    ("iQksu", "फ़ोन"),
    ("iQksVks", "फ़ोटो"),
    ("losaQxs", "सकेंगे"),
    ("lsaQxs", "सकेंगे"),
    ("saQxs", "केंगे"),
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
    ("Å", "ऊ"),
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
    ("Ñ", "कृ"),
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
    ("èkk", "धा"),
    ("èk", "ध"),
    ("è", "ध्"),
    ("é", "ण"),
    ("ê", "य"),
    ("ë", "स"),
    ("ì", "ह"),
    ("í", "द्द"),
    ("î", "ह्र"),
    ("ï", "र"),
    ("ð", "ष्ट"),
    ("ñ", "त्र"),
    ("ò", "ज्ञ"),
    ("ó", "श्च"),
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
    # Stem-based combinations (half glyph + vertical stem 'k' = full letter; 'kk' = letter + aa matra)
    ("'kk", "शा"), ("'k", "श"), ("'", "श्"),
    ("\"kk", "षा"), ("\"k", "ष"), ("\"", "ष्"),
    ("[kk", "खा"), ("[k", "ख"), ("[", "ख्"),
    ("?kk", "घा"), ("?k", "घ"),
    ("{kk", "क्षा"), ("{k", "क्ष"), ("{", "क्ष्"),
    ("Fkk", "था"), ("Fk", "थ"), ("F", "थ्"),
    ("Hkk", "भा"), ("Hk", "भ"), ("H", "भ्"),
    (".kk", "णा"), (".k", "ण"),
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
    ("±", "र्"),
    ("æ", "द्र"),
    ("ª", "्र"),
    (":ijs[kk", "रूपरेखा"),
    (":i", "रूप"),
    ("•", "ख"),
    ("=kk", "त्रा"),
    ("=k", "त्र"),
    ("=", "त्र"),
    ("~", "्"),
    ("L=", "स्त्र"),
    ("Ld", "स्क"),
    ("LFk", "स्थ"),
    ("]", ","),
]

CHANAKYA_CHAR_MAP = {
    'a': 'ं', 'b': 'इ', 'c': 'ब', 'd': 'क', 'e': 'म',
    'g': 'ह', 'h': 'ी', 'i': 'प', 'j': 'र', 'k': 'ा',
    'l': 'स', 'm': 'उ', 'n': 'द', 'o': 'व', 'p': 'च',
    'q': 'ु', 'r': 'त', 's': 'े', 't': 'ज', 'u': 'न',
    'v': 'अ', 'w': 'ू', 'x': 'ग', 'y': 'ल', 'z': '्र',
    'A': '।', 'B': 'ठ', 'C': 'ब्', 'D': 'क्', 'E': 'ढ',
    'G': 'घ', 'J': 'ज्ञ', 'K': 'ज्ञ', 'L': 'स्', 'M': 'ङ',
    'N': 'छ', 'O': 'व्', 'P': 'च्', 'Q': 'फ़', 'R': 'त्',
    'S': 'ै', 'T': 'त्', 'U': 'न्', 'V': 'ट', 'W': 'ठ',
    'X': 'ग्', 'Y': 'ड',
    ';': 'य', ':': 'ः', '/': 'ध्', ',': 'ए',
    '>': 'झ', '<': 'ढ',
    '&': '-', '+': '़',
}

def decode_chanakya_to_unicode(text: str) -> str:
    """
    Decodes text from Walkman-Chanakya / KrutiDev font encoding to standard Unicode Devanagari.
    Accurately handles pre-base 'i' matras, post-base 'Z' rephs, vertical stem 'k' ligatures, nuktas.
    """
    if not text:
        return ""

    s = text

    # Step 1: Multi-char ligatures, dictionary compounds, vertical stem pairs, and symbols
    for src, dst in CHANAKYA_MULTI_MAP:
        s = s.replace(src, dst)

    # Step 2: Chhoti 'i' (f) pre-base matra reordering
    # In Walkman-Chanakya, 'f' precedes the consonant/conjunct (single full consonant or half+full consonant)
    def repl_i(m):
        consonant = m.group(1)
        mapped_c = "".join(CHANAKYA_CHAR_MAP.get(ch, ch) for ch in consonant)
        return mapped_c + "ि"

    s = re.sub(r'f([LFHC\.\èCDPTUX\'\"\[]?[\u0900-\u097F]|[LFHC\.\èCDPTUX\'\"\[]?[a-z])', repl_i, s)

    # Step 3: Reph 'Z' reordering on raw characters before char mapping
    # Move Z before the preceding single consonant / syllable
    def repl_reph(m):
        syllable = m.group(1)
        mapped_s = "".join(CHANAKYA_CHAR_MAP.get(ch, ch) for ch in syllable)
        return "र्" + mapped_s

    s = re.sub(r'([A-Za-z\u0900-\u097F][\u093e\u093f\u0940\u0941\u0942\u0947\u0948\u094b\u094c]?)Z', repl_reph, s)

    # Step 4: Map remaining single characters
    out = []
    for ch in s:
        out.append(CHANAKYA_CHAR_MAP.get(ch, ch))
    res = "".join(out)

    # Step 5: Post cleanups & nuktas
    res = res.replace("ड+", "ड़").replace("ढ+", "ढ़").replace("ज+", "ज़").replace("फ+", "फ़")
    res = res.replace("ाे", "ो").replace("ाै", "ौ")
    # Clean up commas vs Devanagari 'ए'
    res = re.sub(r'([0-9])ए', r'\1,', res)
    return res
