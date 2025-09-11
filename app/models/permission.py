from datetime import datetime, timezone, timedelta

from ..core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, ForeignKey


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None),
    )

    roles = relationship(
        "Role", secondary="role_permission", back_populates="permissions"
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"))
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id"))
