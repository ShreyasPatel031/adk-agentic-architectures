# Critique for 15_RLHF Agent

## Correct Implementation Required

The RLHF (Reinforcement Learning from Human Feedback) architecture requires:

### Core Pattern
Draft → [Critique → Revise] in a loop until quality threshold or max iterations

### Correct ADK Implementation

**Use**: `SequentialAgent` containing `LoopAgent` with nested `SequentialAgent`

```python
# Pattern that works:
draft_agent = Agent(name="Draft", instruction="Generate initial draft", output_key="draft")

critic_agent = Agent(name="Critic", instruction="Critique the draft: {draft}", output_key="critique")

revise_agent = Agent(name="Revise", instruction="Revise draft using critique", output_key="draft")

inner_cycle = SequentialAgent(
    name="CriticRevise",
    sub_agents=[critic_agent, revise_agent]
)

root_agent = SequentialAgent(
    name="RLHF",
    sub_agents=[
        draft_agent,
        LoopAgent(name="refinement", sub_agents=[inner_cycle], max_iterations=3)
    ]
)
```

### Requirements
- ✅ Must have 3 distinct agents: Draft, Critic, Revise
- ✅ Must use LoopAgent for the iterative refinement
- ✅ Must use max_iterations (not custom exit conditions)
- ✅ Must pass draft between agents using output_key and state placeholders

### Common Mistakes to Avoid
- ❌ Using single agent with "act like critic then reviser" instructions
- ❌ Using Custom BaseAgent when SequentialAgent+LoopAgent suffices
- ❌ Not connecting agents via state (output_key/placeholders)
- ❌ Using incorrect module paths (google.adk.runtime doesn't exist)
