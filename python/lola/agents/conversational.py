# Standard imports
import typing as tp

# Third-party imports
# None

# Local imports
from lola.core.state import State
from lola.core.graph import StateGraph
from lola.core.memory import ConversationMemory
from lola.core.agent import BaseAgent

"""
File: Conversational agent template for context-aware interactions.

Purpose: Maintains conversation history for coherent responses.
How: Uses ConversationMemory to seed State, processes via graph.
Why: Enables context retention for dialogue in V1.
Full Path: lola-os/python/lola/agents/conversational.py
"""

class ConversationalAgent(BaseAgent):
    """ConversationalAgent: Retains context for dialogue. Does NOT call real LLMs/tools."""

    def __init__(
        self,
        model: str = "mock-model",
        tools: tp.List[tp.Any] = None,
        graph: tp.Optional[StateGraph] = None,
        memory: tp.Optional[ConversationMemory] = None
    ):
        """
        Initializes Conversational agent with memory.

        Args:
            model: LLM model name (stubbed).
            tools: List of tools (stubbed or real).
            graph: StateGraph (defaults to conversational).
            memory: ConversationMemory for context (defaults to new).

        Does Not: Connect to external APIs.
        """
        super().__init__(model, tools, graph)
        self.memory = memory or ConversationMemory()
        # Inline: Build conversational graph if none provided
        if not graph:
            self.graph = self._build_conversational_graph()

    def _build_conversational_graph(self) -> StateGraph:
        """
        Builds the conversational workflow graph.

        Returns:
            StateGraph with context-aware response node.

        Does Not: Execute the graph.
        """
        graph = StateGraph(State)

        def respond(state: State) -> State:
            # Inline: Combine memory and current query
            context = "\n".join(msg["content"] for msg in self.memory.retrieve())
            prompt = f"Context: {context}\nQuery: {state.messages[-1]['content']}"
            response = self.call_llm(prompt)
            state.messages.append({"role": "assistant", "content": response})
            # Inline: Update memory with new query and response
            self.memory.append(state.messages[-2])  # User query
            self.memory.append({"role": "assistant", "content": response})
            return state

        graph.add_node("respond", respond)
        graph.set_entry_point("respond")
        graph.add_edge("respond", "__end__")
        return graph

    async def run(self, query: str) -> State:
        """
        Executes the conversational workflow.

        Args:
            query: User input or query.

        Returns:
            Final State with response.

        Does Not: Use real LLMs/tools.
        """
        # Inline: Initialize state with query and memory
        self.state = State(messages=self.memory.retrieve() + [{"role": "user", "content": query}])
        # Inline: Run graph with supervision
        final_state = await self.graph.execute(self.state)
        return final_state

__all__ = ["ConversationalAgent"]