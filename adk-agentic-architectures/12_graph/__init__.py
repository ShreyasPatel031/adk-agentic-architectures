"""
Exposes the root_agent for the ADK Graph agent.
"""

from types import SimpleNamespace
from .graph_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
