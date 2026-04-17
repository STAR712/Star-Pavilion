"""会话管理路由"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session

from auth_utils import get_current_user
from config import settings
from database import get_db
from models import Conversation, User
from services.rag_service import get_rag_service

router = APIRouter(prefix="/conversations", tags=["会话管理"])

TZ_OFFSET = 8


class ConversationCreate(BaseModel):
    book_id: int | None = None
    chapter_id: int | None = None
    name: str = "新对话"


class ConversationUpdate(BaseModel):
    name: str | None = None
    messages: list[dict] | None = None


@router.get("")
def list_conversations(
    book_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前登录用户的会话列表"""
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    if book_id is not None:
        query = query.filter(Conversation.book_id == book_id)
    conversations = query.order_by(desc(Conversation.updated_at)).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "book_id": c.book_id,
            "chapter_id": c.chapter_id,
            "timestamp": (
                c.updated_at + timedelta(hours=TZ_OFFSET)
            ).strftime("%Y-%m-%d %H:%M:%S")
            if c.updated_at
            else None,
        }
        for c in conversations
    ]


@router.post("")
def create_conversation(
    req: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建会话"""
    conv = Conversation(
        user_id=current_user.id,
        book_id=req.book_id,
        chapter_id=req.chapter_id,
        name=req.name,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "name": conv.name, "book_id": conv.book_id}


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前登录用户的会话详情"""
    conv = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "id": conv.id,
        "name": conv.name,
        "book_id": conv.book_id,
        "chapter_id": conv.chapter_id,
        "messages": conv.messages,
    }


@router.put("/{conversation_id}")
def update_conversation(
    conversation_id: int,
    req: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新会话"""
    conv = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    if req.messages is not None:
        conv.messages = req.messages
        # 触发对话记忆存储：将最新的用户消息和AI回复存入 ChromaDB
        _store_conversation_memory(conv)
    if req.name is not None:
        conv.name = req.name
    db.commit()
    return {"id": conv.id, "message": "更新成功"}


def _store_conversation_memory(conv: Conversation):
    """将会话中的最新一轮对话存入 ChromaDB 对话记忆"""
    messages = conv.messages or []
    if len(messages) < 2:
        return
    # 找到最后一对 user + assistant 消息
    last_user_msg = None
    last_assistant_msg = None
    for msg in reversed(messages):
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "assistant" and last_assistant_msg is None:
            last_assistant_msg = content
        elif role == "user" and last_user_msg is None:
            last_user_msg = content
        if last_user_msg is not None and last_assistant_msg is not None:
            break
    if last_user_msg and last_assistant_msg:
        # 计算 turn_index
        turn_count = sum(1 for m in messages if m.get("role") == "user")
        try:
            rag_service = get_rag_service()
            rag_service.store_conversation_turn(
                user_id=conv.user_id or settings.default_user_id,
                book_id=conv.book_id,
                conversation_id=conv.id,
                turn_index=turn_count,
                user_msg=last_user_msg,
                assistant_msg=last_assistant_msg,
            )
        except Exception:
            # 记忆存储失败不影响主流程
            pass


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除会话"""
    conv = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(conv)
    db.commit()
    return {"message": "会话已删除"}
