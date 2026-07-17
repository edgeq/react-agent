import inspect
from typing import Callable, Any
from pydantic import BaseModel, create_model

class Tool:
    def __init__(self, func: Callable[..., Any]):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""

        self.model = self._create_validator_model()

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

# --- TEMPORARY TEST BLOCK ---
if __name__ == "__main__":
    # 1. Define a dummy function to test with
    def dummy_tool(query: str, limit: int = 5) -> str:
        """This is a dummy search tool description."""
        return f"Searching for {query} with limit {limit}"

    # 2. Instantiate our Tool wrapper
    test_tool = Tool(dummy_tool)

    # 3. Print the results to see if the inspect code works!
    print("Tool Name:", test_tool.name)
    print("Tool Description:", test_tool.description)
    print("Dynamic Pydantic Model:", test_tool.model)
    print("Generated Schema:", test_tool.model.model_json_schema())