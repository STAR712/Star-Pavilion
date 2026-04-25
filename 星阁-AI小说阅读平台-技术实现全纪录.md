# 星阁（Star-Pavilion）AI 小说阅读平台 — 技术实现全纪录

## 一、项目概述

### 1.1 项目定位

星阁是一个面向小说读者的 AI 增强阅读平台，核心价值在于将大语言模型（LLM）与检索增强生成（RAG）技术融入传统阅读体验，实现"边读边聊"的智能交互。用户在阅读小说时，可以随时向 AI 助手提问关于剧情、人物、伏笔等问题，AI 基于小说原文进行检索和推理后给出精准回答，同时支持引用标注，让回答可溯源。

### 1.2 技术栈总览

| 层级 | 技术选型 | 版本 |
|------|---------|------|
| 前端框架 | Vue 3 (Composition API) | ^3.4.0 |
| 构建工具 | Vite | ^5.4.0 |
| 状态管理 | Pinia + pinia-plugin-persistedstate | ^2.1.0 / ^3.2.0 |
| 路由 | Vue Router 4 | ^4.3.0 |
| HTTP 客户端 | Axios | ^1.7.0 |
| CSS 方案 | TailwindCSS | ^3.4.0 |
| 后端框架 | FastAPI | - |
| ORM | SQLAlchemy | - |
| 数据库 | SQLite | - |
| 向量数据库 | ChromaDB | - |
| 大模型 | 讯飞星辰（Chat + Embedding） | xop35qwen2b / xop3qwen8bembedding |
| Embedding 框架 | LangChain (langchain-chroma, langchain-openai) | - |
| 认证 | PyJWT (HS256) | >=2.8.0 |
| 日志 | structlog | >=24.1.0 |
| 限流 | slowapi | >=0.1.9 |
| 类型检查 | TypeScript | ^5.3.0 |

### 1.3 项目目录结构

```
workspace/
├── apps/
│   ├── api/                          # FastAPI 后端
│   │   ├── main.py                   # 应用入口 + 中间件 + CORS
│   │   ├── config.py                 # Pydantic Settings 配置管理
│   │   ├── database.py               # SQLAlchemy 引擎与会话
│   │   ├── models.py                 # ORM 模型定义
│   │   ├── auth_utils.py             # JWT 认证工具
│   │   ├── rbac.py                   # RBAC 角色权限矩阵
│   │   ├── rate_limit.py             # slowapi 速率限制
│   │   ├── .env                      # 环境变量（不提交）
│   │   ├── .env.example              # 环境变量模板
│   │   ├── requirements.txt          # Python 依赖
│   │   ├── routers/
│   │   │   ├── auth.py               # 认证路由（注册/登录/刷新/登出）
│   │   │   ├── books.py              # 书籍 CRUD + RBAC 权限控制
│   │   │   ├── chapters.py           # 章节 CRUD
│   │   │   ├── bookshelf.py          # 用户书架
│   │   │   ├── conversations.py      # 会话管理
│   │   │   └── chat.py               # SSE 流式对话
│   │   └── services/
│   │       ├── rag_service.py        # RAG 服务主入口（门面模式）
│   │       ├── chunking.py           # 文本分块模块
│   │       ├── retrieval.py          # 混合检索 + 重排序
│   │       ├── memory.py             # 对话记忆 + 分层摘要
│   │       └── generation.py         # System Prompt 构建 + 滑动窗口
│   └── web/                          # Vue 3 前端
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       └── src/
│           ├── main.ts               # 应用入口 + 全局错误处理
│           ├── App.vue
│           ├── style.css
│           ├── api/index.ts          # Axios 封装 + Token 管理
│           ├── router/index.ts       # 路由定义 + 导航守卫
│           ├── stores/
│           │   ├── auth.ts           # 认证状态
│           │   ├── bookshelf.ts      # 书架状态
│           │   ├── reader.ts         # 阅读器状态
│           │   └── toast.ts          # Toast 通知状态
│           ├── composables/
│           │   ├── useToast.ts       # Toast 组合式函数
│           │   └── useFormValidation.ts  # 表单验证组合式函数
│           ├── components/
│           │   ├── AiChatPanel.vue   # AI 对话面板（核心组件）
│           │   ├── AppToast.vue      # 全局 Toast 组件
│           │   ├── SkeletonCard.vue  # 骨架屏卡片
│           │   └── SkeletonList.vue  # 骨架屏列表
│           ├── views/
│           │   ├── HomePage.vue      # 首页（书库）
│           │   ├── BookDetailPage.vue
│           │   ├── ReaderPage.vue    # 阅读器
│           │   ├── BookshelfPage.vue
│           │   ├── LoginPage.vue
│           │   ├── RegisterPage.vue
│           │   ├── AuthorZone.vue
│           │   └── RankPage.vue
│           ├── utils/
│           │   └── markdown.ts       # Markdown 渲染 + 引用标注
│           └── types/
│               └── index.ts          # TypeScript 类型集中定义
└── .gitignore
```

---

## 二、环境初始化与工程配置

### 2.1 后端环境搭建

#### 2.1.1 Python 依赖管理

项目使用 `requirements.txt` 管理后端依赖，核心依赖包括：

```
fastapi          # ASGI 异步 Web 框架
uvicorn          # ASGI 服务器
sqlalchemy       # ORM 框架
pydantic         # 数据验证（FastAPI 内置）
pydantic-settings # 环境变量配置管理
PyJWT>=2.8.0     # JWT Token 签发与验证
httpx            # 异步 HTTP 客户端（Embedding 调用）
langchain-chroma # ChromaDB 向量库集成
langchain-openai # OpenAI 兼容接口（讯飞星辰）
langchain-text-splitters # 文本分块
chromadb         # 向量数据库
structlog>=24.1.0 # 结构化日志
slowapi>=0.1.9   # API 速率限制
```

#### 2.1.2 Pydantic Settings 配置管理

