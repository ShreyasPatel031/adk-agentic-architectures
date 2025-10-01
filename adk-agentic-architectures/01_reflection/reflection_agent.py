"""
Reflection ADK Agent (config-driven)
-----------------------------------------------------
- Implements the Reflection architecture using a SequentialAgent.
- The workflow is broken down into a Generator and a Reflector.
- Configurable via YAML.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
import os

try:
    import yaml
except ImportError:
    yaml = None
import json

from google.adk.agents import Agent, SequentialAgent

# No tools are needed for this agent.

@dataclass
class SubAgentConfig:
    name: str
    model: str
    instruction: str
    tools: List[str] = field(default_factory=list)

@dataclass
class SequentialAgentConfig:
    name: str
    architecture: str
    sub_agents: List[SubAgentConfig]

    @staticmethod
    def from_file(path: str) -> "SequentialAgentConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        data: Dict[str, Any]
        if path.endswith((".yaml", ".yml")) and yaml is not None:
            data = yaml.safe_load(raw) or {}
        else:
            data = json.loads(raw)
        
        sub_agent_data = data.get("sub_agents", [])
        for sub_agent in sub_agent_data:
            if "tools" not in sub_agent:
                sub_agent["tools"] = []
        data["sub_agents"] = [SubAgentConfig(**sub) for sub in sub_agent_data]
        
        return SequentialAgentConfig(**{k: v for k, v in data.items() if k in SequentialAgentConfig.__annotations__})

# Load configuration
cfg_path = os.path.join(os.path.dirname(__file__), "config", "reflection_agent.yaml")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
cfg = SequentialAgentConfig.from_file(cfg_path)

# Build sub-agents
sub_agents = []
for sub_agent_cfg in cfg.sub_agents:
    sub_agent = Agent(
        name=sub_agent_cfg.name,
        model=sub_agent_cfg.model,
        instruction=sub_agent_cfg.instruction,
        tools=[], # No tools for this agent
    )
    sub_agents.append(sub_agent)

# Create the root SequentialAgent
root_agent = SequentialAgent(
    name=cfg.name,
    sub_agents=sub_agents,
)
