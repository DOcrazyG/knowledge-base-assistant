from datetime import datetime

from pydantic import BaseModel


class FileBase(BaseModel):
    user_id: int
    filename: str
    minio_path: str
    size: int


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    file_id: int


class FileDelete(BaseModel):
    file_id: int


class FileInfo(BaseModel):
    id: int
    user_id: int
    filename: str
    minio_path: str
    size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
