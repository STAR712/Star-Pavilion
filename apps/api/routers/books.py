"""书籍管理路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Book, Chapter

router = APIRouter(prefix="/books", tags=["书籍"])


class CreateChapterRequest(BaseModel):
    title: str
    content: str


# ==================== 书籍 CRUD ====================


@router.get("")
def get_books(
    category: Optional[str] = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: Session = Depends(get_db),
):
    """获取书籍列表，支持分页和分类筛选"""
    query = db.query(Book)
    if category:
        query = query.filter(Book.category == category)
    total = query.count()
    books = query.offset((page - 1) * size).limit(size).all()
    return {
        "total": total,
        "page": page,
        "size": size,
        "books": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "cover_url": b.cover_url,
                "category": b.category,
                "description": b.description,
                "word_count": b.word_count,
                "recommend_count": b.recommend_count,
                "read_count": b.read_count,
                "status": b.status,
                "is_free": b.is_free,
                "updated_at": str(b.updated_at) if b.updated_at else None,
            }
            for b in books
        ],
    }


@router.get("/ranking")
def get_ranking(
    sort_by: str = Query("recommend_count", description="排序字段: recommend_count / read_count"),
    size: int = Query(10, ge=1, le=50, description="数量"),
    db: Session = Depends(get_db),
):
    """获取排行榜"""
    if sort_by not in ("recommend_count", "read_count"):
        sort_by = "recommend_count"
    books = (
        db.query(Book)
        .order_by(getattr(Book, sort_by).desc())
        .limit(size)
        .all()
    )
    return {
        "sort_by": sort_by,
        "books": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "cover_url": b.cover_url,
                "category": b.category,
                "description": b.description,
                "word_count": b.word_count,
                "recommend_count": b.recommend_count,
                "read_count": b.read_count,
                "status": b.status,
                "is_free": b.is_free,
            }
            for b in books
        ],
    }


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(Book.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}


@router.get("/{book_id}")
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    """获取书籍详情"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "cover_url": book.cover_url,
        "category": book.category,
        "description": book.description,
        "word_count": book.word_count,
        "recommend_count": book.recommend_count,
        "read_count": book.read_count,
        "status": book.status,
        "is_free": book.is_free,
        "vectorized": book.vectorized,
        "chapter_count": len(book.chapters),
        "created_at": str(book.created_at) if book.created_at else None,
        "updated_at": str(book.updated_at) if book.updated_at else None,
    }


@router.post("")
def create_book(
    title: str,
    author: str = "佚名",
    category: str = "玄幻",
    description: str = "",
    is_free: bool = True,
    db: Session = Depends(get_db),
):
    """创建书籍（作家专区）"""
    book = Book(
        title=title,
        author=author,
        category=category,
        description=description,
        is_free=is_free,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return {"id": book.id, "message": "书籍创建成功"}


@router.put("/{book_id}")
def update_book(
    book_id: int,
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    is_free: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """更新书籍信息"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    if title is not None:
        book.title = title
    if author is not None:
        book.author = author
    if category is not None:
        book.category = category
    if description is not None:
        book.description = description
    if status is not None:
        book.status = status
    if is_free is not None:
        book.is_free = is_free
    db.commit()
    return {"message": "更新成功"}


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """删除书籍"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    # 删除关联的章节
    db.query(Chapter).filter(Chapter.book_id == book_id).delete()
    db.delete(book)
    db.commit()
    return {"message": "删除成功"}


# ==================== 章节 CRUD ====================


@router.get("/{book_id}/chapters")
def get_chapters(book_id: int, db: Session = Depends(get_db)):
    """获取章节列表"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return {
        "book_id": book_id,
        "book_title": book.title,
        "chapters": [
            {
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "word_count": c.word_count,
                "vectorized": c.vectorized,
            }
            for c in book.chapters
        ],
    }


@router.post("/{book_id}/chapters")
def create_chapter(
    book_id: int,
    req: CreateChapterRequest,
    db: Session = Depends(get_db),
):
    """创建章节并触发向量化"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    # 计算章节号
    max_chapter = (
        db.query(Chapter)
        .filter(Chapter.book_id == book_id)
        .order_by(Chapter.chapter_number.desc())
        .first()
    )
    next_number = (max_chapter.chapter_number + 1) if max_chapter else 1

    chapter = Chapter(
        book_id=book_id,
        chapter_number=next_number,
        title=req.title,
        content=req.content,
        word_count=len(req.content),
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # 触发向量化
    try:
        from services.rag_service import rag_service

        rag_service.index_chapter(
            book_id=book_id,
            chapter_id=chapter.id,
            title=req.title,
            content=req.content,
        )
        chapter.vectorized = True
        book.vectorized = True
        # 更新总字数
        book.word_count = sum(c.word_count for c in book.chapters)
        db.commit()
    except Exception as e:
        print(f"向量化失败（不影响章节保存）: {e}")

    return {
        "id": chapter.id,
        "chapter_number": next_number,
        "vectorized": chapter.vectorized,
        "message": "章节创建成功",
    }


@router.get("/{book_id}/chapters/{chapter_number}")
def get_chapter_content(
    book_id: int, chapter_number: int, db: Session = Depends(get_db)
):
    """获取章节内容"""
    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.book_id == book_id, Chapter.chapter_number == chapter_number
        )
        .first()
    )
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    # 获取上一章和下一章信息
    prev_chapter = (
        db.query(Chapter)
        .filter(
            Chapter.book_id == book_id,
            Chapter.chapter_number < chapter_number,
        )
        .order_by(Chapter.chapter_number.desc())
        .first()
    )
    next_chapter = (
        db.query(Chapter)
        .filter(
            Chapter.book_id == book_id,
            Chapter.chapter_number > chapter_number,
        )
        .order_by(Chapter.chapter_number.asc())
        .first()
    )
    return {
        "id": chapter.id,
        "book_id": book_id,
        "chapter_number": chapter.chapter_number,
        "title": chapter.title,
        "content": chapter.content,
        "word_count": chapter.word_count,
        "prev_chapter": (
            prev_chapter.chapter_number if prev_chapter else None
        ),
        "next_chapter": (
            next_chapter.chapter_number if next_chapter else None
        ),
    }


@router.post("/{book_id}/vectorize")
def vectorize_book(book_id: int, db: Session = Depends(get_db)):
    """手动触发全书向量化"""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    from services.rag_service import rag_service

    chapters_data = [
        {"id": c.id, "title": c.title, "content": c.content}
        for c in book.chapters
    ]
    if not chapters_data:
        raise HTTPException(status_code=400, detail="该书籍暂无章节")

    try:
        rag_service.index_book(book_id, chapters_data)
        book.vectorized = True
        for c in book.chapters:
            c.vectorized = True
        db.commit()
        return {
            "message": f"向量化完成，共处理 {len(chapters_data)} 个章节"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"向量化失败: {str(e)}")
