"""
Generates rich multilingual test PDF documents in samples/
covering English, Tamil, Hindi, Arabic (RTL), Chinese, complex tables,
mathematical formulas, and a scanned raster page for OCR testing.
"""
from pathlib import Path
import os
import pymupdf as fitz
from PIL import Image, ImageDraw

SAMPLES_DIR = Path("samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# Find Unicode font
FONT_PATH = None
candidates = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arialuni.ttf"
]
for c in candidates:
    if os.path.exists(c):
        FONT_PATH = c
        break

def get_font_kw():
    if FONT_PATH:
        return {"fontname": "unicode_font", "fontfile": FONT_PATH}
    return {}

def generate_english_pdf():
    doc = fitz.open()
    fkw = get_font_kw()
    page1 = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page1.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    
    fname = "unicode_font" if FONT_PATH else "helv"
    page1.insert_text((50, 70), "Multilingual Document Processing Architecture", fontsize=20, fontname=fname)
    page1.insert_text((50, 105), "1. Introduction to Digital Text Normalization", fontsize=15, fontname=fname)
    page1.insert_text((50, 135), "Digital document preservation requires accurate conversion from vector formats into semantic HTML.", fontsize=11, fontname=fname)
    page1.insert_text((50, 155), "Traditional PDF viewers rely on canvas element rendering or pre-rasterized tiles, losing real text semantics.", fontsize=11, fontname=fname)
    page1.insert_text((50, 175), "By generating clean DOM text nodes, screen readers and editors can freely select, search, and annotate text.", fontsize=11, fontname=fname)
    
    page1.insert_text((50, 215), "2. Core Architectural Principles", fontsize=15, fontname=fname)
    page1.insert_text((50, 240), "- Semantic HTML elements instead of absolute position divs", fontsize=11, fontname=fname)
    page1.insert_text((50, 260), "- Durable text quote and Unicode position anchoring for annotations", fontsize=11, fontname=fname)
    page1.insert_text((50, 280), "- Multi-language OCR integration supporting Indic and RTL scripts", fontsize=11, fontname=fname)
    page1.insert_text((50, 300), "- Offline-first self-contained ZIP bundles", fontsize=11, fontname=fname)

    page1.insert_text((50, 340), "Mathematical Formulation", fontsize=14, fontname=fname)
    page1.insert_text((50, 365), "E = mc^2 and sum(x_i) = X", fontsize=11, fontname=fname)

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page2.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    page2.insert_text((50, 70), "3. Performance Benchmarks", fontsize=16, fontname=fname)
    page2.insert_text((50, 100), "Conversion benchmarks across varying document complexities demonstrate bounded memory utilization.", fontsize=11, fontname=fname)
    
    doc.save(str(SAMPLES_DIR / "sample_english.pdf"))
    doc.close()

def generate_tamil_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    fname = "unicode_font" if FONT_PATH else "helv"

    page.insert_text((50, 70), "தமிழ் இலக்கியம் மற்றும் வரலாறு", fontsize=20, fontname=fname)
    page.insert_text((50, 110), "அறிமுகம்", fontsize=16, fontname=fname)
    page.insert_text((50, 140), "தமிழ் மொழி உலகின் மிகத் தொன்மையான செம்மொழிகளில் ஒன்றாகும்.", fontsize=12, fontname=fname)
    page.insert_text((50, 165), "இது திராவிட மொழிக் குடும்பத்தைச் சேர்ந்த முதன்மையான மொழியாகும்.", fontsize=12, fontname=fname)
    page.insert_text((50, 190), "சங்க இலக்கியங்கள் தமிழர்களின் வாழ்வியல் மற்றும் அறநெறிகளைப் பறைசாற்றுகின்றன.", fontsize=12, fontname=fname)

    page.insert_text((50, 230), "திருக்குறள் சிறப்பு", fontsize=16, fontname=fname)
    page.insert_text((50, 260), "அகர முதல எழுத்தெல்லாம் ஆதி", fontsize=12, fontname=fname)
    page.insert_text((50, 285), "பகவன் முதற்றே உலகு.", fontsize=12, fontname=fname)
    page.insert_text((50, 320), "கற்க கசடறக் கற்பவை கற்றபின்", fontsize=12, fontname=fname)
    page.insert_text((50, 345), "நிற்க அதற்குத் தக.", fontsize=12, fontname=fname)

    doc.save(str(SAMPLES_DIR / "sample_tamil.pdf"))
    doc.close()

def generate_hindi_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    fname = "unicode_font" if FONT_PATH else "helv"

    page.insert_text((50, 70), "हिन्दी साहित्य का संक्षिप्त इतिहास", fontsize=20, fontname=fname)
    page.insert_text((50, 110), "प्रस्तावना", fontsize=16, fontname=fname)
    page.insert_text((50, 140), "हिन्दी विश्व की प्रमुख भाषाओं में से एक है और भारत की आधिकारिक भाषा है।", fontsize=12, fontname=fname)
    page.insert_text((50, 165), "देवनागरी लिपि में लिखी जाने वाली यह भाषा अत्यंत समृद्ध और वैज्ञानिक है।", fontsize=12, fontname=fname)
    
    page.insert_text((50, 205), "मुंशी प्रेमचंद का योगदान", fontsize=16, fontname=fname)
    page.insert_text((50, 235), "उपन्यास सम्राट प्रेमचंद ने भारतीय ग्रामीण समाज का यथार्थवादी चित्रण किया।", fontsize=12, fontname=fname)
    page.insert_text((50, 260), "गोदान और गबन जैसे उपन्यास आज भी मील के पत्थर माने जाते हैं।", fontsize=12, fontname=fname)

    doc.save(str(SAMPLES_DIR / "sample_hindi.pdf"))
    doc.close()

