# app/api/upload.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
import logging

from app.dependencies import verify_api_key
from app.services.storage_service import save_upload_file
from app.models.upload_models import UploadResponse

_LOGGER = logging.getLogger(__name__)


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    authorized: bool = Depends(verify_api_key)
):
    try:
        _LOGGER.debug("Received upload request: filename=%s, content_type=%s", file.filename, file.content_type)
        saved = save_upload_file(file)
    except HTTPException as e:
        _LOGGER.warning("Upload failed: %s", e.detail)
        # Re-raise to preserve status code and detail
        raise e
    except Exception as e:
        _LOGGER.exception("Unexpected error during upload")
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(doc_id=saved["doc_id"], filename=saved["filename"])