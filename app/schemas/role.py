from pydantic import BaseModel
from datetime import datetime


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

    class config:
        orm_mode = True
