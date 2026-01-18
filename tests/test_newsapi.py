import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fetchers.newsapi import NewsAPIFetcher
import os

# --- Mock Data ---
MOCK_API_RESPONSE = {
    "status": "ok",
    "articles": [
        {
            "title": "API News",
            "description": "Content",
            "url": "http://test.com",
            "source": {"name": "Test Source"}
        }
    ]
}

@pytest.mark.asyncio
async def test_newsapi_live_fetch_success():
    # Mock environment variable for API key
    with patch.dict(os.environ, {"NEWS_API_KEY": "fake_key"}):
        # Mock httpx.AsyncClient
        with patch("httpx.AsyncClient") as MockClient:
            # Async context manager mock setup
            mock_instance = MockClient.return_value
            mock_instance.__aenter__.return_value = mock_instance
            
            # Response mock setup
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_API_RESPONSE
            
            # Set the get method to return the mock response
            mock_instance.get = AsyncMock(return_value=mock_response)
            
            # Test run
            fetcher = NewsAPIFetcher(use_mock=False)
            articles = await fetcher.fetch()
            
            assert len(articles) == 1
            assert articles[0].title == "API News"
            assert articles[0].source == "Test Source"

@pytest.mark.asyncio
async def test_newsapi_missing_key():
    # No API key in environment
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            NewsAPIFetcher(use_mock=False)

@pytest.mark.asyncio
async def test_newsapi_mock_mode():
    # Mocking open to simulate reading from mock file
    with patch("builtins.open", new_callable=MagicMock) as mock_open:
        # Mocking file read
        mock_file = MagicMock()
        # Setting the file's read method to return JSON string
        with patch("json.load", return_value=MOCK_API_RESPONSE):
            mock_open.return_value.__enter__.return_value = mock_file
            
            fetcher = NewsAPIFetcher(use_mock=True)
            articles = await fetcher.fetch()
            
            assert len(articles) == 1
            assert articles[0].title == "API News"