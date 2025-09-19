from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    file = "file"
    url = "url"


class itemBase(BaseModel):
    user_id: int
    content_type: ContentType
    source: str
    cleaned_text: str


class itemCreate(itemBase):
    pass


class itemUpdate(itemBase):
    pass


class itemDelete(BaseModel):
    id: int


class KnowledgeItem(itemBase):
    id: int
