# Standard imports
# None

# Third-party imports
# None

# Local imports
from .main import cli

"""
File: Package init for LOLA OS CLI.

Purpose: Exports the main CLI group for use as a command-line tool.
How: Defines __all__ for import convenience.
Why: Makes CLI accessible as a module if needed (e.g., for scripting or tests).
Full Path: lola-os/python/lola/cli/__init__.py
"""

__all__ = ["cli"]