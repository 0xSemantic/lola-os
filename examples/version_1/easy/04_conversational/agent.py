from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.core.agent import BaseAgent

"""
File: Simple conversational agent.
Purpose: Handles basic chat with conversation memory.
How: Extends BaseAgent with ConversationMemory, uses Gemini LLM.
Why: Introduces beginners to conversational agents in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/04_conversational/agent.py
"""

logger = setup_logger("conversational")

class Agent(BaseAgent):
    """Simple conversational agent. Uses ConversationMemory for context retention."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize conversational agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        logger.info("Conversational agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to respond to query with conversation context.

        Args:
            query: User query string (e.g., "Hello, how are you?").
            history: Optional prior messages for context.

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            prompt = self.memory.summarize_history(state.messages)
            response = self.call_llm(f"Respond to: {prompt}")
            state.messages.append({"role": "assistant", "content": response})
            state.tool_results["response"] = response
            logger.info("Conversation response", extra={"query": query})
        except Exception as e:
            error_msg = f"Error responding: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Conversation failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]