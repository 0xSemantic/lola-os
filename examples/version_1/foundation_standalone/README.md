# Foundation Standalone Example

## Overview
Demonstrates basic State creation, modification, and persistence. Why: Tests core data handling without dependencies.

## Prerequisites
- Python 3.12+ and Poetry installed.
- Run `poetry install` in lola-os root.

## Setup
1. `cd examples/version_1/foundation_standalone`
2. `poetry shell` (from root, or ensure env active).

## Run
`python agent.py`

Expected Output: Printed State dict and saved 'example_state.json'.

## Walkthrough
- Imports: From lola.core.
- Create State with message and tool result.
- Save to JSON via StateManager.
- Exercise: Load the saved file with StateManager.load('example_state.json') and print it. Add a reflection field.

## Troubleshooting
- ImportError: Ensure poetry deps installed.
- File not found: Check current dir.
- Validation error: State fields must match types.

## Next Steps
Extend with Graph in combined example.

## Files
- agent.py: Main script.
- config.yaml: Empty (none needed).
- requirements.txt: Empty (use root).
- .env.sample: Empty (none needed).
- README.md: This guide.