import os
from typing import List

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

load_dotenv()

# 嵌入模型配置
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")
EMBEDDING_DIM = os.getenv("EMBEDDING_DIM")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")


class EmbeddingModel:
    _client = None

    def __init__(self):
        if self._client is None:
            logger.info("Loading embedding client")
            self._client = OpenAI(
                api_key=EMBEDDING_API_KEY,
                base_url=EMBEDDING_BASE_URL,
            )

    def embed_sigle(self, text: str):
        try:
            completion = self._client.embeddings.create(
                model=EMBEDDING_MODEL_NAME,
                input=text,
                dimensions=EMBEDDING_DIM,
                encoding_format="float",
            )
            embedding = completion.data[0].embedding
            logger.info(f"Embedding text: {text}")
            return embedding
        except Exception as exc:
            logger.error(f"Error embedding text: {exc}")
            raise exc

    def embed(self, texts: str | List[str]):
        """对文本进行编码"""
        if not isinstance(texts, (str, list)):
            raise ValueError(
                "Invalid input type. Input must be a string or a list of strings."
            )
        if isinstance(texts, str):
            embedding = self.embed_sigle(texts)
            return embedding
        elif isinstance(texts, list):
            embeddings = [self.embed_sigle(text) for text in texts]
            return embeddings


if __name__ == "__main__":
    embed_model = EmbeddingModel()

    text = "This is a test text."
    embedding = embed_model.embed(text)
    print(embedding)