`config.py` 使用 Pydantic v2 的 `BaseSettings` 实现类型安全的配置管理。其核心机制是：通过 `model_config` 中的 `env_file` 和 `env_prefix` 自动将 `.env` 文件中的环境变量映射为 Python 类型化属性。

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",           # 无前缀，直接映射
        extra="forbid",          # 禁止额外字段，防止拼写错误
    )
    xfyun_api_key: str
    xfyun_base_url: str = "https://maas-api.cn-huabei-1.xf-yun.com/v2"
    xfyun_chat_model: str = "xop35qwen2b"
    xfyun_embedding_model: str = "xop3qwen8bembedding"
    auth_secret: str = "star-pavilion-dev-secret-change-in-production"
    access_token_ttl: int = 900      # 15 分钟
    refresh_token_ttl: int = 604800  # 7 天
    cors_origins: str = "http://localhost:5173"
    chroma_dir: str = "./chroma_data"
    default_user_id: int = 1
```

**底层原理**：Pydantic 的 `BaseSettings` 在类实例化时，会按优先级从高到低读取配置值：

1. 构造函数传入的参数
2. 环境变量（`os.environ`）
3. `.env` 文件
4. 类定义中的默认值

`extra="forbid"` 确保如果 `.env` 中存在未在 `Settings` 中声明的字段（如旧的 `API_KEY`），Pydantic 会抛出 `ValidationError`，这是一种"Fail-Fast"策略，能在启动阶段就暴露配置错误。

#### 2.1.3 数据库初始化

`database.py` 使用 SQLAlchemy 的声明式映射创建 SQLite 引擎和会话工厂：

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./star_pavilion.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

**SQLite 的 `check_same_thread=False`**：SQLite 默认不允许跨线程共享连接。FastAPI 使用线程池处理请求，因此需要关闭此检查。在生产环境中替换为 PostgreSQL 时，此参数会被忽略。

### 2.2 前端环境搭建

#### 2.2.1 Vite 构建配置

项目使用 Vite 5 作为构建工具，其核心优势在于：

- **ESM 原生开发服务器**：利用浏览器原生 ES Module 支持，按需编译，冷启动毫秒级
- **Rollup 打包**：生产构建使用 Rollup 进行 Tree-Shaking 和代码分割
- **HMR（Hot Module Replacement）**：模块热替换，修改代码后页面局部更新而非全量刷新

#### 2.2.2 TypeScript 配置

项目使用 `vue-tsc` 进行类型检查，配合 `vite build` 前的 `vue-tsc --noEmit` 确保类型安全。

---

## 三、数据模型设计

### 3.1 ORM 模型定义

项目使用 SQLAlchemy 声明式映射定义了 5 个核心模型：

#### 3.1.1 User（用户表）

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default="reader")
    created_at = Column(DateTime, server_default=func.now())
```

**设计要点**：

- `username` 设置 `unique=True` + `index=True`，唯一约束保证不重复，索引加速登录查询
- `role` 字段存储 RBAC 角色，默认为 `reader`
- `hashed_password` 存储的是 PBKDF2-SHA256 哈希值，而非明文

#### 3.1.2 Book / Chapter（书籍与章节）

```python
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    category = Column(String(50), default="未分类")
    description = Column(Text, default="")
    cover_url = Column(String(500), default="")
    vectorized = Column(Boolean, default=False)
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    chapter_number = Column(Integer, nullable=False)
    vectorized = Column(Boolean, default=False)
    book = relationship("Book", back_populates="chapters")
```

**`cascade="all, delete-orphan"` 的作用**：当删除一本书时，SQLAlchemy 会自动级联删除该书的所有章节。这是 ORM 层面的级联，确保关系数据的一致性。在项目中，我们还额外实现了 ChromaDB 向量的级联删除（见第六章）。

#### 3.1.3 Conversation（会话表）

```python
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    book_id = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    name = Column(String(200), default="新对话")
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**`messages = Column(JSON, default=list)`**：SQLite 从 3.9+ 开始支持 JSON 扩展，SQLAlchemy 的 `JSON` 类型会将 Python 列表/字典序列化为 JSON 字符串存储。这避免了创建额外的 `messages` 表，简化了读写操作。对于中小规模的对话历史（单次对话通常不超过 100 轮），这种方案性能足够。

#### 3.1.4 TokenBlacklist（Token 黑名单表）

```python
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    expired_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

**设计意图**：JWT 是无状态的，一旦签发无法主动撤销。黑名单表解决了"用户登出后 Token 仍有效"的问题。`jti`（JWT ID）是每个 Token 的唯一标识，`expired_at` 记录 Token 的过期时间，用于定期清理已过期的黑名单记录，防止表无限增长。

#### 3.1.5 Bookshelf（用户书架表）

```python
class Bookshelf(Base):
    __tablename__ = "bookshelf"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    current_chapter = Column(Integer, default=1)
    progress = Column(Float, default=0.0)
    __table_args__ = (UniqueConstraint("user_id", "book_id"),)
```

**联合唯一约束** `UniqueConstraint("user_id", "book_id")` 确保同一用户对同一本书只有一个书架记录。

---

## 四、认证与权限体系

### 4.1 JWT 双 Token 机制

#### 4.1.1 为什么需要双 Token？

传统的单 Token 方案存在一个矛盾：Token 有效期太长，被盗后风险大；有效期太短，用户频繁需要重新登录。双 Token 方案通过"短期 Access Token + 长期 Refresh Token"解决了这个问题：

- **Access Token**：有效期 15 分钟，存储在 JavaScript 内存变量中（不写入 localStorage），每次 API 请求通过 `Authorization: Bearer <token>` 头部发送
- **Refresh Token**：有效期 7 天，存储在 HttpOnly Cookie 中，浏览器自动在请求中携带，前端 JavaScript 无法读取

#### 4.1.2 Token 签发流程

```python
def create_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.access_token_ttl),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")

def create_refresh_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.refresh_token_ttl),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")
```

