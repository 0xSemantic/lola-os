# Foundation Combined Example

## Overview
Integrates Graph execution with Memory for a simple workflow. Why: Shows orchestration backbone.

## Prerequisites
Same as standalone.

## Setup
Same as standalone.

## Run
`python agent.py`

Expected Output: Final State with appended message.

## Walkthrough
- Create Graph, add node/edges.
- Use ConversationMemory to init State.
- Async execute and print.
- Exercise: Add reflection_threshold=1 to graph, rerun to see reflection. Create a loop (add_edge('process', 'process')) and test max_turns halt.

## Troubleshooting
Asyncio error: Ensure Python 3.12+.
No output: Check imports.

## Next Steps
Build on this in Phase 2 agents.

## Files
Same structure as standalone.