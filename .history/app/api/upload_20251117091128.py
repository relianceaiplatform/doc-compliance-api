# app/api/upload.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.dependencies import verify_api_key
from app.services.storage_service import save_upload_file
from app.models.upload_models import UploadResponse


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    authorized: bool = Depends(verify_api_key)
):
    try:
        saved = save_upload_file(file)
    except HTTPException as e:
        raise e

    return UploadResponse(
        doc_id=saved["doc_id"],
        filename=saved["filename"]
    )