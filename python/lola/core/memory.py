# Standard imports
import json
from typing import Dict, Any, Optional, List

# Third-party imports
from pydantic import ValidationError

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.libs.litellm.proxy import LLMProxy

"""
File: Memory manager for LOLA agent state persistence and conversation/entity extraction.

Purpose: Provides JSON persistence for State and LLM-based handlers for conversation history/entity extraction.
How: StateManager for load/save JSON, ConversationMemory for LLM extract/summarize using phase 2 proxy.
Why: Enables multi-turn context in V1 agents, with verifiable persistence and sovereign LLM routing.
Full Path: lola-os/python/lola/core/memory.py
"""

logger = setup_logger("lola.core.memory")

class StateManager:
    """StateManager: Simple JSON persistence for State. Does NOT extract entities—use ConversationMemory."""

    @staticmethod
    def save(state: State, file_path: str) -> None:
        """
        Saves State to JSON file for persistence.

        Args:
            state: State to save.
            file_path: Path to JSON file (e.g., "session.json").

        Does Not: Compress or encrypt—raw JSON; use external for security.
        """
        with open(file_path, "w") as f:
            f.write(state.to_json())
        logger.debug("State saved", extra={"path": file_path, "messages_len": len(state.messages)})

    @staticmethod
    def load(file_path: str) -> State:
        """
        Loads State from JSON file, validating on deserializ.

        Args:
            file_path: Path to JSON file.

        Returns:
            Validated State.

        Does Not: Handle missing file—raises FileNotFoundError.
        """
        with open(file_path, "r") as f:
            json_str = f.read()
        try:
            state = State.from_json(json_str)
            logger.debug("State loaded", extra={"path": file_path, "messages_len": len(state.messages)})
            return state
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error("State load failed", extra={"path": file_path, "error": str(e)})
            raise ValueError(f"Invalid state file: {e}") from e

class ConversationMemory:
    """ConversationMemory: LLM-based handlers for history extraction/summarization. Does Not persist—use StateManager."""

    def __init__(self, llm_proxy: Optional[LLMProxy] = None):
        """
        Initialize ConversationMemory with LLM proxy for extraction.

        Args:
            llm_proxy: LLMProxy for LLM calls (loads default if None).

        Does Not: Store history—stateless, pass messages each call.
        """
        self.llm_proxy = llm_proxy or LLMProxy()
        logger.info("ConversationMemory init", extra={"model": self.llm_proxy.model})

    def extract_entities(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extracts entities (names, dates, locations) from messages using LLM.

        Args:
            messages: List of {'role': str, 'content': str}.

        Returns:
            Dict with 'entities': list of extracted items.

        Does Not: Dedupe or categorize—raw LLM output as list.
        """
        prompt = "Extract entities (names, dates, locations) from this conversation as a JSON list: " + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        entities_str = self.llm_proxy.complete(prompt)
        try:
            entities = json.loads(entities_str)
        except json.JSONDecodeError:
            entities = [e.strip() for e in entities_str.split(",") if e.strip()]  # Fallback split
        logger.debug("Entities extracted", extra={"count": len(entities)})
        return {"entities": entities}

    def summarize_history(self, messages: List[Dict[str, str]]) -> str:
        """
        Summarizes conversation history using LLM for context compression.

        Args:
            messages: List of messages.

        Returns:
            Concise summary string.

        Does Not: Include full history—high-level only (max 200 tokens).
        """
        prompt = "Provide a concise summary of this conversation (under 100 words): " + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        summary = self.llm_proxy.complete(prompt, max_tokens=200)
        logger.debug("History summarized", extra={"len": len(summary)})
        return summary

__all__ = ["StateManager", "ConversationMemory"]