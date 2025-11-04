# Standard imports
import asyncio
import importlib.util
from pathlib import Path
from typing import Any

# Third-party imports
import click

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State

"""
File: CLI run command for executing agent scripts.

Purpose: Loads/runs user agent.py with query, outputs state/response.
How: Dynamically imports agent.py as module, instantiates Agent class, calls run async, logs state.
Why: Seamless execution in V1—devs test agents via CLI without boilerplate.
Full Path: lola-os/python/lola/cli/commands/run.py
"""

logger = setup_logger("lola.cli.run")

@click.command()
@click.argument("script_path", type=click.Path(exists=True), default="agent.py")
@click.option("--query", default="Test query", help="Input query for agent.run().")
def run(script_path: str, query: str):
    """
    Runs an agent script (e.g., agent.py) with query.

    Args:
        script_path: Path to agent script (default agent.py).
        query: Query string for agent (default "Test query").

    Does Not: Handle non-Agent classes—assumes 'Agent' in script.
    """
    spec = importlib.util.spec_from_file_location("user_agent", Path(script_path).absolute())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    AgentClass = getattr(module, "Agent", None) or getattr(module, "ReActAgent", None)  # Fallback to common
    if not AgentClass:
        raise click.ClickException("No Agent class in script.")
    agent = AgentClass()
    # Handle both sync and async run methods
    run_method = agent.run
    if asyncio.iscoroutinefunction(run_method):
        state: State = asyncio.run(run_method(query))
    else:
        state: State = run_method(query)
    logger.info("Agent run complete", extra={"query": query, "messages": len(state.messages)})
    click.echo(f"Response: {state.messages[-1]['content'] if state.messages else 'No output'}\nFull State: {state.model_dump_json(indent=2)}")

__all__ = ["run"]