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

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.message},
            ],
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
