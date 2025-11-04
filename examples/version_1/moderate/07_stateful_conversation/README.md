# Stateful Conversation (Moderate Example 7)

A LOLA OS agent for stateful conversations with web tool support.

## Overview
Uses ConversationalAgent with WebCrawlTool and ConversationMemory for stateful chat. Ideal for intermediate users learning context-aware conversations.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/07_stateful_conversation
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
- Or: `poetry run lola run --query "Crawl https://example.com and summarize it"`.
- Expected: Agent response with web content and conversational summary.

## Walkthrough
- `agent.py`: Uses ConversationalAgent with WebCrawlTool and memory for stateful chat.
- `config.yaml`: Sets Gemini model.
- Exercise: Test multi-turn conversation with follow-up queries.

## Troubleshooting
- Context lost? Check ConversationMemory in `agent.py`.
- Web fail? Verify URL in query.

## Best Practices
- Use ConversationMemory for context retention.
- Log conversation and tool actions.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 08_contract_simulator for contract simulation.
- Explore tutorials in docs/ for more.