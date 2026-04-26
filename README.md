# Star Pavilion

> AI Novel Reading Assistant: 一个面向前端开发 + AI 应用求职展示的小说阅读平台。

Star Pavilion 不是追求海量真实小说内容的生产站点，而是一个完整的本地可部署功能框架：它用接近网文站的产品结构承载阅读、书架、排行、详情、阅读器和 AI 阅读助手，并把 RAG、LangChain、流式输出、阅读进度约束和引用标注整合成一个可演示的 AI 应用。

## 项目亮点

- 小说阅读网站框架：首页、全部作品、排行榜、书籍详情、章节目录、阅读器、书架、登录注册。
- RAG 阅读助手：基于小说章节向量检索、当前章节上下文和对话记忆生成回答。
- LangChain 流式问答：后端使用 LangChain 兼容接口，前端通过 SSE 实时展示生成内容。
- 本地轻量部署：Vue 3 + FastAPI + SQLite + Chroma，不需要 Docker，不引入本地大模型。
- 求职展示友好：重点展示 Vue 前端工程、FastAPI 后端接口和 RAG + LangChain AI 应用链路。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3, TypeScript, Vite, Vue Router, Pinia, Tailwind CSS |
| 后端 | FastAPI, SQLAlchemy, SQLite, Pydantic Settings |
| AI | LangChain, Chroma, OpenAI-compatible Chat/Embedding API |
| 通信 | REST API, SSE Streaming |
| 本地数据 | SQLite 业务数据, Chroma 向量库 |

## AI 架构

```text
User Question
  -> RAG Retrieval
       - current chapter context
       - book vector search
       - conversation memory
  -> LangChain-compatible LLM Streaming
  -> Memory Writer
  -> Vue AI Chat Panel
```

当前版本暂不实现复杂智能体编排、工具协议或项目技能扩展，优先把 RAG + LangChain 主链路做清楚，便于本地部署和面试讲解。

## 功能地图

| 页面 | 路由 | 说明 |
| --- | --- | --- |
| 首页 | `/` | 推荐、分类入口、继续阅读、书籍卡片 |
| 全部作品 | `/library` | 分类、状态、属性、关键词、排序筛选 |
| 排行榜 | `/rank` | 按热度和分类查看作品 |
| 详情页 | `/book/:id` | 书籍信息、章节目录、加入书架、开始阅读 |
| 阅读器 | `/read/:bookId/:chapterNum` | 主题、字号、进度、章节跳转、AI 助手 |
| 书架 | `/bookshelf` | 登录后的阅读进度与收藏管理 |

## 快速启动

### 1. 安装依赖

```bash
corepack enable
corepack pnpm install

cd apps/api
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp apps/api/.env.example apps/api/.env
```

编辑 `apps/api/.env`，填入你自己的模型服务配置：

```env
XFYUN_API_KEY=your_xfyun_api_key_here
XFYUN_BASE_URL=https://your-compatible-api-base-url
XFYUN_CHAT_MODEL=your_chat_model
XFYUN_EMBEDDING_MODEL=your_embedding_model
AUTH_SECRET=change_me_to_a_random_secret
```

`.env` 只保留在本地，不要提交到 GitHub。

### 3. 启动后端

```bash
corepack pnpm dev:api
```

默认后端地址：`http://127.0.0.1:8001`

### 4. 启动前端

```bash
corepack pnpm dev:web
```

默认前端地址：`http://localhost:5173`

## 项目结构

```text
apps/
  api/
    routers/
      auth.py
      books.py
      bookshelf.py
      chat.py              # SSE RAG 对话入口
      conversations.py
    services/
      rag_service.py       # RAG、Chroma、LLM、记忆能力
      chunking.py
      retrieval.py
      generation.py
      memory.py
    models.py
    database.py
    config.py
    main.py
  web/
    src/
      api/index.ts
      components/
        AiChatPanel.vue    # AI 阅读助手 + SSE 解析
        NavBar.vue
      views/
        HomePage.vue
        LibraryPage.vue
        BookDetailPage.vue
        ReaderPage.vue
        RankPage.vue
        BookshelfPage.vue
      stores/
      router/
```

## 安全上传说明

这些内容只应保留在本地：

- `apps/api/.env`
- `apps/api/.venv/`
- `apps/web/node_modules/`
- `apps/api/novel.db`
- `apps/api/chroma_db/`
- `.codex/`
- `__pycache__/`
- `.DS_Store`

仓库应提交的是源码、锁文件、`requirements.txt`、`package.json`、`.env.example` 和文档。别人 clone 后使用自己的 API Key 填入 `.env` 即可本地运行。

## 后续路线

- 人物关系图谱：从章节摘要中抽取人物、关系、事件和阵营，前端可视化。
- 章节摘要缓存：把摘要、关键词、伏笔和人物分析结构化缓存，减少重复调用。
