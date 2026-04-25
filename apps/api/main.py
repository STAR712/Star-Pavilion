import structlog
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth_utils import cleanup_expired_blacklist
from config import settings
from database import Base, SessionLocal, engine
from rate_limit import limiter
from routers import auth, books, bookshelf, chat, conversations
from schema import ensure_database_schema
from seed_demo_data import ensure_demo_data
from services.rag_service import ensure_library_vectorized
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库表
    Base.metadata.create_all(bind=engine)
    ensure_database_schema()
    db = SessionLocal()
    try:
        # 清理已过期的 Token 黑名单
        cleanup_expired_blacklist(db)
        ensure_demo_data(db)
        ensure_library_vectorized(db)
    except Exception as exc:
        print(f"初始化失败: {exc}")
    finally:
        db.close()

    # 配置结构化日志
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    logger.info("application_startup", env="development")

    # 速率限制配置（开发环境宽松）
    logger.info("rate_limiting_configured", default="100/minute")

    yield
    # 关闭时清理资源
    pass


app = FastAPI(title="AI小说阅读平台", version="1.0.0", lifespan=lifespan)

# 速率限制
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 中间件配置（从环境变量读取允许的域名）
_cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    return response


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
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
