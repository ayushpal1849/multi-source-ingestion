from datetime import datetime
from typing import List, Tuple

import httpx
from bs4 import BeautifulSoup

from fetchers.common import BaseFetcher, Article


class WebScraperFetcher(BaseFetcher):
    URL = "https://blog.python.org/"
    MAX_ARTICLES = 5
    TIMEOUT = 5
    MAX_RETRIES = 3

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async def fetch(self) -> List[Article]:
        fetched_at = datetime.now().isoformat()

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=self.TIMEOUT,
                    headers=self.HEADERS,
                ) as client:
                    response = await client.get(self.URL)
                    response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                posts = self._extract_posts(soup)

                articles: List[Article] = []
                for title, url in posts[: self.MAX_ARTICLES]:
                    articles.append(
                        Article(
                            title=title,
                            content="",
                            source="blog.python.org",
                            url=url,
                            fetched_at=fetched_at,
                        )
                    )

                return articles

            except httpx.TimeoutException:
                print(f"[WARN] Timeout (attempt {attempt}/{self.MAX_RETRIES})")
            except Exception as e:
                print(f"[ERROR] Web scraping failed: {e}")

            await self._backoff(attempt)

        return []

    def _extract_posts(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        posts: List[Tuple[str, str]] = []

        # Primary selector (current structure)
        h3_titles = soup.find_all("h3", class_="post-title")
        if h3_titles:
            for h3 in h3_titles:
                a = h3.find("a")
                if a:
                    posts.append((a.get_text(strip=True), a.get("href", "")))
            return posts

        # Fallback selector
        section = soup.find(id="index-by-category")
        if section:
            print("[WARN] Using fallback selector for blog.python.org")
            for a in section.find_all("a"):
                posts.append((a.get_text(strip=True), a.get("href", "")))
            return posts

        print("[ALERT] HTML structure changed on blog.python.org")
        return []

    async def _backoff(self, attempt: int):
        import asyncio
        await asyncio.sleep(2 ** attempt)
