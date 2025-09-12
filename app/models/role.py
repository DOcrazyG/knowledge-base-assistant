from datetime import datetime, timezone, timedelta

from ..core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Table, ForeignKey, Integer, Column


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None),
    )

    # Relationship with permissions through the association table
    permissions = relationship(
        "Permission", 
        secondary="role_permission", 
        back_populates="roles",
        lazy="selectin"  # 使用selectin加载权限，提高查询效率
    )