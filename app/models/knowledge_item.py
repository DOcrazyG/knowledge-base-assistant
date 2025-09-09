import os

from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, DateTime, func
from enum import Enum
from pgvector.sqlalchemy import Vector
from typing import List

from ..core.database import Base


class ContentType(str, Enum):
    url = "url"
    file = "file"


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    content_type: Mapped[ContentType] = mapped_column(String(10))
    source: Mapped[str] = mapped_column(String(500))
    cleaned_text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None),
    )
