"""
RAG 服务 - 使用 ChromaDB 存储小说向量，支持双层分块、流式对话和对话记忆
模块化架构：
  - chunking.py: 文本分块
  - retrieval.py: 混合检索 + 重排序
  - memory.py: 对话记忆 + 分层摘要
  - generation.py: 流式生成 + System Prompt 构建
"""

import os
from typing import AsyncGenerator, Optional

from database import SessionLocal
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from models import Book, Chapter

from config import settings
from services.chunking import dual_layer_chunk
from services.generation import build_sliding_window_messages, build_system_prompt
from services.memory import ConversationMemory
from services.retrieval import extract_keywords, hybrid_search


class XfyunEmbeddings(Embeddings):
    """讯飞星辰 Embeddings，手动调用兼容接口以避免 SDK 自动注入不支持的字段。"""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _request_embeddings(self, texts: list[str]) -> list[list[float]]:
        import httpx
        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"讯飞 Embedding 接口调用失败: {response.status_code} {response.text}"
            )
        payload = response.json()
        items = payload.get("data") or []
        if not isinstance(items, list) or not items:
            raise ValueError(f"embedding 响应格式异常: {payload}")
        vectors = [item.get("embedding", []) for item in items]
        if any(not vector for vector in vectors):
            raise ValueError(f"embedding 返回空向量: {payload}")
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._request_embeddings(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._request_embeddings([text])[0]


class RAGService:
    def __init__(self):
        self.embeddings = XfyunEmbeddings(
            api_key=settings.xfyun_api_key,
            base_url=settings.xfyun_base_url,
            model=settings.xfyun_embedding_model,
        )
        self.llm = ChatOpenAI(
            openai_api_key=settings.xfyun_api_key,
            openai_api_base=settings.xfyun_base_url,
            model=settings.xfyun_chat_model,
            streaming=True,
            temperature=0.7,
        )
        self.chroma_dir = settings.chroma_dir
        os.makedirs(self.chroma_dir, exist_ok=True)
        self.window_size = 8

    # ==================== ChromaDB 基础方法 ====================

    def _get_collection_name(self, book_id: int) -> str:
        return f"novel_book_{book_id}"

    def _get_chroma(self, book_id: int) -> Chroma:
        """获取指定书籍的 ChromaDB 向量库"""
        collection_name = self._get_collection_name(book_id)
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_dir,
        )

    def _get_memory_collection(self) -> Chroma:
        """获取对话记忆的 ChromaDB collection"""
        return Chroma(
            collection_name="conversation_memory",
            embedding_function=self.embeddings,
            persist_directory=self.chroma_dir,
        )

    def _get_memory_manager(self) -> ConversationMemory:
        """获取对话记忆管理器"""
        return ConversationMemory(
            memory_collection=self._get_memory_collection(),
            llm=self.llm,
        )

    def _get_direct_chapter_context(
        self,
        book_id: Optional[int],
        chapter_id: Optional[int],
        search_all: bool,
    ) -> str:
        """直接从数据库读取章节正文，作为未向量化时的兜底上下文。"""
        if book_id is None:
            return ""

        db = SessionLocal()
        try:
            current_chapter = None
            if chapter_id is not None:
                current_chapter = (
                    db.query(Chapter)
                    .filter(Chapter.id == chapter_id, Chapter.book_id == book_id)
                    .first()
                )

            if current_chapter is None:
                current_chapter = (
                    db.query(Chapter)
                    .filter(Chapter.book_id == book_id)
                    .order_by(Chapter.chapter_number.asc())
                    .first()
                )

            if current_chapter is None:
                return ""

            snippets = [current_chapter]
            if not search_all:
                previous = (
                    db.query(Chapter)
                    .filter(
                        Chapter.book_id == book_id,
                        Chapter.chapter_number < current_chapter.chapter_number,
                    )
                    .order_by(Chapter.chapter_number.desc())
                    .first()
                )
                if previous is not None:
                    snippets.insert(0, previous)

            context_parts = []
            for chapter in snippets:
                excerpt = chapter.content[:800].strip()
                context_parts.append(
                    f"【{chapter.title}】\n{excerpt}"
                )

            return "\n\n".join(context_parts)
        finally:
            db.close()

    # ==================== 索引方法 ====================

    def index_chapter(
        self, book_id: int, chapter_id: int, title: str, content: str
    ):
        """双层分块索引章节内容"""
        paragraph_chunks, plot_chunks = dual_layer_chunk(content)

        all_texts = []
        all_metadatas = []

        for i, chunk in enumerate(paragraph_chunks):
            all_texts.append(chunk)
            all_metadatas.append({
                "book_id": book_id,
                "chapter_id": chapter_id,
                "chapter_title": title,
                "chunk_type": "paragraph",
                "chunk_index": i,
            })

        for i, chunk in enumerate(plot_chunks):
            all_texts.append(chunk)
            all_metadatas.append({
                "book_id": book_id,
                "chapter_id": chapter_id,
                "chapter_title": title,
                "chunk_type": "plot",
                "chunk_index": i,
            })

        if all_texts:
            chroma = self._get_chroma(book_id)
            chroma.add_texts(texts=all_texts, metadatas=all_metadatas)

    def index_book(self, book_id: int, chapters: list[dict]):
        """索引整本书的所有章节"""
        for chapter in chapters:
            self.index_chapter(
                book_id=book_id,
                chapter_id=chapter["id"],
                title=chapter["title"],
                content=chapter["content"],
            )

    # ==================== 检索方法 ====================

    def search(
        self,
        book_id: int,
        query: str,
        top_k: int = 5,
        max_chapter_id: int | None = None,
        user_id: int | None = None,
    ) -> list[dict]:
        """混合检索：向量相似度 + 关键词过滤 + 重排序"""
        try:
            chroma = self._get_chroma(book_id)
            filters = {}
            if max_chapter_id is not None:
                filters["chapter_id"] = {"$le": max_chapter_id}

            # 提取关键词用于混合检索
            keywords = extract_keywords(query)

            return hybrid_search(
                chroma=chroma,
                query=query,
                query_keywords=keywords,
                top_k=top_k,
                filters=filters if filters else None,
            )
        except Exception:
            return []

    # ==================== 对话记忆方法 ====================

    def store_conversation_turn(
        self,
        user_id: int,
        book_id: Optional[int],
        conversation_id: int,
        turn_index: int,
        user_msg: str,
        assistant_msg: str,
    ):
        """存储一轮对话到 ChromaDB"""
        memory_manager = self._get_memory_manager()
        memory_manager.store_turn(
            user_id=user_id,
            book_id=book_id,
            conversation_id=conversation_id,
            turn_index=turn_index,
            user_msg=user_msg,
            assistant_msg=assistant_msg,
        )

    def search_conversation_memory(
        self,
        query: str,
        user_id: int,
        book_id: Optional[int] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """检索相关历史对话记忆"""
        memory_manager = self._get_memory_manager()
        return memory_manager.search(
            query=query,
            user_id=user_id,
            book_id=book_id,
            top_k=top_k,
        )

    async def summarize_messages(self, messages: list[dict]) -> str:
        """压缩消息为摘要"""
        memory_manager = self._get_memory_manager()
        return await memory_manager.summarize_messages(messages)

    # ==================== 向量删除方法 ====================

    def delete_chapter_vectors(self, book_id: int, chapter_id: int):
        """删除指定章节的向量"""
        try:
            chroma = self._get_chroma(book_id)
            chroma.delete(where={"chapter_id": chapter_id})
        except Exception:
            pass

    def delete_book_vectors(self, book_id: int):
        """删除整本书的向量 collection"""
        try:
            chroma = self._get_chroma(book_id)
            chroma.delete_collection()
        except Exception:
            pass

    # ==================== 流式对话方法 ====================

    async def stream_chat(
        self,
        messages: list[dict],
        book_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        search_all: bool = True,
        user_id: Optional[int] = None,
        role: Optional[str] = None,
        conversation_id: Optional[int] = None,
    ) -> AsyncGenerator[str | dict, None]:
        """流式对话方法"""
        uid = user_id if user_id is not None else settings.default_user_id

        scope_hint = (
            "如果上下文不足，不要透露或猜测后续剧情。"
            if not search_all
            else "如果需要分析后续剧情，也必须基于检索到的原文内容。"
        )
        base_prompt = (
            "你是一个智能小说阅读助手，可以帮助读者理解小说内容、梳理人物关系和分析情节线索。"
            "请优先依据提供的小说原文、当前章节上下文和历史对话回答，不要编造不存在的情节。"
            f"{scope_hint}请用简洁易懂的语言回答问题。"
        )

        # 检索小说内容
        search_results = []
        if book_id and messages:
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            if last_user_msg:
                max_chapter = None if search_all else chapter_id
                search_results = self.search(
                    book_id, last_user_msg, top_k=3,
                    max_chapter_id=max_chapter, user_id=uid,
                )

        # 获取当前章节上下文
        direct_context = ""
        if book_id:
            direct_context = self._get_direct_chapter_context(
                book_id=book_id,
                chapter_id=chapter_id,
                search_all=search_all,
            )

        # 检索对话记忆
        memory_results = []
        if conversation_id and messages:
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            if last_user_msg:
                memory_results = self.search_conversation_memory(
                    query=last_user_msg,
                    user_id=uid,
                    book_id=book_id,
                    top_k=3,
                )

        # 构建 System Prompt（使用 XML 标签）
        system_prompt = build_system_prompt(
            base_prompt=base_prompt,
            search_results=search_results,
            direct_context=direct_context,
            memory_results=memory_results,
            book_id=book_id,
            has_vector_results=bool(search_results),
        )

        # 分层摘要
        older_summary = None
        if conversation_id and messages:
            memory_manager = self._get_memory_manager()
            older_summary = await memory_manager.hierarchical_summarize(messages, conversation_id)

        # 构建滑动窗口消息
        lc_messages = build_sliding_window_messages(
            messages=messages,
            system_prompt=system_prompt,
            window_size=self.window_size,
            older_summary=older_summary,
        )

        # 流式生成
        try:
            async for chunk in self.llm.astream(lc_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            yield f"[错误] 对话服务暂时不可用: {str(e)}"

    def sync_book_to_chroma(
        self,
        db_session,
        book_id: int,
        force_reindex: bool = False,
    ) -> bool:
        book = db_session.query(Book).filter(Book.id == book_id).first()
        if book is None or not book.chapters:
            return False

        chroma = self._get_chroma(book_id)
        should_reindex = force_reindex or not book.vectorized or any(
            not chapter.vectorized for chapter in book.chapters
        )
        if not should_reindex:
            return False

        try:
            chroma.delete_collection()
        except Exception:
            pass

        chapters_data = [
            {"id": chapter.id, "title": chapter.title, "content": chapter.content}
            for chapter in book.chapters
        ]
        self.index_book(book_id, chapters_data)
        book.vectorized = True
        for chapter in book.chapters:
            chapter.vectorized = True
        db_session.commit()
        return True


_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """Lazily create the RAG service so API boot is not blocked by chat config."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def ensure_library_vectorized(db_session, force: bool = False) -> int:
    rag_service = get_rag_service()
    books = db_session.query(Book).order_by(Book.id.asc()).all()
    processed = 0
    for book in books:
        if rag_service.sync_book_to_chroma(
            db_session,
            book.id,
            force_reindex=force,
        ):
            processed += 1
    return processed
