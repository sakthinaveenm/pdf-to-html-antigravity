"""
Durable Background Job Processor and Queue Worker.
Pulls jobs from SQLite, processes conversions through the complete pipeline,
updates real-time progress, supports cancellation, failure recovery,
and disk storage management.
"""
import time
import json
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.config.settings import settings
from backend.app.db.database import SessionLocal
from backend.app.models.entities import Job, Document, DocumentRevision
from backend.app.constants.statuses import JobStatus, PageClassification
from backend.app.services.converters.orchestrator import conversion_orchestrator
from backend.app.services.converters.base import ConversionOptions
from backend.app.services.html.generator import html_generation_service
from backend.app.services.html.normalizer import html_normalization_service
from backend.app.services.validation.quality_service import quality_service
from backend.app.services.export.export_service import export_service

logger = logging.getLogger(__name__)

class JobProcessor:
    def __init__(self):
        self._stop_event = threading.Event()
        self._worker_thread = None
        self._active_jobs = set()

    def start_worker(self):
        self._recover_stale_jobs()
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name="JobQueueWorker")
            self._worker_thread.start()
            logger.info("Job Queue Worker started successfully.")

    def stop_worker(self):
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=3.0)

    def _recover_stale_jobs(self):
        """Reset jobs left in active state due to server crash/restart."""
        db = SessionLocal()
        try:
            stale_jobs = db.query(Job).filter(
                Job.status.in_([
                    JobStatus.INSPECTING.value,
                    JobStatus.CONVERTING.value,
                    JobStatus.OCR_PROCESSING.value,
                    JobStatus.NORMALIZING.value,
                    JobStatus.VALIDATING.value
                ])
            ).all()
            for job in stale_jobs:
                job.status = JobStatus.QUEUED.value
                job.progress = 0
                job.current_step = "Recovered after restart, queued for retry"
            if stale_jobs:
                db.commit()
                logger.info(f"Recovered {len(stale_jobs)} stale jobs back to QUEUED state.")
        except Exception as e:
            logger.error(f"Error recovering stale jobs: {e}")
        finally:
            db.close()

    def _worker_loop(self):
        while not self._stop_event.is_set():
            db = SessionLocal()
            job = None
            try:
                # Fetch next queued job
                job = db.query(Job).filter(Job.status == JobStatus.QUEUED.value).order_by(Job.created_at.asc()).first()
                if job:
                    self._process_single_job(db, job)
            except Exception as e:
                logger.error(f"Error in job worker loop: {e}", exc_info=True)
            finally:
                db.close()

            # Bounded poll sleep
            time.sleep(1.0)

    def _process_single_job(self, db: Session, job: Job):
        job_id = job.id
        doc_id = job.document_id
        pdf_path = Path(job.file_path)

        logger.info(f"Starting execution of Job {job_id} for file {job.filename}")

        # Check cancellation
        db.refresh(job)
        if job.status == JobStatus.CANCELED.value:
            return

        try:
            # 1. Step: Inspecting
            job.status = JobStatus.INSPECTING.value
            job.progress = 15
            job.current_step = "Inspecting PDF geometry, fonts and page structure"
            job.updated_at = datetime.now(timezone.utc)
            db.commit()

            # Set up output directories
            doc_dir = settings.DOCUMENTS_DIR / doc_id
            doc_dir.mkdir(parents=True, exist_ok=True)
            assets_dir = doc_dir / "assets"
            assets_dir.mkdir(parents=True, exist_ok=True)
            revisions_dir = doc_dir / "revisions"
            revisions_dir.mkdir(parents=True, exist_ok=True)

            doc_lang = getattr(job, "document_language", None) or "AUTO"
            options = ConversionOptions(
                document_id=doc_id,
                ocr_languages=job.ocr_languages,
                document_language=doc_lang,
                force_ocr=job.force_ocr,
                assets_dir=assets_dir
            )

            # 2. Step: Converting
            db.refresh(job)
            if job.status == JobStatus.CANCELED.value:
                return

            job.status = JobStatus.CONVERTING.value
            job.progress = 40
            job.current_step = f"Converting with engine {job.converter}"
            db.commit()

            canonical_doc = conversion_orchestrator.convert(
                source_path=pdf_path,
                options=options,
                preferred_engine=job.converter
            )

            # 3. Step: Normalizing & Generating HTML
            db.refresh(job)
            if job.status == JobStatus.CANCELED.value:
                return

            job.status = JobStatus.NORMALIZING.value
            job.progress = 70
            job.current_step = "Generating semantic HTML & applying security sanitization"
            db.commit()

            raw_html = html_generation_service.generate_html(canonical_doc, standalone=True)
            normalized_html = html_normalization_service.normalize(raw_html, document_id=doc_id)
            reader_css = html_generation_service.get_reader_css()

            # 4. Step: Validating Quality
            job.status = JobStatus.VALIDATING.value
            job.progress = 85
            job.current_step = "Evaluating text selectability and Unicode integrity"
            db.commit()

            quality_report = quality_service.evaluate(canonical_doc, normalized_html)

            # 5. Save Files to Storage
            (doc_dir / "document.html").write_text(normalized_html, encoding="utf-8")
            (doc_dir / "reader.css").write_text(reader_css, encoding="utf-8")
            (doc_dir / "document.json").write_text(canonical_doc.model_dump_json(indent=2), encoding="utf-8")
            (doc_dir / "quality-report.json").write_text(quality_report.model_dump_json(indent=2), encoding="utf-8")
            
            metadata = {
                "documentId": doc_id,
                "jobId": job_id,
                "title": canonical_doc.title,
                "filename": job.filename,
                "sha256": job.sha256,
                "pageCount": len(canonical_doc.pages),
                "language": canonical_doc.language,
                "converter": job.converter,
                "ocrLanguages": job.ocr_languages,
                "qualityStatus": quality_report.overallStatus
            }
            (doc_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

            # Pre-build self-contained export ZIP
            export_service.build_export_zip(doc_id)

            # 6. Create or update Document record in DB
            doc_record = db.query(Document).filter(Document.id == doc_id).first()
            if not doc_record:
                doc_record = Document(
                    id=doc_id,
                    job_id=job_id,
                    title=canonical_doc.title,
                    filename=job.filename,
                    sha256=job.sha256,
                    language=canonical_doc.language,
                    page_count=len(canonical_doc.pages),
                    current_revision=1,
                    quality_status=quality_report.overallStatus,
                    storage_path=str(doc_dir),
                    metadata_json=json.dumps(metadata),
                    quality_json=quality_report.model_dump_json()
                )
                db.add(doc_record)
            else:
                doc_record.title = canonical_doc.title
                doc_record.quality_status = quality_report.overallStatus

            # Add initial revision 1
            rev_record = DocumentRevision(
                id=f"rev-{doc_id}-001",
                document_id=doc_id,
                revision_number=1,
                html_content=normalized_html,
                ast_json=canonical_doc.model_dump_json(),
                change_summary="Initial conversion from PDF"
            )
            db.add(rev_record)

            # Mark Completed
            job.status = JobStatus.COMPLETED.value
            job.progress = 100
            job.current_step = "Conversion completed successfully"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Job {job_id} successfully completed.")

        except Exception as e:
            logger.error(f"Job {job_id} failed with error: {e}", exc_info=True)
            db.refresh(job)
            job.status = JobStatus.FAILED.value
            job.progress = 100
            job.current_step = "Failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

job_processor = JobProcessor()

