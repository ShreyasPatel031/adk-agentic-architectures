"""
Exposes the root_agent for the ADK Multi-Agent system.
"""

from types import SimpleNamespace
from .multi_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)