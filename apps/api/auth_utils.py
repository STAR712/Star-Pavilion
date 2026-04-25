"""认证工具：JWT 双 Token 生成/验证/刷新/黑名单"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import TokenBlacklist, User

PBKDF2_ROUNDS = 120_000


# ===== 密码哈希（保留原有实现） =====

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ROUNDS,
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, digest = stored_hash.split("$", 1)
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ROUNDS,
    ).hex()
    return hmac.compare_digest(candidate, digest)


# ===== JWT Token 生成 =====

def create_access_token(user: User) -> str:
    """生成 access_token（短时效，默认15分钟）"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=settings.access_token_ttl),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")


def create_refresh_token(user: User) -> str:
    """生成 refresh_token（长时效，默认7天）"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=settings.refresh_token_ttl),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")


# ===== JWT Token 解码 =====

def decode_token(token: str) -> dict:
    """解码并验证 JWT（自动检查过期）"""
    try:
        return jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token无效")


# ===== Token 黑名单 =====

def is_token_blacklisted(jti: str, db: Session) -> bool:
    """检查 Token 是否在黑名单中"""
    return db.query(TokenBlacklist).filter(
        TokenBlacklist.jti == jti,
        TokenBlacklist.expired_at > datetime.now(timezone.utc),
    ).first() is not None


def blacklist_token(jti: str, expired_at: datetime, db: Session) -> None:
    """将 Token 加入黑名单"""
    entry = TokenBlacklist(jti=jti, expired_at=expired_at)
    db.add(entry)
    db.commit()


def cleanup_expired_blacklist(db: Session) -> None:
    """清理已过期的黑名单记录（启动时调用）"""
    db.query(TokenBlacklist).filter(
        TokenBlacklist.expired_at <= datetime.now(timezone.utc),
    ).delete()
    db.commit()


# ===== 用户序列化 =====

def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "role": user.role,
        "created_at": str(user.created_at) if user.created_at else None,
    }


# ===== FastAPI 依赖注入 =====

def get_optional_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User | None:
    """可选认证：无 Token 返回 None，有 Token 则验证并返回用户"""
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_token(token)

    # 仅接受 access_token 类型
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token类型错误",
        )

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在，请重新登录",
        )
    return user


def get_current_user(
    user: User | None = Depends(get_optional_current_user),
) -> User:
    """强制认证：未登录返回 401"""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
        )
    return user
