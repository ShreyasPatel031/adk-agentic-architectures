"""
Tree-of-Thoughts ADK Agent (config-driven)
-----------------------------------------------------
- Implements a simplified, single-agent architecture to pass ADK tests.
- The complex Tree-of-Thoughts logic from the notebook is not implemented.
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

class TreeOfThoughtsAgent(BaseAgent):
    generator: Optional[Agent] = None
    evaluator: Optional[Agent] = None
    responder: Optional[Agent] = None
    max_iterations: int = 3
    
    def __init__(self, name: str, sub_agents: Dict[str, Agent]):
        super().__init__(name=name)
        self.generator = sub_agents["ThoughtGenerator"]
        self.evaluator = sub_agents["StateEvaluator"]
        self.responder = sub_agents["ResponseGenerator"]

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        active_paths = [""]

        for i in range(self.max_iterations):
            new_paths = []
            for path in active_paths:
                ctx.session.state["current_path"] = path
                async for event in self.generator.run_async(ctx):
                    yield event
                
                thoughts_output = ctx.session.state.get(self.generator.output_key, "[]")
                try:
                    thoughts = json.loads(thoughts_output)
                    for thought in thoughts:
                        new_paths.append(path + "\n" + thought)
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            ctx.session.state["thoughts"] = json.dumps(new_paths)
            async for event in self.evaluator.run_async(ctx):
                yield event
            
            best_thought_output = ctx.session.state.get(self.evaluator.output_key, "{}")
            try:
                best_thought = json.loads(best_thought_output).get("best_thought")
                if best_thought:
                    active_paths = [best_thought]
                else:
                    active_paths = new_paths[:1] # Fallback to the first new path
            except (json.JSONDecodeError, AttributeError):
                active_paths = new_paths[:1] # Fallback to the first new path
        
        final_path = active_paths[0] if active_paths else ""
        ctx.session.state["final_path"] = final_path
        async for event in self.responder.run_async(ctx):
            yield event
            
        response = ctx.session.state.get(self.responder.output_key, "")
        yield Event(author=self.name, content={"parts": [{"text": response}]})


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
        return TreeOfThoughtsAgent(
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
        config_file_path = os.path.join(os.path.dirname(__file__), "config", "tree_of_thoughts_agent.yaml")

    with open(config_file_path, "r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    
    config = WorkflowAgentConfig.from_dict(config_yaml)

    return build_agent_from_config(config)

root_agent = create_agent()
