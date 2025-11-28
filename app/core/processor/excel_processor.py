import os
from typing import BinaryIO

import pandas as pd

from .base import BaseProcessor


class ExcelProcessor(BaseProcessor):
    async def process_document(self, file_data: BinaryIO, filename: str):
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in [".xls", ".xlsx"]:
            raise ValueError(
                f"ExcelProcessor can not handle the file with extension like {file_extension}"
            )
        md_text = await self.parse_excel(file_data)
        return md_text

    async def parse_excel(self, file_data: BinaryIO):
        data = pd.read_excel(file_data)
        return data.to_markdown(index=False)
