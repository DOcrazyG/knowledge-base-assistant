from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, DateTime, func
from datetime import datetime, timezone, timedelta
from typing import Text

from ..core.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    session_id: Mapped[str] = mapped_column(String(50))
    question: Mapped[str] = mapped_column(String(2000))
    answer: Mapped[str] = mapped_column(String(4000))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None),
    )
