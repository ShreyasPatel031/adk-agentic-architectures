"""
Exposes the root_agent for the ADK Dry Run agent.
"""

from types import SimpleNamespace
from .dry_run_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