**HS256 算法原理**：HMAC-SHA256 是一种对称加密签名算法。签发时，服务端用 `auth_secret` 对 JWT Header + Payload 的 Base64URL 编码计算 HMAC-SHA256 摘要，作为签名附加到 Token 末尾。验证时，服务端重新计算摘要并与 Token 中的签名比对。由于使用同一个密钥，签名和验证效率都很高（O(1)），适合单体应用。

**JWT 结构**：`Header.Payload.Signature`

- Header: `{"alg": "HS256", "typ": "JWT"}`
- Payload: `{"sub": "1", "username": "alice", "role": "reader", "type": "access", "exp": 1714000000, "jti": "uuid"}`
- Signature: `HMACSHA256(base64url(header) + "." + base64url(payload), secret)`

#### 4.1.3 HttpOnly Cookie 的安全机制

Refresh Token 通过 `Set-Cookie` 响应头设置：

```python
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,       # JavaScript 无法读取
    secure=False,        # 开发环境关闭，生产环境应开启（HTTPS）
    samesite="lax",      # 防止 CSRF
    max_age=settings.refresh_token_ttl,
    path="/api/auth/refresh",  # 仅在刷新端点发送
)
```

**安全属性解析**：

- `httponly=True`：这是最关键的安全属性。它告诉浏览器：这个 Cookie 只能由浏览器在 HTTP 请求中自动携带，JavaScript 的 `document.cookie` API 无法访问它。这有效防御了 XSS 攻击窃取 Refresh Token。
- `samesite="lax"`：防止跨站请求伪造（CSRF）。`Lax` 模式允许顶级导航的 GET 请求携带 Cookie，但阻止跨站 POST 请求。
- `path="/api/auth/refresh"`：限制 Cookie 的作用域，只有访问 `/api/auth/refresh` 路径时浏览器才会发送此 Cookie，减少暴露面。

#### 4.1.4 前端 Token 管理与静默刷新

Access Token 存储在 JavaScript 模块级变量中（非 localStorage）：

```typescript
let accessToken: string | null = null

export function setAccessToken(token: string) {
  accessToken = token
}
export function getAccessToken(): string | null {
  return accessToken
}
export function clearAccessToken() {
  accessToken = null
}
```

**为什么不用 localStorage？** localStorage 中的数据对同源下的所有 JavaScript 代码可见，包括第三方脚本。如果网站存在 XSS 漏洞，攻击者可以通过 `localStorage.getItem()` 窃取 Token。而 JavaScript 变量存储在内存中，页面刷新后自然清空，安全性更高。

**Axios 拦截器实现静默刷新**：

```typescript
let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 如果正在刷新，将请求加入队列等待
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      try {
        const { data } = await axios.post('/api/auth/refresh', {}, {
          withCredentials: true,  // 发送 HttpOnly Cookie
        })
        setAccessToken(data.access_token)
        // 重试所有排队的请求
        pendingRequests.forEach((cb) => cb(data.access_token))
        pendingRequests = []
        // 重试原始请求
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch {
        clearAccessToken()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)
```

**并发请求处理机制**：当多个请求同时收到 401 时，第一个请求触发刷新，后续请求进入 `pendingRequests` 队列等待。刷新完成后，所有排队请求使用新 Token 重试。这避免了多个请求同时触发刷新导致的竞态条件。

### 4.2 RBAC 角色权限控制

#### 4.2.1 权限矩阵

```python
ROLES = {
    "reader": {"can_read": True, "can_write_bookshelf": True, "can_create_book": False, "can_delete_book": False},
    "author": {"can_read": True, "can_write_bookshelf": True, "can_create_book": True, "can_delete_book": False},
    "admin":  {"can_read": True, "can_write_bookshelf": True, "can_create_book": True, "can_delete_book": True},
}
```

#### 4.2.2 权限检查集成

在 `books.py` 路由中，写操作端点通过 FastAPI 的依赖注入系统实现权限检查：

```python
@router.post("/")
async def create_book(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_permission(current_user.role, "can_create_book"):
        raise HTTPException(status_code=403, detail="权限不足：需要作家或管理员权限")
    # ... 业务逻辑
```

**FastAPI 依赖注入原理**：`Depends(get_current_user)` 告诉 FastAPI 在处理请求前先执行 `get_current_user` 函数。该函数从请求头中提取 JWT、验证签名和有效期、检查黑名单，最终返回 `User` 对象或抛出 401 异常。这是一种"装饰器模式"的变体，将横切关注点（认证、鉴权）从业务逻辑中解耦。

### 4.3 API 速率限制

使用 `slowapi` 库实现基于 IP 的速率限制：

```python
# rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# auth.py - 敏感端点更严格
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, ...):
    ...
```

**底层原理**：slowapi 基于 `limits` 库实现了滑动窗口速率限制算法。对于 `100/minute`，它将时间窗口分为多个小桶（如每秒一个桶），每个桶记录该时间段的请求数。判断是否超限时，统计当前窗口内所有桶的请求总数。相比固定窗口算法，滑动窗口避免了窗口边界处的突发流量问题。

---

## 五、前端架构深度解析

### 5.1 Vue 3 响应式原理

Vue 3 使用 `Proxy` 替代了 Vue 2 的 `Object.defineProperty` 实现响应式系统。其核心原理：

```typescript
// 简化原理示意
const state = reactive({ count: 0 })
// 等价于
const state = new Proxy({ count: 0 }, {
  get(target, key) {
    track(target, key)  // 收集依赖
    return target[key]
  },
  set(target, key, value) {
    target[key] = value
    trigger(target, key)  // 触发更新
    return true
  }
})
```

**`Proxy` 相比 `defineProperty` 的优势**：

1. **可以拦截动态新增的属性**：Vue 2 需要 `Vue.set()`，Vue 3 直接赋值即可
2. **可以拦截数组索引和 length 变化**：Vue 2 对数组方法进行了重写（`push`、`pop` 等），Vue 3 原生支持
3. **性能更优**：`Proxy` 是语言层面的拦截，不需要递归遍历对象的所有属性

