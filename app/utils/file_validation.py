# app/utils/file_validation.py
import magic
from fastapi import HTTPException


def sniff_mime_type(stream) -> str:
    # Note: python-magic may require system package libmagic.
    try:
        mime = magic.from_buffer(stream.read(2048), mime=True)
        stream.seek(0)
        return mime
    except Exception:
        return "application/octet-stream"


def ensure_allowed(ext: str):
    allowed = {"pdf", "docx", "doc"}
    if ext.lower() not in allowed:
        raise HTTPException(400, "Unsupported file type")

