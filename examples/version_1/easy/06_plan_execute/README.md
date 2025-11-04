# Plan Execute (Easy Example 6)

A LOLA OS agent using plan-execute loop for web crawling.

## Overview
Uses PlanExecuteAgent with WebCrawlTool to plan and crawl websites. Ideal for beginners learning planning workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/06_plan_execute
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
- Expected: Agent response with plan and crawled content.

## Walkthrough
- `agent.py`: Uses PlanExecuteAgent for planning and web crawling.
- `config.yaml`: Sets Gemini model.
- Exercise: Modify prompt to include a multi-step plan.

## Troubleshooting
- Plan fail? Check LLM response format.
- Crawl fail? Verify URL in query.

## Best Practices
- Use planning for structured tasks.
- Log plan and execution steps.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 07_gas_estimator for blockchain tasks.
- Explore tutorials in docs/ for more.