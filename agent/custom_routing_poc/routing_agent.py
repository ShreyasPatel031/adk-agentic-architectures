"""
POC: ADK Custom BaseAgent with Conditional Routing
Tests if we can implement graph-like conditional logic in ADK
"""

from typing import AsyncGenerator
from google.adk.agents import Agent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search

class ConditionalRoutingAgent(BaseAgent):
    """Custom agent that routes based on query analysis"""
    
    analyzer: Agent
    search_agent: Agent
    direct_agent: Agent
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Step 1: Run analyzer
        async for event in self.analyzer.run_async(ctx):
            yield event
        
        # Step 2: Get routing decision from state
        decision = ctx.session.state.get("routing_decision", "DIRECT").strip().upper()
        
        # Step 3: Route conditionally
        if "SEARCH" in decision:
            async for event in self.search_agent.run_async(ctx):
                yield event
        else:
            async for event in self.direct_agent.run_async(ctx):
                yield event

# Create sub-agents
analyzer = Agent(
    name="Analyzer",
    model="gemini-2.5-flash-lite",
    instruction="""Analyze the user's query and output ONLY one word:
- Output "SEARCH" if they ask to find information, look something up, or search
- Output "DIRECT" if they ask something you can answer directly
- Output only one word: SEARCH or DIRECT""",
    output_key="routing_decision"
)

search_agent = Agent(
    name="SearchAgent",
    model="gemini-2.5-flash-lite",
    instruction="You are a search specialist. Use google_search to find information. Provide complete answers.",
    tools=[google_search]
)

direct_agent = Agent(
    name="DirectAgent",
    model="gemini-2.5-flash-lite",
    instruction="You are a helpful assistant. Answer the user's question directly and completely."
)

# Create the custom routing agent
root_agent = ConditionalRoutingAgent(
    name="ConditionalRoutingPOC",
    analyzer=analyzer,
    search_agent=search_agent,
    direct_agent=direct_agent
)
