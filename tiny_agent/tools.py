import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
import json


class Tool:
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.func = func
        self.name = name or func.__name__
        self.description = description or inspect.getdoc(func) or ""
        self._schema = self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        sig = inspect.signature(self.func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation is not inspect.Parameter.empty:
                if param.annotation is int:
                    param_type = "integer"
                elif param.annotation is float:
                    param_type = "number"
                elif param.annotation is bool:
                    param_type = "boolean"
                elif param.annotation is list or param.annotation is List:
                    param_type = "array"
                elif param.annotation is dict or param.annotation is Dict:
                    param_type = "object"

            properties[param_name] = {"type": param_type}
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def get_schema(self) -> Dict[str, Any]:
        return self._schema

    async def execute(self, **kwargs) -> str:
        try:
            if inspect.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)

            if isinstance(result, (dict, list)):
                return json.dumps(result, ensure_ascii=False)
            return str(result)
        except Exception as e:
            return f"Error executing tool {self.name}: {str(e)}"


def tool(name: Optional[str] = None, description: Optional[str] = None):
    def decorator(func: Callable):
        t = Tool(func, name, description)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await t.execute(**kwargs)

        wrapper.__tool__ = t
        return wrapper

    return decorator
