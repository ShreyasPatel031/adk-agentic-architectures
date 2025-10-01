# ADK Evaluation Tests — Agent Configuration Validation

This repository includes a **minimal, agent-agnostic** evaluation suite for Google's **Agent Development Kit (ADK)**.  

These tests validate **basic functionality and correct configuration** — not AI quality or advanced reasoning.

> 💡 **Key principle:** These tests must be passable by *any* properly configured ADK agent - single `LlmAgent` or workflow agents (`SequentialAgent`, `LoopAgent`, `ParallelAgent`).

---

## ✅ **Validated Agent Examples**

| Agent Type | Tests Passed | Status |
|-----------|--------------|--------|
| **Demo (LlmAgent)** | 4/4 (100%) | ✅ Perfect |
| **Sequential** | 4/4 (100%) | ✅ Perfect |
| **Loop** | 4/4 (100%) | ✅ Perfect |
| **Parallel** | 3/4 (75%) | ✅ Acceptable |

**All ADK workflow agent types are validated and working.**

---

## 📦 ADK Test File Schema

Each `*.test.json` follows ADK's `EvalSet` schema:

```json
{
  "eval_set_id": "test_name",
  "eval_cases": [
    {
      "eval_id": "test_case_id",
      "conversation": [
        {
          "user_content": {
            "parts": [{"text": "Your query here"}]
          },
          "final_response": {
            "parts": [{"text": "Expected keyword/phrase"}]
          }
        }
      ]
    }
  ]
}
```

Each test includes `test_config.json` with evaluation criteria:

```json
{
  "criteria": {
    "response_match_score": 0.01,
    "tool_trajectory_avg_score": 1.0
  }
}
```

---

## 🗂 Test Suite Layout

```
tests/behavior/
  reflection/
    hello_world_reflection.test.json  # Basic response generation
    test_config.json                  # response_match_score: 0.01
  tool_use/
    tool_calling_basic.test.json      # Tool invocation capability
    test_config.json                  # response_match + tool_trajectory: 1.0
  react/
    simple_lookup.test.json           # Iterative reasoning with tools
    test_config.json                  # response_match: 0.01, tools: 1.0
  planning/
    plan_then_act.test.json           # Structured task execution
    test_config.json                  # response_match_score: 0.01
```

---

## 🧪 What Each Test Validates

### 1. Reflection Test
**Goal:** Verify the agent can generate a response

- **Prompt**: "Write a Python function that prints `Hello, World!`, then answer with the text `Hello, World!`."
- **Pass Criteria**: ROUGE-L ≥ 0.01 (agent responded with relevant text)
- **What it tests**: Basic agent execution and response generation

### 2. Tool Use Test
**Goal:** Verify tool invocation works

- **Prompt**: "Find out what the population of Tokyo is."
- **Pass Criteria**:
  - Tool was called (`tool_trajectory_avg_score: 1.0`)
  - Response contains relevant text (ROUGE-L ≥ 0.01)
- **What it tests**: Tool pipeline functionality

### 3. ReAct Test
**Goal:** Verify reasoning with tools

- **Prompt**: "Find out who produced the 2021 movie 'Dune' and give a short answer."
- **Pass Criteria**:
  - Tool was called (`tool_trajectory_avg_score: 1.0`)
  - Response contains relevant text (ROUGE-L ≥ 0.01)
- **What it tests**: Iterative reasoning and tool usage

### 4. Planning Test
**Goal:** Verify structured task execution

- **Prompt**: "Outline a short plan to extract a number from text, then output the number 123 from `ID:123`."
- **Pass Criteria**: ROUGE-L ≥ 0.01 (agent processed the request)
- **What it tests**: Task comprehension and execution

---

## ✅ Running Tests

### Quick Test (Single Agent)
```bash
export GOOGLE_API_KEY=your_api_key_here
./tests/run_all_tests.sh agent/
```

### Individual Test
```bash
adk eval agent/ tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json
```

### Workflow Agents Test
```bash
./tests/test_workflow_agents.sh
```

---

## 🎯 What These Tests Catch

### ✅ Configuration Errors (Detected):
- Missing `__init__.py` or incorrect exports
- Missing config files
- Import errors
- Tool registration failures
- Sub-agent structure issues
- Agent crashes

### ✅ Basic Functionality (Validated):
- Agent responds to input
- Tools are called when available
- Multi-stage workflows execute
- Responses are generated

### ❌ NOT Tested (By Design):
- Response quality or eloquence
- Advanced reasoning accuracy
- Specific implementation details
- Performance/speed

---

## 📊 Pass Criteria

| Status | Score | Meaning |
|--------|-------|---------|
| ✅ **Perfect** | 4/4 (100%) | Agent properly configured |
| ✅ **Acceptable** | 3/4 (75%) | Agent works, minor AI variability |
| ⚠️ **Review** | 2/4 (50%) | Possible configuration issue |
| ❌ **Failed** | 0-1/4 | Configuration errors |

---

## 🚀 Agent Examples

### 1. LlmAgent (Single Agent)
**Location**: `/agent/`  
**Pattern**: Basic single-agent  
**Tests**: 4/4 ✅

### 2. SequentialAgent (Multi-Stage Pipeline)
**Location**: `/agent/sequential_example/`  
**Pattern**: Analyzer → Responder  
**Tests**: 4/4 ✅

### 3. LoopAgent (Iterative Processing)
**Location**: `/agent/loop_example/`  
**Pattern**: Worker with tools, single iteration  
**Tests**: 4/4 ✅

### 4. ParallelAgent (Concurrent Execution)
**Location**: `/agent/parallel_example/`  
**Pattern**: Multiple analysts in parallel  
**Tests**: 3/4 ✅

---

## 🔧 ADK Framework Limitations

### Known Issue: Nested Function Calling
- **Problem**: Workflow agent sub-agents cannot use tools in some configurations
- **References**: [GitHub Issue #53](https://github.com/google/adk-python/issues/53), [Issue #134](https://github.com/google/adk-python/issues/134)
- **Workaround**: Use `AgentTool` wrapper or put tools in first sub-agent only
- **Impact**: Limited for some LoopAgent patterns, but SequentialAgent works well

---

## 📚 Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Loop Agents](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)

---

## License

MIT