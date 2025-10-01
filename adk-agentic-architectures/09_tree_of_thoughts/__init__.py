"""
Exposes the root_agent for the ADK Tree-of-Thoughts agent.
"""

from types import SimpleNamespace
from .tree_of_thoughts_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
