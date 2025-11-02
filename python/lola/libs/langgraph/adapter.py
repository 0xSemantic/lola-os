# Standard imports
import typing as tp
from typing import Optional

# Third-party imports
from langgraph.graph import StateGraph, END, START

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.libs.litellm.proxy import LLMProxy

"""
File: Adapter for LangGraph with LOLA-specific supervision extensions.

Purpose: Extends LangGraph StateGraph for agent workflows with built-in turn limits and reflection nodes.
How: Adds methods for supervision (e.g., add_turn_limit, add_reflection_node using LLMProxy for reflection).
Why: Fixes common LangGraph issues like infinite loops/context loss in V1 agents, ensuring reliable orchestration.
Full Path: lola-os/python/lola/libs/langgraph/adapter.py
"""

logger = setup_logger("lola.langgraph")

class SupervisedStateGraph(StateGraph):
    """SupervisedStateGraph: LangGraph extension with LOLA supervision. Does NOT handle state—use core/state.py."""

    def __init__(self, state_schema: tp.Any, config: Optional[tp.Dict] = None):
        """
        Initialize SupervisedStateGraph with state schema and optional config.

        Args:
            state_schema: Pydantic model or dict for state (e.g., core/state.py State).
            config: Optional dict for LLM model/turn limit (loads from utils/config if None).

        Does Not: Compile graph—call compile() after adding nodes/edges.
        """
        super().__init__(state_schema)
        self.config = config or load_config().model_dump()
        self.llm_proxy = LLMProxy(self.config["llm_model"])
        self.turn_count = 0
        self.max_turns = self.config.get("max_turns", 10)
        logger.info("SupervisedStateGraph init", extra={"max_turns": self.max_turns})

    def add_turn_limit_node(self, name: str = "turn_limit") -> "SupervisedStateGraph":
        """
        Adds a node to enforce turn limits.

        Args:
            name: Node name (default: "turn_limit").

        Returns:
            Self for chaining.

        Does Not: Handle reflection—use add_reflection_node().
        """
        def turn_limit_node(state: tp.Dict) -> tp.Dict:
            self.turn_count += 1
            if self.turn_count >= self.max_turns:
                logger.warning("Turn limit reached", extra={"turns": self.turn_count})
                return {"next": END, "reason": "max_turns_exceeded"}
            return state
        self.add_node(name, turn_limit_node)
        logger.debug("Turn limit node added", extra={"node": name})
        return self

    def add_reflection_node(self, name: str = "reflection", reflect_prompt: str = "Reflect on this step: {state}") -> "SupervisedStateGraph":
        """
        Adds a reflection node using LLMProxy for self-critique.

        Args:
            name: Node name (default: "reflection").
            reflect_prompt: Prompt template for reflection.

        Returns:
            Self for chaining.

        Does Not: Enforce limits—use add_turn_limit_node().
        """
        def reflection_node(state: tp.Dict) -> tp.Dict:
            prompt = reflect_prompt.format(state=str(state))
            reflection = self.llm_proxy.complete(prompt)
            state["reflection"] = reflection
            logger.info("Reflection added", extra={"reflection_len": len(reflection)})
            return state
        self.add_node(name, reflection_node)
        logger.debug("Reflection node added", extra={"node": name, "prompt": reflect_prompt})
        return self

    def compile_supervised(self) -> tp.Any:
        """
        Compiles graph with supervision edges (e.g., turn_limit -> reflection -> END).

        Returns:
            Compiled graph.

        Does Not: Add custom nodes—call add_* methods first.
        """
        # Inline: Default supervision edges for safety, including START entrypoint
        if "turn_limit" in self.nodes:
            self.add_edge(START, "turn_limit")
            next_node = "reflection" if "reflection" in self.nodes else END
            self.add_edge("turn_limit", next_node)
            if "reflection" in self.nodes:
                self.add_edge("reflection", END)
        compiled = super().compile()
        logger.info("Supervised graph compiled", extra={"nodes": len(self.nodes)})
        return compiled

__all__ = ["SupervisedStateGraph"]