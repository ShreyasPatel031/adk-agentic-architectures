# ADK Agent Suite - Configuration Validation Examples

This directory contains validated ADK agent examples that demonstrate proper configuration and pass all tests.

---

## ✅ Validated Agents

| Agent | Type | Tests | Status |
|-------|------|-------|--------|
| **default_agent** | LlmAgent | 4/4 | ✅ Perfect |
| **sequential_example** | SequentialAgent | 4/4 | ✅ Perfect |
| **loop_example** | LoopAgent | 4/4 | ✅ Perfect |
| **parallel_example** | ParallelAgent | 3/4 | ✅ Acceptable |

---

## Quick Start

### Run All Tests
```bash
export GOOGLE_API_KEY=your_key

# Test demo agent
./tests/run_all_tests.sh agent/

# Test workflow agents
./tests/test_workflow_agents.sh
```

### Test Individual Agent
```bash
adk eval agent/ tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json
```

---

## Agent Examples

### 1. LlmAgent (Single Agent) - `agent/`

**Use for**: Simple queries, basic tool use, single-stage processing

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="DemoAgent",
    model="gemini-2.5-flash-lite",
    instruction="You are a helpful assistant. Use tools when needed.",
    tools=[google_search]
)
```

### 2. SequentialAgent (Multi-Stage) - `agent/sequential_example/`

**Use for**: Planning, pipelines, code review, multi-step workflows

```python
from google.adk.agents import Agent, SequentialAgent

analyzer = Agent(name="Analyzer", model="gemini-2.5-flash-lite", ...)
responder = Agent(name="Responder", model="gemini-2.5-flash-lite", ...)

root_agent = SequentialAgent(
    name="Pipeline",
    sub_agents=[analyzer, responder]
)
```

### 3. LoopAgent (Iterative) - `agent/loop_example/`

**Use for**: ReAct, iterative refinement, self-improvement

```python
from google.adk.agents import Agent, LoopAgent

worker = Agent(name="Worker", model="gemini-2.5-flash-lite", tools=[google_search])

root_agent = LoopAgent(
    name="LoopAgent",
    sub_agents=[worker],
    max_iterations=5
)
```

### 4. ParallelAgent (Concurrent) - `agent/parallel_example/`

**Use for**: Ensemble, multi-perspective analysis, concurrent tasks

```python
from google.adk.agents import Agent, ParallelAgent

analyst1 = Agent(name="Analyst1", model="gemini-2.5-flash-lite", ...)
analyst2 = Agent(name="Analyst2", model="gemini-2.5-flash-lite", ...)

root_agent = ParallelAgent(
    name="Ensemble",
    sub_agents=[analyst1, analyst2]
)
```

---

## Creating New Agents

### Template Structure
```
your_agent/
├── __init__.py              # Exports agent.root_agent
├── your_agent.py            # Agent implementation
└── config/
    └── config.yaml          # All configuration
```

### __init__.py
```python
from .your_agent import root_agent
from types import SimpleNamespace

agent = SimpleNamespace(root_agent=root_agent)
```

### your_agent.py
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="YourAgent",
    model="gemini-2.5-flash-lite",
    instruction="Your instructions here",
    tools=[google_search]
)
```

---

## Configuration-Driven Agents

For config-driven agents (like `agent/default_agent.py`), all settings come from YAML:

### config.yaml
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
import os, yaml
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
    tools=[google_search] if "google_search" in cfg.tools else None
)
```

---

## ADK Framework Limitations

### Tool Usage in Workflow Agents
- **Issue**: Sub-agents in LoopAgent/SequentialAgent cannot always use tools
- **Reference**: [GitHub Issue #53](https://github.com/google/adk-python/issues/53)
- **Workaround**: 
  - Put tools in first sub-agent only (SequentialAgent)
  - Use max_iterations instead of exit_loop (LoopAgent)
  - Use AgentTool wrapper for delegation

---

## Testing

### Structure Validation
```bash
python3 tests/validate_agent.py agent/
```

### Behavior Tests
```bash
./tests/run_all_tests.sh agent/
```

### Pass Criteria
- ✅ 4/4 (100%) = Perfect configuration
- ✅ 3/4 (75%) = Acceptable (minor AI variation)
- ⚠️ 2/4 (50%) = Review needed
- ❌ 0-1/4 = Configuration errors

---

## Iterative Development & Testing

### Quick Feedback Loop (No Full Test Suite)

**1. Interactive Testing with ADK Web**:
```bash
export GOOGLE_API_KEY=your_key
adk web agent/your_agent/
```
- Opens UI at http://localhost:8000
- Test queries immediately
- See full event stream and responses
- Faster than running full test suite

**2. Single Test Iteration**:
```bash
# Test just one scenario
adk eval agent/your_agent/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json \
  --print_detailed_results
```
- See actual vs expected responses
- Check tool trajectory
- Identify specific issues

**3. Structure-Only Validation** (instant feedback):
```bash
python3 tests/validate_agent.py agent/your_agent/
```
- Catches import errors immediately
- Verifies module structure
- No API calls, runs in <1 second

### Common Issues & How to Debug

**Issue**: Agent outputs verification status instead of answer
```
Response: "SUCCESS" or "FAILURE"
Expected: Actual answer to the question
```
**Fix**: Add final Synthesizer agent that presents the verified result

**Issue**: Tools not being called
```
tool_trajectory_avg_score: 0.0 (expected 1.0)
```
**Debug**:
```bash
# Check tool availability in interactive mode
adk web agent/your_agent/
# Try: "Find the capital of France"
# Watch event stream for tool calls
```
**Fix**: Ensure first sub-agent has tools, update instructions to encourage tool use

**Issue**: Response doesn't match expected
```
response_match_score: 0.02 (expected ≥ 0.01)
```
**Debug**: Use `--print_detailed_results` to see actual response
**Fix**: Check if agent is answering the question or just running its internal process

### Self-Testing Pattern

When building complex architectures:

```python
# Add this to your agent file for quick testing
if __name__ == "__main__":
    import asyncio
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    async def test_agent():
        session_service = InMemorySessionService()
        session = session_service.create_session(
            app_name="test",
            user_id="dev"
        )
        
        runner = InMemoryRunner(
            agent=root_agent,
            app_name="test",
            session_service=session_service
        )
        
        # Test query
        content = types.Content(
            role='user',
            parts=[types.Part(text="Hello")]
        )
        
        print("Testing agent...")
        async for event in runner.run_async("dev", session.id, content):
            if event.final_response:
                print(f"Response: {event.content.parts[0].text}")
    
    asyncio.run(test_agent())
```

Run with: `python3 agent/your_agent/your_agent.py`

## Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Loop Agents](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [Custom Agents](https://google.github.io/adk-docs/agents/custom-agents/)
- Test Documentation: `../tests/ADK_Eval_Tests_Revised.md`