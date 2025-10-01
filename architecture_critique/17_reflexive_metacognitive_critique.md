# Critique for 17_Reflexive_Metacognitive Agent

## Implementation Analysis

Current implementation has import errors: `No module named 'google.adk.runtime'`

### Correct Implementation Required

The Reflexive Metacognitive architecture analyzes queries and routes based on confidence.

### Core Pattern
Self-Check → Route (if confident → direct answer, if uncertain → use tools, if risky → escalate)

### Correct ADK Implementation

**Use**: Custom BaseAgent with conditional routing

```python
from google.adk.agents import BaseAgent, Agent
from google.adk.agents.invocation_context import InvocationContext  # NOT google.adk.runtime
from google.adk.events import Event
from google.genai import types

class SelfCheckAgent(BaseAgent):
    name: str = "self_check"
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Compute confidence (0.0 to 1.0)
        confidence = 0.72  # Replace with actual scoring logic
        ctx.session.state["confidence"] = confidence
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"confidence={confidence}")])
        )

class ConditionalRouter(BaseAgent):
    name: str = "router"
    safe_agent: Agent
    risky_agent: Agent
    threshold: float = 0.6
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        conf = ctx.session.state.get("confidence", 0.0)
        
        # Programmatic routing
        chosen = self.risky_agent if conf >= self.threshold else self.safe_agent
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Routing to {chosen.name}")])
        )
        
        # Delegate to chosen agent
        async for event in chosen.run_async(ctx):
            yield event

# Create sub-agents
safe = Agent(name="SafePath", model="gemini-2.5-flash-lite", instruction="Conservative response")
risky = Agent(name="RiskyPath", model="gemini-2.5-flash-lite", instruction="Aggressive response", tools=[google_search])

# Assemble
from google.adk.agents import SequentialAgent
root_agent = SequentialAgent(
    name="Reflexive",
    sub_agents=[
        SelfCheckAgent(),
        ConditionalRouter(safe_agent=safe, risky_agent=risky, threshold=0.6)
    ]
)
```

### Requirements
- ✅ Must use InvocationContext (NOT LocalContext or google.adk.runtime)
- ✅ Must create Event with invocation_id and types.Content
- ✅ Must use ctx.session.state for sharing data
- ✅ Must properly type-hint AsyncGenerator[Event, None]
- ✅ Router must be Custom BaseAgent with Pydantic field declarations

### Common Mistakes to Avoid
- ❌ Importing from google.adk.runtime (doesn't exist)
- ❌ Using ctx.event() (doesn't exist)
- ❌ Using ctx.input_text (doesn't exist)
- ❌ Setting instance vars without Pydantic field declarations
- ❌ Not properly initializing BaseAgent subclass with Pydantic model
