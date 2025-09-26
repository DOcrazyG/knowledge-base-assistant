from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from loguru import logger

from ...schemas import chat_history as chat_history_schemas
from ...models import chat_history as chat_history_models


async def save_to_chat_history(
    db: AsyncSession, chat_history: chat_history_schemas.ChatHistoryCreate
):
    db_chat_history = chat_history_models.ChatHistory(
        user_id=chat_history.user_id,
        session_id=chat_history.session_id,
        question=chat_history.question,
        answer=chat_history.answer,
    )
    try:
        db.add(db_chat_history)
        await db.commit()
        await db.refresh(db_chat_history)
        return db_chat_history
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error adding chat history: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from exc
