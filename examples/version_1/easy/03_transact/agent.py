from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.onchain.transact import TransactTool
from lola.core.agent import BaseAgent

"""
File: Simple EVM transaction agent.
Purpose: Sends a basic transaction on Sepolia.
How: Extends BaseAgent with TransactTool, uses Gemini LLM.
Why: Introduces beginners to blockchain writes in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/03_transact/agent.py
"""

logger = setup_logger("transact")

class Agent(BaseAgent):
    """Simple EVM transaction agent. Binds TransactTool for sending transactions."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize transaction agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.tool = TransactTool()
        logger.info("Transaction agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to send a transaction on Sepolia.

        Args:
            query: User query string (e.g., "Send 0.1 ETH to 0x... on Sepolia").
            history: Optional prior messages for context (unused here).

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            # Parse query for address and value
            parts = query.split(" ")
            to_address = parts[3]
            value = float(parts[1])
            result = self.tool.execute(to=to_address, value=value, chain="sepolia")
            state.messages.append({"role": "assistant", "content": result})
            state.tool_results["transact"] = result
            logger.info("Transaction completed", extra={"to": to_address, "value": value})
        except Exception as e:
            error_msg = f"Error sending transaction: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Transaction failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]