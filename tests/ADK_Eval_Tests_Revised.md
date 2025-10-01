# ADK Agent Evaluation & Testing Guide

This guide explains how to test and validate ADK agents using our comprehensive test suite.

## 🎯 What This Test Suite Does

**Purpose**: Validate that your ADK agents are **properly configured and functional** - not to test AI quality or reasoning accuracy.

**Key Principle**: These tests should be passable by ANY properly configured ADK agent (single `LlmAgent` or workflow agents like `SequentialAgent`, `LoopAgent`, `ParallelAgent`).

## 📊 Test Results Interpretation

| Status | Score | Meaning | Action Required |
|--------|-------|---------|----------------|
| ✅ **Perfect** | 4/4 (100%) | Agent properly configured | None - ready for use |
| ✅ **Good** | 3/4 (75%) | Agent works, minor AI variability | None - acceptable |
| ⚠️ **Review** | 2/4 (50%) | Possible configuration issue | Check agent setup |
| ❌ **Failed** | 0-1/4 | Configuration errors | Fix before using |

## 🧪 Test Categories

### 1. **Reflection Test** (`hello_world_reflection`)
- **Goal**: Basic response generation
- **Prompt**: "Write a Python function that prints `Hello, World!`, then answer with the text `Hello, World!`."
- **Pass Criteria**: ROUGE-L ≥ 0.01 (agent responded with relevant text)
- **What it catches**: Import errors, agent crashes, basic execution issues

### 2. **Tool Use Test** (`tool_calling_basic`)
- **Goal**: Tool invocation capability
- **Prompt**: "Find out what the population of Tokyo is."
- **Pass Criteria**: 
  - Tool was called (`tool_trajectory_avg_score: 1.0`)
  - Response contains relevant text (ROUGE-L ≥ 0.005)
- **What it catches**: Tool registration failures, tool calling issues

### 3. **ReAct Test** (`simple_lookup`)
- **Goal**: Iterative reasoning with tools
- **Prompt**: "Find out who produced the 2021 movie 'Dune' and give a short answer."
- **Pass Criteria**:
  - Tool was called (`tool_trajectory_avg_score: 1.0`)
  - Response contains relevant text (ROUGE-L ≥ 0.01)
- **What it catches**: Multi-step reasoning issues, tool integration problems

### 4. **Planning Test** (`plan_then_act`)
- **Goal**: Structured task execution
- **Prompt**: "Outline a short plan to extract a number from text, then output the number 123 from `ID:123`."
- **Pass Criteria**: ROUGE-L ≥ 0.01 (agent processed the request)
- **What it catches**: Task comprehension issues, execution flow problems

## 🚀 How to Run Tests

### Quick Test (Single Agent)
```bash
export GOOGLE_API_KEY=your_api_key_here
./tests/run_all_tests.sh adk-agentic-architectures/01_reflection/
```

### Test All Agents
```bash
./test_all_agents.sh
```

### Quick Sample Test (First 3 Agents)
```bash
./tests/test_sample_agents.sh
```

### Individual Test
```bash
adk eval adk-agentic-architectures/01_reflection/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json
```

### Interactive Testing (Fastest for Development)
```bash
adk web adk-agentic-architectures/01_reflection/
# Opens UI at http://localhost:8000
# Test queries immediately without running full test suite
```

## 🔧 Common Issues & Solutions

### Issue: "Tests passed: 0"
**Symptoms**: All tests failing
**Causes**: 
- Missing `__init__.py` or incorrect exports
- Import errors in agent code
- Missing required dependencies

**Solution**:
```bash
# Check structure first
python3 tests/validate_agent.py adk-agentic-architectures/your_agent/
```

### Issue: "tool_trajectory_avg_score: 0.0"
**Symptoms**: Tools not being called
**Causes**:
- Tools not properly registered
- Agent instructions don't encourage tool use
- Workflow agent sub-agents can't access tools

**Solution**:
```bash
# Test interactively to see tool calls
adk web adk-agentic-architectures/your_agent/
# Try: "Find the capital of France"
# Watch event stream for tool calls
```

### Issue: "response_match_score: 0.0"
**Symptoms**: Response doesn't match expected
**Causes**:
- Agent answering internal process instead of user question
- Agent outputting verification status instead of answer

**Solution**:
```bash
# See actual response
adk eval adk-agentic-architectures/your_agent/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json \
  --print_detailed_results
```

## 📁 Test File Structure

```
tests/
├── validate_agent.py              # Structure validation
├── run_all_tests.sh              # Single agent test runner
├── behavior/
│   ├── reflection/
│   │   ├── hello_world_reflection.test.json
│   │   └── test_config.json
│   ├── tool_use/
│   │   ├── tool_calling_basic.test.json
│   │   └── test_config.json
│   ├── react/
│   │   ├── simple_lookup.test.json
│   │   └── test_config.json
│   └── planning/
│       ├── plan_then_act.test.json
│       └── test_config.json
```

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

## 🔄 Development Workflow

### 1. Structure Validation (Instant)
```bash
python3 tests/validate_agent.py adk-agentic-architectures/your_agent/
```
- Catches import errors immediately
- Verifies module structure
- No API calls, runs in <1 second

### 2. Interactive Testing (Fast)
```bash
adk web adk-agentic-architectures/your_agent/
```
- Test queries immediately
- See full event stream and responses
- Faster than running full test suite

### 3. Single Test (Focused)
```bash
adk eval adk-agentic-architectures/your_agent/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json \
  --print_detailed_results
```
- See actual vs expected responses
- Check tool trajectory
- Identify specific issues

### 4. Full Test Suite (Complete)
```bash
./tests/run_all_tests.sh adk-agentic-architectures/your_agent/
```
- Comprehensive validation
- All test categories
- Final verification before deployment

## 📚 Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Loop Agents](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [Custom Agents](https://google.github.io/adk-docs/agents/custom-agents/)

---

## License

MIT