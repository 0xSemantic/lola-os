# ReAct Agent Demo

**Overview**: Runs a ReActAgent with a mock query to demonstrate reasoning-action loops.

**Prerequisites**: Poetry, Python 3.12+, lola-os dependencies (`poetry install`).

**Setup**:
```bash
cd examples/version_1/agents_standalone
poetry shell
```

**Run**:
```bash
poetry run python agent.py
```

**Expected Output**:
```
=== Final State ===
User: Solve a puzzle
System: Stub LLM response for prompt: Reason about: Solve a puzzle...
System: Action taken
Reflection: None
```

**Exercise**: Modify `config={"recursion_limit": 3}` and observe additional loops.

**Troubleshooting**:
- ImportError? Run `poetry install`.
- Path issues? Verify file location.
