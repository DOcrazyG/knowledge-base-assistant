from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv

from ..dependencies.security import get_current_user
from ..dependencies.depends import get_db
from ..models.user import User
from ..schemas.chat_history import ChatHistoryCreate
from ..core.database import SessionLocal
from ..services.crud import chat_history as chat_history_crud
from ..services.crud.knowledge_item import get_knowledge_items_by_user
from ..core.embedding import EmbeddingModel
from ..core.qdrant_db import qdrant_client, QDRANT_COLLECTION_NAME
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert

# 加载环境变量
load_dotenv()

router = APIRouter(prefix="/chat", tags=["chat"])

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
else:
    client = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/completions", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        session_id = (
            request.session_id
            or f"session_{current_user.id}_{hash(request.message) % 10000}"
        )

        # 使用用户查询向量数据库获取相关上下文
        context = await _retrieve_context_from_qdrant(request.message, current_user.id)

        # 构建包含上下文的消息
        messages = [{"role": "system", "content": "You are a helpful assistant."}]

        # 如果有上下文，则添加上下文信息
        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Here is some context information: {context}",
                }
            )

        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        answer = response.choices[0].message.content
        await chat_history_crud.save_to_chat_history(
            db,
            ChatHistoryCreate(
                user_id=current_user.id,
                session_id=session_id,
                question=request.message,
                answer=answer,
            ),
        )

        return ChatResponse(answer=answer, session_id=session_id)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling OpenAI API: {str(e)}"
        )


async def _retrieve_context_from_qdrant(
    query: str, user_id: int, limit: int = 5
) -> str:
    """
    从Qdrant向量数据库中检索与查询相关的上下文
    """
    # 生成查询向量
    embedding_model = EmbeddingModel()
    query_vector = embedding_model.embed_sigle(query)

    # 在Qdrant中搜索相似内容（仅搜索当前用户的内容）
    search_result = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
    )

    # 提取相关内容
    contexts = [result.payload.get("content", "") for result in search_result]
    return "\n".join(contexts)
