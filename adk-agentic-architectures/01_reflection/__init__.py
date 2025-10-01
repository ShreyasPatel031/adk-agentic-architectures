"""
Exposes the root_agent for the ADK Reflection agent.
"""

from types import SimpleNamespace
from .reflection_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
