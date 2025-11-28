from datetime import datetime

from pydantic import BaseModel


class PermissionBase(BaseModel):
    name: str
    description: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
