# Standard imports
import typing as tp

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field

# Local imports
# None for this file

"""
File: Defines the State model for LOLA OS workflows.

Purpose: Provides a validated, serializable structure for passing data between graph nodes and agents.
How: Uses Pydantic for type validation and serialization to ensure consistent state management.
Why: Ensures reliability in agent orchestration by preventing invalid data propagation, foundational for V1.
Full Path: lola-os/python/lola/core/state.py
"""

class State(BaseModel):
    """State: Serializable model for workflow data. Does NOT handle persistence, use StateManager."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    messages: tp.List[tp.Dict[str, str]] = Field(default_factory=list, description="List of conversation messages")
    tools_results: tp.Dict[str, tp.Any] = Field(default_factory=dict, description="Results from tool executions")
    reflection: tp.Optional[str] = Field(None, description="Optional reflection note from supervision")

__all__ = ["State"]