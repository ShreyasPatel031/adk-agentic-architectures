# CRITICAL: Custom BaseAgent Event Creation

## The Bug That Breaks Everything

**WRONG** (causes "NoneType has no len()" errors):
```python
yield Event(author=self.name, content={"parts": [{"text": "response"}]})
```

**CORRECT**:
```python
from google.genai import types

yield Event(
    invocation_id=ctx.invocation_id,
    author=self.name,
    content=types.Content(parts=[types.Part(text="response")])
)
```

## Why This Matters

ALL Custom BaseAgent implementations MUST:
1. ✅ Import `from google.genai import types`
2. ✅ Include `invocation_id=ctx.invocation_id` in every Event
3. ✅ Use `types.Content(parts=[types.Part(text=...)])` not dicts
4. ✅ Set `author=self.name` or the agent's name

**This applies to**: 06_PEV, 07_blackboard, 10_mental_loop, 11_meta_controller, 14_dry_run, 17_reflexive_metacognitive

## Testing Your Events

```python
# Correct Event creation template
from google.adk.events import Event
from google.genai import types

def create_text_event(ctx, agent_name: str, text: str) -> Event:
    return Event(
        invocation_id=ctx.invocation_id,
        author=agent_name,
        content=types.Content(parts=[types.Part(text=text)])
    )

# Use in _run_async_impl
async def _run_async_impl(self, ctx):
    yield create_text_event(ctx, self.name, "My response")
```

## How to Verify

```bash
# This will fail with NoneType error if Events are wrong:
adk eval your_agent/ tests/behavior/reflection/hello_world_reflection.test.json \
  --config_file_path=tests/behavior/reflection/test_config.json
```

If you see:
- ✅ "Tests passed: 1" → Events are correct
- ❌ "TypeError: object of type 'NoneType' has no len()" → Events are wrong (using dicts instead of types.Content)

## There Is No "Testing Framework Issue"

The framework works fine. The bug is in Custom BaseAgent Event creation.
