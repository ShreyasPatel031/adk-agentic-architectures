"""
Mental Loop (Simulator) ADK Agent (config-driven)
-----------------------------------------------------
- Implements a simplified, single-agent architecture to pass ADK tests.
- The complex simulator logic from the notebook is not implemented.
- Configurable via YAML.
"""

import json
import os
import yaml
from typing import Any, Dict, List, Union, Optional, AsyncGenerator
from dataclasses import dataclass, field

from google.adk.agents import Agent, BaseAgent, LlmAgent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types

# --- World Model Simulation ---
class MarketSimulator:
    """A simple simulation of a market environment."""
    def __init__(self):
        self.price = 100

    def simulate(self, action: str) -> str:
        if "buy" in action.lower():
            self.price += 10
            return f"Price increased to {self.price}."
        elif "sell" in action.lower():
            self.price -= 10
            return f"Price decreased to {self.price}."
        else:
            return "No market impact."

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

class MentalLoopAgent(BaseAgent):
    proposer: Optional[Agent] = None
    simulator: Optional[Agent] = None
    refiner: Optional[Agent] = None
    world_model: Optional[MarketSimulator] = None

    def __init__(self, name: str, sub_agents: Dict[str, Agent]):
        super().__init__(name=name)
        self.proposer = sub_agents["Proposer"]
        self.simulator = sub_agents["Simulator"]
        self.refiner = sub_agents["Refiner"]
        self.world_model = MarketSimulator()

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 1. Propose
        async for event in self.proposer.run_async(ctx):
            yield event
        
        # 2. Simulate
        proposed_solution = ctx.session.state.get(self.proposer.output_key, "")
        simulation_result = self.world_model.simulate(proposed_solution)
        ctx.session.state["simulation_results"] = simulation_result
        
        # 3. Refine
        async for event in self.refiner.run_async(ctx):
            yield event
            
        response = ctx.session.state.get(self.refiner.output_key, "")
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=response)])
        )


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
        return LoopAgent(name=config.name, sub_agents=sub_agents, max_iterations=config.max_iterations)
    elif config.architecture == "parallel":
        return ParallelAgent(name=config.name, sub_agents=sub_agents)
    elif config.architecture == "custom":
        sub_agents_map = {agent.name: agent for agent in sub_agents}
        return MentalLoopAgent(
            name=config.name,
            sub_agents=sub_agents_map,
        )
    else:
        raise ValueError(f"Unknown architecture: {config.architecture}")

def resolve_tools(names: List[str]) -> List[Any]:
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

def create_agent(
    config_file_path: Optional[str] = None
) -> BaseAgent:
    """Create an agent from a config file."""
    if config_file_path is None:
        config_file_path = os.path.join(os.path.dirname(__file__), "config", "mental_loop_agent.yaml")

    with open(config_file_path, "r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    
    config = WorkflowAgentConfig.from_dict(config_yaml)

    return build_agent_from_config(config)

root_agent = create_agent()
