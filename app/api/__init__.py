# app/api/__init__.py
from fastapi import APIRouter


upload_router = APIRouter()
report_router = APIRouter()
fix_router = APIRouter()
download_router = APIRouter()
health_router = APIRouter()


# Import modules to register routers
from . import upload, report, fix, download, health # noqa: F401
