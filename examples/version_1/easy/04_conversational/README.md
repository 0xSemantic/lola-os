# Conversational (Easy Example 4)

A LOLA OS agent for simple conversational tasks.

## Overview
Uses BaseAgent with ConversationMemory to maintain chat context. Ideal for beginners learning conversational agents.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/04_conversational
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
- Or: `poetry run lola run --query "Hello, how are you?"`.
- Expected: Agent response with conversational reply.

## Walkthrough
- `agent.py`: Uses BaseAgent with ConversationMemory for simple chat.
- `config.yaml`: Sets Gemini model.
- Exercise: Try multiple queries to test context (e.g., "Tell me more").

## Troubleshooting
- No response? Check `GEMINI_API_KEY` in `.env`.
- Context lost? Verify ConversationMemory usage.

## Best Practices
- Keep queries simple for testing.
- Log conversation history.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 05_react_basic for ReAct logic.
- Explore tutorials in docs/ for more.