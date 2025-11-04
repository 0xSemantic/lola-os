# Conversational with Tools (Moderate Example 3)

A LOLA OS conversational agent with web crawling capabilities.

## Overview
Uses ConversationalAgent with WebCrawlTool to handle chat queries with web data. Ideal for intermediate users learning tool-augmented conversations.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/03_conversational_with_tools
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
- Or: `poetry run lola run --query "What's the latest news on https://news.ycombinator.com?"`.
- Expected: Agent response with web content and conversational reply.

## Walkthrough
- `agent.py`: Uses ConversationalAgent with WebCrawlTool for chat-based web queries.
- `config.yaml`: Sets Gemini model.
- Exercise: Add support for specific selectors in the query.

## Troubleshooting
- Web fail? Check URL or selectors in query.
- No response? Verify `GEMINI_API_KEY`.

## Best Practices
- Use context-aware prompts for better responses.
- Log tool actions and errors.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 04_plan_transact for planning transactions.
- Explore tutorials in docs/ for more.