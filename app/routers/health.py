from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["meta"])

@router.get("/live")
def liveness():
    return {"status": "ok"}

@router.get("/ready")
def readiness():
    # add checks if needed (db ping, cache ping, etc.)
    return {"status": "ready"}
