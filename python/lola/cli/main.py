# Standard imports
import click

# Third-party imports
# None

# Local imports
# None (commands imported in group)

"""
File: CLI entry point for LOLA OS with command groups.

Purpose: Provides top-level CLI (lola) with subcommands (create/run) for agent management.
How: Uses Click group to organize commands, with version/help.
Why: Developer-friendly interface in V1 for scaffolding/running agents without code.
Full Path: lola-os/python/lola/cli/main.py
"""

@click.group()
@click.version_option("1.0.0")
def cli():
    """LOLA OS CLI: Scaffold and run on-chain AI agents."""
    pass

# Inline: Import/add commands (lazy to avoid circular)
from .commands.create import create
from .commands.run import run
cli.add_command(create)
cli.add_command(run)

__all__ = ["cli"]