在项目中，所有 Store（auth、bookshelf、reader、toast）都使用 `reactive` 状态，组件中使用 `ref` 和 `computed` 实现局部响应式。

### 5.2 Pinia 状态管理与持久化

#### 5.2.1 Pinia 的设计哲学

Pinia 是 Vue 3 官方推荐的状态管理库，相比 Vuex 的改进：

- **去掉了 Mutations**：直接在 Actions 中修改 State，简化了代码
- **完整的 TypeScript 支持**：自动推导 State 类型
- **模块化设计**：每个 Store 是独立的模块，不需要嵌套

#### 5.2.2 状态持久化

使用 `pinia-plugin-persistedstate` 实现状态持久化到 localStorage：

```typescript
export const useReaderStore = defineStore('reader', {
  state: () => ({
    currentBookId: null as number | null,
    currentChapter: 1,
    fontSize: 18,
    theme: 'paper' as 'paper' | 'night' | 'eye',
    sidebarOpen: true,
  }),
  persist: true  // 全量持久化
})
```

**持久化原理**：插件在 Store 的 `$subscribe` 回调中监听状态变化，每次变化后将 State 序列化为 JSON 写入 `localStorage`。应用启动时，从 `localStorage` 读取数据并合并到 Store 的初始状态中。

**认证状态的持久化策略**：`auth` store 使用 `persist: true` 持久化 `user` 对象，但不持久化 `accessToken`（Token 仅存在于内存中）。页面刷新后，`hydrateSession()` 方法通过 HttpOnly Cookie 中的 Refresh Token 静默恢复会话：

```typescript
async hydrateSession() {
  try {
    const { data } = await axios.post('/api/auth/refresh', {}, {
      withCredentials: true,
    })
    this.setSession({ access_token: data.access_token, user: data.user })
  } catch {
    this.clearSession()
  }
}
```

### 5.3 路由守卫与导航控制

```typescript
router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await authStore.hydrateSession()  // 尝试静默恢复会话

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    return { path: '/' }
  }
})
```

**导航守卫执行流程**：

1. 用户访问 `/bookshelf`（`meta.requiresAuth = true`）
2. 守卫先调用 `hydrateSession()`，尝试用 Cookie 中的 Refresh Token 获取新 Access Token
3. 如果刷新成功，`isAuthenticated` 变为 `true`，放行
4. 如果刷新失败（Cookie 过期或不存在），重定向到 `/login?redirect=/bookshelf`
5. 登录成功后，通过 `redirect` 参数跳回原页面

### 5.4 表单验证架构

项目实现了一个声明式表单验证 Composable `useFormValidation`，支持以下规则类型：

```typescript
const { fields, validateAll, touchField } = useFormValidation({
  username: [
    { required: true, message: '请输入用户名' },
    { minLength: 2, message: '用户名至少 2 个字符' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { minLength: 6, message: '密码至少 6 个字符' },
    { validate: (value) => /[A-Z]/.test(value) || '密码需要包含大写字母' },
  ],
})
```

**验证策略**：

- **blur 验证**：用户离开输入框时触发 `touchField()`，仅验证当前字段
- **submit 验证**：提交时调用 `validateAll()`，全量验证所有字段
- **服务端错误映射**：登录失败时，根据错误信息中的关键词（如"用户名"、"密码"）映射到具体字段的错误提示

### 5.5 全局错误处理

```typescript
app.config.errorHandler = (err, instance, info) => {
  console.error(`[Vue Error] ${info}:`, err)
  try {
    const toastStore = useToastStore()
    toastStore.error(`应用错误: ${err.message}`)
  } catch { /* pinia 未就绪 */ }
}

window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise]:', event.reason)
  try {
    const toastStore = useToastStore()
    toastStore.error('网络请求异常，请稍后重试')
  } catch { /* pinia 未就绪 */ }
})
```

**双层错误捕获**：

1. `app.config.errorHandler`：捕获 Vue 组件生命周期、渲染、计算属性等 Vue 内部的未捕获错误
2. `window.onunhandledrejection`：捕获未处理的 Promise 拒绝（如 API 请求失败但未 catch）

---

## 六、RAG（检索增强生成）系统

这是项目最核心的 AI 模块，采用模块化架构，将 RAG 流水线拆分为 4 个独立模块。

### 6.1 系统架构总览

```
用户提问
    │
    ▼
┌─────────────────────────────────────────────────┐
│              RAG Pipeline                        │
│                                                   │
│  1. chunking.py ─── 文本分块（双层策略）          │
│         │                                          │
│         ▼                                          │
│  2. retrieval.py ── 混合检索 + 重排序             │
│         │                                          │
│         ▼                                          │
│  3. memory.py ───── 对话记忆检索                   │
│         │                                          │
│         ▼                                          │
│  4. generation.py ── System Prompt 构建            │
│         │                                          │
│         ▼                                          │
│  LLM 流式生成 ────── SSE 推送给前端               │
└─────────────────────────────────────────────────┘
```

### 6.2 文本分块（Chunking）

#### 6.2.1 为什么需要分块？

大语言模型的上下文窗口有限（本项目使用的讯飞星辰模型通常支持 8K-32K Token），而一部长篇小说可能有数十万字。直接将整本书输入 LLM 既不现实也不经济。分块（Chunking）将长文本切分为语义完整的片段，每个片段独立向量化后存入向量数据库，检索时只召回最相关的几个片段。

#### 6.2.2 双层分块策略

```python
def create_paragraph_splitter(chunk_size=500, chunk_overlap=50):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", ""],
    )

def create_plot_splitter(chunk_size=1000, chunk_overlap=100):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", ""],
    )
```

**设计原理**：

1. **段落级分块（500 字）**：使用更细粒度的分隔符（包括 `！`、`？`、`；`），适合精确检索。当用户问"某角色在哪一章说了什么"时，小粒度块能提供更精确的定位。

2. **剧情级分块（1000 字）**：使用更粗的分隔符，保留更完整的上下文。适合需要理解剧情走向的问题，如"这一章的主要矛盾是什么"。

