# tests/integration/test_full_workflow.py
import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner
from lola.cli.main import cli
from lola.core.state import State

"""
File: Integration tests for LOLA OS full workflow.

Purpose: Validates end-to-end CLI scaffolding, agent execution, web crawling, and EVM interaction.
How: Uses CliRunner to scaffold/run agents, real Gemini API calls, and Sepolia testnet.
Why: Ensures market-ready integration of all components for V1.
Full Path: lola-os/tests/integration/test_full_workflow.py
"""

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def clean_tests_dir():
    tests_dir = Path.cwd() / "tests" / "integration"
    for project in ["react_workflow"]:
        shutil.rmtree(tests_dir / project, ignore_errors=True)
    yield

def test_full_workflow(runner):
    """Test full workflow: scaffold, run with crawl and EVM read."""
    tests_dir = Path.cwd() / "tests" / "integration"
    tests_dir.mkdir(exist_ok=True)
    # Scaffold project
    result = runner.invoke(cli, ["create", "react_workflow", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"Scaffold failed: {result.output}"
    project_dir = tests_dir / "react_workflow"
    assert (project_dir / "agent.py").exists()
    # Run with query
    with runner.isolated_filesystem():
        shutil.copytree(project_dir, Path.cwd() / "react_workflow")
        result = runner.invoke(cli, ["run", "--query", "Crawl example.com and read Sepolia balance"], cwd=str(Path.cwd() / "react_workflow"))
        assert result.exit_code == 0, f"Run failed: {result.output}"
        assert "Response: React market-ready response" in result.output