"""
Exposes the root_agent for the ADK Planning agent.
"""

from types import SimpleNamespace
from .planning_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
