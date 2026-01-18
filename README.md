# Multi-Source Data Ingestion Pipeline

## Overview
An asynchronous backend pipeline designed to ingest, normalize, and unify data from multiple sources:
1.  **NewsAPI** (REST API)
2.  **Local CSV** (File System)
3.  **Python.org Blog** (Web Scraper)

Built using **Python 3.14**, **AsyncIO**, and **HTTPX**. Designed with the Strategy Pattern for scalability.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ayushpal1849/multi-source-ingestion.git
    cd multi-source-ingestion
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory and add:
    ```
    NEWS_API_KEY=your_api_key_here
    ```

## Running the Pipeline
```bash
python main.py
```
Output will be saved to output/articles.json.

## Testing
This project includes a full test suite using pytest and pytest-asyncio.

```bash
python -m pytest
```

## Architecture
* **BaseFetcher (ABC):** Enforces a strict contract for all data sources.

* **AsyncIO:** Ensures non-blocking execution for I/O-bound tasks.

* **Robustness:** Includes retry logic and fallback mechanisms for scraping.