# Tools and @tool Decorator

Creating custom tools in `tiny-agent-py` is incredibly simple. Any Python function can be exposed to the LLM using the `@tool` decorator.

## Usage

```python
from tiny_agent.tools import tool

@tool()
def calculate_sum(a: int, b: int) -> int:
    """
    Calculates the sum of two integers.
    """
    return a + b
```

## Requirements
1. **Type Hints**: You must provide type hints for all arguments and the return value. This is how the agent generates the tool schema for the LLM.
2. **Docstring**: You must provide a docstring. The LLM reads this description to understand what the tool does and when to use it.

When you initialize the agent, simply pass the function in the `tools` list:
```python
agent = Agent(tools=[calculate_sum])
```
