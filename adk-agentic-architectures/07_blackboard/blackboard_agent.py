"""
Blackboard ADK Agent (config-driven)
-----------------------------------------------------
- Implements the Blackboard architecture using a CustomAgent as required by the critique.
- A Controller agent dynamically routes tasks to specialist agents in a loop.
- Configurable via YAML.
"""

import json
import os
import yaml
from typing import Any, Dict, List, Union, Optional, AsyncGenerator
from dataclasses import dataclass, field

from google.adk.agents import Agent, BaseAgent, LlmAgent, SequentialAgent, LoopAgent
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

class BlackboardAgent(BaseAgent):
    controller: Optional[Agent] = None
    specialists: Optional[Dict[str, Agent]] = None
    max_iterations: int = 5

    def __init__(self, name: str, controller: Agent, specialists: Dict[str, Agent], max_iterations: int = 5):
        super().__init__(name=name)
        self.controller = controller
        self.specialists = specialists
        self.max_iterations = max_iterations

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        if "blackboard" not in ctx.session.state:
            ctx.session.state["blackboard"] = {"completed_analyses": [], "results": {}}
        
        final_result = ""
        for i in range(self.max_iterations):
            async for event in self.controller.run_async(ctx):
                yield event
            
            controller_output = ctx.session.state.get(self.controller.output_key, "FINISH")
            next_agent_name = controller_output.strip()

            if next_agent_name == "FINISH":
                # If we are finishing, check if there's a synthesis result to output
                final_result = ctx.session.state["blackboard"]["results"].get("synthesis_result", "Process finished without a final result.")
                break

            specialist = self.specialists.get(next_agent_name)
            if specialist:
                async for event in specialist.run_async(ctx):
                    yield event
                
                specialist_output = ctx.session.state.get(specialist.output_key, "")
                ctx.session.state["blackboard"]["completed_analyses"].append(next_agent_name)
                ctx.session.state["blackboard"]["results"][specialist.output_key] = specialist_output
                
                # If the last agent was the synthesizer, we can finish.
                if next_agent_name == "SynthesisSpecialist":
                    final_result = specialist_output
                    break
            else:
                # Controller hallucinated a specialist that doesn't exist.
                final_result = "Controller chose an invalid specialist. Ending process."
                break
        
        yield Event(author=self.name, content={"parts": [{"text": final_result}]})


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
    elif config.architecture == "custom":
        sub_agents_map = {agent.name: agent for agent in sub_agents}
        controller = sub_agents_map.pop("Controller", None)
        if controller is None:
            raise ValueError("A 'Controller' agent must be defined in the config.")
        specialists = sub_agents_map
        return BlackboardAgent(
            name=config.name,
            controller=controller,
            specialists=specialists
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
        config_file_path = os.path.join(os.path.dirname(__file__), "config", "blackboard_agent.yaml")

    with open(config_file_path, "r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    
    config = WorkflowAgentConfig.from_dict(config_yaml)

    return build_agent_from_config(config)

root_agent = create_agent()
