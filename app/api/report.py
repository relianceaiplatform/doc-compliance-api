# app/api/report.py
from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import verify_api_key
from app.services.extraction_service import extract_text
from app.services.compliance_service import analyze_text
from app.services.storage_service import get_uploaded_file_path


router = APIRouter(prefix="/report", tags=["report"])


@router.get("/{doc_id}")
async def report(doc_id: str, authorized: bool = Depends(verify_api_key)):
    path = get_uploaded_file_path(doc_id)
    if not path:
        raise HTTPException(404, "Document not found")

    text = extract_text(path)
    report = analyze_text(text, doc_id=doc_id)
    return report