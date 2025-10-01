"""
Cellular Automata ADK Agent
-----------------------------------------------------
- Implements a simulation pattern with repeated grid updates
- Uses LoopAgent with custom BaseAgent for grid state management
- Demonstrates Conway's Game of Life or similar cellular automata
"""

import os
import yaml
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field

from google.adk.agents import Agent, BaseAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

# Built-in tools registry
_BUILTIN_TOOL_REGISTRY: Dict[str, Any] = {}

def _maybe_import_builtin_tools() -> None:
    """Lazy load built-in tools to avoid import errors."""
    global _BUILTIN_TOOL_REGISTRY
    if _BUILTIN_TOOL_REGISTRY:
        return
    try:
        from google.adk.tools import google_search
        _BUILTIN_TOOL_REGISTRY["google_search"] = google_search
    except ImportError:
        pass

def resolve_tools(names: List[str]) -> List[Any]:
    _maybe_import_builtin_tools()
    tools = []
    for n in names:
        t = _BUILTIN_TOOL_REGISTRY.get(n)
        if t:
            tools.append(t)
    return tools

class CellularStepAgent(BaseAgent):
    """
    Custom agent that performs one step of cellular automata simulation.
    Maintains grid state in session.state and applies CA rules.
    """
    name: str = "CellularStep"
    
    def apply_ca_rules(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Apply Conway's Game of Life rules (simplified example).
        - Any live cell with 2-3 neighbors survives
        - Any dead cell with exactly 3 neighbors becomes alive
        - All other cells die or stay dead
        """
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        new_grid = [[0] * cols for _ in range(rows)]
        
        for i in range(rows):
            for j in range(cols):
                # Count live neighbors
                neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < rows and 0 <= nj < cols:
                            neighbors += grid[ni][nj]
                
                # Apply rules
                if grid[i][j] == 1:  # Live cell
                    if neighbors in [2, 3]:
                        new_grid[i][j] = 1
                else:  # Dead cell
                    if neighbors == 3:
                        new_grid[i][j] = 1
        
        return new_grid
    
    def initialize_grid(self, size: int = 10) -> List[List[int]]:
        """Initialize a simple pattern (e.g., glider or blinker)."""
        grid = [[0] * size for _ in range(size)]
        # Simple blinker pattern in the center
        center = size // 2
        grid[center][center - 1] = 1
        grid[center][center] = 1
        grid[center][center + 1] = 1
        return grid
    
    def grid_to_string(self, grid: List[List[int]]) -> str:
        """Convert grid to a visual string representation."""
        return "\n".join("".join("█" if cell else "·" for cell in row) for row in grid)
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Get current grid from state or initialize
        grid = ctx.session.state.get("grid")
        if grid is None:
            grid = self.initialize_grid(10)
            ctx.session.state["grid"] = grid
        
        # Apply cellular automata rules
        new_grid = self.apply_ca_rules(grid)
        ctx.session.state["grid"] = new_grid
        
        # Track iteration count
        tick = ctx.session.state.get("tick", 0) + 1
        ctx.session.state["tick"] = tick
        
        # Create visual representation
        grid_str = self.grid_to_string(new_grid)
        live_cells = sum(sum(row) for row in new_grid)
        
        response = f"Generation {tick} - Live cells: {live_cells}\n{grid_str}"
        
        # Yield event with proper types
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            content=types.Content(parts=[types.Part(text=response)])
        )


@dataclass
class AgentConfig:
    name: str
    architecture: str
    max_iterations: int = 5

def create_agent(config_file_path: Optional[str] = None) -> BaseAgent:
    """Create the cellular automata agent."""
    if config_file_path is None:
        config_file_path = os.path.join(os.path.dirname(__file__), "config", "cellular_automata_agent.yaml")
    
    # Load config
    with open(config_file_path, "r", encoding="utf-8") as file:
        config_yaml = yaml.safe_load(file)
    
    max_iterations = config_yaml.get("max_iterations", 5)
    
    # Create the loop agent with cellular step
    root_agent = LoopAgent(
        name="CellularAutomata",
        sub_agents=[CellularStepAgent()],
        max_iterations=max_iterations
    )
    
    return root_agent

root_agent = create_agent()
