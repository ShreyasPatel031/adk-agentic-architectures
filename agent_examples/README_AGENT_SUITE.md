# ADK Agent Development Guide

This guide shows you how to create, configure, and test ADK agents using proven patterns and examples.

## 🚀 Quick Start

### 1. Set Up Environment
```bash
export GOOGLE_API_KEY=your_api_key_here
```

### 2. Test Existing Agents
```bash
# Test all agentic architectures
./test_all_agents.sh

# Test a specific agent
./tests/run_all_tests.sh adk-agentic-architectures/01_reflection/
```

### 3. Create New Agent
```bash
# Copy template and modify
cp -r agent_examples/default_agent/ my_new_agent/
# Edit the files as needed
```

## 📚 Agent Architecture Patterns

### 1. **Single Agent** (`LlmAgent`)
**Best for**: Simple queries, basic tool use, single-stage processing

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="MyAgent",
    model="gemini-2.5-flash-lite",
    instruction="You are a helpful assistant. Use tools when needed.",
    tools=[google_search]
)
```

### 2. **Sequential Agent** (`SequentialAgent`)
**Best for**: Multi-stage workflows, planning pipelines, code review

```python
from google.adk.agents import Agent, SequentialAgent

analyzer = Agent(
    name="Analyzer", 
    model="gemini-2.5-flash-lite",
    instruction="Analyze the input and provide insights."
)

responder = Agent(
    name="Responder", 
    model="gemini-2.5-flash-lite",
    instruction="Based on the analysis, provide a helpful response."
)

root_agent = SequentialAgent(
    name="AnalysisPipeline",
    sub_agents=[analyzer, responder]
)
```

### 3. **Loop Agent** (`LoopAgent`)
**Best for**: Iterative refinement, ReAct patterns, self-improvement

```python
from google.adk.agents import Agent, LoopAgent

worker = Agent(
    name="Worker", 
    model="gemini-2.5-flash-lite",
    tools=[google_search],
    instruction="Process the task iteratively. Use tools when needed."
)

root_agent = LoopAgent(
    name="IterativeProcessor",
    sub_agents=[worker],
    max_iterations=5
)
```

### 4. **Parallel Agent** (`ParallelAgent`)
**Best for**: Ensemble methods, multi-perspective analysis, concurrent tasks

```python
from google.adk.agents import Agent, ParallelAgent

analyst1 = Agent(
    name="TechnicalAnalyst", 
    model="gemini-2.5-flash-lite",
    instruction="Focus on technical aspects of the problem."
)

analyst2 = Agent(
    name="BusinessAnalyst", 
    model="gemini-2.5-flash-lite",
    instruction="Focus on business implications of the solution."
)

root_agent = ParallelAgent(
    name="MultiPerspective",
    sub_agents=[analyst1, analyst2]
)
```

### 5. **Custom Agent** (`BaseAgent`)
**Best for**: Complex architectures, specialized workflows, custom logic

```python
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from typing import AsyncGenerator

class MyCustomAgent(BaseAgent):
    name: str = "CustomAgent"
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Your custom logic here
        result = "Custom processing completed"
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=result)])
        )

root_agent = MyCustomAgent()
```

## 📁 Agent Directory Structure

Every agent should follow this structure:

```
your_agent/
├── __init__.py              # Exports agent.root_agent
├── your_agent.py            # Agent implementation
└── config/
    └── config.yaml          # Configuration (optional)
```

### Required: `__init__.py`
```python
from .your_agent import root_agent
from types import SimpleNamespace

agent = SimpleNamespace(root_agent=root_agent)
```

### Agent Implementation: `your_agent.py`
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="YourAgentName",
    model="gemini-2.5-flash-lite",
    instruction="Your specific instructions here.",
    tools=[google_search]  # Add tools as needed
)
```

## 🧪 Testing Your Agent

### 1. Structure Validation (Instant Feedback)
```bash
python3 tests/validate_agent.py adk-agentic-architectures/your_agent/
```
- Catches import errors immediately
- Verifies module structure
- No API calls, runs in <1 second

### 2. Interactive Testing (Development)
```bash
adk web adk-agentic-architectures/your_agent/
```
- Opens UI at http://localhost:8000
- Test queries immediately
- See full event stream and responses
- Perfect for development and debugging