3. **chunk_overlap（块重叠）**：相邻块之间有 50-100 字符的重叠，防止关键信息被切断在两个块的边界处。例如，一个跨越第 3 段和第 4 段的对话，如果没有重叠，可能被拆分到两个块中导致语义不完整。

**RecursiveCharacterTextSplitter 的递归分割原理**：该分块器按照 `separators` 列表的顺序尝试分割。首先尝试按 `\n\n`（段落）分割，如果某个块仍然超过 `chunk_size`，则递归地按 `\n`（换行）分割，以此类推。这确保了分割点优先选择自然语言边界（段落 > 句子 > 字符），而非机械地按字符数截断。

### 6.3 Embedding 向量化

#### 6.3.1 讯飞星辰 Embedding 接口

项目通过自定义 `XfyunEmbeddings` 类对接讯飞星辰的 Embedding API：

```python
class XfyunEmbeddings(Embeddings):
    def _request_embeddings(self, texts: list[str]) -> list[list[float]]:
        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": texts},
            timeout=60.0,
        )
        payload = response.json()
        return [item["embedding"] for item in payload["data"]]
```

**为什么手动实现而不直接用 SDK？** 讯飞星辰的 OpenAI 兼容接口在某些参数上可能与 LangChain 内置的 OpenAI Embeddings 不完全兼容。手动实现可以精确控制请求参数，避免 SDK 自动注入不支持的字段导致 API 报错。

#### 6.3.2 向量数据库（ChromaDB）

ChromaDB 是一个轻量级的嵌入式向量数据库，适合开发和小规模部署：

```python
def _get_chroma(self, book_id: int) -> Chroma:
    return Chroma(
        collection_name=f"novel_book_{book_id}",
        embedding_function=self.embeddings,
        persist_directory=self.chroma_dir,
    )
```

**每本书一个 Collection 的设计**：将不同书籍的向量存储在不同的 Collection 中，检索时只需在对应书籍的 Collection 内搜索，避免了跨书籍的噪声干扰，同时提高了检索速度（减少搜索空间）。

**ChromaDB 底层存储**：ChromaDB 默认使用 SQLite 存储元数据，使用 hnswlib 库实现 HNSW（Hierarchical Navigable Small World）索引进行近似最近邻搜索。HNSW 是一种基于图的索引结构，构建多层导航图，查询时从顶层入口开始，逐层向下搜索，时间复杂度约为 O(log N)，在百万级向量规模下仍能保持毫秒级响应。

### 6.4 混合检索与重排序

#### 6.4.1 检索流程

```python
def hybrid_search(chroma, query, query_keywords, top_k=5, filters=None,
                  keyword_weight=0.3, vector_weight=0.7):
    # Step 1: 向量相似度检索（扩大召回）
    expanded_k = top_k * 2
    vector_results = chroma.similarity_search(query, k=expanded_k, filter=filters)

    # Step 2: 基于关键词重叠度的重排序
    scored_results = []
    for doc in vector_results:
        content = doc.page_content.lower()
        overlap_count = sum(1 for kw in query_keywords if kw.lower() in content)
        keyword_score = overlap_count / max(len(query_keywords), 1)
        idx = vector_results.index(doc)
        vector_score = 1.0 - (idx / max(len(vector_results), 1))
        final_score = vector_weight * vector_score + keyword_weight * keyword_score
        scored_results.append({"content": doc.page_content, "metadata": doc.metadata, "score": final_score})

    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]
```

#### 6.4.2 向量检索原理

向量检索的核心是**余弦相似度**（Cosine Similarity）。Embedding 模型将文本映射为高维向量（如 768 维），语义相近的文本在向量空间中距离更近。

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

其中 `A · B` 是向量点积，`||A||` 是向量的 L2 范数。余弦相似度的值域为 [-1, 1]，值越大表示方向越一致（语义越相近）。

ChromaDB 内部使用 HNSW 索引加速最近邻搜索，不需要遍历所有向量计算相似度。

#### 6.4.3 关键词提取

```python
def extract_keywords(query: str) -> list[str]:
    words = re.split(r'[\s,，。！？、；：""''（）\(\)\[\]【】]+', query)
    stop_words = {'的', '了', '是', '在', '有', '和', ...}
    return [w.strip() for w in words if w.strip() and w.strip() not in stop_words and len(w.strip()) > 0]
```

采用基于停用词的简单分词策略，过滤掉中文常见虚词（的、了、是...），保留实词作为关键词。对于中文场景，这种轻量级方案在大多数查询中表现足够，避免了引入 jieba 等分词库的额外依赖。

#### 6.4.4 重排序的数学逻辑

重排序采用**加权线性组合**策略：

```
final_score = 0.7 × vector_score + 0.3 × keyword_score
```

- `vector_score`：基于向量检索结果的排名位置计算，第一名得 1.0，最后一名得 0.0。这是一种"排名分数"（Rank Score），而非原始相似度值。
- `keyword_score`：查询关键词在文档中的命中率 = 命中关键词数 / 总关键词数。

**为什么使用排名分数而非原始相似度？** 不同查询的相似度分布差异很大（有的查询最高相似度 0.9，有的只有 0.6），直接使用原始值会导致分数不可比。排名分数将所有查询归一化到 [0, 1] 区间，使权重参数在不同查询间保持一致的效果。

**权重选择（0.7/0.3）**：向量检索权重更高，因为它能捕捉语义相似性（如"悲伤"和"难过"会被视为相近），而关键词匹配只能捕捉字面匹配。关键词权重作为补充，确保包含明确关键词的文档不会被遗漏。

### 6.5 对话记忆与分层摘要

#### 6.5.1 对话记忆存储

每轮对话结束后，将 user + assistant 消息对存入 ChromaDB 的 `conversation_memory` Collection：

