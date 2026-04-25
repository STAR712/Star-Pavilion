"""用户认证路由：注册、登录、刷新 Token、登出"""

from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth_utils import (
    blacklist_token,
    cleanup_expired_blacklist,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    is_token_blacklisted,
    serialize_user,
    verify_password,
)
from config import settings
from database import get_db
from models import User
from rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["用户认证"])


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=64)


@router.post("/register")
@limiter.limit("3/minute")
def register(request: Request, req: AuthRequest, response: Response, db: Session = Depends(get_db)):
    """注册新用户，返回 access_token + HttpOnly refresh_token Cookie"""
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

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "user": serialize_user(user),
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, req: AuthRequest, response: Response, db: Session = Depends(get_db)):
    """登录，返回 access_token + HttpOnly refresh_token Cookie"""
    username = req.username.strip()
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    _set_refresh_cookie(response, refresh_token)

    return {
        "access_token": access_token,
        "user": serialize_user(user),
    }


@router.post("/refresh")
def refresh_token(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    """用 refresh_token 换取新的 access_token（同时滑动续期 refresh_token）"""
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少refresh_token")

    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token类型错误")

    if is_token_blacklisted(payload["jti"], db):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已失效，请重新登录")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    # 生成新的 access_token
    new_access_token = create_access_token(user)

    # 滑动续期：同时刷新 refresh_token
    new_refresh_token = create_refresh_token(user)
    _set_refresh_cookie(response, new_refresh_token)

    return {"access_token": new_access_token, "user": serialize_user(user)}


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    """登出：将 refresh_token 加入黑名单 + 清除 Cookie"""
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            blacklist_token(
                jti=payload["jti"],
                expired_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                db=db,
            )
        except Exception:
            pass  # Token 已无效，忽略

    response.delete_cookie(key="refresh_token", path="/api/auth/refresh")

    return {"message": "已退出登录"}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return serialize_user(user)


# ===== 内部工具 =====

def _set_refresh_cookie(response: Response, token: str) -> None:
    """设置 refresh_token HttpOnly Cookie"""
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False,  # 开发环境 HTTP；生产环境部署 HTTPS 时改为 True
        samesite="lax",
        max_age=settings.refresh_token_ttl,
        path="/api/auth/refresh",
    )
