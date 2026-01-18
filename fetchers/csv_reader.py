import csv
from datetime import datetime
from typing import List
from io import StringIO

import aiofiles

from fetchers.base import BaseFetcher, Article


class CSVFetcher(BaseFetcher):
    def __init__(self, file_path: str):
        self.file_path = file_path

    async def fetch(self) -> List[Article]:
        articles: List[Article] = []

        try:
            async with aiofiles.open(self.file_path, mode="r", encoding="utf-8") as file:
                content = await file.read()

            reader = csv.DictReader(StringIO(content))

            for row in reader:
                articles.append(
                    Article(
                        title=(row.get("Headline") or "").strip(),
                        content=(row.get("Body") or "").strip(),
                        source="csv",
                        url="",
                        fetched_at=datetime.now().isoformat(),
                    )
                )

        except FileNotFoundError:
            print(f"[ERROR] CSV file not found: {self.file_path}")
            return []

        return articles
