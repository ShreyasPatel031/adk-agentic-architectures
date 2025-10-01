"""
Exposes the root_agent for the ADK Cellular Automata agent.
"""

from types import SimpleNamespace
from .cellular_automata_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
