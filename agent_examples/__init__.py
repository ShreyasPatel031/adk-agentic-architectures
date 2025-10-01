"""
ADK Agent Implementation
A config-driven, agent-agnostic implementation for ADK evaluation tests.
"""

from .default_agent import root_agent

# ADK eval expects: agent_module.agent.root_agent
from types import SimpleNamespace
agent = SimpleNamespace(root_agent=root_agent)