def generate_arabic_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    fname = "unicode_font" if FONT_PATH else "helv"

    page.insert_text((100, 70), "تاريخ اللغة العربية وآدابها", fontsize=20, fontname=fname)
    page.insert_text((100, 110), "المقدمة", fontsize=16, fontname=fname)
    page.insert_text((100, 140), "تعد اللغة العربية إحدى أكثر اللغات انتشاراً ونمواً في العالم.", fontsize=12, fontname=fname)
    page.insert_text((100, 165), "تتميز بثرائها اللغوي وبلاغتها العالية ونظامها النحوي الدقيق.", fontsize=12, fontname=fname)
    page.insert_text((100, 190), "كتبت بها أعظم المؤلفات العلمية والأدبية عبر العصور التاريخية.", fontsize=12, fontname=fname)
    doc.save(str(SAMPLES_DIR / "sample_arabic.pdf"))
    doc.close()

def generate_chinese_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    fname = "unicode_font" if FONT_PATH else "helv"

    page.insert_text((50, 70), "现代技术与文献数字化", fontsize=20, fontname=fname)
    page.insert_text((50, 110), "引言", fontsize=16, fontname=fname)
    page.insert_text((50, 140), "多语言文档处理平台支持对各种复杂文字进行准确的结构化提取与转换。", fontsize=12, fontname=fname)
    page.insert_text((50, 165), "通过保留原文档的阅读顺序与段落层级，生成完全可选择与编辑的网页内容。", fontsize=12, fontname=fname)
    doc.save(str(SAMPLES_DIR / "sample_chinese.pdf"))
    doc.close()

def generate_tables_and_math_pdf():
    doc = fitz.open()
    fkw = get_font_kw()
    page = doc.new_page(width=595, height=842)
    if FONT_PATH:
        page.insert_font(fontname="unicode_font", fontfile=FONT_PATH)
    fname = "unicode_font" if FONT_PATH else "helv"

    page.insert_text((50, 60), "Scientific Data and Tabular Analysis", fontsize=18, fontname=fname)
    page.insert_text((50, 95), "The following table records experimental accuracy across language models:", fontsize=11, fontname=fname)

    y = 120
    rect = fitz.Rect(50, y, 545, y + 25)
    page.draw_rect(rect, color=(0.8, 0.8, 0.8), fill=(0.95, 0.95, 0.95))
    page.insert_text((60, y + 17), "Language", fontsize=11, fontname=fname)
    page.insert_text((180, y + 17), "Script Family", fontsize=11, fontname=fname)
    page.insert_text((320, y + 17), "Accuracy (%)", fontsize=11, fontname=fname)
    page.insert_text((440, y + 17), "Status", fontsize=11, fontname=fname)

    rows = [
        ("English", "Latin", "99.8%", "Verified"),
        ("Tamil", "Dravidian/Indic", "98.5%", "Verified"),
        ("Hindi", "Devanagari/Indic", "98.9%", "Verified"),
        ("Arabic", "Semitic (RTL)", "97.8%", "Verified"),
        ("Chinese", "CJK Ideographic", "99.1%", "Verified"),
    ]

    for i, (lang, fam, acc, stat) in enumerate(rows):
        row_y = y + 25 * (i + 1)
        page.draw_rect(fitz.Rect(50, row_y, 545, row_y + 25), color=(0.85, 0.85, 0.85))
        page.insert_text((60, row_y + 17), lang, fontsize=10, fontname=fname)
        page.insert_text((180, row_y + 17), fam, fontsize=10, fontname=fname)
        page.insert_text((320, row_y + 17), acc, fontsize=10, fontname=fname)
        page.insert_text((440, row_y + 17), stat, fontsize=10, fontname=fname)

    doc.save(str(SAMPLES_DIR / "sample_tables_math.pdf"))
    doc.close()

def generate_scanned_image_pdf():
    img_width, img_height = 800, 1100
    img = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(img)

    draw.text((60, 60), "Historical Archive - Scanned Document", fill="black")
    draw.text((60, 100), "Confidential Records 1948", fill="black")
    draw.text((60, 140), "This page has no digital text font stream.", fill="black")
    draw.text((60, 170), "It is a scanned photographic facsimile requiring Tesseract OCR.", fill="black")
    draw.text((60, 200), "Optical character recognition converts this bitmap to selectable DOM nodes.", fill="black")

    img_path = SAMPLES_DIR / "temp_scanned.png"
    img.save(str(img_path))

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_image(page.rect, filename=str(img_path))
    doc.save(str(SAMPLES_DIR / "sample_scanned.pdf"))
    doc.close()
    
    if img_path.exists():
        img_path.unlink()

def main():
    print("Generating comprehensive test sample PDFs...")
    generate_english_pdf()
    generate_tamil_pdf()
    generate_hindi_pdf()
    generate_arabic_pdf()
    generate_chinese_pdf()
    generate_tables_and_math_pdf()
    generate_scanned_image_pdf()
    print("All sample PDFs created successfully in samples/")

if __name__ == "__main__":
    main()
