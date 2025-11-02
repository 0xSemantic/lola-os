# python/lola/agents/react.py
# Standard imports
import asyncio
from typing import List, Dict, Any
import json 

# Third-party imports
# None (uses phase 2 litellm)

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.base import BaseTool
from lola.core.agent import BaseAgent 

"""
File: ReAct agent template for LOLA OS with reasoning/action loop.

Purpose: Implements ReAct (Reason-Act) pattern for agents, alternating LLM reasoning and tool action until resolution.
How: Extends core BaseAgent with run loop: LLM reason → parse action → execute tool → observe → repeat; uses memory for context.
Why: Enables dynamic tool use in V1 (e.g., web_crawl + onchain), with verifiable reasoning chain in state.
Full Path: lola-os/python/lola/agents/react.py
"""

logger = setup_logger("lola.agents.react")

class ReActAgent(BaseAgent):
    """ReActAgent: ReAct template with loop for reasoning/action. Does NOT limit turns—use graph for supervision."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None):
        """
        Init ReActAgent with model and tools.

        Args:
            model: LLM model (default config).
            tools: List of BaseTool for action.

        Does Not: Auto-bind—call bind_tools.
        """
        super().__init__(model, tools)
        self.memory = ConversationMemory(self.llm_proxy)

    def run(self, query: str) -> State:
        """
        Runs ReAct loop: Reason → Act → Observe until done.

        Args:
            query: Initial user query.

        Returns:
            Final State with messages (reasoning/actions) and tool_results.

        Does Not: Handle infinite loop—add max_turns in subclass.
        """
        state = State(messages=[{"role": "user", "content": query}])
        max_turns = 5  # Inline: Configurable limit
        for turn in range(max_turns):
            # Reason with LLM
            reasoning_prompt = self._build_reason_prompt(state)
            reasoning = self.call_llm(reasoning_prompt)
            state.messages.append({"role": "assistant", "content": f"Reasoning: {reasoning}"})
            # Parse action
            action = self._parse_action(reasoning)
            if action.get("action") == "finish":
                state.messages.append({"role": "assistant", "content": f"Final answer: {action.get('output', '')}"})
                break
            # Execute tool
            tool_name = action.get("tool")
            tool_args = action.get("tool_input", {})
            if tool_name not in [t.name for t in self.tools]:
                state.tool_results[tool_name] = "Tool not found"
                continue
            tool = next(t for t in self.tools if t.name == tool_name)
            tool_result = tool.execute(**tool_args)
            state.tool_results[tool_name] = tool_result
            state.messages.append({"role": "tool", "content": f"Observation: {tool_result}"})
            logger.info("ReAct turn", extra={"turn": turn + 1, "action": tool_name, "result_type": type(tool_result).__name__})
        return state

    def _build_reason_prompt(self, state: State) -> str:
        """Builds prompt for reasoning based on state/history."""
        history = self.memory.summarize_history(state.messages)
        tools_desc = "\n".join([f"{t.name}: {t.description}" for t in self.tools])
        return f"""History: {history}
Tools available:
{tools_desc}
Query: {state.messages[-1]['content']}
Reason step-by-step, then output in this format:
Thought: [your reasoning]
Action: [tool name or 'finish' if done]
Input: [JSON dict for tool input if Action is tool, or output if finish]"""

    def _parse_action(self, reasoning: str) -> Dict[str, Any]:
        """Parses LLM reasoning for action/tool_input or finish/output."""
        lines = reasoning.split("\n")
        action = {}
        for line in lines:
            if line.startswith("Thought:"):
                action["thought"] = line.split(":", 1)[1].strip()
            elif line.startswith("Action:"):
                action["action"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("Input:"):
                input_str = line.split(":", 1)[1].strip()
                if action["action"] == "finish":
                    action["output"] = input_str
                else:
                    try:
                        action["tool_input"] = json.loads(input_str)
                    except json.JSONDecodeError:
                        action["tool_input"] = {}
        if "action" in action and action["action"] != "finish":
            action["tool"] = action["action"]
            action["action"] = "tool"
        return action

__all__ = ["ReActAgent"]