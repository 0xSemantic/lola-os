import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.onchain.contract_call import ContractCallTool
from lola.tools.onchain.transact import TransactTool
from lola.tools.onchain.utils import simulate_call
from lola.agents.plan_execute import PlanExecuteAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Dynamic contract interactor agent.
Purpose: Dynamically plans and executes contract calls and transactions.
How: Uses PlanExecuteAgent with SupervisedStateGraph for contract interactions.
Why: Demonstrates advanced contract workflows in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/02_dynamic_contract_interactor/agent.py
"""

logger = setup_logger("dynamic_contract_interactor")

class Agent(PlanExecuteAgent):
    """Agent for dynamic contract calls and transactions with planning."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [ContractCallTool(), TransactTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("plan", self._plan)
        self.graph.add_node("simulate", self._simulate)
        self.graph.add_node("execute", self._execute)
        self.graph.set_entry_point("plan")
        self.graph.add_edge("plan", "simulate")
        self.graph.add_conditional_edge("simulate", self._should_execute)
        logger.info("Dynamic contract interactor initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run planned workflow for contract interactions.

        Args:
            query: User query string (e.g., "Simulate and execute transfer 0.1 ETH to 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Contract interaction completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in contract interaction: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Contract interaction failed", extra={"error": str(e)})
        return state

    def _plan(self, state: State) -> State:
        """Plan contract interaction steps."""
        prompt = self._build_prompt(state, "plan")
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["plan"] = response
        return state

    def _simulate(self, state: State) -> State:
        """Simulate contract call if needed."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] == "simulate_call":
            result = simulate_call(**action["input"])
            state.messages.append({"role": "tool", "content": result})
            state.tool_results["simulate_call"] = result
        return state

    def _execute(self, state: State) -> State:
        """Execute contract call or transaction."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] in ["contract_call", "transact"]:
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results[action["tool"]] = tool_result
        return state

    def _should_execute(self, state: State) -> str:
        """Determine if execution is needed."""
        action = self._parse_action(state.messages[-1]["content"])
        return "execute" if action["action"] in ["contract_call", "transact"] else None

    def _build_prompt(self, state: State, stage: str) -> str:
        """Build prompt for planning or execution."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools] + ["simulate_call"])
        return f"History: {history}\nStage: {stage}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'simulate_call or contract_call or transact or finish', 'tool': 'tool_name', 'input': {{'contract_address': '0x...', 'function_name': 'balanceOf', 'chain': 'sepolia'}} or {'to': '0x...', 'value': 0.1, 'chain': 'sepolia'} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute selected tool."""
        try:
            for tool in self.tools:
                if tool.name == action["tool"]:
                    return tool.execute(**action["input"])
            return "No valid tool executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"tool": action["tool"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]