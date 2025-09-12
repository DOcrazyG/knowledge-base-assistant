from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Annotated, AsyncGenerator
from fastapi import Depends

from ..core.database import SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

DBSession = Annotated[AsyncSession, Depends(get_db)]