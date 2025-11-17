# app/models/fix_models.py
from pydantic import BaseModel

class FixResponse(BaseModel):
    doc_id: str
    fixed_filename: str

