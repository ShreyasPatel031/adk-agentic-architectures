"""
Exposes the root_agent for the ADK Mental Loop agent.
"""

from types import SimpleNamespace
from .mental_loop_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
