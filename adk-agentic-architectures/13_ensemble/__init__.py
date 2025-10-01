"""
Exposes the root_agent for the ADK Ensemble agent.
"""

from types import SimpleNamespace
from .ensemble_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