```python
def store_turn(self, user_id, book_id, conversation_id, turn_index, user_msg, assistant_msg):
    text = f"用户：{user_msg}\n助手：{assistant_msg}"
    metadata = {
        "user_id": user_id,
        "book_id": book_id,
        "conversation_id": conversation_id,
        "turn_index": turn_index,
        "role": "conversation_turn",
    }
    self.memory_collection.add_texts(texts=[text], metadatas=[metadata])
```

**设计意图**：当用户在第 20 轮对话中提到"之前你说的那个角色"，系统通过向量相似度检索之前的相关对话轮次，将上下文注入 System Prompt，使 LLM 能够"回忆"之前的讨论内容。

#### 6.5.2 分层摘要机制

```python
async def hierarchical_summarize(self, messages, conversation_id):
    turn_count = sum(1 for m in messages if m.get("role") == "user")
    if turn_count < self.sub_summary_interval:  # 默认 10 轮
        return None

    # 1. 生成子摘要
    sub_summary = await self.summarize_messages(messages)
    self.memory_collection.add_texts(
        texts=[f"[子摘要-第{turn_count}轮]\n{sub_summary}"],
        metadatas=[{"conversation_id": conversation_id, "role": "sub_summary"}]
    )

    # 2. 检索所有子摘要，生成总摘要
    all_summaries = self.memory_collection.similarity_search(
        f"对话摘要 conversation_id={conversation_id}",
        k=10,
        filter={"conversation_id": conversation_id, "role": "sub_summary"},
    )
    if len(all_summaries) > 1:
        total_summary = await self.summarize_messages(
            [{"role": "system", "content": f"以下是多段对话子摘要，请合并为一段总摘要：\n\n{combined}"}]
        )
        return total_summary
```

**分层摘要解决的问题**：长对话中，如果保留所有历史消息，会超出 LLM 的上下文窗口。分层摘要策略：

1. 每 10 轮对话生成一次"子摘要"
2. 子摘要存储到 ChromaDB，可被向量检索
3. 当子摘要超过 1 个时，合并生成"总摘要"
4. 在构建最终 Prompt 时，用总摘要替代旧消息，保留最近 8 轮原文

这种"滑动窗口 + 摘要"的组合策略，在保留近期精确上下文的同时，不丢失远期的重要信息。

### 6.6 System Prompt 构建与 XML 标签

```python
def build_system_prompt(base_prompt, search_results, direct_context, memory_results,
                        book_id, has_vector_results):
    system_prompt = base_prompt

    if search_results:
        context_parts = []
        for r in search_results:
            chapter_title = r["metadata"].get("chapter_title", "未知章节")
            context_parts.append(f"【{chapter_title}】\n{r['content']}")
        system_prompt += f"\n\n<novel_context>\n{context_text}\n</novel_context>"

    if direct_context:
        system_prompt += f"\n\n<current_chapter>\n{direct_context}\n</current_chapter>"

    if memory_results:
        system_prompt += f"\n\n<conversation_history>\n{memory_text}\n</conversation_history>"

    if search_results and book_id:
        system_prompt += "\n\n<citation_instruction>当你引用小说中的具体内容时，请在引用后标注来源，格式为：[来源: 第X章 章节名]</citation_instruction>"
```

**XML 标签的作用**：使用 `<novel_context>`、`<current_chapter>`、`<conversation_history>` 等 XML 标签将不同来源的内容清晰分隔。这利用了 LLM 对结构化标记的良好理解能力，帮助模型区分"小说原文"、"当前章节"和"历史对话"，避免混淆不同来源的信息。

**引用标注指令**：通过 `<citation_instruction>` 标签指示 LLM 在引用小说内容时标注来源章节。前端 Markdown 渲染器会将 `[来源: 第X章 章节名]` 转换为可点击的引用标签，实现回答的可溯源。

### 6.7 滑动窗口消息构建

```python
def build_sliding_window_messages(messages, system_prompt, window_size=8, older_summary=None):
    turns = []  # 按轮次分组
    current_turn = []
    for msg in messages:
        current_turn.append(msg)
        if msg.get("role") == "assistant":
            turns.append(current_turn)
            current_turn = []

    lc_messages = [SystemMessage(content=system_prompt)]
    if len(turns) > window_size:
        # 旧消息用摘要替代
        older_turns = turns[:-window_size]
        recent_turns = turns[-window_size:]
        if older_summary:
            lc_messages.append(HumanMessage(content=f"[之前的对话摘要]\n{older_summary}"))
        for turn in recent_turns:
            for msg in turn:
                # 转换为 LangChain Message 对象
```

**滑动窗口原理**：保留最近 `window_size`（默认 8）轮对话的原文，超出部分使用分层摘要替代。这控制了发送给 LLM 的 Token 数量，在上下文质量和成本之间取得平衡。

### 6.8 SSE 流式传输

#### 6.8.1 后端 SSE 端点

```python
@router.post("/stream")
async def chat_stream(req: ChatRequest, ...):
    async def event_generator():
        full_response = ""
        async for chunk in rag_service.stream_chat(
            messages=req.messages, book_id=req.book_id, ...
        ):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**SSE（Server-Sent Events）原理**：SSE 是一种基于 HTTP 的单向实时通信协议。服务端保持 HTTP 连接不断开，持续向客户端推送数据。每个事件以 `data: ` 开头，以 `\n\n` 结尾。相比 WebSocket，SSE 更轻量（基于标准 HTTP）、自动重连（浏览器原生支持）、更适合单向推送场景。

#### 6.8.2 前端流式接收

```typescript
async function sendMessage() {
  const response = await streamChat(messages.value, props.bookId, props.chapterId, searchAll.value, convId)
  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    consumeSseChunk(decoder.decode(value, { stream: true }))
    scrollToBottom()
  }
}

