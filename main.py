import json
import os
from dataclasses import asdict
from typing import List

from dotenv import load_dotenv

from fetchers.base import Article
from fetchers.newsapi import NewsAPIFetcher
from fetchers.csv_reader import CSVFetcher
from fetchers.web_scraper import WebScraperFetcher


# Load environment variables
load_dotenv()

# Async pipeline runner

async def run_pipeline() -> None:
    all_articles: List[Article] = []

    # Instantiate fetchers
    newsapi_fetcher = NewsAPIFetcher(use_mock=True)
    csv_fetcher = CSVFetcher(file_path="input/sample_data.csv")
    web_scraper_fetcher = WebScraperFetcher()

    # Run fetchers
    newsapi_articles = await newsapi_fetcher.fetch()
    csv_articles = await csv_fetcher.fetch()
    web_articles = await web_scraper_fetcher.fetch()

    # Aggregate results
    all_articles.extend(newsapi_articles)
    all_articles.extend(csv_articles)
    all_articles.extend(web_articles)
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # Serialize dataclasses to JSON
    output_path = "output/articles.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            [asdict(article) for article in all_articles],
            f,
            indent=2,
            ensure_ascii=False,
        )

    # Print summary
    print(
        f"Fetched {len(newsapi_articles)} articles from NewsAPI, "
        f"{len(csv_articles)} from CSV, "
        f"{len(web_articles)} from Web Scraper."
    )
    
    print("NewsAPI:", len(newsapi_articles))
    print("CSV:", len(csv_articles))
    print("Web:", len(web_articles))

    print(f"Total articles saved: {len(all_articles)}")
    print(f"Output file: {output_path}")


# Entry point
if __name__ == "__main__":
    import asyncio

    asyncio.run(run_pipeline())
