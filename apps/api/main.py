from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import books, bookshelf, chat, conversations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时清理资源
    pass


app = FastAPI(title="AI小说阅读平台", version="1.0.0", lifespan=lifespan)

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(books.router, prefix="/api")
app.include_router(bookshelf.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI小说阅读平台 API", "version": "1.0.0"}