function consumeSseChunk(chunk: string) {
  parserBuffer.value += chunk
  const blocks = parserBuffer.value.split('\n\n')
  parserBuffer.value = blocks.pop() || ''  // 最后一个可能不完整，保留到下次

  for (const block of blocks) {
    const line = block.split('\n').find(item => item.startsWith('data: '))
    if (!line) continue
    const data = line.slice(6).trim()
    if (data === '[DONE]') continue
    const parsed = JSON.parse(data)
    if (parsed.content) streamingContent.value += parsed.content
  }
}
```

**流式解析的关键**：网络传输可能将一个完整的 SSE 事件拆分为多个 TCP 包到达，因此使用 `parserBuffer` 缓存不完整的块。`split('\n\n')` 将缓冲区按事件边界分割，最后一个元素可能不完整（没有以 `\n\n` 结尾），保留到下次接收时拼接。

**`fetch` 而非 `axios` 的原因**：Axios 的响应拦截器会等待整个响应完成后才触发回调，无法实现流式处理。`fetch` API 的 `response.body` 返回一个 `ReadableStream`，可以通过 `getReader()` 逐块读取。

### 6.9 数据一致性：级联删除

当删除书籍或章节时，需要同步清理 ChromaDB 中的向量数据：

```python
# books.py - 删除书籍
@router.delete("/{book_id}")
async def delete_book(book_id: int, ...):
    # 1. 删除 SQLite 中的章节
    db.query(Chapter).filter(Chapter.book_id == book_id).delete()
    # 2. 级联删除 ChromaDB 向量
    try:
        rag_service = get_rag_service()
        rag_service.delete_book_vectors(book_id)
    except Exception:
        pass  # 向量删除失败不影响主流程
    # 3. 删除 SQLite 中的书籍
    db.delete(book)
    db.commit()
```

```python
# rag_service.py
def delete_book_vectors(self, book_id: int):
    chroma = self._get_chroma(book_id)
    chroma.delete_collection()  # 删除整个 Collection

def delete_chapter_vectors(self, book_id: int, chapter_id: int):
    chroma = self._get_chroma(book_id)
    chroma.delete(where={"chapter_id": chapter_id})  # 按元数据过滤删除
```

**一致性策略**：采用"SQLite 为主，ChromaDB 为辅"的策略。SQLite 中的数据是权威来源，ChromaDB 是衍生数据。删除时先删 SQLite，再尝试删 ChromaDB。如果 ChromaDB 删除失败，不影响主流程（向量数据成为"孤儿数据"，但不会导致功能异常）。这是一种"最终一致性"策略。

---

## 七、对话持久化与用户隔离

### 7.1 对话生命周期管理

前端 `AiChatPanel.vue` 组件实现了完整的对话生命周期：

```
用户打开面板 → 加载对话列表 → 选择/创建对话 → 发送消息 → 流式接收 → 保存到后端
```

**核心状态**：

- `conversationId`：当前活跃的对话 ID
- `messages`：当前对话的消息列表（本地内存）
- `conversationList`：对话历史列表

**`ensureConversation()` 机制**：用户发送第一条消息时，自动创建后端对话记录，后续消息都关联到此对话 ID。这实现了"无感创建"——用户不需要手动点击"新建对话"。

### 7.2 用户隔离

所有会话 API 都通过 `get_current_user` 依赖注入强制用户认证，并按 `user_id` 过滤数据：

```python
@router.get("")
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    # ...
```

切换账号后，`hydrateSession()` 会用新账号的 Refresh Token 获取新 Access Token，对话列表和消息自然隔离（因为查询条件是 `user_id = 新用户ID`）。

---

## 八、前端 UI 工程化

### 8.1 骨架屏（Skeleton Screen）

骨架屏在数据加载期间显示灰色占位块，模拟内容布局，提供比 Loading Spinner 更好的用户感知：

```vue
<!-- SkeletonCard.vue -->
<div class="skeleton-card">
  <div class="skeleton-card__cover">
    <div class="skeleton-pulse"></div>
  </div>
  <div class="skeleton-card__body">
    <div class="skeleton-pulse skeleton-pulse--title"></div>
    <div class="skeleton-pulse skeleton-pulse--text"></div>
  </div>
</div>
```

**Shimmer 动画原理**：使用 CSS `linear-gradient` 配合 `background-size: 200%` 和 `@keyframes` 实现从左到右的光泽扫过效果：

```css
.skeleton-pulse {
  background: linear-gradient(90deg,
    rgba(200, 180, 160, 0.15) 25%,
    rgba(200, 180, 160, 0.3) 50%,
    rgba(200, 180, 160, 0.15) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}
@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### 8.2 Toast 通知系统

Toast 系统由三层组成：

1. **Pinia Store** (`toast.ts`)：管理通知队列，支持 `success`/`error`/`warning`/`info` 四种类型
2. **Composable** (`useToast.ts`)：提供 `useToast().success(msg)` 快捷调用
3. **Vue 组件** (`AppToast.vue`)：通过 `Teleport` 挂载到 `body`，使用 `TransitionGroup` 实现入场/离场动画

### 8.3 Markdown 渲染与引用标注

自定义 Markdown 渲染器支持标准语法 + 引用标签：

```typescript
function renderInline(input: string) {
  return escapeHtml(input)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\[来源:\s*第(\d+)章\s*([^\]]*)\]/g,
      '<span class="citation-tag" data-chapter="$1">[来源: 第$1章 $2]</span>')
}
```

引用标签 `[来源: 第X章 章节名]` 被渲染为带有 `citation-tag` 类名的 `<span>` 元素，通过 CSS 样式化为可点击的标签，视觉上与普通文本区分。

---

## 九、后端工程化

### 9.1 结构化日志（structlog）

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO
    cache_logger_on_first_use=True,
)
```

**structlog 的优势**：相比 Python 标准库的 `logging`，structlog 输出结构化数据（字典），便于日志聚合系统（如 ELK、Loki）解析和检索。每个日志事件包含 `level`、`timestamp`、`event` 等标准字段，以及业务自定义字段。

### 9.2 HTTP 请求日志中间件

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info("http_request", method=request.method, path=request.url.path,
                status=response.status_code, duration_ms=round(duration * 1000, 2))
    return response
```

记录每个 HTTP 请求的方法、路径、状态码和耗时，用于性能监控和问题排查。

