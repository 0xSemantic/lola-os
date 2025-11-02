# Tutorial: Build Your First "Agent" Stub (Phase 1 Utils)

1. Use utils_combined/agent.py as base.
2. Add: `config = load_config()` for model/key.
3. Log: `logger.debug("Agent init", extra={"model": config.llm_model})`.
4. Run/test: See extras in log.

Extend (Phase 6): Bind real agent.

Exercise: Add RPC log—`extra["rpcs"] = config.evm_rpcs.keys()`.

# Tutorial: First Agent with Core (Phase 3)

1. Import: `from lola.core import BaseAgent, State`
2. Class: `class MyAgent(BaseAgent): def run(self, query): response = self.call_llm(query); return State(messages=[...])`
3. Run: `agent = MyAgent(); state = agent.run("Query")`
4. Extend: Add self.graph = LOLAStateGraph(); self.graph.add_node("reason", self.reason_node); state = asyncio.run(self.graph.execute(initial))`

Exercise: Use self.memory.summarize_history(state.messages) → Print summary.


# Tutorial: First Agent Template (Phase 6)

1. Import: `from lola.agents import ReActAgent, PlanExecuteAgent; from lola.tools import WebCrawlTool`
2. Init: `agent = ReActAgent(); agent.bind_tools([WebCrawlTool()])`
3. Run: `state = agent.run("Research Alice's balance")`
4. Extend: Switch to PlanExecuteAgent for structured; Conversational for chat.

Exercise: Bind TransactTool, run "Plan and transfer 1 ETH"—check sim.