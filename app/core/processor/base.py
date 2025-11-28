from abc import ABC, abstractmethod
from typing import BinaryIO

from ..database import MINIO_BUCKET_NAME, minio_client


class BaseProcessor(ABC):
    minio_client = minio_client
    MINIO_BUCKET_NAME = MINIO_BUCKET_NAME

    @abstractmethod
    async def process_document(self, file_data: BinaryIO, filename: str) -> str:
        pass
