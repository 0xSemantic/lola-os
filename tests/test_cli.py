# Standard imports
import shutil
from pathlib import Path
import pytest
from click.testing import CliRunner

# Third-party imports
from unittest.mock import patch

# Local imports
from lola.cli.main import cli
from lola.core.state import State

"""
File: Tests for LOLA CLI (create/run) with scaffolding in project tests/ folder.

Purpose: Validates CLI commands scaffold/run agents with real files/output in project's tests/, preserving for inspection.
How: CliRunner for invoke; uses project's templates; scaffolds in tests/ with unique template-based names; mocks async; cleans before tests.
Why: Ensures market-ready CLI in Phase 7, with >80% coverage, visible artifacts, and no template deletion.
Full Path: lola-os/tests/test_cli.py
"""

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def clean_tests_dir():
    """Clean tests/ scaffolded projects before each test to avoid 'exists' errors."""
    tests_dir = Path.cwd() / "tests"
    for project in ["react_project", "react_run", "react_duplicate", "react_sync"]:
        shutil.rmtree(tests_dir / project, ignore_errors=True)
    yield

@pytest.fixture
def mock_async_run():
    with patch('lola.cli.commands.run.asyncio.run') as mock_run:
        mock_run.return_value = State(messages=[{"role": "assistant", "content": "Mock response"}])
        yield mock_run

def test_create_files(runner):
    """Test CLI create command scaffolds correct files in tests/."""
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    result = runner.invoke(cli, ["create", "react_project", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"Create failed: {result.output}"
    project_dir = tests_dir / "react_project"
    assert project_dir.exists(), "Project directory not created"
    assert (project_dir / "agent.py").exists(), "agent.py missing"
    assert (project_dir / "config.yaml").exists(), "config.yaml missing"
    assert (project_dir / ".env.sample").exists(), ".env.sample missing"
    assert (project_dir / "README.md").exists(), "README.md missing"

def test_run_output(runner, mock_async_run):
    """Test CLI run command executes agent and outputs state."""
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    result = runner.invoke(cli, ["create", "react_run", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"Create failed: {result.output}"
    with runner.isolated_filesystem():
        # Copy project to temp dir for run
        temp_dir = Path.cwd()
        shutil.copytree(tests_dir / "react_run", temp_dir / "react_run")
        result = runner.invoke(cli, ["run", "--query", "CLI test"], cwd=str(temp_dir / "react_run"))
        assert result.exit_code == 0, f"Run failed: {result.output}"
        assert "Response: Mock response" in result.output, "Expected response not in output"
        assert "Full State:" in result.output, "State dump missing"
        mock_async_run.assert_called()

def test_create_edge_existing(runner):
    """Test CLI create fails if project exists (non-force)."""
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    result = runner.invoke(cli, ["create", "react_duplicate", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"First create failed: {result.output}"
    result = runner.invoke(cli, ["create", "react_duplicate", "--template", "react", "--target-dir", str(tests_dir)])
    assert result.exit_code != 0, "Create should fail on existing project without --force"
    assert "exists—skipped" in result.output, "Expected skip message not found"
    # Test overwrite with --force
    result = runner.invoke(cli, ["create", "react_duplicate", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"Overwrite failed: {result.output}"
    assert "overwritten" in result.output, "Expected overwritten message not found"

def test_run_edge_invalid_script(runner):
    """Test CLI run fails on nonexistent script."""
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", "nonexistent.py"])
        assert result.exit_code != 0, "Run should fail on nonexistent script"
        assert "Path 'nonexistent.py' does not exist" in result.output, "Expected error message not found"

def test_run_sync_agent(runner):
    """Test CLI run handles sync agent run method."""
    tests_dir = Path.cwd() / "tests"
    tests_dir.mkdir(exist_ok=True)
    result = runner.invoke(cli, ["create", "react_sync", "--template", "react", "--target-dir", str(tests_dir), "--force"])
    assert result.exit_code == 0, f"Create failed: {result.output}"
    with runner.isolated_filesystem():
        # Copy project to temp dir for run
        temp_dir = Path.cwd()
        shutil.copytree(tests_dir / "react_sync", temp_dir / "react_sync")
        result = runner.invoke(cli, ["run", "--query", "Sync test"], cwd=str(temp_dir / "react_sync"))
        assert result.exit_code == 0, f"Sync run failed: {result.output}"
        assert "Response: React market-ready response to Sync test" in result.output, "Expected sync response not found"