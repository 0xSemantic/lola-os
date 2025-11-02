# agents/__init__.py remains the same
from lola.core.agent import BaseAgent
from .react import ReActAgent
from .plan_execute import PlanExecuteAgent
from .conversational import ConversationalAgent

__all__ = ["BaseAgent", "ReActAgent", "PlanExecuteAgent", "ConversationalAgent"]