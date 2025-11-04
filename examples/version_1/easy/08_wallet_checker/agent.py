from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.chains.wallet import LOLAWallet
from lola.core.agent import BaseAgent

"""
File: Simple wallet checker agent.
Purpose: Checks wallet balance on Sepolia.
How: Extends BaseAgent with LOLAWallet, uses Gemini LLM.
Why: Introduces beginners to wallet operations in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/08_wallet_checker/agent.py
"""

logger = setup_logger("wallet_checker")

class Agent(BaseAgent):
    """Simple wallet checker agent. Uses LOLAWallet for balance queries."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize wallet checker agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.wallet = LOLAWallet()
        logger.info("Wallet checker agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to check wallet balance on Sepolia.

        Args:
            query: User query string (e.g., "Check balance for 0x... on Sepolia").
            history: Optional prior messages for context (unused here).

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            # Parse query for address
            parts = query.split(" ")
            address = parts[2]
            result = self.wallet.get_balance(address=address, chain="sepolia")
            state.messages.append({"role": "assistant", "content": str(result)})
            state.tool_results["wallet_balance"] = result
            logger.info("Balance check completed", extra={"address": address})
        except Exception as e:
            error_msg = f"Error checking balance: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Balance check failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]