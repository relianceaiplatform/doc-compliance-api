# app/config.py
import os
from pathlib import Path


BASE_DIR = Path(os.environ.get("BASE_DIR", "."))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", str(BASE_DIR / "static")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE_BYTES", 20 * 1024 * 1024))
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY") or os.environ.get("OPENAI_API_KEY")
MISTRAL_BASE_URL = os.environ.get("MISTRAL_BASE_URL", "https://api.mistral.ai")
LANGUAGE_TOOL_LANG = os.environ.get("LANGUAGE_TOOL_LANG", "en-US")


# Allowed extensions
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}