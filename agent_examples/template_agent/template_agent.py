"""
Template ADK Agent
------------------
This is a template for creating new ADK agents.
Modify this file to implement your specific agent logic.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search


def create_agent() -> Agent:
    """Create and configure the agent."""
    return Agent(
        name="TemplateAgent",
        model="gemini-2.5-flash-lite",
        instruction="""You are a helpful AI assistant.
        
Your job is to:
- Answer user questions accurately and helpfully
- Use tools when needed to gather information
- Provide clear, concise responses
- Be polite and professional

When you need to search for information, use the available tools.""",
        tools=[google_search]  # Add tools as needed
    )


# Create the root agent
root_agent = create_agent()
