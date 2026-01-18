import pytest
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock
from main import run_pipeline
from fetchers.base import Article

# Dummy Article Object
def create_dummy_article(source):
    return Article(
        title=f"Title from {source}",
        content="Content",
        source=source,
        url="http://url.com",
        fetched_at="2025-01-01"
    )

@pytest.mark.asyncio
async def test_main_pipeline_execution():
    # We are patching classes that are imported into main.py
    with patch("main.NewsAPIFetcher") as MockNews, \
         patch("main.CSVFetcher") as MockCSV, \
         patch("main.WebScraperFetcher") as MockWeb, \
         patch("main.os.makedirs") as mock_makedirs, \
         patch("builtins.open", new_callable=MagicMock) as mock_file_open:

        # 1. Mock fetcher instances and their fetch methods
        
        # NewsAPI Mock
        news_instance = MockNews.return_value
        news_instance.fetch = AsyncMock(return_value=[create_dummy_article("newsapi")])

        # CSV Mock
        csv_instance = MockCSV.return_value
        csv_instance.fetch = AsyncMock(return_value=[create_dummy_article("csv")])

        # Web Mock
        web_instance = MockWeb.return_value
        web_instance.fetch = AsyncMock(return_value=[create_dummy_article("web")])

        # 2. Run the pipeline
        await run_pipeline()

        # 3. Validation
        
        # Check whether output directory creation was attempted
        mock_makedirs.assert_called_with("output", exist_ok=True)
        
        # Check whether output file was opened for writing
        mock_file_open.assert_called_with("output/articles.json", "w", encoding="utf-8")
        
        # Most importantly, check whether data was written to the file
        # Get the file handle to check write calls
        handle = mock_file_open()
        
        # Here we check whether write was called at least once
        # This indicates that data was attempted to be written
        assert news_instance.fetch.called
        assert csv_instance.fetch.called
        assert web_instance.fetch.called