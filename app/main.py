from fastapi import FastAPI
from .config import settings
from .routers import health, users

app = FastAPI(title=settings.app_name, version="0.1.0")

@app.get("/", tags=["meta"])
def root():
    return {"service": settings.app_name, "status": "ok"}

app.include_router(health.router)
app.include_router(users.router)

# Optional DB init at startup:
# from .db import init_db
# @app.on_event("startup")
# def _startup():
#     init_db()
