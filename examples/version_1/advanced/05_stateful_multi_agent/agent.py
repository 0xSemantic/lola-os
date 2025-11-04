import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.web_crawl import WebCrawlTool
from lola.tools.onchain.contract_call import ContractCallTool
from lola.agents.conversational import ConversationalAgent
from lola.agents.react import ReActAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Stateful multi-agent system.
Purpose: Coordinates multiple agents for web and contract tasks.
How: Uses SupervisedStateGraph to orchestrate ConversationalAgent and ReActAgent.
Why: Demonstrates advanced multi-agent coordination in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/05_stateful_multi_agent/agent.py
"""

logger = setup_logger("stateful_multi_agent")

class Agent:
    """Multi-agent system for coordinating web and contract tasks."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize multi-agent system with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        self.memory = ConversationMemory(LLMProxy(model))
        self.conversational = ConversationalAgent(model)
        self.react = ReActAgent(model)
        self.react.tools = [WebCrawlTool(), ContractCallTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("converse", self._converse)
        self.graph.add_node("react", self._react)
        self.graph.set_entry_point("converse")
        self.graph.add_conditional_edge("converse", self._route_to_react)
        logger.info("Multi-agent system initialized", extra={"model": model, "agents": ["conversational", "react"]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run multi-agent workflow for complex tasks.

        Args:
            query: User query string (e.g., "Discuss market trends and check contract 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Multi-agent workflow completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in multi-agent workflow: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Multi-agent workflow failed", extra={"error": str(e)})
        return state

    def _converse(self, state: State) -> State:
        """Handle conversational tasks."""
        state = self.conversational.run(state.messages[-1]["content"], state.messages[:-1])
        return state

    def _react(self, state: State) -> State:
        """Handle ReAct-based tool tasks."""
        state = self.react.run(state.messages[-1]["content"], state.messages[:-1])
        return state

    def _route_to_react(self, state: State) -> str:
        """Route to ReAct agent if tools are needed."""
        prompt = f"Query: {state.messages[-1]['content']}\nShould this use tools? Respond with JSON: {{'route': 'react' or 'finish'}}"
        response = self.conversational.call_llm(prompt)
        try:
            action = json.loads(response)
            return action["route"]
        except json.JSONDecodeError:
            logger.warning("Invalid routing response", extra={"response": response})
            return "finish"

__all__ = ["Agent"]