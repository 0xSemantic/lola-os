# Standard imports
import asyncio

# Third-party imports
# (none)

# Local imports
from lola.agents.conversational import ConversationalAgent
from lola.core.memory import ConversationMemory
from lola.core.state import State

"""
File: Combined Conversational agent demo with memory.

Purpose: Shows ConversationalAgent retaining context from memory.
How: Seeds memory, runs queries, prints state with history.
Why: Demonstrates context-aware dialogue for V1.
Full Path: lola-os/examples/version_1/agents_combined/agent.py
"""

async def main() -> None:
    """
    Runs ConversationalAgent with memory.

    Does Not: Use real LLMs/tools.
    """
    memory = ConversationMemory()
    memory.append({"role": "user", "content": "Hi, I'm Bob"})
    agent = ConversationalAgent(model="mock-model", memory=memory)
    final_state = await agent.run("What's my name?")
    print("=== Final State ===")
    for msg in final_state.messages:
        print(f"{msg['role'].title()}: {msg['content']}")
    print(f"Reflection: {final_state.reflection}")

if __name__ == "__main__":
    asyncio.run(main())

__all__ = ["main"]