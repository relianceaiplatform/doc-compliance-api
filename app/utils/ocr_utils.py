# app/utils/ocr_utils.py
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
import tempfile


def ocr_pdf_if_needed(path: Path) -> str:
    # convert pdf to images and OCR them
    images = convert_from_path(str(path))
    text_chunks = []
    for im in images:
        txt = pytesseract.image_to_string(im)
        if txt:
            text_chunks.append(txt)
    return "\n".join(text_chunks)

