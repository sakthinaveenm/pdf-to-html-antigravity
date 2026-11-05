"""
Document Export Service.
Packages self-contained offline ZIP bundles containing document.html, reader.css,
embedded images, metadata.json, and quality-report.json with relative links.
"""
import zipfile
import json
from pathlib import Path
from typing import Optional
from backend.app.config.settings import settings

class ExportService:
    @staticmethod
    def build_export_zip(document_id: str) -> Path:
        doc_dir = settings.DOCUMENTS_DIR / document_id
        if not doc_dir.exists():
            raise FileNotFoundError(f"Document directory {doc_dir} not found.")

        exports_dir = doc_dir / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        zip_path = exports_dir / f"{document_id}.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add document.html
            html_file = doc_dir / "document.html"
            if html_file.exists():
                zf.write(html_file, arcname="document.html")

            # Add reader.css
            css_file = doc_dir / "reader.css"
            if css_file.exists():
                zf.write(css_file, arcname="reader.css")

            # Add document.json AST
            ast_file = doc_dir / "document.json"
            if ast_file.exists():
                zf.write(ast_file, arcname="document.json")

            # Add metadata.json
            meta_file = doc_dir / "metadata.json"
            if meta_file.exists():
                zf.write(meta_file, arcname="metadata.json")

            # Add quality-report.json
            quality_file = doc_dir / "quality-report.json"
            if quality_file.exists():
                zf.write(quality_file, arcname="quality-report.json")

            # Add all assets
            assets_dir = doc_dir / "assets"
            if assets_dir.exists():
                for asset in assets_dir.glob("*"):
                    if asset.is_file():
                        zf.write(asset, arcname=f"assets/{asset.name}")

        return zip_path

export_service = ExportService()

