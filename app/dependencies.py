# app/dependencies.py
from fastapi import Header, HTTPException
from typing import Optional
import os


API_KEY = os.environ.get("API_KEY") or None


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    # Simple header-based API key auth for demonstration
    # Treat empty API_KEY as not configured (allow anonymous access)
    if API_KEY is None:
        return True
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True
