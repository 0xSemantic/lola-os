from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.onchain.contract_call import ContractCallTool
from lola.core.agent import BaseAgent

"""
File: Simple EVM contract reader agent.
Purpose: Reads data from an EVM smart contract.
How: Extends BaseAgent with ContractCallTool, uses Gemini LLM.
Why: Introduces beginners to blockchain reads in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/02_contract_reader/agent.py
"""

logger = setup_logger("contract_reader")

class Agent(BaseAgent):
    """Simple EVM contract reader agent. Binds ContractCallTool for read-only calls."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize contract reader agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.tool = ContractCallTool()
        logger.info("Contract reader agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to read contract data on Sepolia.

        Args:
            query: User query string (e.g., "Read balanceOf 0x... on Sepolia").
            history: Optional prior messages for context (unused here).

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            # Parse query for contract address and function
            parts = query.split(" ")
            contract_address = parts[2]
            function_name = parts[1]
            result = self.tool.execute(
                contract_address=contract_address,
                function_name=function_name,
                chain="sepolia"
            )
            state.messages.append({"role": "assistant", "content": result})
            state.tool_results["contract_call"] = result
            logger.info("Contract call completed", extra={"address": contract_address, "function": function_name})
        except Exception as e:
            error_msg = f"Error reading contract: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Contract call failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]