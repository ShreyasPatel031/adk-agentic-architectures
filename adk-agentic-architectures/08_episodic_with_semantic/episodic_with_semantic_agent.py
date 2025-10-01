import json
import os
import yaml
from typing import Any, Dict, List, Union, Optional, AsyncGenerator
from dataclasses import dataclass, field

from google.adk.agents import Agent, BaseAgent, LlmAgent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

# --- Memory Simulation ---
EPISODIC_MEMORY = []  # Simulates a log of conversation turns
SEMANTIC_MEMORY = {}  # Simulates a graph store: {entity: {relationship: [entity]}}

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

class EpisodicWithSemanticAgent(BaseAgent):
    retriever: Optional[Agent] = None
    generator: Optional[Agent] = None
    updater: Optional[Agent] = None

    def __init__(self, name: str, sub_agents: Dict[str, Agent]):
        super().__init__(name=name)
        self.retriever = sub_agents["MemoryRetriever"]
        self.generator = sub_agents["ResponseGenerator"]
        self.updater = sub_agents["MemoryUpdater"]

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 1. Retrieve
        ctx.session.state["episodic_memory"] = json.dumps(EPISODIC_MEMORY[-5:]) # Last 5 turns
        ctx.session.state["semantic_memory"] = json.dumps(SEMANTIC_MEMORY)
        async for event in self.retriever.run_async(ctx):
            yield event
        
        # 2. Generate
        retrieved_memories = ctx.session.state.get(self.retriever.output_key, "")
        async for event in self.generator.run_async(ctx):
            yield event

        # 3. Update
        response = ctx.session.state.get(self.generator.output_key, "")
        user_request = ctx.get_request_content_str()
        
        ctx.session.state["conversation_history"] = f"User: {user_request}\nAgent: {response}"

        async for event in self.updater.run_async(ctx):
            yield event
            
        memory_update_output = ctx.session.state.get(self.updater.output_key, "{}")
        try:
            memory_update = json.loads(memory_update_output)
            if "episodic" in memory_update:
                EPISODIC_MEMORY.append(memory_update["episodic"])
            if "semantic" in memory_update:
                for rel in memory_update["semantic"]:
                    if len(rel) == 3:
                        entity1, relationship, entity2 = rel
                        if entity1 not in SEMANTIC_MEMORY:
                            SEMANTIC_MEMORY[entity1] = {}
                        if relationship not in SEMANTIC_MEMORY[entity1]:
                            SEMANTIC_MEMORY[entity1][relationship] = []
                        SEMANTIC_MEMORY[entity1][relationship].append(entity2)
        except (json.JSONDecodeError, AttributeError):
            pass


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
        return EpisodicWithSemanticAgent(
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
        config_file_path = os.path.join(os.path.dirname(__file__), "config", "episodic_with_semantic_agent.yaml")

    with open(config_file_path, "r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    
    config = WorkflowAgentConfig.from_dict(config_yaml)

    return build_agent_from_config(config)

root_agent = create_agent()
