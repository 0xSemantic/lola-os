# Standard imports
import json
from pathlib import Path

# Third-party imports
# (none)

# Local imports
from lola.core.state import State
from lola.core.memory import StateManager

"""
File: Standalone demonstration of State creation and persistence.

Purpose: Show developers how to initialise, mutate and save a State object.
How: Uses the core State and StateManager classes; writes JSON to disk.
Why: Gives a zero-dependency entry point to verify the Phase-1 foundation.
Full Path: lola-os/examples/version_1/foundation_standalone/agent.py
"""

def main() -> None:
    """
    Entry point – creates a State, adds data, persists it, then prints.

    Does Not: Load the file (left as an exercise in README).
    """
    # Inline: Initialise a realistic starting state
    state = State(
        messages=[{"role": "user", "content": "Hello, LOLA OS!"}],
        tools_results={"example_tool": "demo_result"},
        reflection="Initial reflection"
    )

    # Inline: Persist to a deterministic location
    output_path = Path(__file__).with_name("example_state.json")
    StateManager.save(state, output_path)

    # Inline: Pretty-print for immediate feedback
    print("State saved to:", output_path)
    print(json.dumps(state.dict(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

__all__ = ["main"]