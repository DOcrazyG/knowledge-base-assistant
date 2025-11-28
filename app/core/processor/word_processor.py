import os
from io import BytesIO
from typing import BinaryIO

import mammoth
from markdownify import markdownify as md

from ...utils.save2minio import upload_file
from .base import BaseProcessor


@mammoth.images.img_element
def convert_image(image):
    with image.open() as image_bytes:
        filename = os.path.basename(image_bytes.name)
        content = image_bytes.read()
        image_url = upload_file(
            BytesIO(content),
            filename,
            len(content),
            image.content_type,
        )

    return {"src": image_url}


class WordProcessor(BaseProcessor):
    async def process_document(self, file_data: BinaryIO, filename: str):
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in [".docx"]:
            raise ValueError(
                f"WordProcessor can not handle the file with extension like {file_extension}"
            )
        md_text = await self.parse_docx(file_data)
        return md_text

    async def parse_docx(self, file_data: BinaryIO):
        result = mammoth.convert_to_html(fileobj=file_data, convert_image=convert_image)
        md_text = md(result.value, heading_style="ATX")
        return md_text
