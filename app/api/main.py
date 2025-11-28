# app/api/main.py
from __future__ import annotations

from fastapi import FastAPI

from app.main import create_app

# Re-export the main FastAPI app for compatibility with
# Uvicorn/Gunicorn paths like `app.api.main:app`.
app: FastAPI = create_app()
