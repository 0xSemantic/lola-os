# Standard imports
import asyncio
from typing import List

# Third-party imports
# (none)

# Local imports
from lola.core.graph import StateGraph
from lola.core.state import State
from lola.core.memory import ConversationMemory

"""
File: Combined Graph + Memory demo.

Purpose: Shows a simple async graph that processes a state initialised from memory.
How: Builds a StateGraph, adds a node, executes it, and prints the final state.
Why: Validates the orchestration backbone (graph + supervision) in a single script.
Full Path: lola-os/examples/version_1/foundation_combined/agent.py
"""

async def main() -> None:
    """
    Async entry point – builds graph, feeds memory-initialised state, runs.

    Does Not: Use external tools or LLMs (Phase-1 only).
    """
    # Inline: Build a tiny processing node
    def process_node(state: State) -> State:
        state.messages.append({"role": "system", "content": "Node processed"})
        return state

    # Inline: Assemble graph with supervision defaults
    graph = StateGraph()
    graph.add_node("processor", process_node)
    graph.set_entry_point("processor")
    graph.set_finish_point("processor")

    # Inline: Seed state from conversation memory
    mem = ConversationMemory()
    mem.append({"role": "user", "content": "What is the weather?"})
    mem.append({"role": "assistant", "content": "I need a tool..."})
    initial_state = State(messages=mem.retrieve())

    # Inline: Execute with async supervision
    final_state = await graph.execute(initial_state)

    # Inline: Human-readable output
    print("=== Final State ===")
    for msg in final_state.messages:
        print(f"{msg['role'].title()}: {msg['content']}")
    if final_state.reflection:
        print(f"Reflection: {final_state.reflection}")

if __name__ == "__main__":
    asyncio.run(main())

__all__ = ["main"]