"""
Main FastAPI Application Entrypoint.
Initializes SQLite database, registers routers, configures CORS,
and starts the durable background worker loop.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.app.config.settings import settings
from backend.app.db.database import init_db
from backend.app.workers.job_worker import job_processor
from backend.app.api.jobs import router as jobs_router
from backend.app.api.documents import router as documents_router
from backend.app.api.highlights import router as highlights_router
from backend.app.api.system import router as system_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pdf_converter")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info("Starting background durable job worker thread...")
    job_processor.start_worker()
    yield
    # Shutdown
    logger.info("Stopping background job worker thread...")
    job_processor.stop_worker()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Local-first Multilingual PDF to Semantic HTML Converter API",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local-first usage
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "detail": str(exc)}
    )

# Register API v1 Routers
app.include_router(system_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(highlights_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "message": "Multilingual PDF to HTML Conversion Platform API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "capabilities": f"{settings.API_V1_PREFIX}/capabilities"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
