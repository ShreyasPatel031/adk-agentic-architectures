"""
Exposes the root_agent for the ADK Blackboard agent.
"""

from types import SimpleNamespace
from .blackboard_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
