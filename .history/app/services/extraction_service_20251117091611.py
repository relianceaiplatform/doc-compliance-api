# app/services/extraction_service.py
from pathlib import Path
import pdfplumber
import docx
from app.utils.ocr_utils import ocr_pdf_if_needed


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()

    if ext == ".pdf":
        text = _extract_pdf(path)
        if not text.strip():
            # attempt OCR fallback
            text = ocr_pdf_if_needed(path)
        return text

    elif ext in (".docx", ".doc"):
        return _extract_docx(path)

    else:
        return ""




def _extract_pdf(path: Path) -> str:
text_chunks = []
with pdfplumber.open(path) as pdf:
for page in pdf.pages:
txt = page.extract_text()
if txt:
text_chunks.append(txt)
return "\n".join(text_chunks)




def _extract_docx(path: Path) -> str:
doc = docx.Document(path)
paras = [p.text for p in doc.paragraphs if p.text]
return "\n".join(paras)
