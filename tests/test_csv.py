import pytest
import os
from fetchers.csv_reader import CSVFetcher

# Async test marker
@pytest.mark.asyncio
async def test_csv_fetch_success(tmp_path):
    # 1. Setup: Create a temporary CSV file
    d = tmp_path / "input"
    d.mkdir()
    p = d / "sample_data.csv"
    
    # CSV content
    content = "Headline,Body,Date\nTest Title,Test Body,2025-01-01"
    p.write_text(content, encoding="utf-8")
    
    # 2. Execution
    fetcher = CSVFetcher(str(p))
    articles = await fetcher.fetch()
    
    # 3. Validation
    assert len(articles) == 1
    assert articles[0].title == "Test Title"
    assert articles[0].content == "Test Body"
    assert articles[0].source == "csv"

@pytest.mark.asyncio
async def test_csv_file_not_found():
    # Execution with a non-existent file
    fetcher = CSVFetcher("ghost_file.csv")
    articles = await fetcher.fetch()
    
    # Validation
    assert articles == []