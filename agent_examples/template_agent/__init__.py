"""
Template agent for creating new ADK agents.
Copy this directory and modify the files as needed.
"""

from types import SimpleNamespace
from .template_agent import root_agent

agent = SimpleNamespace(root_agent=root_agent)
