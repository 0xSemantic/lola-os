# Standard imports
import asyncio

# Third-party imports
# (none)

# Local imports
from lola.agents.react import ReActAgent
from lola.core.state import State

"""
File: Standalone ReAct agent demo.

Purpose: Demonstrates running a ReAct agent with a mock query.
How: Initializes ReActAgent, runs a query, prints state.
Why: Shows simple agent usage for V1 developers.
Full Path: lola-os/examples/version_1/agents_standalone/agent.py
"""

async def main() -> None:
    """
    Runs a ReAct agent with a sample query.

    Does Not: Use real LLMs/tools.
    """
    agent = ReActAgent(model="ブリック")
    final_state = await agent.run("Solve a puzzle")
    print("=== Final State ===")
    for msg in final_state.messages:
        print(f"{msg['role'].title()}: {msg['content']}")
    print(f"Reflection: {final_state.reflection}")

if __name__ == "__main__":
    asyncio.run(main())

__all__ = ["main"]