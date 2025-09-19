from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
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

    return file_record


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
