# app/services/storage_service.py
import uuid
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
import shutil

_LOGGER = logging.getLogger(__name__)


def _secure_filename(name: str) -> str:
    # minimal sanitizer — production: use werkzeug.utils.secure_filename or similar
    return "".join(c for c in name if c.isalnum() or c in "._-").rstrip(".")


def save_upload_file(file: UploadFile) -> dict:
    name = file.filename
    if not name:
        _LOGGER.debug("Upload rejected: missing filename (content_type=%s)", getattr(file, 'content_type', None))
        raise HTTPException(status_code=400, detail="Missing filename")
    ext = name.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        _LOGGER.debug("Upload rejected: unsupported extension '%s' for filename=%s", ext, name)
        raise HTTPException(status_code=400, detail="Unsupported file type")
    # Read contents in a safe way; note UploadFile also supports async read
    try:
        contents = file.file.read()
    except Exception as e:
        _LOGGER.exception("Failed reading uploaded file %s", name)
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")
    if len(contents) > MAX_FILE_SIZE:
        _LOGGER.debug("Upload rejected: file too large (%d bytes) for filename=%s", len(contents), name)
        raise HTTPException(status_code=413, detail="File too large")
    doc_id = str(uuid.uuid4())
    outdir = UPLOAD_DIR / doc_id
    outdir.mkdir(parents=True, exist_ok=True)
    safe = _secure_filename(name)
    dest = outdir / safe
    with dest.open("wb") as f:
        f.write(contents)
    return {"doc_id": doc_id, "filename": safe}


def get_uploaded_file_path(doc_id: str) -> Path | None:
    folder = UPLOAD_DIR / doc_id
    if not folder.exists():
        return None
    files = list(folder.iterdir())
    return files[0] if files else None


def save_fixed_doc(doc_id: str, corrected_text: str) -> Path:
    folder = UPLOAD_DIR / doc_id
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / f"fixed_{doc_id}.docx"
    from docx import Document
    doc = Document()
    for line in corrected_text.splitlines():
        doc.add_paragraph(line)
    doc.save(out)
    return out


def get_fixed_file_path(doc_id: str) -> Path | None:
    folder = UPLOAD_DIR / doc_id
    if not folder.exists():
        return None
    for f in folder.iterdir():
        if f.name.startswith("fixed_"):
            return f
    return None

