from fastapi import Depends
from .config import settings

def get_settings() -> dict:
    return {"name": settings.app_name, "debug": settings.debug}
