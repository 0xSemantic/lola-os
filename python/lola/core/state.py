# Standard imports
from typing import Dict, Any, Optional, List
from datetime import datetime

# Third-party imports
from pydantic import BaseModel, field_validator, ValidationError

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Pydantic state model for LOLA agent workflows.

Purpose: Defines structured, validated state for graph orchestration, with serialization for memory persistence.
How: BaseModel with messages/tool_results/timestamp fields, validators for length/content, config for defaults like max_messages.
Why: Ensures consistent, verifiable state passing in V1 agents, preventing context overflow and enabling JSON memory.
Full Path: lola-os/python/lola/core/state.py
"""

logger = setup_logger("lola.core.state")

class State(BaseModel):
    """State: Pydantic model for agent/graph state. Does NOT persist—use memory.py for JSON save/load."""

    messages: List[Dict[str, str]] = []
    """List of {'role': 'user/system/assistant', 'content': str} messages."""

    tool_results: Dict[str, Any] = {}
    """Dict of tool name → result (e.g., {'web_crawl': {'content': str}})."""

    timestamp: Optional[str] = None
    """ISO timestamp for state snapshot."""

    def __init__(self, **data):
        """
        Initialize State with optional config defaults for validation (e.g., max_messages).

        Args:
            **data: Field values (messages, tool_results).

        Does Not: Auto-timestamp—set manually or on save.
        """
        config = load_config()
        data["config"] = config  # Pass config for validator access
        super().__init__(**data)
        self.timestamp = datetime.now().isoformat()

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v, info):
        """Validate messages length and content using config max."""
        config_data = info.data.get("config", load_config()).model_dump()
        max_len = config_data.get("max_messages", 50)
        if len(v) > max_len:
            raise ValueError(f"Messages exceed {max_len}; trim history.")
        for msg in v:
            if not msg.get("content", "").strip():
                raise ValueError("Message content cannot be empty.")
        return v

    def to_json(self) -> str:
        """
        Serializes state to JSON string for persistence.

        Returns:
            JSON string.

        Does Not: Compress—raw model_dump_json.
        """
        log_data = self.model_dump(exclude=["timestamp", "config"])
        logger.debug("State serialized", extra={"keys": list(log_data.keys()), "messages_len": len(self.messages)})
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "State":
        """
        Deserializes JSON to State, validating with config.

        Args:
            json_str: JSON string.

        Returns:
            Validated State.

        Does Not: Handle malformed JSON—raises on parse error.
        """
        try:
            state = cls.model_validate_json(json_str)
            config = load_config()
            state.model_validate({"config": config})  # Re-validate with current config
            logger.debug("State deserialized", extra={"messages_len": len(state.messages), "timestamp": state.timestamp})
            return state
        except ValidationError as e:
            logger.error("State validation failed on load", extra={"error": str(e)})
            raise ValueError(f"Invalid state file: {e}") from e

__all__ = ["State"]