### 3. Single Test (Focused)
```bash
adk eval adk-agentic-architectures/your_agent/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json \
  --print_detailed_results
```

### 4. Full Test Suite (Complete)
```bash
./tests/run_all_tests.sh adk-agentic-architectures/your_agent/
```

## 🎯 Test Results Guide

| Score | Status | Meaning |
|-------|--------|---------|
| 4/4 | ✅ Perfect | Agent properly configured |
| 3/4 | ✅ Good | Agent works, minor AI variability |
| 2/4 | ⚠️ Review | Possible configuration issue |
| 0-1/4 | ❌ Failed | Configuration errors |

## 🔧 Common Issues & Solutions

### Issue: Agent outputs verification status instead of answer
```
Response: "SUCCESS" or "FAILURE"
Expected: Actual answer to the question
```
**Fix**: Add final Synthesizer agent that presents the verified result

### Issue: Tools not being called
```
tool_trajectory_avg_score: 0.0 (expected 1.0)
```
**Debug**: Use interactive mode to see tool calls
**Fix**: Ensure first sub-agent has tools, update instructions to encourage tool use

### Issue: Response doesn't match expected
```
response_match_score: 0.02 (expected ≥ 0.01)
```
**Debug**: Use `--print_detailed_results` to see actual response
**Fix**: Check if agent is answering the question or just running its internal process

## 🏗️ Configuration-Driven Agents

For complex agents, use YAML configuration:

### `config/config.yaml`
```yaml
name: YourAgentName
model: gemini-2.5-flash-lite
instruction: |
  You are a helpful AI assistant.
  When asked to use tools, USE them.
  Keep responses concise.
temperature: 0.0
max_turns: 8
tools:
  - google_search
architecture: single
```

### Python Implementation
```python
from dataclasses import dataclass, field
from typing import List
import yaml
from google.adk.agents import Agent
from google.adk.tools import google_search

@dataclass
class AgentConfig:
    name: str
    model: str
    instruction: str
    tools: List[str] = field(default_factory=list)

def load_config(path: str) -> AgentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return AgentConfig(**{k: v for k, v in data.items() if k in AgentConfig.__annotations__})

cfg = load_config("config/config.yaml")

root_agent = Agent(
    name=cfg.name,
    model=cfg.model,
    instruction=cfg.instruction,
    tools=[google_search] if "google_search" in cfg.tools else []
)
```

## 🚀 Adding Your Agent to the Test Suite

1. **Create your agent** following the directory structure above
2. **Test individually**:
   ```bash
   ./tests/run_all_tests.sh adk-agentic-architectures/your_agent/
   ```
3. **Add to comprehensive test**:
   ```bash
   # Add your agent to the test_all_agents.sh script
   # The script automatically discovers agents in adk-agentic-architectures/
   ```
4. **Run full suite**:
   ```bash
   ./test_all_agents.sh
   ```

## 📚 Advanced Patterns

### Multi-Agent with Custom Logic
```python
class CustomMultiAgent(BaseAgent):
    name: str = "CustomMultiAgent"
    
    def __init__(self):
        self.sub_agents = {
            "analyzer": Agent(name="Analyzer", model="gemini-2.5-flash-lite"),
            "synthesizer": Agent(name="Synthesizer", model="gemini-2.5-flash-lite")
        }
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Custom orchestration logic
        async for event in self.sub_agents["analyzer"].run_async(ctx):
            yield event
        
        # Process results and call next agent
        async for event in self.sub_agents["synthesizer"].run_async(ctx):
            yield event
```

### Agent with Session State
```python
class StatefulAgent(BaseAgent):
    name: str = "StatefulAgent"
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Access session state
        if "counter" not in ctx.session.state:
            ctx.session.state["counter"] = 0
        
        ctx.session.state["counter"] += 1
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Counter: {ctx.session.state['counter']}")])
        )
```

## 📚 Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Loop Agents](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [Custom Agents](https://google.github.io/adk-docs/agents/custom-agents/)
- [Testing Guide](../tests/ADK_Eval_Tests_Revised.md)

---

## License

MIT