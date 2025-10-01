"""
PEV ADK Agent (config-driven)
-----------------------------------------------------
- Implements the PEV architecture using a LoopAgent containing a SequentialAgent.
- This creates a bounded retry loop for the Plan-Execute-Verify cycle.
- Configurable via YAML.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union, Optional, AsyncGenerator
import os

try:
    import yaml
except ImportError:
    yaml = None
import json

from google.adk.agents import Agent, SequentialAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

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
    try:
        from google.adk.tools import code_executor
        _BUILTIN_TOOL_REGISTRY["code_executor"] = code_executor
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
class WorkflowAgentConfig:
    name: str
    architecture: str
    sub_agents: List[Union[SubAgentConfig, "WorkflowAgentConfig"]] = field(default_factory=list)
    max_iterations: Optional[int] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "WorkflowAgentConfig":
        sub_agent_configs = []
        for sub in data.get("sub_agents", []):
            if "architecture" in sub:
                sub_agent_configs.append(WorkflowAgentConfig.from_dict(sub))
            else:
                sub_agent_configs.append(SubAgentConfig(**sub))
        
        return WorkflowAgentConfig(
            name=data["name"],
            architecture=data["architecture"],
            sub_agents=sub_agent_configs,
            max_iterations=data.get("max_iterations")
        )

class StopChecker(BaseAgent):
    """A custom agent that checks the verifier's output and stops the loop on SUCCESS."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        verification_output = ctx.session.state.get("verification", "{}")
        should_stop = False
        try:
            verification_json = json.loads(verification_output)
            if verification_json.get("status") == "SUCCESS":
                should_stop = True
                # Carry the final result forward for the synthesizer
                ctx.session.state["result"] = verification_json.get("final_result", "")
        except (json.JSONDecodeError, AttributeError):
            pass # If output is not as expected, continue the loop
            
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))

def resolve_tools(names: List[str]) -> List[Any]:
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

def build_agent_from_config(config: Union[SubAgentConfig, WorkflowAgentConfig]) -> BaseAgent:
    """Recursively builds agents and workflow agents from config."""
    if isinstance(config, SubAgentConfig):
        return Agent(
            name=config.name,
            model=config.model,
            instruction=config.instruction,
            tools=resolve_tools(config.tools),
            output_key=config.output_key,
        )
    
    sub_agents = [build_agent_from_config(sub) for sub in config.sub_agents]
    
    if config.architecture == "sequential":
        return SequentialAgent(name=config.name, sub_agents=sub_agents)
    elif config.architecture == "loop":
        # Inject the custom StopChecker agent at the end of the loop cycle
        loop_agents = sub_agents.copy()
        if isinstance(loop_agents[0], SequentialAgent):
             loop_agents[0].sub_agents.append(StopChecker(name="StopChecker"))
        return LoopAgent(name=config.name, sub_agents=loop_agents, max_iterations=config.max_iterations)
    else:
        raise ValueError(f"Unknown architecture: {config.architecture}")

# Load configuration
cfg_path = os.path.join(os.path.dirname(__file__), "config", "pev_agent.yaml")
if not os.path.exists(cfg_path):
    raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

with open(cfg_path, "r", encoding="utf-8") as f:
    raw_data = yaml.safe_load(f) if yaml else json.load(f)

cfg = WorkflowAgentConfig.from_dict(raw_data)

# Build the root agent from the nested configuration
root_agent = build_agent_from_config(cfg)
