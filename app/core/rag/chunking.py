from typing import List

from chonkie import TableChunker, RecursiveChunker, RecursiveRules


class DocumentChunker:
    """文档分块处理器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_excel(self, text: str) -> List[str]:
        chunker = TableChunker(
            tokenizer="character",
            chunk_size=self.chunk_size,
        )
        chunks = chunker.chunk(text)
        return [chunk.text for chunk in chunks]

    def chunk_word(self, markdown_text: str) -> List[str]:
        """
        针对Markdown文本的分块处理
        """
        chunker = RecursiveChunker(
            tokenizer_or_token_counter="character",
            chunk_size=self.chunk_size,
            rules=RecursiveRules(),
            min_characters_per_chunk=24,
        )
        chunks = chunker.chunk(markdown_text)
        return [chunk.text for chunk in chunks]
