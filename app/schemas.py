from pydantic import BaseModel

class Ping(BaseModel):
    message: str = "pong"
