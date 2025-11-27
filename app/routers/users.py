from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.schemas import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    full_name: str

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    class Config:
        from_attributes = True

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_session)):
    if db.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(409, "Email already exists")
    user = User(**payload.model_dump())
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_session)):
    return db.exec(select(User).order_by(User.id)).all()
