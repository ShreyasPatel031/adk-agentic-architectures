"""
Exposes the root_agent for the ADK ReAct agent.
"""

from types import SimpleNamespace
from .react_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
