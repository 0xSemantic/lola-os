# Standard imports
import abc
from typing import List, Optional, Any

# Third-party imports
# None (uses phase 2 litellm proxy)

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.graph import LOLAStateGraph
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy

"""
File: Base agent class for LOLA OS, integrating LLM, graph, and memory for orchestration.

Purpose: Abstract base for agent templates, handling init/bind/run with LLM calls, graph execution, and memory integration.
How: Init with config model, uses LLMProxy for call_llm, LOLAStateGraph for workflow, ConversationMemory for context.
Why: Unifies agent logic in V1, ensuring scalable, sovereign orchestration with verifiable state and reflection.
Full Path: lola-os/python/lola/core/agent.py
"""

logger = setup_logger("lola.core.agent")

class BaseAgent(abc.ABC):
    """BaseAgent: Abstract base for LOLA agents, with LLM, graph, and memory. Does Not implement run—subclass for templates."""

    def __init__(self, model: Optional[str] = None, tools: List[Any] = None):
        """
        Initialize BaseAgent with model, tools, and default graph/memory.

        Args:
            model: LLM model for proxy (loads from config if None).
            tools: List of tools to bind (e.g., phase 5 onchain/web).

        Does Not: Execute workflow—call run() in subclass.
        """
        config = load_config()
        self.model = model or config.llm_model
        self.llm_proxy = LLMProxy(self.model)
        self.memory = ConversationMemory(self.llm_proxy)
        self.tools = tools or []
        self.graph = LOLAStateGraph()
        logger.info("BaseAgent init", extra={"model": self.model, "tools": len(self.tools)})

    def call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Calls LLM via proxy with prompt for reasoning/reflection.

        Args:
            prompt: Input prompt string.
            max_tokens: Max output tokens (default: 1000).

        Returns:
            Response content string.

        Does Not: Add to state—return raw for graph/memory use.
        """
        response = self.llm_proxy.complete(prompt, max_tokens=max_tokens)
        logger.debug("LLM call", extra={"prompt_len": len(prompt), "response_len": len(response)})
        return response

    @abc.abstractmethod
    def run(self, query: str) -> State:
        """
        Abstract method to execute agent's task via graph.

        Args:
            query: User query string.

        Returns:
            Final State with messages/tool_results/entities.

        Does Not: Bind tools—call bind_tools() before run.
        """
        pass

    def bind_tools(self, tools: List[Any]) -> None:
        """
        Binds tools to agent for graph node use.

        Args:
            tools: List of tools (e.g., phase 5 base/onchain).

        Does Not: Validate tool signatures—assume compatible with state.
        """
        self.tools.extend(tools)
        logger.info("Tools bound", extra={"added": len(tools), "total": len(self.tools)})

__all__ = ["BaseAgent"]