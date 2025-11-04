from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.onchain.utils import gas_estimate
from lola.core.agent import BaseAgent

"""
File: Simple gas estimator agent.
Purpose: Estimates gas for EVM transactions.
How: Extends BaseAgent with gas_estimate utility, uses Gemini LLM.
Why: Introduces beginners to gas estimation in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/07_gas_estimator/agent.py
"""

logger = setup_logger("gas_estimator")

class Agent(BaseAgent):
    """Simple gas estimator agent. Uses gas_estimate utility."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize gas estimator agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        logger.info("Gas estimator agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to estimate gas for a transaction on Sepolia.

        Args:
            query: User query string (e.g., "Estimate gas for sending 0.1 ETH to 0x...").
            history: Optional prior messages for context (unused here).

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            # Parse query for address and value
            parts = query.split(" ")
            to_address = parts[4]
            value = float(parts[3])
            result = gas_estimate(to=to_address, value=value, chain="sepolia")
            state.messages.append({"role": "assistant", "content": str(result)})
            state.tool_results["gas_estimate"] = result
            logger.info("Gas estimation completed", extra={"to": to_address, "value": value})
        except Exception as e:
            error_msg = f"Error estimating gas: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Gas estimation failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]