### 9.3 全局异常处理

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc), exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})
```

捕获所有未处理的异常，记录结构化日志并返回统一的 500 响应，防止敏感的错误信息泄露给客户端。

---

## 十、FastAPI 异步处理机制

### 10.1 ASGI 与异步 I/O

FastAPI 基于 ASGI（Asynchronous Server Gateway Interface）协议，底层使用 Starlette 框架。与传统的 WSGI（同步）不同，ASGI 支持异步 I/O 操作：

```python
# 同步（WSGI）- 阻塞
@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()  # 阻塞等待数据库响应
    return books

# 异步（ASGI）- 非阻塞
@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async for chunk in rag_service.stream_chat(...):  # 非阻塞等待 LLM 响应
        yield chunk
```

**异步 I/O 的核心原理**：Python 的 `async/await` 基于协程（Coroutine）和事件循环（Event Loop）。当一个异步操作（如 HTTP 请求、数据库查询）等待 I/O 时，协程会"挂起"（yield control），事件循环可以执行其他协程。当 I/O 完成时，协程被"恢复"（resume）。这实现了单线程下的并发处理。

**本项目中的异步场景**：

1. LLM 流式生成：`async for chunk in self.llm.astream(lc_messages)` — 等待模型逐 token 生成
2. Embedding HTTP 请求：`httpx.post()` — 等待讯飞 API 响应
3. SSE 流式推送：`StreamingResponse(event_generator())` — 逐步推送数据

---

## 十一、前端类型系统

### 11.1 类型集中化

`types/index.ts` 集中定义了项目中使用的 TypeScript 类型：

```typescript
export type UserRole = 'reader' | 'author' | 'admin'
export interface UserInfo { id: number; username: string; role: UserRole }
export interface ChatMessage { role: 'user' | 'assistant' | 'system'; content: string }
export interface ConversationSummary { id: number; name: string; book_id: number | null }
export interface BookshelfEntry { id: number; book_id: number; book_title: string; ... }
export interface ApiResponse<T = unknown> { data?: T; detail?: string }
export interface PaginatedResponse<T> { total: number; page: number; items: T[] }
```

**类型集中化的优势**：

1. **单一数据源**：所有接口定义在一个文件中，修改时只需改一处
2. **跨组件复用**：多个组件引用同一个类型定义，确保数据结构一致
3. **IDE 智能提示**：TypeScript 编译器根据类型定义提供自动补全和类型检查

---

## 十二、关键技术决策记录

### 12.1 为什么选择 SQLite 而非 PostgreSQL？

**开发阶段**：SQLite 是零配置的嵌入式数据库，无需安装和启动独立服务，适合快速开发和单机部署。SQLAlchemy 的 ORM 抽象使得未来迁移到 PostgreSQL 只需更改连接字符串和少量 SQL 方言差异。

**局限性**：SQLite 不支持并发写入（写锁是数据库级别的），在高并发场景下可能成为瓶颈。生产环境建议迁移到 PostgreSQL。

### 12.2 为什么选择 ChromaDB 而非 Milvus/Qdrant？

ChromaDB 是嵌入式向量数据库，与 SQLite 类似，零配置启动。对于单本书（通常不超过 1000 个文本块）的向量检索，ChromaDB 的性能完全足够。Milvus/Qdrant 适合百万级以上的大规模向量检索，但需要独立部署和更多资源。

### 12.3 为什么 Access Token 存内存而非 localStorage？

这是一个安全性与便利性的权衡：

- **localStorage**：持久化，刷新不丢失，但可被 XSS 攻击读取
- **Cookie**：HttpOnly 可防 XSS，但 CSRF 风险需要 SameSite 策略配合
- **内存变量**：最安全（XSS 无法读取 JS 变量以外的内存），但刷新后丢失

项目选择了"内存 + Cookie 刷新"的组合方案：Access Token 存内存（短期，15 分钟），Refresh Token 存 HttpOnly Cookie（长期，7 天）。刷新后通过静默刷新机制恢复，用户体验与 localStorage 方案一致，但安全性更高。

### 12.4 为什么手动实现 SSE 解析而非使用 EventSource API？

浏览器原生 `EventSource` API 只支持 GET 请求，而项目的流式对话需要 POST 请求（因为需要发送消息体）。因此使用 `fetch` + `ReadableStream` 手动解析 SSE 格式。

---

## 十三、部署与运维考量

### 13.1 环境变量管理

- `.env`：实际环境变量（不提交到 Git）
- `.env.example`：环境变量模板（提交到 Git，供新开发者参考）

### 13.2 生产环境检查清单

- [ ] 将 `AUTH_SECRET` 更换为强随机字符串（至少 32 位）
- [ ] 将 Cookie 的 `secure` 参数设为 `True`（需要 HTTPS）
- [ ] 将 SQLite 迁移为 PostgreSQL
- [ ] 将 ChromaDB 迁移为独立部署的向量数据库
- [ ] 配置 CORS `cors_origins` 为实际域名
- [ ] 启用 `structlog` 的 JSON 输出模式（替代 ConsoleRenderer）
- [ ] 配置反向代理（Nginx）处理 HTTPS 和静态文件

---

## 十四、总结

星阁项目从零到 Production-Ready 的技术路线，涵盖了以下核心领域：

1. **认证安全**：JWT 双 Token + HttpOnly Cookie + RBAC + 速率限制
2. **AI 引擎**：RAG 双层分块 + 混合检索 + 重排序 + 分层摘要 + 引用标注
3. **前端架构**：Vue 3 Composition API + Pinia 持久化 + 表单验证 + 骨架屏 + Toast
4. **后端工程**：FastAPI 异步 + 结构化日志 + 全局异常处理 + 中间件
5. **数据一致性**：SQLite 与 ChromaDB 级联删除 + 最终一致性策略

整个技术栈的选择遵循"开发效率优先，预留生产迁移路径"的原则，在保证功能完整性的同时，确保代码结构清晰、可维护、可扩展。
