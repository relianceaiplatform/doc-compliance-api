# tests/test_api.py
import io
import os
from fastapi.testclient import TestClient
from app.main import app
from docx import Document

client = TestClient(app)


def test_health():
    r = client.get("/health/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upload_docx_and_report(tmp_path):
    # create sample docx
    p = tmp_path / "sample.docx"
    doc = Document()
    doc.add_paragraph("This are wrong.")
    doc.save(p)

    with open(p, "rb") as fh:
        files = {"file": ("sample.docx", fh, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        r = client.post("/upload/", files=files)
    assert r.status_code == 200
    body = r.json()
    assert "doc_id" in body
    doc_id = body["doc_id"]

    r2 = client.get(f"/report/{doc_id}")
    assert r2.status_code == 200
    data = r2.json()
    assert "summary" in data
    assert "issues" in data


def test_upload_unsupported_file():
    r = client.post("/upload/", files={"file": ("f.txt", io.BytesIO(b"hello"), "text/plain")})
    assert r.status_code == 400

