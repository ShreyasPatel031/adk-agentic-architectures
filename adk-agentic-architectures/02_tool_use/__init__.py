"""
Exposes the root_agent for the ADK Tool Use agent.
"""

from types import SimpleNamespace
from .tool_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)