# app/models/report_models.py
from pydantic import BaseModel
from typing import Optional, List

class ComplianceIssue(BaseModel):
    category: str
    severity: str
    sentence: Optional[str]
    message: str
    suggestion: Optional[str]
    offset_start: Optional[int]
    offset_end: Optional[int]

class ComplianceReport(BaseModel):
    doc_id: Optional[str]
    filename: Optional[str]
    summary: str
    issues: List[ComplianceIssue]

