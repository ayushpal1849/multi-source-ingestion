# Development Process Log

## Problem Statement
The goal was to build a robust, asynchronous data ingestion pipeline that fetches data from three disparate sources (NewsAPI, Local CSV, Web Scraper), normalizes them into a consistent schema, and saves the output as a JSON file.

**Key Challenges:**
1.  **Concurrency:** Fetching data sequentially is slow. The system needs to be asynchronous.
2.  **Data Consistency:** Different sources have different field names (e.g., 'Headline' vs 'title').
3.  **Resilience:** External APIs fail, and website HTML structures change. The system must handle these edge cases.

## Architecture Decisions
- **Design Pattern:** I used the **Strategy Pattern** via an Abstract Base Class (`BaseFetcher`). This enforces a strict contract (`fetch() -> List[Article]`) for all current and future fetchers.
- **Concurrency:** I chose `asyncio` and `httpx` instead of `requests`. Since this is an I/O-bound task, running fetchers concurrently significantly reduces total execution time.
- **Data Model:** Used Python `dataclasses` for the `Article` schema to ensure type safety and prevent "dictionary chaos" during normalization.

---

## Step-by-Step Execution & AI Collaboration

### Task 1: Setup & Base Class
- **Goal:** Define the interface and data model.
- **AI Prompt:** "Create an Abstract Base Class `BaseFetcher` using `dataclasses` for the Article model. Fields: title, content, source, url, fetched_at."
- **My Review & Refinement:**
    - The AI initially provided a synchronous method.
    - **Correction:** I modified the `fetch` method to be `async def fetch(self)` to support non-blocking I/O operations later in the pipeline.

### Task 2: CSV Fetcher Implementation
- **Goal:** Read local data efficiently.
- **AI Prompt:** "Write a `CSVFetcher` that inherits from `BaseFetcher`. Map 'Headline' to 'title' and 'Body' to 'content'."
- **My Review & Refinement:**
    - The AI suggested using the standard `open()` function.
    - **Critique:** In an async pipeline, standard file I/O blocks the event loop.
    - **Fix:** I rewrote the implementation to use `aiofiles` for non-blocking file reading, ensuring consistency with the async architecture.

### Task 3: NewsAPI Implementation
- **Goal:** Fetch live data with error handling.
- **AI Prompt:** "Write a `NewsAPIFetcher` using `httpx`. Handle API keys from env vars and map the JSON response to the Article class."
- **My Review & Refinement:**
    - The initial code lacked retry logic. If the API blipped, the task would fail immediately.
    - **Enhancement:** I asked AI to add a "Exponential Backoff" retry mechanism (`MAX_RETRIES = 3`).
    - **Edge Case Handling:** Added logic to fallback to the `description` field if `content` is empty in the API response.

### Task 4: Web Scraper Implementation (The Tricky Part)
- **Goal:** Scrape Python.org blogs without getting blocked.
- **AI Prompt:** "Scrape `blog.python.org`. Use `BeautifulSoup` to extract titles from `h3.post-title`. Add User-Agent headers."
- **My Review & Refinement:**
    - **Observation:** Websites often change their DOM structure. A single selector is brittle.
    - **Optimization:** I implemented a **Fallback Selector** logic. If `h3.post-title` returns no results, the code automatically tries finding links in the `#index-by-category` section.
    - **Outcome:** This makes the scraper resilient to minor UI changes on the target website.

### Task 5: Pipeline Orchestration
- **Goal:** Run everything together.
- **My Review:**
    - Used `asyncio.gather` (conceptually) or sequential awaits in `main.py` to aggregate results.
    - Added a summary printout to verify data counts from each source before saving.

---

## Testing & Debugging Journey (Critical)

While writing tests, I encountered a significant challenge:

**The Bug:**
When running `pytest`, I received: `TypeError: object MagicMock can't be used in 'await' expression`.

**Root Cause:**
I was using `unittest.mock.MagicMock` to mock the `httpx` client. However, since my code uses `await client.get()`, Python expected an "awaitable" object, but standard Mocks are synchronous.

**The Solution:**
I researched and switched to using **`AsyncMock`** for the `fetch` methods and `httpx` calls. This ensures the mocks mimic the asynchronous behavior of the real fetchers. This experience deepened my understanding of testing async code in Python.

---

## Future Improvements
1.  **Database Integration:** Replace JSON output with PostgreSQL (using `asyncpg`) for better data querying.
2.  **Dockerization:** Containerize the application for easier deployment.
3.  **Logging:** Replace `print` statements with a structured logger (`logging` module) for production monitoring.