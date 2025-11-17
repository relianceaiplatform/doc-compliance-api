# app/api/download.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from app.dependencies import verify_api_key
from app.services.storage_service import get_uploaded_file_path, get_fixed_file_path


router = APIRouter(prefix="/download", tags=["download"])


@router.get("/original/{doc_id}")
async def download_original(doc_id: str, authorized: bool = Depends(verify_api_key)):
    path = get_uploaded_file_path(doc_id)
    if not path:
        raise HTTPException(404, "Document not found")
    return FileResponse(path, filename=path.name)


@router.get("/fixed/{doc_id}")
async def download_fixed(doc_id: str, authorized: bool = Depends(verify_api_key)):
    path = get_fixed_file_path(doc_id)
    if not path:
        raise HTTPException(404, "Fixed document not found")
    return FileResponse(path, filename=path.name)
