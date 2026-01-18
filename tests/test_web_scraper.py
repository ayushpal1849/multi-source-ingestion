import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fetchers.web_scraper import WebScraperFetcher

# --- Mock HTML Content ---
MOCK_HTML = """
<html>
    <body>
        <h3 class="post-title">
            <a href="https://blog.python.org/test">Python Released</a>
        </h3>
        <h3 class="post-title">
            <a href="https://blog.python.org/test2">Another Post</a>
        </h3>
    </body>
</html>
"""

@pytest.mark.asyncio
async def test_scraper_fetch_success():
    with patch("httpx.AsyncClient") as MockClient:
        # Mock setup
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = MOCK_HTML
        
        mock_instance.get = AsyncMock(return_value=mock_response)
        
        # Run fetcher
        fetcher = WebScraperFetcher()
        articles = await fetcher.fetch()

        # Validation
        assert len(articles) == 2
        assert articles[0].title == "Python Released"
        assert articles[0].url == "https://blog.python.org/test"
        assert articles[0].source == "blog.python.org"

@pytest.mark.asyncio
async def test_scraper_fallback_logic():
    # Fallback HTML structure
    FALLBACK_HTML = """
    <html>
        <div id="index-by-category">
            <a href="fallback-url">Fallback Title</a>
        </div>
    </html>
    """
    
    with patch("httpx.AsyncClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = FALLBACK_HTML
        
        mock_instance.get = AsyncMock(return_value=mock_response)

        fetcher = WebScraperFetcher()
        articles = await fetcher.fetch()

        assert len(articles) == 1
        assert articles[0].title == "Fallback Title"