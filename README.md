# Star-Pavilion（星阁）

> 用 AI 重新定义小说阅读体验

一个在校大学生的个人研究项目 -- 基于 RAG 检索增强生成技术，让读者在阅读小说时可以和 AI 实时对话，讨论剧情、分析人物、甚至预测走向。

---

## 为什么做这个项目

说实话，最初只是因为对 RAG 和 LLM 应用充满了好奇。看了很多论文和博客，总觉得"光看不做等于没学"，于是决定动手搭一个完整的前后端项目来验证自己的想法。

从选技术栈到踩各种坑（比如 ChromaDB 的 metadata 过滤语法、SSE 流式传输在前端的解析、双层分块策略的 chunk_size 反复调参），整个过程虽然磕磕绊绊，但确实让我对"AI 应用到底怎么落地"有了更具体的理解。这不是一个生产级项目，但它是我认真探索 RAG 技术的一个阶段性成果。

---

## 核心功能

- 📖 **沉浸式阅读器** -- 支持多主题切换、字号调节，提供舒适的阅读体验
- 💬 **RAG 智能对话** -- 基于小说内容的检索增强对话，AI 回答有据可查，不是瞎编
- 🔄 **SSE 流式传输** -- 打字机效果的实时响应，体验接近 ChatGPT
- 🧠 **抗遗忘多轮记忆** -- 多层级缓存设计，让 AI 在长对话中不会"失忆"
- 🔒 **会话隔离** -- 每本书、每个章节的对话互不干扰，支持防剧透模式

---

## 技术架构

### 前端

| 技术 | 用途 |
|------|------|
| Vue 3 (Composition API) | 组件化开发，响应式状态管理 |
| TypeScript | 类型安全，减少运行时错误 |
| Vite | 极速开发体验和构建 |
| Pinia + persistedstate | 全局状态管理 + 本地持久化 |
| TailwindCSS | 原子化 CSS，快速搭建 UI |
| Vue Router | SPA 路由，页面懒加载 |

### 后端

| 技术 | 用途 |
|------|------|
| FastAPI | 高性能异步 Web 框架 |
| SQLAlchemy | ORM，操作 SQLite 数据库 |
| SQLite | 轻量级关系型数据库，存储业务数据 |
| ChromaDB | 向量数据库，存储文本嵌入 |
| LangChain | LLM 应用开发框架 |
| OpenAI API (兼容接口) | LLM 推理 + 文本向量化 |

---

## 设计亮点

### 1. 基于 Metadata 过滤的会话隔离

每个用户的对话数据需要严格隔离，这里没有用复杂的权限网关，而是通过**数据层面的维度过滤**来实现：

- **RBAC 角色绑定**：API 请求通过 `Authorization` Header 携带 `api_key`，后端据此识别用户身份
- **SQLite 维度**：`Conversation` 表的 `user_id` / `book_id` / `chapter_id` 字段实现关系型数据隔离
- **ChromaDB 维度**：每个分块携带 `book_id`、`chapter_id`、`chunk_type` 等 metadata，检索时通过 `filter` 参数限定范围

```python
# ChromaDB metadata 过滤示例 -- 只检索当前章节及之前的内容（防剧透）
results = chroma.similarity_search(
    query,
    k=top_k,
    filter={"chapter_id": {"$le": max_chapter_id}},
)
```

这个方案的优点是简单直接，不需要额外的中间件；缺点是如果未来用户量变大，可能需要更细粒度的权限控制。

### 2. 多层级缓存的抗遗忘记忆流

LLM 的上下文窗口有限，长对话容易"遗忘"前面的内容。为了解决这个问题，设计了一个多层级缓存架构：

```
IndexedDB (前端即时缓存)
    ↓ 页面刷新不丢失
SQLite (完整历史落盘)
    ↓ 结构化存储，支持按 user_id / book_id 查询
ChromaDB (向量化语义检索)
    ↓ 语义相似度匹配，召回最相关的历史片段
LLM 摘要压缩
    ↓ 超过窗口长度时，对早期对话进行摘要压缩
```

- **前端层**：Pinia + `pinia-plugin-persistedstate` 将对话状态持久化到 IndexedDB，页面刷新后对话不丢失
- **后端层**：`Conversation` 模型用 JSON 字段存储完整消息列表，支持随时回溯
- **检索层**：历史对话内容可以被分块索引到 ChromaDB，后续对话时通过语义检索召回相关上下文
- **压缩层**：当对话轮数超过 LLM 上下文窗口时，对早期消息进行摘要压缩，保留关键信息

### 3. 双层分块检索策略

小说文本的分块策略直接决定了 RAG 的检索质量。经过反复实验，最终采用了双层分块方案：

