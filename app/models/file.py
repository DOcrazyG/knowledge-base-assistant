from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    minio_path: Mapped[str] = mapped_column(String(500))
    filename: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None),
    )
