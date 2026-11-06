"""
System and Capabilities API Router.
Exposes runtime hardware capabilities, installed Tesseract OCR languages,
and converter availability.
"""
from fastapi import APIRouter
from backend.app.config.settings import settings
from backend.app.schemas.capabilities import SystemCapabilities, ConverterInfo
from backend.app.services.ocr.tesseract_service import ocr_service
from backend.app.services.converters.orchestrator import conversion_orchestrator
from backend.app.constants.languages import TESSERACT_LANG_NAMES

router = APIRouter(tags=["System"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/capabilities", response_model=SystemCapabilities)
def get_capabilities():
    hw = settings.detect_hardware_capabilities()
    installed_langs = ocr_service.get_installed_languages()
    conv_caps = conversion_orchestrator.get_all_capabilities()

    converters_info = [
        ConverterInfo(
            name=cap.engine_name,
            available=cap.is_available,
            version=cap.version,
            description=cap.notes
        )
        for cap in conv_caps.values()
    ]

    lang_details = [
        {
            "code": code,
            "name": TESSERACT_LANG_NAMES.get(code, code),
            "installed": True
        }
        for code in installed_langs
    ]

    return SystemCapabilities(
        platform=hw["platform"],
        cpuCount=hw["cpu_count"],
        totalRamGb=hw["total_ram_gb"],
        gpuAvailable=hw["gpu_available"],
        gpuName=hw["gpu_name"],
        gpuMemoryMb=hw["gpu_memory_mb"],
        recommendedDevice=hw["recommended_device"],
        defaultWorkers=hw["default_workers"],
        installedOcrLanguages=installed_langs,
        languageDetails=lang_details,
        converters=converters_info,
        defaultConverter=settings.DEFAULT_CONVERTER
    )
