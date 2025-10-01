"""
Exposes the root_agent for the ADK PEV agent.
"""

from types import SimpleNamespace
from .pev_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
