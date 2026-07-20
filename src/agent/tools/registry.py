import json
import inspect
from typing import Callable, Any
from pydantic import BaseModel, create_model, ValidationError

class Tool:
    def __init__(self, func: Callable[..., Any]):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""

        self.model = self._create_validator_model()
        self.schema = self._generate_schema()

    def _create_validator_model(self) -> type[BaseModel]:
        sig = inspect.signature(self.func)
        fields = {}
        for name, param in sig.parameters.items():
            if param.name == "self" or param.name == "cls":
                continue

            annotation = param.annotation
            if annotation is inspect.Parameter.empty:
               annotation = str

            default = param.default
            if default == inspect.Parameter.empty:
                default = ...
                
            fields[name] = (annotation, default)

        model_name = f"{self.name.capitalize()}Input"

        return create_model(model_name, **fields)
    
    def _generate_schema(self) -> dict[str, Any]:
        pydantic_schema = self.model.model_json_schema()
        schema_properties = pydantic_schema['properties']
        open_ai_schema = {
            "strict": True,
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        }
        for key, value in schema_properties.items():
            value.pop("title", None)
            open_ai_schema["parameters"]["properties"][key] = value
            open_ai_schema["parameters"]["required"].append(key)
        return open_ai_schema

_registry: dict[str, Tool] = {}

def tool(func: Callable[..., Any]) -> Callable[..., Any]:
    registered_tool = Tool(func)
    _registry[registered_tool.name] = registered_tool
    return func;

def execute_tool(name: str, arguments_json: str) -> str:
    tool_to_use = _registry.get(name)

    if not tool_to_use:
        return f"Error: Tool '{name}' not found"

    try:
        args = json.loads(arguments_json)
    except Exception as e:
        return f"Error: Invalid JSON arguments: {str(e)}"

    try:
        validated_data = tool_to_use.model(**args)
    except ValidationError as e:
        return f"Error: Invalid Tool arguments: {str(e)}"
    
    try: 
        result = tool_to_use.func(**validated_data.model_dump())
        return str(result)
    except Exception as e:
        return f"Error executing tool: {str(e)}"

def get_tool_schemas() -> list[dict[str, Any]]:
    """Returns all registered tool schemas for the OpenAI API"""
    tool_schema_list = []
    for _, tool in _registry.items():
        tool_schema_list.append(tool.schema)
    return tool_schema_list
