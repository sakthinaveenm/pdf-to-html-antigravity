from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import os
import shutil
import platform
import psutil

class Settings(BaseSettings):
    APP_NAME: str = "Multilingual PDF to HTML Converter"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    ORIGINALS_DIR: Path = STORAGE_DIR / "originals"
    DOCUMENTS_DIR: Path = STORAGE_DIR / "documents"
    SCRATCH_DIR: Path = STORAGE_DIR / "scratch"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{STORAGE_DIR}/jobs.db"
    
    # Worker and concurrency settings
    # Hardware target: AMD Ryzen 7 4800H / Apple Silicon, 16GB RAM, RTX 3050 Ti 4GB VRAM
    MAX_CONCURRENT_WORKERS: int = 1
    DEFAULT_CONVERTER: str = "AUTO"  # AUTO, MARKER, DOCLING, NATIVE
    
    # Memory limits (in MB)
    MAX_MEMORY_PER_WORKER_MB: int = 4096
    
    # File upload limits
    MAX_UPLOAD_SIZE_BYTES: int = 150 * 1024 * 1024  # 150 MB
    MAX_PDF_PAGES: int = 1000
    
    # OCR settings
    DEFAULT_OCR_LANGUAGES: str = "eng+tam+hin"
    TESSERACT_CMD: str = shutil.which("tesseract") or "/opt/homebrew/bin/tesseract"
    TESSDATA_PREFIX: str = os.environ.get(
        "TESSDATA_PREFIX",
        "/opt/homebrew/share/tessdata" if Path("/opt/homebrew/share/tessdata").exists() else "/usr/share/tessdata"
    )
    
    # Device execution mode
    DEVICE_MODE: str = "cpu"  # cpu, cuda, mps, auto
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    def ensure_directories(self) -> None:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
        self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    def detect_hardware_capabilities(self) -> dict:
        total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_count = psutil.cpu_count(logical=True)
        
        gpu_available = False
        gpu_name = "None"
        gpu_memory_mb = 0
        device = "cpu"
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_mb = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                gpu_available = True
                gpu_name = "Apple Metal Performance Shaders (MPS)"
                gpu_memory_mb = int(total_ram_gb * 1024 * 0.7)  # Shared unified memory
                device = "mps"
        except ImportError:
            pass

        return {
            "platform": platform.platform(),
            "cpu_count": cpu_count,
            "total_ram_gb": round(total_ram_gb, 2),
            "gpu_available": gpu_available,
            "gpu_name": gpu_name,
            "gpu_memory_mb": gpu_memory_mb,
            "recommended_device": device,
            "default_workers": self.MAX_CONCURRENT_WORKERS,
        }

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.ensure_directories()
