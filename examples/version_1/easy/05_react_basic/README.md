# ReAct Basic (Easy Example 5)

A LOLA OS agent using ReAct loop for web crawling.

## Overview
Uses ReActAgent with WebCrawlTool to crawl websites with reasoning. Ideal for beginners learning ReAct logic.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/05_react_basic
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
- Expected: Agent response with crawled content and reasoning.

## Walkthrough
- `agent.py`: Uses ReActAgent for single-step web crawling.
- `config.yaml`: Sets Gemini model.
- Exercise: Modify prompt to include selectors (e.g., "h1").

## Troubleshooting
- Crawl fail? Check URL or internet connection.
- JSON error? Verify LLM response format.

## Best Practices
- Use ReAct for structured reasoning.
- Log tool actions for debugging.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 06_plan_execute for planning tasks.
- Explore tutorials in docs/ for more.