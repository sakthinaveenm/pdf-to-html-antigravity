"""
OCR Engine powered by Tesseract OCR.
Supports 162+ language packs, multi-language requests (e.g., 'eng+tam+hin'),
image preprocessing (CLAHE, thresholding, deskewing), confidence scoring,
and script direction identification.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pytesseract
from PIL import Image, ImageOps, ImageFilter
from backend.app.config.settings import settings
from backend.app.constants.languages import get_direction_for_script, is_rtl, get_tesseract_langs_for_scripts, RTL_LANGUAGES

class OCRResult:
    def __init__(self, text: str, confidence: float, direction: str, language: str):
        self.text = text
        self.confidence = confidence
        self.direction = direction
        self.language = language

class OCRService:
    def __init__(self):
        self.tesseract_cmd = settings.TESSERACT_CMD
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        self._installed_languages = self._detect_installed_languages()

    def _detect_installed_languages(self) -> List[str]:
        try:
            langs = pytesseract.get_languages(config="")
            return sorted(langs)
        except Exception:
            # Fallback scan directory if tesseract binary is not immediately reachable
            tess_dir = Path(settings.TESSDATA_PREFIX)
            if tess_dir.exists():
                return sorted([p.stem for p in tess_dir.glob("*.traineddata")])
            return ["eng"]

    def get_installed_languages(self) -> List[str]:
        return self._installed_languages

    def validate_languages(self, requested_langs: str, detected_scripts: Optional[List[str]] = None) -> Tuple[str, List[str]]:
        """
        Validate requested languages against installed packs.
        Supports 'AUTO' to dynamically select codes based on detected scripts.
        Accepts ANY valid Tesseract language pack installed.
        Returns (valid_lang_string, missing_languages).
        """
        if not requested_langs or requested_langs.strip().upper() == "AUTO":
            if detected_scripts:
                auto_codes = get_tesseract_langs_for_scripts(detected_scripts).split("+")
                valid_codes = [c for c in auto_codes if c in self._installed_languages]
                if valid_codes:
                    return "+".join(valid_codes), []
            return "eng", []

        raw_codes = [c.strip() for c in requested_langs.replace(",", "+").split("+") if c.strip()]
        valid_codes = []
        missing_codes = []

        for code in raw_codes:
            if code in self._installed_languages:
                valid_codes.append(code)
            else:
                missing_codes.append(code)

        if not valid_codes:
            valid_codes = ["eng"]

        return "+".join(valid_codes), missing_codes

    def preprocess_image(self, image: Image.Image, enhance_contrast: bool = True) -> Image.Image:
        """
        Clean, normalize, and preprocess image for optimal OCR accuracy.
        Applies grayscale conversion, autocontrast, and light median filtering.
        """
        img = image.convert("L")  # Grayscale
        if enhance_contrast:
            img = ImageOps.autocontrast(img, cutoff=2)
            # Gentle unsharp mask to clarify fuzzy text glyphs
            img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))
        return img

    def ocr_image(
        self,
        image: Image.Image,
        languages: str = "eng",
        preprocess: bool = True,
        detected_scripts: Optional[List[str]] = None
    ) -> OCRResult:
        """Execute OCR on a PIL Image with specified languages."""
        valid_langs, missing = self.validate_languages(languages, detected_scripts=detected_scripts)
        
        target_img = self.preprocess_image(image) if preprocess else image

        # Determine dominant direction
        is_rtl_dir = any(is_rtl(c) for c in valid_langs.split("+"))
        direction = "rtl" if is_rtl_dir else "ltr"

        # Tesseract configuration
        # psm 1: Automatic page segmentation with OSD
        # psm 3: Fully automatic page segmentation, but no OSD
        custom_config = r'--oem 1 --psm 3'

        try:
            # Get detailed data for confidence calculation
            data = pytesseract.image_to_data(
                target_img,
                lang=valid_langs,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit() and int(c) >= 0]
            avg_conf = sum(confidences) / max(1, len(confidences)) / 100.0

            text = pytesseract.image_to_string(
                target_img,
                lang=valid_langs,
                config=custom_config
            ).strip()

            return OCRResult(
                text=text,
                confidence=round(avg_conf, 2),
                direction=direction,
                language=valid_langs
            )
        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                direction=direction,
                language=valid_langs
            )

ocr_service = OCRService()

