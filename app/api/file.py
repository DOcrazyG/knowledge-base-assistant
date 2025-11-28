from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import os
import uuid

from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user
from ..schemas.file import FileInfo, FileCreate
from ..utils.save2minio import upload_file
from ..schemas.user import User
from ..models.file import File
from ..services.crud.file import create_file, get_file
from ..models.knowledge_item import KnowledgeItem
from ..schemas.knowledge_item import ItemCreate
from ..services.crud.knowledge_item import create_knowledge_item
from ..core.rag.qdrant_db import qdrant_client, QDRANT_COLLECTION_NAME
from ..core.rag.embedding import EmbeddingModel
from ..core.rag.chunking import DocumentChunker

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file_to_minio(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    上传文件到MinIO并保存元数据到数据库
    同时处理支持的文档格式，提取文本内容并存储到知识库
    """
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # 重置文件指针
    file.file.seek(0)

    # 上传到MinIO
    file_url = upload_file(
        data=file.file,
        object_name=unique_filename,
        size=file.size,
        content_type=file.content_type,
    )

    # 创建文件记录
    file_record = await create_file(
        db,
        FileCreate(
            user_id=current_user.id,
            minio_path=file_url,
            filename=file.filename or unique_filename,
            size=file.size or 0,
        ),
    )

    # 简化文档处理逻辑
    file_content = await _process_document_if_supported(
        file, file_url, current_user, db
    )

    return file_content


async def _process_document_if_supported(
    file: UploadFile, file_url: str, current_user: User, db: AsyncSession
):
    """内部函数：处理支持的文档格式"""
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""

    if file_ext == ".docx":
        from ..core.processor import WordProcessor

        word_processor = WordProcessor()

        file.file.seek(0)
        processed_text = await word_processor.process_document(
            file_data=file.file, filename=file.filename
        )

        # 将处理后的内容存储到知识库
        knowledge_item = ItemCreate(
            user_id=current_user.id,
            content_type="file",
            source=file_url,
            cleaned_text=processed_text[:500],  # 限制长度以适应数据库字段
        )
        await create_knowledge_item(db, knowledge_item)

        # 将内容分块并存储到Qdrant向量数据库
        await _store_chunks_to_qdrant(processed_text, file_url, current_user.id, "docx")

        logger.debug(f"Word content: {processed_text}")
        return processed_text
    elif file_ext in [".xlsx", ".xls"]:
        from ..core.processor import ExcelProcessor

        excel_processor = ExcelProcessor()

        file.file.seek(0)
        processed_text = await excel_processor.process_document(
            file_data=file.file, filename=file.filename
        )

        # 将处理后的内容存储到知识库
        knowledge_item = ItemCreate(
            user_id=current_user.id,
            content_type="file",
            source=file_url,
            cleaned_text=processed_text[:500],  # 限制长度以适应数据库字段
        )
        await create_knowledge_item(db, knowledge_item)

        # 将内容存储到Qdrant向量数据库
        await _store_chunks_to_qdrant(
            processed_text, file_url, current_user.id, "excel"
        )

        logger.debug(f"Excel content: {processed_text}")
        return processed_text
    else:
        return None


async def _store_chunks_to_qdrant(
    content: str, source: str, user_id: int, file_type: str
):
    """
    将内容分块并存储到Qdrant向量数据库
    """
    # 创建文档分块器
    chunker = DocumentChunker()

    # 根据文件类型进行不同的分块处理
    if file_type == "docx":
        chunks = chunker.chunk_word(content)
    else:  # excel
        chunks = chunker.chunk_excel(content)

    # 为每个块生成向量并存储到Qdrant
    for i, chunk in enumerate(chunks):
        # 生成向量
        embedding_model = EmbeddingModel()
        vector = embedding_model.embed(chunk)

        # 准备payload数据
        payload = {
            "content": chunk,
            "source": source,
            "user_id": user_id,
            "file_type": file_type,
            "chunk_index": i,
        }

        # 存储到Qdrant，使用UUID格式的point ID
        import uuid

        point_id = str(uuid.uuid4())
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[{"id": point_id, "vector": vector, "payload": payload}],
        )

    logger.info(f"Stored {len(chunks)} chunks to Qdrant for user {user_id}")


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取文件信息
    """
    db_file = await get_file(db, file_id)
    return db_file
