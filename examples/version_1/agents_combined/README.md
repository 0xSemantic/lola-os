
# Conversational Agent Demo

**Overview**: Runs a ConversationalAgent with memory to show context retention.

**Prerequisites**: Same as above.

**Setup**:
```bash
cd examples/version_1/agents_combined
poetry shell
```

**Run**:
```bash
poetry run python agent.py
```

**Expected Output**:
```
=== Final State ===
User: Hi, I'm Bob
User: What's my name?
Assistant: Stub LLM response for prompt: Context: Hi, I'm Bob\nQuery: What's my name?...
Reflection: None
```

**Exercise**: Add another memory entry and query to test context growth.

**Troubleshooting**: Same as above.