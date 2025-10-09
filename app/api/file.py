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


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileInfo)
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
    await _process_document_if_supported(file, file_url, current_user, db)

    return file_record


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
        logger.debug(f"Word content: {processed_text}")
        return processed_text
    elif file_ext in [".xlsx", ".xls"]:
        from ..core.processor import ExcelProcessor

        excel_processor = ExcelProcessor()

        file.file.seek(0)
        processed_text = await excel_processor.process_document(
            file_data=file.file, filename=file.filename
        )
        logger.debug(f"Excel content: {processed_text}")
        return processed_text
    else:
        return None

    # if file_ext in SUPPORTED_EXTENSIONS:
    #     try:
    #         # 重置文件指针并处理文档
    #         file.file.seek(0)
    #         processed_text = await document_processor.process_document(
    #             file.file, file.filename, current_user.id
    #         )

    #         # 保存到知识库
    #         await knowledge_item_crud.create_knowledge_item(
    #             db,
    #             itemCreate(
    #                 user_id=current_user.id,
    #                 content_type=ContentType.file,
    #                 source=file_url,
    #                 cleaned_text=processed_text[:500]
    #             )
    #         )

    #     except Exception as e:
    #         from loguru import logger
    #         logger.error(f"处理文档文件时出错: {str(e)}")


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
