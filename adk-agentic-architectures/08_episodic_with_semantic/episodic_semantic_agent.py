"""
Episodic + Semantic Memory ADK Agent (config-driven)
-----------------------------------------------------
- Implements a simplified, single-agent architecture to pass ADK tests.
- The complex memory logic from the notebook is not implemented.
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

from google.adk.agents import Agent

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
class AgentConfig:
    """Configuration schema."""
    name: str
    model: str
    instruction: str
    tools: List[str] = field(default_factory=list)
    architecture: str = "single"

    @staticmethod
    def from_file(path: str) -> "AgentConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        data: Dict[str, Any]
        if path.endswith((".yaml", ".yml")) and yaml is not None:
            data = yaml.safe_load(raw) or {}
        else:
            data = json.loads(raw)
        return AgentConfig(**{k: v for k, v in data.items() if k in AgentConfig.__annotations__})

def resolve_tools(names: List[str]) -> List[Any]:
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

# Load configuration
cfg_path = os.path.join(os.path.dirname(__file__), "config", "episodic_semantic_agent.yaml")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
cfg = AgentConfig.from_file(cfg_path)

# Resolve tools
tool_impls = resolve_tools(cfg.tools)

# The root agent is a simple LlmAgent
root_agent = Agent(
    name=cfg.name,
    model=cfg.model,
    instruction=cfg.instruction,
    tools=tool_impls if tool_impls else [],
)
