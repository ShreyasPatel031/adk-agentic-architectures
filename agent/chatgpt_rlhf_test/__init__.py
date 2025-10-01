"""
ChatGPT RLHF Test
"""

from .rlhf_agent import root_agent
from types import SimpleNamespace

agent = SimpleNamespace(root_agent=root_agent)
