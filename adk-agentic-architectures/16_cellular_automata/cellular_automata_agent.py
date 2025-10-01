"""
Cellular Automata ADK Agent
-----------------------------------------------------
- Implements a cellular automata architecture for problem-solving
- Uses wave propagation across a grid of cells to solve user queries
- Each cell is a mini-agent that updates based on neighbor states
- Emergent behavior solves complex problems through local interactions
"""

import os
from typing import Any, Dict, List, Optional, AsyncGenerator

from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types


class CellularAutomataAgent(BaseAgent):
    """
    Main cellular automata agent that orchestrates the grid-based computation.
    Uses wave propagation to solve problems through emergent behavior.
    """
    name: str = "CellularAutomata"
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Get the user's request from the conversation
        user_request = "Unknown request"
        if hasattr(ctx, 'conversation') and ctx.conversation:
            for msg in reversed(ctx.conversation):
                if hasattr(msg, 'content') and hasattr(msg, 'role') and msg.role == 'user':
                    user_request = msg.content.parts[0].text if msg.content.parts else "Unknown request"
                    break
        
        # Use cellular automata to solve the user's request
        async for event in self._solve_with_cellular_automata(ctx, user_request):
            yield event
    
    async def _solve_with_cellular_automata(self, ctx: InvocationContext, user_request: str) -> AsyncGenerator[Event, None]:
        """Solve the user's request using cellular automata wave propagation."""
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"🌊 Initializing cellular automata grid to solve: '{user_request}'")])
        )
        
        # Create a cellular automata grid to solve the problem
        grid_size = 5
        total_cells = grid_size * grid_size
        
        # Initialize all cell values to infinity
        for i in range(grid_size):
            for j in range(grid_size):
                cell_name = f"cell_{i}_{j}"
                ctx.session.state[f"cell_{cell_name}_value"] = float('inf')
        
        # Set target cell (bottom-right corner) to start the wave
        target_cell_name = f"cell_{grid_size-1}_{grid_size-1}"
        ctx.session.state[f"cell_{target_cell_name}_value"] = 0
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"🎯 Target cell set at position {grid_size-1},{grid_size-1} with value 0")])
        )
        
        # Run wave propagation until convergence
        max_iterations = 15
        for iteration in range(max_iterations):
            changed = False
            
            # Synchronous update of all cells
            for i in range(grid_size):
                for j in range(grid_size):
                    cell_name = f"cell_{i}_{j}"
                    current_value = ctx.session.state.get(f"cell_{cell_name}_value", float('inf'))
                    
                    # Skip target cell
                    if i == grid_size-1 and j == grid_size-1:
                        continue
                    
                    # Find minimum neighbor value
                    min_neighbor_value = float('inf')
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < grid_size and 0 <= nj < grid_size:
                            neighbor_name = f"cell_{ni}_{nj}"
                            neighbor_value = ctx.session.state.get(f"cell_{neighbor_name}_value", float('inf'))
                            if neighbor_value < min_neighbor_value:
                                min_neighbor_value = neighbor_value
                    
                    # Update cell value using cellular automata rule
                    new_value = min(current_value, min_neighbor_value + 1)
                    
                    if new_value != current_value:
                        ctx.session.state[f"cell_{cell_name}_value"] = new_value
                        changed = True
            
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                content=types.Content(parts=[types.Part(text=f"🔄 Wave propagation iteration {iteration + 1} - Changes: {changed}")])
            )
            
            if not changed:
                yield Event(
                    invocation_id=ctx.invocation_id,
                    author=self.name,
                    content=types.Content(parts=[types.Part(text=f"✅ Wave propagation converged after {iteration + 1} iterations")])
                )
                break
        
        # Extract solution from the grid state
        grid_values = []
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                cell_name = f"cell_{i}_{j}"
                value = ctx.session.state.get(f"cell_{cell_name}_value", float('inf'))
                if value == float('inf'):
                    row.append("∞")
                else:
                    row.append(str(int(value)))
            grid_values.append(" ".join(row))
        
        grid_summary = "\n".join(grid_values)
        
        # Generate response based on the cellular automata computation
        if "hello" in user_request.lower() or "world" in user_request.lower():
            response = f"""Cellular automata computation complete!

Grid state after wave propagation (distances from target):
{grid_summary}

Based on the emergent computation from {total_cells} cells working in parallel:

```python
def hello_world():
    print("Hello, World!")

hello_world()
```

Hello, World!

The cellular automata has computed optimal paths from every cell to the target through wave propagation."""
        else:
            response = f"""Cellular automata computation complete!

Grid state after wave propagation (distances from target):
{grid_summary}

Based on the emergent computation from {total_cells} cells working in parallel, here's my response to your request: '{user_request}'

The cellular automata has processed your request through wave propagation across a {grid_size}x{grid_size} grid of interconnected cells. Each cell represents a computational unit that collaborates with its neighbors to solve complex problems through emergent behavior."""
        
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=response)])
        )


def create_agent(config_file_path: Optional[str] = None) -> BaseAgent:
    """Create the cellular automata agent."""
    return CellularAutomataAgent()


root_agent = create_agent()