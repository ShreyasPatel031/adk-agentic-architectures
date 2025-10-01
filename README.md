# ADK Agent Architectures - General Purpose Benchmark Suite

This repository provides a **config-driven, agent-agnostic ADK agent suite** for building and evaluating different AI agent architectures using Google's **Agent Development Kit (ADK)**.

## 🎯 Purpose

Create general-purpose AI agents using the ADK framework with:
- **Different architectures** (single, ReAct, sequential, loop, multi-agent, etc.)
- **Flexible configuration** via YAML files
- **Benchmarking capabilities** to compare trade-offs between cost, latency, context window, etc.
- **Agent-agnostic tests** that validate basic functionality without enforcing specific implementations

## 📁 Project Structure

```
adk-agentic-architectures/
├── agent/
│   ├── __init__.py              # Exports root_agent for ADK
│   ├── default_agent.py         # Config-driven agent implementation
│   └── README_AGENT_SUITE.md    # Detailed agent documentation
├── config/
│   └── default_agent.yaml       # Default agent configuration
├── tests/
│   └── behavior/
│       ├── reflection/
│       │   ├── hello_world_reflection.test.json
│       │   └── test_config.json
│       ├── tool_use/
│       │   ├── tool_calling_basic.test.json
│       │   └── test_config.json
│       ├── react/
│       │   ├── simple_lookup.test.json
│       │   └── test_config.json
│       └── planning/
│           ├── plan_then_act.test.json
│           └── test_config.json
├── ADK_Eval_Tests_Revised.md    # Test specification
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Authentication

Set up Google Cloud authentication (choose one):

```bash
# Option 1: Application Default Credentials
gcloud auth application-default login

# Option 2: Service Account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### 3. Run Tests

```bash
# Test all evaluation cases
python -c "
from agent import root_agent

# Reflection test
print(root_agent.process_message('Write a Python function that prints Hello, World!, then answer with the text Hello, World!.'))

# Tool use test
print(root_agent.process_message('Use any available tool to find or compute something simple and respond with a short result.'))

# ReAct test
print(root_agent.process_message('Find out who produced the 2021 movie Dune and give a short answer.'))

# Planning test
print(root_agent.process_message('Outline a short plan to extract a number from text, then output the number 123 from ID:123.'))
"
```

Or run ADK evaluation:

```bash
# Reflection
adk eval agent/__init__.py tests/behavior/reflection/hello_world_reflection.test.json

# Tool Use
adk eval agent/__init__.py tests/behavior/tool_use/tool_calling_basic.test.json

# ReAct
adk eval agent/__init__.py tests/behavior/react/simple_lookup.test.json

# Planning
adk eval agent/__init__.py tests/behavior/planning/plan_then_act.test.json
```

## 🧪 Evaluation Tests

The test suite is **agent-agnostic** and designed as smoke tests to validate basic functionality:

1. **Reflection** (`hello_world_reflection.test.json`)
   - Goal: Validate trivial output generation
   - Pass: Final response contains "Hello, World!"

2. **Tool Use** (`tool_calling_basic.test.json`)
   - Goal: Validate tool invocation works
   - Pass: At least one tool call occurs (any tool name accepted)

3. **ReAct** (`simple_lookup.test.json`)
   - Goal: Validate reasoning and multi-step action
   - Pass: At least one tool call + short answer

4. **Planning** (`plan_then_act.test.json`)
   - Goal: Validate structured reasoning
   - Pass: Final response contains "123"

### Design Principles

- ✅ **No required tool names** — any tool invocation satisfies tests
- ✅ **Minimal pass criteria** — only check if functionality works, not how
- ✅ **No coupling** — tests don't assume specific models, libraries, or frameworks
- ✅ **Low thresholds** — avoid blocking early development

## ⚙️ Configuration

Edit `config/default_agent.yaml` to customize your agent:

```yaml
name: RootAgent
model: gemini-2.5-flash-lite
instruction: |
  You are a helpful AI assistant.
  - Use tools when helpful.
  - Be concise.
temperature: 0.2
max_turns: 8
tools:
  - google_search
architecture: single  # Options: single|react|sequential|loop
```

Or override via environment:

```bash
export AGENT_CONFIG=/path/to/custom-config.yaml
```

## 🏗️ Adding New Architectures

The suite is designed to support multiple agent architectures:

### Current: Single Agent
The default implementation uses a single ADK `Agent` with built-in tools.

### Future Architectures

**ReAct Agent:**
- Compose a loop that appends observations and re-prompts
- Add reasoning traces before each action

**Planner/Executor:**
- Create a planner agent that outputs a plan
- Execute steps using tools or sub-agents

**Multi-Agent:**
- Orchestrate multiple `Agent` instances
- Each with specialized tools and instructions

**Sequential/Loop:**
- Use ADK's workflow agents for structured control flow
- Chain multiple steps deterministically

As long as your module exports a `root_agent` callable, ADK can evaluate it.

## 📊 Benchmarking

This suite is designed for **General Purpose Benchmarking** where you can vary:

- **Model** (latency vs. quality trade-offs)
- **Temperature** (determinism vs. creativity)
- **Tools** (cost/latency considerations)
- **Max turns** (cost containment)
- **Context window** (via model choice)

Create multiple YAML configs and run the same evaluations to compare:

```bash
# Test different configurations
AGENT_CONFIG=config/fast-agent.yaml python test.py
AGENT_CONFIG=config/quality-agent.yaml python test.py
AGENT_CONFIG=config/cost-optimized.yaml python test.py
```

## 🛠️ Built-in Tools

Available ADK built-in tools (from [ADK documentation](https://google.github.io/adk-docs/tools/built-in-tools/)):

- **Google Search** - Web search capabilities
- **Code Execution** - Run code snippets
- **Vertex AI RAG** - Retrieval-augmented generation
- **BigQuery** - Database queries
- **Vertex AI Search** - Search within your data

Add tools to your config:

```yaml
tools:
  - google_search
  # - code_executor  # Uncomment when available
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Ensure all tests pass
2. Keep agent implementations agent-agnostic
3. Document configuration changes
4. Follow the existing code structure

## 📚 Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Tools Guide](https://google.github.io/adk-docs/tools/)
- [ADK Evaluation Guide](https://google.github.io/adk-docs/evaluate/)
- [Test Specification](./ADK_Eval_Tests_Revised.md)
- [Agent Suite Documentation](./agent/README_AGENT_SUITE.md)
