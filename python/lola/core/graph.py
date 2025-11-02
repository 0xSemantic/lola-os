# python/lola/core/graph.py
# Standard imports
import asyncio
from typing import Dict, Any, Optional, Callable

# Third-party imports
from langgraph.graph import END

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.libs.langgraph.adapter import SupervisedStateGraph
from lola.core.state import State

"""
File: LangGraph extension for LOLA agent orchestration with async execution and supervision.

Purpose: Builds and executes async workflows for agents, integrating supervision (turns/reflection via phase 2 adapter) and config-driven limits.
How: Extends SupervisedStateGraph with add_node/edge/compile/execute(async for parallel), using LLM for reflection in supervision.
Why: Enables reliable, verifiable agent reasoning in V1, with async for concurrency and reflection to prevent loops/context loss.
Full Path: lola-os/python/lola/core/graph.py
"""

logger = setup_logger("lola.core.graph")

class LOLAStateGraph(SupervisedStateGraph):
    """LOLAStateGraph: Core graph for agent workflows with async execution. Does NOT bind tools—use agent.bind_tools()."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LOLAStateGraph with optional config for limits/LLM.

        Args:
            config: Dict for max_turns/llm_model (loads from utils/config if None).

        Does Not: Add nodes/edges—call add_node/add_edge after init.
        """
        config = config or load_config().model_dump()
        super().__init__(State, config)
        logger.info("LOLAStateGraph init", extra={"max_turns": self.max_turns, "model": config.get("llm_model")})

    def add_node(self, name: str, func: Callable[[State], State]) -> "LOLAStateGraph":
        """
        Adds a node to the graph for workflow step.

        Args:
            name: Unique node name.
            func: Callable taking/returning State (async/sync OK).

        Returns:
            Self for chaining.

        Does Not: Add edges—use add_edge after.
        """
        super().add_node(name, func)
        logger.debug("Node added", extra={"name": name, "func_type": "async" if asyncio.iscoroutinefunction(func) else "sync"})
        return self

    def add_edge(self, from_node: str, to_node: str) -> "LOLAStateGraph":
        """
        Adds an edge from node to node/END.

        Args:
            from_node: Source node name.
            to_node: Target node name or END.

        Returns:
            Self for chaining.

        Does Not: Validate cycles—LangGraph checks on compile.
        """
        super().add_edge(from_node, to_node)
        logger.debug("Edge added", extra={"from": from_node, "to": to_node})
        return self

    async def execute(self, initial_state: Dict[str, Any]) -> State:
        """
        Async executes the graph with initial state, compiling if needed.

        Args:
            initial_state: Dict to initialize State (e.g., {"messages": [...]}).

        Returns:
            Final State after workflow.

        Does Not: Handle interruptions—use LangGraph interrupt param if needed.
        """
        compiled = self.compile_supervised()
        final_dict = await compiled.ainvoke(initial_state)
        final_state = State.model_validate(final_dict)
        logger.info("Graph executed", extra={"steps": len(final_state.messages), "timestamp": final_state.timestamp})
        return final_state

__all__ = ["LOLAStateGraph"]