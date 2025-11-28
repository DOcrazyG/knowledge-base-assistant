import os

from dotenv import load_dotenv
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

# Qdrant配置
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE"))


class QdrantClientManager:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QdrantClientManager, cls).__new__(cls)
        return cls._instance

    def get_client(self):
        if self._client is None:
            self._client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            self._initialize_collection()
        return self._client

    def _initialize_collection(self):
        """初始化集合"""
        try:
            # 检查集合是否存在
            collection_info = self._client.get_collection(
                collection_name=QDRANT_COLLECTION_NAME
            )
            logger.info(f"Collection {QDRANT_COLLECTION_NAME} already exists")
        except Exception:
            # 集合不存在，创建新集合
            logger.info(f"Creating collection {QDRANT_COLLECTION_NAME}")
            self._client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )


# 全局客户端实例
qdrant_client_manager = QdrantClientManager()
qdrant_client = qdrant_client_manager.get_client()
