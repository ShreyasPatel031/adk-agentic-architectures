"""
Multi-Agent ADK Agent (config-driven)
-----------------------------------------------------
- Implements a multi-agent system using a SequentialAgent.
- The workflow is broken down into a TechnicalAnalyst, a ResearchAnalyst, and a Manager.
- Configurable via YAML.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os

try:
    import yaml
except ImportError:
    yaml = None
import json

from google.adk.agents import Agent, SequentialAgent

# Built-in tools registry
_BUILTIN_TOOL_REGISTRY: Dict[str, Any] = {}

def _maybe_import_builtin_tools() -> None:
    """Lazy load built-in tools to avoid import errors."""
    global _BUILTIN_TOOL_REGISTRY
    if _BUILTIN_TOOL_REGISTRY:
        return
    try:
        from google.adk.tools import google_search
        _BUILTIN_TOOL_REGISTRY["google_search"] = google_search
    except ImportError:
        pass

@dataclass
class SubAgentConfig:
    name: str
    model: str
    instruction: str
    tools: List[str] = field(default_factory=list)
    output_key: Optional[str] = None

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
        data["sub_agents"] = [SubAgentConfig(**sub) for sub in sub_agent_data]
        
        return SequentialAgentConfig(**{k: v for k, v in data.items() if k in SequentialAgentConfig.__annotations__})

def resolve_tools(names: List[str]) -> List[Any]:
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

# Load configuration
cfg_path = os.path.join(os.path.dirname(__file__), "config", "multi_agent.yaml")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
cfg = SequentialAgentConfig.from_file(cfg_path)

# Build sub-agents
sub_agents = []
for sub_agent_cfg in cfg.sub_agents:
    sub_tool_impls = resolve_tools(sub_agent_cfg.tools)
    sub_agent = Agent(
        name=sub_agent_cfg.name,
        model=sub_agent_cfg.model,
        instruction=sub_agent_cfg.instruction,
        tools=sub_tool_impls,
        output_key=sub_agent_cfg.output_key,
    )
    sub_agents.append(sub_agent)

# Create the root SequentialAgent
root_agent = SequentialAgent(
    name=cfg.name,
    sub_agents=sub_agents,
)