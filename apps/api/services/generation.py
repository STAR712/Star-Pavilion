"""生成模块 - 流式对话 + System Prompt 构建"""
from typing import AsyncGenerator, Optional

from langchain_core.messages import HumanMessage, SystemMessage


def build_system_prompt(
    base_prompt: str,
    search_results: list[dict],
    direct_context: str,
    memory_results: list[dict],
    book_id: Optional[int],
    has_vector_results: bool,
) -> str:
    """
    构建 System Prompt，使用 XML 标签分离内容来源

    XML 标签结构：
    <novel_context> 小说检索内容 </novel_context>
    <current_chapter> 当前章节内容 </current_chapter>
    <conversation_history> 历史对话记忆 </conversation_history>
    """
    system_prompt = base_prompt

    # 小说检索内容
    if search_results:
        context_parts = []
        for r in search_results:
            meta = r["metadata"]
            chapter_title = meta.get("chapter_title", "未知章节")
            context_parts.append(f"【{chapter_title}】\n{r['content']}")
        context_text = "\n\n".join(context_parts)
        system_prompt += f"\n\n<novel_context>\n以下是小说中的相关内容，请参考回答：\n\n{context_text}\n</novel_context>"

    # 当前章节内容
    if direct_context:
        if has_vector_results:
            system_prompt += f"\n\n<current_chapter>\n当前阅读的章节摘要如下，可作为补充上下文：\n\n{direct_context}\n</current_chapter>"
        else:
            system_prompt += f"\n\n<current_chapter>\n以下是当前阅读到的章节内容，请优先依据这些内容回答：\n\n{direct_context}\n</current_chapter>"

    # 历史对话记忆
    if memory_results:
        memory_parts = []
        for r in memory_results:
            meta = r["metadata"]
            turn_idx = meta.get("turn_index", "?")
            memory_parts.append(f"[历史对话第{turn_idx}轮]\n{r['content']}")
        memory_text = "\n\n".join(memory_parts)
        system_prompt += f"\n\n<conversation_history>\n以下是之前的相关对话记忆，请参考以保持对话连贯性：\n\n{memory_text}\n</conversation_history>"

    # 引用标注指令
    if search_results and book_id:
        system_prompt += (
            "\n\n<citation_instruction>"
            "当你引用小说中的具体内容时，请在引用后标注来源，格式为："
            "[来源: 第X章 章节名]，其中X为章节号，章节名为对应章节标题。"
            "如果无法确定具体章节，可标注 [来源: 小说相关内容]。"
            "</citation_instruction>"
        )

    return system_prompt


def build_sliding_window_messages(
    messages: list[dict],
    system_prompt: str,
    window_size: int = 8,
    older_summary: str | None = None,
) -> list:
    """
    构建带滑动窗口的消息列表
    - 保留最近 window_size 轮原文
    - 超出部分使用摘要替代
    """
    # 将 messages 按轮次分组
    turns = []
    current_turn = []
    for msg in messages:
        current_turn.append(msg)
        if msg.get("role") == "assistant":
            turns.append(current_turn)
            current_turn = []
    if current_turn:
        turns.append(current_turn)

    lc_messages = [SystemMessage(content=system_prompt)]

    if len(turns) > window_size:
        older_turns = turns[:-window_size]
        recent_turns = turns[-window_size:]

        # 使用传入的摘要或压缩旧消息
        summary = older_summary
        if not summary:
            older_messages = []
            for turn in older_turns:
                older_messages.extend(turn)
            # 简单截断作为兜底
            summary = "...(历史对话已省略)"

        if summary:
            lc_messages.append(HumanMessage(content=f"[之前的对话摘要]\n{summary}"))

        for turn in recent_turns:
            for msg in turn:
                msg_role = msg.get("role", "user")
                msg_content = msg.get("content", "")
                if msg_role == "user":
                    lc_messages.append(HumanMessage(content=msg_content))
                elif msg_role == "assistant":
                    lc_messages.append(HumanMessage(content=f"[之前回答] {msg_content}"))
    else:
        for msg in messages:
            msg_role = msg.get("role", "user")
            msg_content = msg.get("content", "")
            if msg_role == "user":
                lc_messages.append(HumanMessage(content=msg_content))
            elif msg_role == "assistant":
                lc_messages.append(HumanMessage(content=f"[之前回答] {msg_content}"))

    return lc_messages
