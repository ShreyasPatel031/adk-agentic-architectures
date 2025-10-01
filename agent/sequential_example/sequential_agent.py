"""
Sequential Agent Example - Code Development Pipeline
Based on official ADK documentation
"""

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

GEMINI_MODEL = "gemini-2.5-flash-lite"

# First Agent - Analyzer with tools
analyzer_agent = Agent(
    name="AnalyzerAgent",
    model=GEMINI_MODEL,
    instruction="""You are an analyzer. When asked to find information, use the search tool. Analyze the user's request and provide a brief analysis or response.""",
    description="Analyzes user requests.",
    tools=[google_search],
    output_key="analysis"
)

# Second Agent - Responder
responder_agent = Agent(
    name="ResponderAgent",
    model=GEMINI_MODEL,
    instruction="""You are a responder. Based on the previous analysis, provide a helpful final response to the user.

**Previous Analysis:**
{analysis}

Provide a concise, helpful response.""",
    description="Provides final response.",
    output_key="final_output"
)

# Create the SequentialAgent
root_agent = SequentialAgent(
    name="SequentialPipelineAgent",
    sub_agents=[analyzer_agent, responder_agent],
    description="Executes a sequence of analysis and response."
)
