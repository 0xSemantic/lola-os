# Standard imports
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

# Third-party imports
# None (uses phase 1/4 for log/validate)

# Local imports
from lola.utils.logging import setup_logger

"""
File: Base tool class for LOLA agents with execute/validate/bind.

Purpose: Abstract base for all tools, handling execution, validation, and binding to agents for V1 workflows.
How: ABC with abstract execute, validate params via config/string, bind to agent tools list for graph use.
Why: Ensures consistent tool interface in V1, sovereignty (config validation), easy extension (subclass for onchain/web).
Full Path: lola-os/python/lola/tools/base.py
"""

logger = setup_logger("lola.tools.base")

class BaseTool(ABC):
    """BaseTool: Abstract base for LOLA tools. Does NOT execute—subclass for specific (e.g., web/onchain)."""

    def __init__(self, name: str, description: str):
        """
        Initialize BaseTool with name/description for agent binding.

        Args:
            name: Tool name (e.g., "web_crawl").
            description: Tool description for LLM prompt.

        Does Not: Validate params—override in subclass.
        """
        self.name = name
        self.description = description
        logger.debug("BaseTool init", extra={"name": name, "description_len": len(description)})

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Executes tool with params.

        Args:
            **kwargs: Tool-specific params (e.g., url for web_crawl).

        Returns:
            Result (str/dict for state.tool_results).

        Does Not: Validate—call validate first.
        """
        pass

    def validate(self, **kwargs) -> Dict[str, bool | str]:
        """
        Validates tool params via basic str check (subclass for custom).

        Args:
            **kwargs: Tool params.

        Returns:
            Dict {"valid": bool, "error": str if invalid}.

        Does Not: Load config—use parent if needed.
        """
        # Inline: Basic str check; subclass for specific (e.g., URL regex)
        if not all(isinstance(v, str) and v.strip() for v in kwargs.values()):
            return {"valid": False, "error": "All params must be non-empty str."}
        logger.debug("Tool validated", extra={"params_count": len(kwargs)})
        return {"valid": True}

    def bind_to_agent(self, agent: Any) -> None:
        """
        Binds tool to agent for graph use.

        Args:
            agent: BaseAgent instance with tools list.

        Does Not: Execute—add to agent.tools list.
        """
        if not hasattr(agent, "tools") or not isinstance(agent.tools, list):
            raise ValueError("Agent must have 'tools' list for binding.")
        agent.tools.append(self)
        logger.info("Tool bound to agent", extra={"tool": self.name, "agent_type": type(agent).__name__})

__all__ = ["BaseTool"]