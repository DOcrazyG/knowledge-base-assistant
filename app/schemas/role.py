from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .permission import Permission


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleDelete(RoleBase):
    pass


class Role(RoleBase):
    id: int
    name: str
    created_at: datetime
    permissions: Optional[List[Permission]] = []

    class Config:
        orm_mode = True