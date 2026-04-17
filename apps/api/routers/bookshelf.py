from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth_utils import get_current_user
from database import get_db
from models import Book, Bookshelf, User

router = APIRouter(prefix="/bookshelf", tags=["书架"])


class AddBookshelfRequest(BaseModel):
    book_id: int


class UpdateProgressRequest(BaseModel):
    current_chapter: int
    progress: float


@router.get("")
def get_bookshelf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前登录用户的书架"""
    items = (
        db.query(Bookshelf)
        .filter(Bookshelf.user_id == current_user.id)
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
                    "book_category": book.category,
                    "book_description": book.description,
                    "book_status": book.status,
                    "book_word_count": book.word_count,
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
def add_to_bookshelf(
    req: AddBookshelfRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """加入当前登录用户书架"""
    book = db.query(Book).filter(Book.id == req.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    existing = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == current_user.id,
            Bookshelf.book_id == req.book_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="该书已在书架中")
    item = Bookshelf(user_id=current_user.id, book_id=req.book_id)
    db.add(item)
    db.commit()
    return {"message": "已加入书架"}


@router.put("/{book_id}")
def update_progress(
    book_id: int,
    req: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前登录用户的阅读进度"""
    item = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == current_user.id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """从当前登录用户书架移出"""
    item = (
        db.query(Bookshelf)
        .filter(
            Bookshelf.user_id == current_user.id,
            Bookshelf.book_id == book_id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="书架中无此书")
    db.delete(item)
    db.commit()
    return {"message": "已移出书架"}
