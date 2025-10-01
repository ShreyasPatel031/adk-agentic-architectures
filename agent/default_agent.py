"""
Default ADK Root Agent (config-driven, agent-agnostic)
-----------------------------------------------------
- Uses Google ADK's Agent class directly
- Configurable via YAML at runtime (path from AGENT_CONFIG env var or default)
- Exposes `root_agent` for ADK evaluation import

This agent is intentionally simple and uses ADK's Agent class directly.
The ADK Runner handles all execution, async operations, and session management.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os

try:
    import yaml
except Exception:
    yaml = None
import json

# ADK imports
try:
    from google.adk.agents import Agent
except Exception as e:
    Agent = None

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
    except Exception:
        pass
    try:
        from google.adk.tools import code_executor
        _BUILTIN_TOOL_REGISTRY["code_executor"] = code_executor
    except Exception:
        pass

@dataclass
class AgentConfig:
    """Configuration schema - all defaults should be in YAML file."""
    name: str
    model: str
    instruction: str
    temperature: float = 0.0
    max_turns: int = 8
    tools: List[str] = field(default_factory=list)
    architecture: str = "single"
    tool_timeouts: Dict[str, int] = field(default_factory=dict)

    @staticmethod
    def from_file(path: str) -> "AgentConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        data: Dict[str, Any]
        if path.endswith((".yaml", ".yml")) and yaml is not None:
            data = yaml.safe_load(raw) or {}
        else:
            data = json.loads(raw)
        cfg = AgentConfig(**{k: v for k, v in data.items() if k in AgentConfig.__annotations__})
        return cfg

def resolve_tools(names: List[str]) -> List[Any]:
    """Map tool names from config to actual tool callables."""
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

# Load configuration - REQUIRED, no defaults
cfg_path = os.path.join(os.path.dirname(__file__), "config", "default_agent.yaml")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(
        f"Configuration file required but not found: {cfg_path}\n"
        f"Please create config/default_agent.yaml with required fields: name, model, instruction"
    )
cfg = AgentConfig.from_file(cfg_path)

# Resolve tools
tool_impls = resolve_tools(cfg.tools)

# Create the ADK Agent directly
# ADK's Runner handles all execution, sessions, and async operations
if Agent is not None:
    root_agent = Agent(
        name=cfg.name,
        model=cfg.model,
        instruction=cfg.instruction,
        tools=tool_impls if tool_impls else None,
    )
else:
    # Stub for environments without ADK
    class StubAgent:
        def __init__(self):
            self.name = cfg.name
    root_agent = StubAgent()