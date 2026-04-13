from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Bookshelf, Book
from config import settings

router = APIRouter(prefix="/bookshelf", tags=["书架"])


class AddBookshelfRequest(BaseModel):
    book_id: int
    user_id: int | None = None


class UpdateProgressRequest(BaseModel):
    current_chapter: int
    progress: float
    user_id: int | None = None


def _get_user_id(request_user_id: int | None) -> int:
    """获取实际 user_id，如果请求中未提供则使用默认值"""
    return request_user_id if request_user_id is not None else settings.default_user_id


@router.get("")
def get_bookshelf(
    user_id: int | None = Query(None, description="用户ID，不传则使用默认用户"),
    db: Session = Depends(get_db),
):
    """获取用户书架"""
    uid = user_id if user_id is not None else settings.default_user_id
    items = (
        db.query(Bookshelf)
        .filter(Bookshelf.user_id == uid)
        .all()
    )
    result = []
    for item in items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            result.append(
                {
                    "id": item.id,
                    "book_id": item.book_id,
                    "book_title": book.title,
                    "book_author": book.author,
                    "book_cover_url": book.cover_url,
                    "current_chapter": item.current_chapter,
                    "progress": item.progress,
                    "added_at": str(item.added_at) if item.added_at else None,
                    "updated_at": (
                        str(item.updated_at) if item.updated_at else None
                    ),
                }
            )
    return result


@router.post("")
def add_to_bookshelf(req: AddBookshelfRequest, db: Session = Depends(get_db)):
    """加入书架"""
    uid = _get_user_id(req.user_id)
    book = db.query(Book).filter(Book.id == req.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    existing = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == uid,
            Bookshelf.book_id == req.book_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="该书已在书架中")
    item = Bookshelf(user_id=uid, book_id=req.book_id)
    db.add(item)
    db.commit()
    return {"message": "已加入书架"}


@router.put("/{book_id}")
def update_progress(
    book_id: int, req: UpdateProgressRequest, db: Session = Depends(get_db)
):
    """更新阅读进度"""
    uid = _get_user_id(req.user_id)
    item = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == uid,
            Bookshelf.book_id == book_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="书架中无此书")
    item.current_chapter = req.current_chapter
    item.progress = req.progress
    db.commit()
    return {"message": "进度已更新"}


@router.delete("/{book_id}")
def remove_from_bookshelf(
    book_id: int,
    user_id: int | None = Query(None, description="用户ID，不传则使用默认用户"),
    db: Session = Depends(get_db),
):
    """移出书架"""
    uid = user_id if user_id is not None else settings.default_user_id
    item = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == uid,
            Bookshelf.book_id == book_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="书架中无此书")
    db.delete(item)
    db.commit()
    return {"message": "已移出书架"}
