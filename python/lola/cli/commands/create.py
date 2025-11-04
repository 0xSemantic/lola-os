# Standard imports
import os
import shutil
from pathlib import Path
from typing import Optional

# Third-party imports
import click

# Local imports
from lola.utils.logging import setup_logger

"""
File: CLI create command for scaffolding agent projects.

Purpose: Generates ready-to-run agent folder from templates (react/plan_execute/conversational).
How: Copies template files (agent.py/config/.env.sample/README), customizes if needed, logs; prompts for overwrite if exists.
Why: Zero-mastery onboarding in V1—devs start building agents instantly.
Full Path: lola-os/python/lola/cli/commands/create.py
"""

logger = setup_logger("lola.cli.create")

@click.command()
@click.argument("project_name", type=str)
@click.option("--template", default="react", type=click.Choice(["react", "plan_execute", "conversational"]), help="Agent template type.")
@click.option("--target-dir", default=None, type=str, help="Target directory for project (default: current dir).")
@click.option("--templates-dir", default=None, type=str, help="Directory for templates (default: templates/ in root).")
@click.option("--force", is_flag=True, help="Force overwrite if project exists (non-interactive).")
def create(project_name: str, template: Optional[str] = "react", target_dir: Optional[str] = None, templates_dir: Optional[str] = None, force: bool = False):
    """
    Scaffolds a new agent project folder.

    Args:
        project_name: Folder name for scaffolded project.
        template: Agent type (react/plan_execute/conversational; default react).
        target_dir: Directory to create project in (optional).
        templates_dir: Directory containing templates (optional).
        force: Overwrite existing without prompt.
    """
    root = Path(target_dir or os.getcwd())
    templates_base = Path(templates_dir or Path(__file__).parent.parent.parent.parent.parent / "templates")
    template_dir = templates_base / template

    if not template_dir.exists():
        logger.error("Template not found", extra={"template_name": template, "template_path": str(template_dir)})
        raise click.ClickException(f"Template '{template}' not found at {template_dir}.")

    project_dir = root / project_name

    if project_dir.exists():
        if force or click.confirm(f"Project '{project_name}' exists at {project_dir}. Overwrite?", default=False):
            shutil.rmtree(project_dir)
            logger.info("Existing project overwritten", extra={"project_path": str(project_dir)})
        else:
            logger.info("Project creation skipped", extra={"project_path": str(project_dir)})
            raise click.ClickException(f"Project '{project_name}' exists—skipped.")

    shutil.copytree(template_dir, project_dir)
    logger.info("Project scaffolded", extra={"project_name": project_name, "template_name": template, "file_count": len(list(project_dir.iterdir()))})
    click.echo(f"Project '{project_name}' created with {template} template in {project_dir}. Run: cd {project_dir} && poetry run python agent.py")

__all__ = ["create"]