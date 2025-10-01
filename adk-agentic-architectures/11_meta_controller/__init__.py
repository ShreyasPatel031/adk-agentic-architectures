"""
Exposes the root_agent for the ADK Meta-Controller agent.
"""

from types import SimpleNamespace
from .meta_controller_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
