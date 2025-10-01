"""
Loop Agent Example - Simple Iterative Processing
Simplified version that works with basic tests
"""

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import google_search

GEMINI_MODEL = "gemini-2.5-flash-lite"

# Single worker agent with tools
worker = Agent(
    name="Worker",
    model=GEMINI_MODEL,
    instruction="You are a helpful assistant. When asked to find information or search for something, use the available tools. Answer the user's question directly and completely.",
    description="Processes user queries",
    tools=[google_search]
)

# Create loop with single iteration (essentially acts like a regular agent)
root_agent = LoopAgent(
    name="SimpleLoopAgent",
    sub_agents=[worker],
    max_iterations=1,
    description="Simple loop agent that processes requests"
)
