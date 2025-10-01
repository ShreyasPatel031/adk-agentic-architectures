# Critique for 16_Cellular_Automata Agent

## Correct Implementation Required

Cellular Automata is a simulation pattern with repeated grid updates.

### Core Pattern
Initialize grid → Update grid state N times → Return final grid

### Correct ADK Implementation

**Use**: `LoopAgent` with single step agent

```python
class CellularStepAgent(BaseAgent):
    name: str = "cellular_step"
    
    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        # Get current grid from state or initialize
        grid = ctx.session.state.get("grid", [[0]*10 for _ in range(10)])
        
        # Apply cellular automata rules (Conway's Game of Life, etc.)
        new_grid = apply_ca_rules(grid)
        ctx.session.state["grid"] = new_grid
        
        # Track iteration count
        tick = ctx.session.state.get("tick", 0) + 1
        ctx.session.state["tick"] = tick
        
        # Yield event
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Grid updated: generation {tick}")])
        )

root_agent = LoopAgent(
    name="CellularAutomata",
    sub_agents=[CellularStepAgent()],
    max_iterations=10
)
```

### Requirements
- ✅ Must use LoopAgent with max_iterations
- ✅ Must maintain grid state in ctx.session.state
- ✅ Must properly create Event objects (no ctx.event())
- ✅ Must increment iteration counter in state

### Common Mistakes to Avoid
- ❌ Using instance variables (_tick) instead of session state
- ❌ Calling ctx.event() (doesn't exist)
- ❌ Not properly initializing grid state
- ❌ Using until= parameter (doesn't exist in ADK)
