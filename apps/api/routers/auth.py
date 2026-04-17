from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth_utils import (
    create_access_token,
    get_current_user,
    hash_password,
    serialize_user,
    verify_password,
)
from database import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["用户认证"])


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=64)


@router.post("/register")
def register(req: AuthRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空",
        )

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    user = User(
        username=username,
        password_hash=hash_password(req.password),
        role="reader",
        avatar="",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "token": create_access_token(user),
        "user": serialize_user(user),
    }


@router.post("/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    return {
        "token": create_access_token(user),
        "user": serialize_user(user),
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return serialize_user(user)


@router.post("/logout")
def logout():
    return {"message": "已退出登录"}
