from enum import Enum

from pydantic import BaseModel


class ContentType(str, Enum):
    file = "file"
    url = "url"


class ItemBase(BaseModel):
    user_id: int
    content_type: ContentType
    source: str
    cleaned_text: str


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemDelete(BaseModel):
    id: int


class KnowledgeItem(ItemBase):
    id: int
