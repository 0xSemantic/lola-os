# Web Crawler (Easy Example 1)

A LOLA OS agent for simple web crawling.

## Overview
Uses BaseAgent with WebCrawlTool to scrape website content. Ideal for beginners learning LOLA OS basics.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/01_web_crawler
   ```
2. Install (if not root):
   ```bash
   poetry install
   ```
3. Copy env:
   ```bash
   cp .env.sample .env
   ```
4. Edit `.env` with `GEMINI_API_KEY`.

## Run
```bash
poetry run python agent.py
```
- Or: `poetry run lola run --query "Crawl https://example.com"`.
- Expected: Agent response with website content.

## Walkthrough
- `agent.py`: Simple BaseAgent using WebCrawlTool.
- `config.yaml`: Sets Gemini model.
- Exercise: Change query to crawl another site (e.g., "Crawl https://news.ycombinator.com").

## Troubleshooting
- Crawl fail? Check URL format or internet connection.
- Key error? Verify `GEMINI_API_KEY` in `.env`.

## Best Practices
- Use simple queries for testing.
- Log errors for debugging.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 02_contract_reader for blockchain tasks.
- Explore tutorials in docs/ for more.