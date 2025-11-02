# Standard imports
from typing import Dict, str

# Third-party imports
# None

# Local imports
from lola.core.agent import BaseAgent
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.core.state import State

"""
File: Standalone example: BaseAgent with simple LLM call.

Purpose: Demonstrates BaseAgent init, call_llm, and run for basic agent flow.
How: Loads config, extends BaseAgent with mock run using call_llm, logs/prints state.
Why: Onboarding to V3 core—shows sovereign LLM integration without graph/tools.
Full Path: lola-os/examples/version_1/core_standalone/agent.py
"""

class SimpleAgent(BaseAgent):
    """SimpleAgent: Minimal BaseAgent extension for demo. Does Not use graph/memory—base call_llm only."""

    def run(self, query: str) -> State:
        """
        Runs simple LLM query via call_llm.

        Args:
            query: User query string.

        Returns:
            State with query and LLM response.

        Does Not: Use tools or graph—direct LLM.
        """
        response = self.call_llm(f"Answer: {query}")
        state = State(messages=[{"role": "user", "content": query}, {"role": "assistant", "content": response}])
        return state

if __name__ == "__main__":
    # Inline: Load config for model
    config = load_config()
    logger = setup_logger()
    agent = SimpleAgent()
    state = agent.run("What is LOLA OS?")
    logger.info("Standalone agent run", extra={"messages_len": len(state.messages)})
    print(f"Query: {state.messages[0]['content']}")
    print(f"Response: {state.messages[1]['content']}")