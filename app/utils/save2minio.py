from ..core.database import minio_client, MINIO_BUCKET_NAME, MINIO_ENDPOINT, MINIO_SECURE
from typing import BinaryIO
from loguru import logger


def upload_file(data: BinaryIO, object_name: str, size: int, content_type: str):

    try:
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)
    except Exception as exc:
        logger.error(f"failed to create MinIO bucket:{exc}")
        raise exc

    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=object_name,
            data=data,
            length=size,
            content_type=content_type,
        )
        protocol = "https" if MINIO_SECURE else "http"
        url = f"{protocol}://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{object_name}"
        return url
    except Exception as exc:
        logger.error(f"failed to upload file to MinIO:{exc}")
        raise exc