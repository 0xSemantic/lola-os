# CLI Standalone Example: Scaffold and Run Basic Agent

## Overview
This example shows LOLA CLI basics: Create a project, run with query. Why? To onboard devs to CLI as entry point.

## Prerequisites
- Poetry/LOLA installed (poetry install in root).
- Gemini key (optional for real LLM).

## Setup
1. From root: poetry shell.
2. Run create: lola create my_agent --template react.

## Run
cd my_agent && lola run --query "Hello world"
- Expected: Agent response/state.

## Walkthrough
- create: Copies template/agent.py etc.
- run: Loads agent.py, calls run("query").
- Exercise: Edit agent.py to add tool, rerun.

## Troubleshooting
- No lola? poetry install again.
- Key error? Set GEMINI_API_KEY in .env.

## Best Practices
- Use --template for type.
- Customize README for project.

## Next Steps
- Add EVM: Bind onchain tools.
- Files: agent.py (main), etc.