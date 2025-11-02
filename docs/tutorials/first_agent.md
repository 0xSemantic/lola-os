# Tutorial: First Agent with Core (Phase 3)

1. Import: `from lola.core import BaseAgent, State`
2. Class: `class MyAgent(BaseAgent): def run(self, query): response = self.call_llm(query); return State(messages=[...])`
3. Run: `agent = MyAgent(); state = agent.run("Query")`
4. Extend: Add self.graph = LOLAStateGraph(); self.graph.add_node("reason", self.reason_node); state = asyncio.run(self.graph.execute(initial))`

Exercise: Use self.memory.summarize_history(state.messages) → Print summary.