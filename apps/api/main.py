from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, SessionLocal, engine
from routers import auth, books, bookshelf, chat, conversations
from schema import ensure_database_schema
from seed_demo_data import ensure_demo_data
from services.rag_service import ensure_library_vectorized


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库表
    Base.metadata.create_all(bind=engine)
    ensure_database_schema()
    db = SessionLocal()
    try:
        ensure_demo_data(db)
        ensure_library_vectorized(db)
    except Exception as exc:
        print(f"示例数据初始化失败: {exc}")
    finally:
        db.close()
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
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(bookshelf.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(conversations.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI小说阅读平台 API", "version": "1.0.0"}
