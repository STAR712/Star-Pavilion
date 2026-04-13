import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import settings
from services.rag_service import rag_service

router = APIRouter(prefix="/chat", tags=["AI对话"])


class ChatRequest(BaseModel):
    messages: list[dict]
    book_id: int | None = None
    chapter_id: int | None = None
    search_all: bool = True
    user_id: int | None = None
    role: str | None = None
    conversation_id: int | None = None


@router.post("/stream")
async def stream_chat(req: ChatRequest):
    """流式对话（SSE），携带 book_id + chapter_id + user_id + conversation_id"""
    uid = req.user_id if req.user_id is not None else settings.default_user_id
    user_role = req.role if req.role is not None else settings.default_user_role

    async def event_generator():
        full_response = ""
        try:
            async for chunk in rag_service.stream_chat(
                messages=req.messages,
                book_id=req.book_id,
                chapter_id=req.chapter_id,
                search_all=req.search_all,
                user_id=uid,
                role=user_role,
                conversation_id=req.conversation_id,
            ):
                # chunk 可能是 str (content) 或 dict (memory_stored 等事件)
                if isinstance(chunk, str):
                    full_response += chunk
                    data = json.dumps({"content": chunk}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                elif isinstance(chunk, dict):
                    data = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {data}\n\n"

            # 流式结束后，存储对话记忆
            if req.conversation_id and full_response:
                try:
                    # 提取最后一条用户消息
                    last_user_msg = ""
                    for msg in reversed(req.messages):
                        if msg.get("role") == "user":
                            last_user_msg = msg.get("content", "")
                            break
                    if last_user_msg:
                        rag_service.store_conversation_turn(
                            user_id=uid,
                            book_id=req.book_id,
                            conversation_id=req.conversation_id,
                            turn_index=sum(1 for m in req.messages if m.get("role") == "user"),
                            user_msg=last_user_msg,
                            assistant_msg=full_response,
                        )
                        memory_data = json.dumps({"memory_stored": True}, ensure_ascii=False)
                        yield f"data: {memory_data}\n\n"
                except Exception:
                    # 记忆存储失败不影响主流程
                    pass

            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
