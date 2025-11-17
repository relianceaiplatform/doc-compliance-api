# app/main.py
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from app.api import upload_router, report_router, fix_router, download_router, health_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="DocCompliance API")

# CORS — tune origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
from app.api.upload import router as _upload
from app.api.report import router as _report
from app.api.fix import router as _fix
from app.api.download import router as _download
from app.api.health import router as _health
from app.api.agent import router as _agent

app.include_router(_upload)
app.include_router(_report)
app.include_router(_fix)
app.include_router(_download)
app.include_router(_health)
app.include_router(_agent)


@app.get("/")
async def root():
    return {"message": "DocCompliance API — see /docs"}

