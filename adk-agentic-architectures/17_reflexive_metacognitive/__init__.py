"""
Exposes the root_agent for the ADK Reflexive Metacognitive agent.
"""

from types import SimpleNamespace
from .reflexive_metacognitive_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
