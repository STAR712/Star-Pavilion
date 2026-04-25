"""对话记忆模块 - 分层摘要 + 记忆检索"""
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage


class ConversationMemory:
    """对话记忆管理器"""

    def __init__(self, memory_collection: Chroma, llm):
        self.memory_collection = memory_collection
        self.llm = llm
        self.sub_summary_interval = 10  # 每 10 轮生成一次子摘要

    def store_turn(
        self,
        user_id: int,
        book_id: Optional[int],
        conversation_id: int,
        turn_index: int,
        user_msg: str,
        assistant_msg: str,
    ):
        """存储一轮对话到 ChromaDB"""
        text = f"用户：{user_msg}\n助手：{assistant_msg}"
        metadata = {
            "user_id": user_id,
            "book_id": book_id,
            "conversation_id": conversation_id,
            "turn_index": turn_index,
            "role": "conversation_turn",
        }
        self.memory_collection.add_texts(texts=[text], metadatas=[metadata])

    def search(
        self,
        query: str,
        user_id: int,
        book_id: Optional[int] = None,
        top_k: int = 5,
    ) -> list[dict]:
        """检索相关历史对话记忆"""
        try:
            filters = {"user_id": user_id}
            if book_id is not None:
                filters["book_id"] = book_id
            results = self.memory_collection.similarity_search(
                query, k=top_k, filter=filters
            )
            return [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in results
            ]
        except Exception:
            return []

    async def summarize_messages(self, messages: list[dict]) -> str:
        """将一组消息压缩为摘要"""
        if not messages:
            return ""
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
            return conversation_text[:500]

    async def hierarchical_summarize(self, messages: list[dict], conversation_id: int) -> str | None:
        """
        分层摘要：
        - 每 sub_summary_interval 轮生成一次子摘要
        - 子摘要存储到 ChromaDB，metadata 标记 role=sub_summary
        - 返回最新的总摘要（所有子摘要的合并摘要）
        """
        turn_count = sum(1 for m in messages if m.get("role") == "user")
        if turn_count < self.sub_summary_interval:
            return None

        # 生成子摘要
        sub_summary = await self.summarize_messages(messages)

        # 存储子摘要到 ChromaDB
        metadata = {
            "conversation_id": conversation_id,
            "role": "sub_summary",
            "turn_count": turn_count,
        }
        self.memory_collection.add_texts(texts=[f"[子摘要-第{turn_count}轮]\n{sub_summary}"], metadatas=[metadata])

        # 检索所有子摘要，生成总摘要
        try:
            all_summaries = self.memory_collection.similarity_search(
                f"对话摘要 conversation_id={conversation_id}",
                k=10,
                filter={"conversation_id": conversation_id, "role": "sub_summary"},
            )
            if len(all_summaries) > 1:
                summary_texts = [doc.page_content for doc in all_summaries]
                combined = "\n\n".join(summary_texts)
                total_summary = await self.summarize_messages(
                    [{"role": "system", "content": f"以下是多段对话子摘要，请合并为一段总摘要：\n\n{combined}"}]
                )
                return total_summary
        except Exception:
            pass

        return sub_summary
