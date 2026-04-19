import pytest
from typing import List, Dict
from tiny_agent.tools import Tool, tool


@pytest.mark.asyncio
async def test_tool_schema_types():
    def dummy_func(a: int, b: float, c: bool, d: list, e: dict, f: List, g: Dict):
        pass

    t = Tool(dummy_func)
    schema = t.get_schema()
    props = schema["function"]["parameters"]["properties"]

    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "number"
    assert props["c"]["type"] == "boolean"
    assert props["d"]["type"] == "array"
    assert props["e"]["type"] == "object"
    assert props["f"]["type"] == "array"
    assert props["g"]["type"] == "object"


@pytest.mark.asyncio
async def test_tool_execute_async():
    async def async_func(x: int) -> int:
        return x * 2

    t = Tool(async_func)
    result = await t.execute(x=5)
    assert result == "10"


@pytest.mark.asyncio
async def test_tool_execute_json_return():
    def dict_func() -> dict:
        return {"key": "value"}

    def list_func() -> list:
        return [1, 2, 3]

    t_dict = Tool(dict_func)
    result_dict = await t_dict.execute()
    assert result_dict == '{"key": "value"}'

    t_list = Tool(list_func)
    result_list = await t_list.execute()
    assert result_list == "[1, 2, 3]"


@pytest.mark.asyncio
async def test_tool_execute_exception():
    def error_func():
        raise ValueError("Test error")

    t = Tool(error_func)
    result = await t.execute()
    assert "Error executing tool error_func: Test error" in result


@pytest.mark.asyncio
async def test_tool_decorator_wrapper():
    @tool(name="test_wrapper")
    async def my_func(x: int):
        return x + 1

    result = await my_func(x=5)
    assert result == "6"


@pytest.mark.asyncio
async def test_tools_decorator():
    @tool(name="add_numbers", description="Adds two numbers")
    def add(a: int, b: int) -> int:
        return a + b

    assert hasattr(add, "__tool__")
    schema = add.__tool__.get_schema()
    assert schema["function"]["name"] == "add_numbers"

    result = await add.__tool__.execute(a=5, b=3)
    assert result == "8"
