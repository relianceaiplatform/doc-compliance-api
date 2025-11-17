import uuid
import json
import threading
import time
from typing import Dict, Any
from pathlib import Path

from app.services.extraction_service import extract_text
from app.services.rewrite_service import rewrite_text
from app.services.storage_service import save_fixed_doc, UPLOAD_DIR

JOBS_DIR = UPLOAD_DIR / "_jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)


def _persist(job_id: str, data: Dict[str, Any]):
    (JOBS_DIR / f"{job_id}.json").write_text(json.dumps(data, indent=2))


class SimpleAgentOrchestrator:
    """A minimal orchestrator that runs simple agent jobs in background threads.

    This is intentionally small and synchronous per-step; it provides a job
    lifecycle and logs so clients can poll progress. Use as a starting point
    for a more robust queue/worker solution.
    """

    def __init__(self, model: str = "open-mistral-7b"):
        self.model = model

    def create_job(self, doc_id: str, goal: str) -> str:
        job_id = str(uuid.uuid4())
        job = {"id": job_id, "doc_id": doc_id, "goal": goal, "status": "queued", "logs": []}
        _persist(job_id, job)
        threading.Thread(target=self._run_job, args=(job_id,), daemon=True).start()
        return job_id

    def _append_log(self, job: Dict[str, Any], msg: str):
        job.setdefault("logs", []).append({"ts": time.time(), "msg": msg})
        _persist(job["id"], job)

    def _run_job(self, job_id: str):
        job_file = JOBS_DIR / f"{job_id}.json"
        job = json.loads(job_file.read_text())
        job["status"] = "running"
        _persist(job_id, job)
        try:
            self._append_log(job, "Extracting text from document")
            text = extract_text(UPLOAD_DIR / job["doc_id"] / "") if False else None
            # fallback: try to locate uploaded file and extract text
            from app.services.storage_service import get_uploaded_file_path

            path = get_uploaded_file_path(job["doc_id"])
            if not path:
                raise RuntimeError("Uploaded file not found")
            text = extract_text(path)

            self._append_log(job, "Requesting plan from model")
            planner_prompt = f"Goal: {job['goal']}\nDocument excerpt:\n{text[:2000]}\nProvide an ordered plan (steps)."
            plan = rewrite_text(planner_prompt)
            self._append_log(job, f"Planner output: {plan[:500]}")

            self._append_log(job, "Applying corrections based on goal")
            corrected = rewrite_text(f"Make the document comply with: {job['goal']}\n\n{text}")
            out = save_fixed_doc(job["doc_id"], corrected)
            self._append_log(job, f"Fixed document saved: {out.name}")
            job["status"] = "completed"
            self._append_log(job, "Job completed successfully")
        except Exception as e:
            job["status"] = "failed"
            self._append_log(job, f"Error: {e}")
        finally:
            _persist(job_id, job)
