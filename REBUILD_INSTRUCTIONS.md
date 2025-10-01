# Architecture Rebuild Instructions

All critiques have been updated with:
- ✅ Analysis of what's wrong with current implementation
- ✅ Correct ADK patterns to use
- ✅ Working code examples using GENERIC capabilities (not domain-specific)
- ✅ Requirements checklist
- ✅ Common mistakes to avoid

## Status Summary

| Architecture | Current Status | Action Needed |
|--------------|----------------|---------------|
| 01_reflection | ✅ Passes 4/4 | None - keep as-is |
| 02_tool_use | ✅ Likely passes | Verify tests |
| 03_ReAct | ✅ Likely passes | Verify tests |
| 04_planning | ✅ Passes 4/4 | None - keep as-is |
| 05_multi_agent | ✅ Passes 4/4 | None - keep as-is |
| 06_PEV | ❌ Outputs "SUCCESS" not answer | Add Presenter agent |
| 07_blackboard | ❌ Wrong architecture | Rebuild with Custom BaseAgent |
| 08_episodic_semantic | ❓ Check status | Use memory tools |
| 09_tree_of_thoughts | ❓ Check status | Use ParallelAgent |
| 10_mental_loop | ❓ Check status | Needs Custom BaseAgent |
| 11_meta_controller | ❌ Wrong architecture | Rebuild with Custom BaseAgent |
| 12_graph | ❓ Check status | Single Agent with memory |
| 13_ensemble | ❓ Check status | ParallelAgent + Aggregator |
| 14_dry_run | ❓ Check status | SequentialAgent or Custom |
| 15_RLHF | ❓ Check status | SequentialAgent + LoopAgent |
| 16_cellular_automata | ❓ Check status | LoopAgent |
| 17_reflexive_metacognitive | ❌ Import errors | Fix imports, Custom BaseAgent |

## Quick Iteration Process

### 1. Structure Validation First
```bash
python3 tests/validate_agent.py adk-agentic-architectures/XX_name/
```
Catches: import errors, missing files, wrong exports

### 2. Interactive Testing
```bash
export GOOGLE_API_KEY=your_key
adk web adk-agentic-architectures/XX_name/
```
- Test in browser at localhost:8000
- See actual responses immediately
- Check if agent answers questions or just runs internal process

### 3. Single Test Check
```bash
adk eval adk-agentic-architectures/XX_name/ \
  tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json \
  --print_detailed_results
```
See actual vs expected responses

### 4. Full Test Suite
```bash
./tests/run_all_tests.sh adk-agentic-architectures/XX_name/
```
Aim for 3-4/4 passing

## Key Principles

### Use Generic Capabilities

**DO**:
- ✅ RetrievalSpecialist (searches/gathers info)
- ✅ AnalysisSpecialist (reasons/analyzes)
- ✅ GenerationSpecialist (creates content/code)
- ✅ SynthesisSpecialist (combines results)
- ✅ Evaluator (judges quality)
- ✅ Simulator (predicts outcomes)

**DON'T**:
- ❌ MathAgent, ResearchAgent (domain-specific)
- ❌ NewsAnalyst, TechnicalAnalyst (use-case specific)
- ❌ CodingAgent, FinancialAgent (not reusable)

### Ensure User Gets Actual Answers

**Common bug**: Internal process outputs (like "SUCCESS", "APPROVED", "PLAN CREATED") becoming final response

**Fix**: Add final Presenter/Synthesizer agent that outputs user-facing answer

### When to Use Which Pattern

| Need | ADK Pattern | Example |
|------|-------------|---------|
| Fixed sequence | SequentialAgent | Reflection, Planning |
| Parallel execution | ParallelAgent | Ensemble, Tree of Thoughts |
| Bounded retry loop | LoopAgent | RLHF, Cellular Automata |
| Conditional routing | Custom BaseAgent | Blackboard, Meta-Controller, Mental Loop |
| Simple tool use | Single Agent | Tool Use, ReAct |

## Testing Philosophy

**These are GENERAL-PURPOSE tests**:
- They test if agent can answer questions
- They test if agent can use tools
- They test if agent produces useful outputs

**They are NOT testing**:
- Domain-specific accuracy
- Complex multi-step reasoning quality
- Specific architectural purity

**If agent fails**: It means agent isn't answering user questions properly, not that tests are wrong.

Good architecture serves users, not the other way around.
