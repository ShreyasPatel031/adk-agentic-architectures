"""
Parallel Agent Example - Multi-Perspective Analysis
Based on official ADK documentation pattern
"""

from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search

GEMINI_MODEL = "gemini-2.5-flash-lite"

# Create multiple analysts that work in parallel
analyst1 = Agent(
    name="Analyst1",
    model=GEMINI_MODEL,
    instruction="""You are a practical analyst. When asked to find information, use the search tool. Analyze the user's request from a practical, real-world perspective.
Provide a concise analysis focusing on practical implications and actionable insights.""",
    description="Provides practical analysis",
    tools=[google_search]
)

analyst2 = Agent(
    name="Analyst2",
    model=GEMINI_MODEL,
    instruction="""You are a theoretical analyst. Analyze the user's request from a theoretical, conceptual perspective.
Provide a concise analysis focusing on underlying principles and theoretical frameworks.""",
    description="Provides theoretical analysis"
)

analyst3 = Agent(
    name="Analyst3",
    model=GEMINI_MODEL,
    instruction="""You are a critical analyst. Analyze the user's request from a critical perspective.
Provide a concise analysis focusing on potential issues, limitations, and areas of concern.""",
    description="Provides critical analysis"
)

# Create the ParallelAgent
root_agent = ParallelAgent(
    name="ParallelAnalysisAgent",
    sub_agents=[analyst1, analyst2, analyst3],
    description="Executes multiple analyses in parallel for diverse perspectives."
)
