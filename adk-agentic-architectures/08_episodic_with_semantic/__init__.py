"""
Exposes the root_agent for the ADK Episodic + Semantic Memory agent.
"""

from types import SimpleNamespace
from .episodic_semantic_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
