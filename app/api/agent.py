from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from pathlib import Path
import json

from app.services.agent_orchestrator import SimpleAgentOrchestrator
from app.services.storage_service import UPLOAD_DIR

router = APIRouter()
agent = SimpleAgentOrchestrator()


class JobCreateRequest(BaseModel):
    doc_id: str
    goal: str


@router.post("/agent/jobs")
def create_job(req: JobCreateRequest) -> Dict[str, Any]:
    # validate that uploaded doc exists
    folder = UPLOAD_DIR / req.doc_id
    if not folder.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    job_id = agent.create_job(req.doc_id, req.goal)
    return {"job_id": job_id}


@router.get("/agent/jobs/{job_id}")
def get_job(job_id: str) -> Dict[str, Any]:
    job_file = UPLOAD_DIR / "_jobs" / f"{job_id}.json"
    if not job_file.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(job_file.read_text())


@router.get("/agent/jobs")
def list_jobs() -> List[Dict[str, Any]]:
    jobs = []
    folder = UPLOAD_DIR / "_jobs"
    if not folder.exists():
        return jobs
    for f in folder.iterdir():
        if f.suffix.lower() == ".json":
            try:
                jobs.append(json.loads(f.read_text()))
            except Exception:
                continue
    return jobs
