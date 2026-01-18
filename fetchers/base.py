from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List

@dataclass
class Article:
    title: str
    content: str
    source: str
    url: str
    fetched_at: str

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self) -> List[Article]:
        """
        Fetch articles from a source.

        Returns:
            List[Article]: A list of fetched articles
        """
        pass
