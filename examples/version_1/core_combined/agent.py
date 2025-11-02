# Standard imports
import asyncio
from typing import Dict, str, Any

# Third-party imports
# None

# Local imports
from lola.core.agent import BaseAgent
from lola.core.graph import LOLAStateGraph
from lola.core.memory import ConversationMemory
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.core.state import State

"""
File: Combined example: Agent with graph workflow and memory extraction.

Purpose: Demonstrates BaseAgent + graph + memory for multi-turn orchestration.
How: Inits agent with graph (add node/edge), memory, executes query, extracts/summarizes, logs/prints.
Why: Shows V3 full core integration—async workflow with context persistence.
Full Path: lola-os/examples/version_1/core_combined/agent.py
"""

class GraphAgent(BaseAgent):
    """GraphAgent: BaseAgent extension with graph and memory for combined demo. Does Not bind tools—base LLM only."""

    def __init__(self):
        """
        Init GraphAgent with graph and memory.

        Does Not: Load config—parent does.
        """
        super().__init__()
        self.graph = LOLAStateGraph()
        self.graph.add_node("reason", self.reason_node)
        self.graph.add_edge("__start__", "reason")
        self.graph.add_edge("reason", END)
        self.memory = ConversationMemory(self.llm_proxy)
        logger.info("GraphAgent init", extra={"nodes": 1})

    def reason_node(self, state: State) -> State:
        """
        Sample graph node: Reasons with LLM on state.

        Args:
            state: Input State.

        Returns:
            Updated State with reason.

        Does Not: Use tools—simple LLM reflection.
        """
        prompt = f"Reason on query: {state.messages[-1]['content']}"
        reason = self.call_llm(prompt)
        state.tool_results["reason"] = reason
        logger.debug("Reason node executed", extra={"reason_len": len(reason)})
        return state

    def run(self, query: str) -> State:
        """
        Runs graph workflow with query, extracts entities/summary.

        Args:
            query: User query string.

        Returns:
            Final State with reason/entities/summary.

        Does Not: Persist—use StateManager.save.
        """
        initial = State(messages=[{"role": "user", "content": query}])
        final_state = asyncio.run(self.graph.execute(initial.model_dump()))
        final_state.entities = self.memory.extract_entities(final_state.messages)
        final_state.tool_results["summary"] = self.memory.summarize_history(final_state.messages)
        logger.info("GraphAgent run", extra={"entities_count": len(final_state.entities.get("entities", []))})
        return final_state

if __name__ == "__main__":
    # Inline: Load config for model/key
    config = load_config()
    logger = setup_logger()
    agent = GraphAgent()
    state = agent.run("Plan a trip to New York on 2025-01-01 for Alice.")
    logger.info("Combined core demo", extra={"state_keys": list(state.model_dump().keys())})
    print(f"Reason: {state.tool_results['reason'][:100]}...")
    print(f"Entities: {state.entities['entities']}")
    print(f"Summary: {state.tool_results['summary']}")