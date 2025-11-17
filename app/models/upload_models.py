# app/models/upload_models.py
from pydantic import BaseModel

class UploadResponse(BaseModel):
    doc_id: str
    filename: str

