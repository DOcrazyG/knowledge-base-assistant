from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, DateTime, func
from datetime import datetime, timezone, timedelta

from ..core.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    knowledge_item_id: Mapped[int] = mapped_column(ForeignKey("knowledge_items.id"))
    minio_path: Mapped[str] = mapped_column(String(500))
    filename: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).replace(tzinfo=None),
    )