| 分块类型 | chunk_size | chunk_overlap | 适用场景 |
|----------|-----------|---------------|---------|
| 段落级 (paragraph) | 500 字符 | 50 字符 | 精确检索，如"某个人物说了什么" |
| 剧情点级 (plot) | 1000 字符 | 100 字符 | 上下文理解，如"这一章讲了什么" |

```python
# 段落级分块器 -- 细粒度，按自然段落和句号切分
paragraph_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "；", ""],
)

# 剧情点级分块器 -- 粗粒度，保留更多上下文
plot_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", ""],
)
```

两种分块结果都存入同一个 ChromaDB Collection，通过 `chunk_type` metadata 区分。检索时可以根据问题类型灵活选择，或者混合使用取并集。

### 4. SSE 流式对话

为了实现类似 ChatGPT 的打字机效果，采用了 SSE（Server-Sent Events）方案：

**后端**：FastAPI 的 `StreamingResponse` + `text/event-stream` 媒体类型

```python
@router.post("/stream")
async def stream_chat(req: ChatRequest):
    async def event_generator():
        async for chunk in rag_service.stream_chat(...):
            data = json.dumps({"content": chunk}, ensure_ascii=False)
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**前端**：原生 `fetch` + `ReadableStream` + `TextDecoder`（stream 模式）

```typescript
const response = await streamChat(messages, bookId, chapterId)
const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  const text = decoder.decode(value, { stream: true })
  // 逐行解析 SSE data 字段，实时更新 UI
}
```

没有用 EventSource（因为它只支持 GET 请求），也没有引入额外的 SSE 库，原生 API 就够用了。踩的一个坑是 `TextDecoder` 的 `stream: true` 选项不能漏，否则多字节字符（比如中文）可能会在 chunk 边界处被截断，出现乱码。

---

## 快速启动

### 环境要求

- Node.js >= 18
- Python >= 3.10
- pnpm

### 后端

```bash
# 1. 进入后端目录
cd apps/api

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 配置环境变量（编辑 .env 文件）
# OPENAI_API_KEY=your_api_key
# OPENAI_BASE_URL=your_api_base_url

# 4. 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
# 1. 回到项目根目录
cd ../..

# 2. 安装前端依赖
pnpm install

# 3. 启动前端开发服务器
pnpm dev:web
```

前端默认运行在 `http://localhost:5173`，已配置 Vite proxy 将 `/api` 请求转发到后端 `http://localhost:8000`。

也可以在根目录通过 `pnpm dev:api` 一键启动后端。

---

## 项目结构

```
star-pavilion/
├── apps/
│   ├── api/                      # 后端服务 (FastAPI)
│   │   ├── routers/
│   │   │   ├── books.py          # 书籍与章节接口
│   │   │   ├── bookshelf.py      # 书架管理接口
│   │   │   ├── chat.py           # SSE 流式对话接口
│   │   │   └── conversations.py  # 会话管理接口
│   │   ├── services/
│   │   │   └── rag_service.py    # RAG 核心服务（分块、检索、流式生成）
│   │   ├── models.py             # SQLAlchemy 数据模型
│   │   ├── database.py           # 数据库连接配置
│   │   ├── config.py             # 环境变量配置
│   │   ├── main.py               # FastAPI 应用入口
│   │   └── requirements.txt      # Python 依赖
│   │
│   └── web/                      # 前端应用 (Vue 3)
│       └── src/
│           ├── api/
│           │   └── index.ts      # API 请求封装（Axios + Fetch）
│           ├── components/
│           │   ├── AiChatPanel.vue   # AI 对话面板（SSE 流式）
│           │   ├── BookCard.vue      # 书籍卡片组件
│           │   └── NavBar.vue        # 导航栏
│           ├── views/
│           │   ├── HomePage.vue      # 首页
│           │   ├── BookDetailPage.vue # 书籍详情
│           │   ├── ReaderPage.vue    # 阅读器
│           │   ├── RankPage.vue      # 排行榜
│           │   └── AuthorZone.vue    # 作者专区
│           ├── stores/
│           │   ├── reader.ts         # 阅读器状态
│           │   └── bookshelf.ts      # 书架状态
│           ├── composables/
│           │   └── useScroll.ts      # 滚动相关 composable
│           ├── directives/
│           │   └── lazyLoad.ts       # 图片懒加载指令
│           ├── router/
│           │   └── index.ts          # 路由配置
│           └── main.ts               # 应用入口
│
├── package.json                   # 根项目配置
├── pnpm-workspace.yaml            # pnpm 工作区配置
└── README.md
```

---

## License

[MIT](./LICENSE)
