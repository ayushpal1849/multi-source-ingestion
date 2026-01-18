import json
import os
from datetime import datetime
from typing import List

import httpx
from dotenv import load_dotenv

from fetchers.common import BaseFetcher, Article

load_dotenv()


class NewsAPIFetcher(BaseFetcher):
    BASE_URL = "https://newsapi.org/v2/top-headlines"
    TIMEOUT = 5

    def __init__(self, use_mock: bool = True):
        """
        use_mock=True  -> read from temp.json
        use_mock=False -> call real API
        """
        self.use_mock = use_mock
        self.api_key = os.getenv("NEWS_API_KEY")

        if not self.use_mock and not self.api_key:
            raise ValueError("NEWS_API_KEY missing")

    async def fetch(self) -> List[Article]:
        if self.use_mock:
            print("[MOCK] Reading NewsAPI data from temp.json")
            return self._read_from_mock()

        print("[LIVE] Fetching data from NewsAPI")
        return await self._fetch_from_api()

    # MOCK MODE
    
    def _read_from_mock(self) -> List[Article]:
        try:
            with open("mock/newsapi_temp.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._normalize(data)
        except Exception as e:
            print(f"[ERROR] Failed to read mock file: {e}")
            return []

    # REAL API MODE
    async def _fetch_from_api(self) -> List[Article]:
        params = {
            "category": "technology",
            "apiKey": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.BASE_URL, params=params)

            if response.status_code != 200:
                print(
                    f"[ERROR] NewsAPI failed "
                    f"({response.status_code}): {response.text}"
                )
                return []

            return self._normalize(response.json())

        except Exception as e:
            print(f"[ERROR] NewsAPI request failed: {e}")
            return []

    # NORMALIZATION
    def _normalize(self, data: dict) -> List[Article]:
        if data.get("status") != "ok":
            print("[ERROR] Invalid NewsAPI response")
            return []

        fetched_at = datetime.now().isoformat()
        articles: List[Article] = []

        for item in data.get("articles", []):
            articles.append(
                Article(
                    title=item.get("title") or "",
                    content=item.get("content")
                    or item.get("description")
                    or "",
                    source=item.get("source", {}).get("name", "newsapi"),
                    url=item.get("url") or "",
                    fetched_at=fetched_at,
                )
            )

        return articles
