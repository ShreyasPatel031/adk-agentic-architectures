"""
Testing ChatGPT's proposed RLHF implementation
"""
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, SequentialAgent, LoopAgent
from google.adk.events import Event
from google.genai import types

def _text_event(ctx, author: str, text: str) -> Event:
    return Event(
        invocation_id=ctx.invocation_id,
        author=author,
        content=types.Content(parts=[types.Part(text=text)]),
    )

class DraftAgent(BaseAgent):
    name: str = "draft_agent"
    description: str = "Writes an initial draft."

    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        yield _text_event(ctx, self.name, "Draft: placeholder text for RLHF loop")

class CriticAgent(BaseAgent):
    name: str = "critic_agent"
    description: str = "Critiques the current draft."

    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        yield _text_event(ctx, self.name, "Critique: identify issues A/B/C")

class ReviseAgent(BaseAgent):
    name: str = "revise_agent"
    description: str = "Revises the draft based on critique."

    async def _run_async_impl(self, ctx) -> AsyncGenerator[Event, None]:
        yield _text_event(ctx, self.name, "Revised: applied fixes to A/B/C")

inner_cycle = SequentialAgent(
    name="rlhf_inner_cycle",
    sub_agents=[CriticAgent(), ReviseAgent()],
)

root_agent = SequentialAgent(
    name="rlhf_root",
    sub_agents=[
        DraftAgent(),
        LoopAgent(name="rlhf_loop", sub_agents=[inner_cycle], max_iterations=3),
    ],
)
