from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), default="")
    avatar = Column(String(255), default="")
    role = Column(String(20), default="reader")  # reader / author / admin
    created_at = Column(DateTime, server_default=func.now())
    bookshelf = relationship("Bookshelf", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), default="佚名")
    cover_url = Column(String(500), default="")
    category = Column(String(50), default="玄幻")
    description = Column(Text, default="")
    word_count = Column(Integer, default=0)
    recommend_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    status = Column(String(20), default="连载中")  # 连载中/已完结
    is_free = Column(Boolean, default=True)
    vectorized = Column(Boolean, default=False)  # 是否已向量化
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    chapters = relationship(
        "Chapter", back_populates="book", order_by="Chapter.chapter_number",
        cascade="all, delete-orphan",
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    vectorized = Column(Boolean, default=False)  # 章节是否已向量化
    created_at = Column(DateTime, server_default=func.now())
    book = relationship("Book", back_populates="chapters")


class Bookshelf(Base):
    __tablename__ = "bookshelves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    current_chapter = Column(Integer, default=1)
    progress = Column(Float, default=0.0)  # 阅读进度百分比
    added_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="bookshelf")
    book = relationship("Book")


class Conversation(Base):
    """AI 对话会话模型"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    name = Column(String(200), nullable=False, default="新对话")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="conversations")


class TokenBlacklist(Base):
    """JWT refresh_token 黑名单（登出时写入）"""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    expired_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
