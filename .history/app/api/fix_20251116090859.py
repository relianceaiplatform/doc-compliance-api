# app/api/fix.py
from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import verify_api_key
from app.services.storage_service import get_uploaded_file_path, save_fixed_doc
from app.services.extraction_service import extract_text
from app.services.rewrite_service import rewrite_text


router = APIRouter(prefix="/fix", tags=["fix"])


@router.post("/{doc_id}")
async def fix(doc_id: str, authorized: bool = Depends(verify_api_key)):
path = get_uploaded_file_path(doc_id)
if not path:
raise HTTPException(404, "Document not found")
text = extract_text(path)
corrected = rewrite_text(text)
out_path = save_fixed_doc(doc_id, corrected)
return {"doc_id": doc_id, "fixed_filename": out_path.name}