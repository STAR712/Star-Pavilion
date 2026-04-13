"""
RAG 服务 - 使用 ChromaDB 存储小说向量，支持双层分块、流式对话和对话记忆
"""

import os
import re
from typing import AsyncGenerator, Optional

from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings


class XfyunEmbeddings(OpenAIEmbeddings):
    """讯飞星辰 Embeddings，继承 OpenAIEmbeddings 并移除 encoding_format 参数"""

    def _get_headers(self) -> dict:
        headers = super()._get_headers()
        return headers


class RAGService:
    def __init__(self):
        self.embeddings = XfyunEmbeddings(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
            model=settings.embed_model,
        )
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
            model=settings.model_name,
            streaming=True,
            temperature=0.7,
        )
        self.chroma_dir = settings.chroma_dir
        os.makedirs(self.chroma_dir, exist_ok=True)
        # 章节段落级分块器
        self.paragraph_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "；", ""],
        )
        # 关键剧情点级分块器
        self.plot_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", "。", ""],
        )
        # 滑动窗口大小：保留最近 N 轮原文
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

    # ==================== 索引方法 ====================

    def index_chapter(
        self, book_id: int, chapter_id: int, title: str, content: str
    ):
        """
        双层分块索引章节内容：
        1. 段落级分块（细粒度，用于精确检索）
        2. 剧情点级分块（粗粒度，用于上下文理解）
        """
        # 段落级分块
        paragraph_chunks = self.paragraph_splitter.split_text(content)
        # 剧情点级分块
        plot_chunks = self.plot_splitter.split_text(content)

        # 合并所有分块，带元数据标记
        all_texts = []
        all_metadatas = []

        for i, chunk in enumerate(paragraph_chunks):
            all_texts.append(chunk)
            all_metadatas.append(
                {
                    "book_id": book_id,
                    "chapter_id": chapter_id,
                    "chapter_title": title,
                    "chunk_type": "paragraph",
                    "chunk_index": i,
                    "user_id": 1,  # 小说内容是全局共享的，使用默认值
                }
            )

        for i, chunk in enumerate(plot_chunks):
            all_texts.append(chunk)
            all_metadatas.append(
                {
                    "book_id": book_id,
                    "chapter_id": chapter_id,
                    "chapter_title": title,
                    "chunk_type": "plot",
                    "chunk_index": i,
                    "user_id": 1,  # 小说内容是全局共享的，使用默认值
                }
            )

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
        """检索相关文本片段，可通过 max_chapter_id 限制只检索当前章节及之前的内容"""
        try:
            chroma = self._get_chroma(book_id)
            # 构建 ChromaDB filter
            filters = {}
            if max_chapter_id is not None:
                filters["chapter_id"] = {"$le": max_chapter_id}
            if user_id is not None:
                filters["user_id"] = user_id

            if filters:
                results = chroma.similarity_search(query, k=top_k, filter=filters)
            else:
                results = chroma.similarity_search(query, k=top_k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in results
            ]
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
        """
        将一轮对话（用户消息+AI回复）向量化存入 ChromaDB 对话记忆
        存储文本格式为 "用户：{user_msg}\n助手：{assistant_msg}"
        metadata 包含 {user_id, book_id, conversation_id, turn_index, role}
        """
        text = f"用户：{user_msg}\n助手：{assistant_msg}"
        metadata = {
            "user_id": user_id,
            "book_id": book_id,
            "conversation_id": conversation_id,
            "turn_index": turn_index,
            "role": "conversation_turn",
        }
        memory_collection = self._get_memory_collection()
        memory_collection.add_texts(texts=[text], metadatas=[metadata])

    def search_conversation_memory(
        self,
        query: str,
        user_id: int,
        book_id: Optional[int] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """
        在对话记忆 collection 中做向量相似度检索
        可按 user_id 和 book_id 过滤
        """
        try:
            memory_collection = self._get_memory_collection()
            filters = {"user_id": user_id}
            if book_id is not None:
                filters["book_id"] = book_id
            results = memory_collection.similarity_search(
                query, k=top_k, filter=filters
            )
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in results
            ]
        except Exception:
            return []

    async def summarize_messages(self, messages: list[dict]) -> str:
        """
        调用 LLM 将一组消息压缩为摘要文本（异步）
        """
        if not messages:
            return ""
        # 构建需要摘要的消息文本
        msg_texts = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            role_label = "用户" if role == "user" else "助手"
            msg_texts.append(f"{role_label}：{content}")
        conversation_text = "\n".join(msg_texts)

        prompt = (
            "请将以下对话内容压缩为一段简洁的摘要，保留关键信息和上下文。"
            "摘要应该能让读者理解之前讨论了什么，但不需要包含所有细节。\n\n"
            f"对话内容：\n{conversation_text}\n\n"
            "请输出摘要："
        )
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content
        except Exception:
            # 摘要失败时返回简单的拼接
            return conversation_text[:500]

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
        """
        流式对话方法
        - 如果提供了 book_id，会先检索相关文本作为上下文
        - search_all=True 时检索全部章节，False 时只检索当前章节及之前的内容（防剧透）
        - 如果提供了 conversation_id，会检索相关历史对话记忆作为额外上下文
        - 实现滑动窗口：保留最近 window_size 轮原文，超出部分压缩为摘要
        - 使用 LangChain 的流式输出
        - 返回值同时 yield content (str) 和 memory_stored (dict) 标记
        """
        uid = user_id if user_id is not None else settings.default_user_id

        system_prompt = "你是一个智能小说阅读助手，可以帮助读者理解小说内容、分析人物关系、预测剧情走向。请用简洁易懂的语言回答问题。"

        # 如果有 book_id，检索相关上下文
        if book_id and messages:
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            if last_user_msg:
                # search_all=True 检索全部章节，False 只检索当前章节及之前
                max_chapter = None if search_all else chapter_id
                search_results = self.search(
                    book_id, last_user_msg, top_k=3,
                    max_chapter_id=max_chapter, user_id=uid,
                )
                if search_results:
                    context_parts = []
                    for r in search_results:
                        meta = r["metadata"]
                        chapter_title = meta.get("chapter_title", "未知章节")
                        context_parts.append(
                            f"【{chapter_title}】\n{r['content']}"
                        )
                    context_text = "\n\n".join(context_parts)
                    system_prompt += (
                        f"\n\n以下是小说中的相关内容，请参考回答：\n\n{context_text}"
                    )

        # 如果有 conversation_id，检索相关历史对话记忆
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
                if memory_results:
                    memory_parts = []
                    for r in memory_results:
                        meta = r["metadata"]
                        turn_idx = meta.get("turn_index", "?")
                        memory_parts.append(
                            f"[历史对话第{turn_idx}轮]\n{r['content']}"
                        )
                    memory_text = "\n\n".join(memory_parts)
                    system_prompt += (
                        f"\n\n以下是之前的相关对话记忆，请参考以保持对话连贯性：\n\n{memory_text}"
                    )

        # 构建带滑动窗口的消息列表
        # 将 messages 按轮次分组（每轮 = 1个user + 1个assistant）
        turns = []
        current_turn = []
        for msg in messages:
            current_turn.append(msg)
            if msg.get("role") == "assistant":
                turns.append(current_turn)
                current_turn = []
        if current_turn:
            turns.append(current_turn)

        # 滑动窗口：保留最近 window_size 轮原文
        if len(turns) > self.window_size:
            older_turns = turns[:-self.window_size]
            recent_turns = turns[-self.window_size:]

            # 压缩旧消息为摘要
            older_messages = []
            for turn in older_turns:
                older_messages.extend(turn)
            summary = await self.summarize_messages(older_messages)

            # 构建最终消息列表：摘要 + 最近轮次
            lc_messages = [SystemMessage(content=system_prompt)]
            if summary:
                lc_messages.append(
                    HumanMessage(content=f"[之前的对话摘要]\n{summary}")
                )
            for turn in recent_turns:
                for msg in turn:
                    msg_role = msg.get("role", "user")
                    msg_content = msg.get("content", "")
                    if msg_role == "user":
                        lc_messages.append(HumanMessage(content=msg_content))
                    elif msg_role == "assistant":
                        lc_messages.append(
                            HumanMessage(content=f"[之前回答] {msg_content}")
                        )
        else:
            # 消息数在窗口内，直接使用
            lc_messages = [SystemMessage(content=system_prompt)]
            for msg in messages:
                msg_role = msg.get("role", "user")
                msg_content = msg.get("content", "")
                if msg_role == "user":
                    lc_messages.append(HumanMessage(content=msg_content))
                elif msg_role == "assistant":
                    lc_messages.append(
                        HumanMessage(content=f"[之前回答] {msg_content}")
                    )

        # 流式生成
        try:
            async for chunk in self.llm.astream(lc_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            yield f"[错误] 对话服务暂时不可用: {str(e)}"


# 全局 RAG 服务实例
rag_service = RAGService()
